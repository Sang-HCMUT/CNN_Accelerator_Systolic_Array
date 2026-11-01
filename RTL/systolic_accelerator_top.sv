`timescale 1ns / 1ps

// Module: systolic_accelerator_top.sv
// Pure Structural Top-Level INT8 Systolic GEMM Accelerator.
// Modular design with dedicated sub-blocks:
//   1. gemm_controller: Central FSM & Sequencer
//   2. matrix_buffer_a: On-chip Storage for Weight Matrix A
//   3. matrix_buffer_b: On-chip Storage for Activation Matrix B
//   4. systolic_skew_unit: Input Skewing Pipeline Registers
//   5. systolic_array_core: 2D Processing Element Mesh
//   6. quantize_relu_unit: Post-Processing Datapath
//   7. matrix_buffer_c: On-chip Output & Debug Storage

module systolic_accelerator_top #(
    parameter ARRAY_SIZE = 8,   // Size of 2D systolic array (8x8 = 64 PEs)
    parameter DATA_WIDTH = 8,   // INT8 operands
    parameter ACC_WIDTH  = 32,  // INT32 accumulator
    parameter MAX_K      = 16   // Maximum inner dimension K supported in buffers
)(
    input  logic                                          clk,
    input  logic                                          rst_n,
    
    // Command & Status
    input  logic                                          start,
    input  logic [7:0]                                    k_dim,        // Length of inner dimension K
    input  logic                                          bypass_relu,
    input  logic [4:0]                                    shift_bits,   // Quantization shift
    output logic                                          done,
    output logic                                          busy,
    output logic                                          error,
    
    // Host Write Interface for Matrix A (Row-major, ARRAY_SIZE x MAX_K)
    input  logic                                          wr_a_en,
    input  logic [$clog2(ARRAY_SIZE*MAX_K)-1:0]           wr_a_addr,
    input  logic signed [DATA_WIDTH-1:0]                  wr_a_data,
    input  logic                                          wr_packed_a_en,
    input  logic [$clog2(ARRAY_SIZE*MAX_K)-3:0]           wr_packed_a_addr,
    input  logic [31:0]                                   wr_packed_a_data,
    
    // Host Write Interface for Matrix B (Row-major, MAX_K x ARRAY_SIZE)
    input  logic                                          wr_b_en,
    input  logic [$clog2(ARRAY_SIZE*MAX_K)-1:0]           wr_b_addr,
    input  logic signed [DATA_WIDTH-1:0]                  wr_b_data,
    input  logic                                          wr_packed_b_en,
    input  logic [$clog2(ARRAY_SIZE*MAX_K)-3:0]           wr_packed_b_addr,
    input  logic [31:0]                                   wr_packed_b_data,
    
    // Host Read Interface for Output Matrix C (Row-major, ARRAY_SIZE x ARRAY_SIZE)
    input  logic [$clog2(ARRAY_SIZE*ARRAY_SIZE)-1:0]      rd_c_addr,
    output logic signed [DATA_WIDTH-1:0]                  rd_c_data,
    output logic signed [ACC_WIDTH-1:0]                   rd_c_acc_data,
    input  logic [$clog2(ARRAY_SIZE*ARRAY_SIZE)-3:0]      rd_c_packed_addr,
    output logic [31:0]                                   rd_c_packed_int8
);

    localparam ADDR_A_WIDTH = $clog2(ARRAY_SIZE * MAX_K);
    localparam ADDR_B_WIDTH = $clog2(ARRAY_SIZE * MAX_K);
    localparam ADDR_C_WIDTH = $clog2(ARRAY_SIZE * ARRAY_SIZE);

    // Internal Structural Interconnect Wires
    
    // Controller control wires
    logic        sys_en;
    logic        sys_clear_acc;
    logic        stream_en;
    logic [7:0]  k_step;
    logic        ctrl_quant_in_en;
    logic [$clog2(ARRAY_SIZE)-1:0] ctrl_readout_r;
    logic [$clog2(ARRAY_SIZE)-1:0] ctrl_readout_c;
    logic [ADDR_C_WIDTH-1:0]       ctrl_readout_idx;
    logic                          ctrl_wr_acc_en;
    logic [ADDR_C_WIDTH-1:0]       ctrl_wr_acc_addr;
    logic                          ctrl_wr_int8_en;
    logic [ADDR_C_WIDTH-1:0]       ctrl_wr_int8_addr;
    logic                          ctrl_wr_row_en;
    logic [$clog2(ARRAY_SIZE)-1:0] ctrl_wr_row_idx;

    // Buffer streaming wires
    logic signed [DATA_WIDTH-1:0] a_row_raw [ARRAY_SIZE];
    logic signed [DATA_WIDTH-1:0] b_col_raw [ARRAY_SIZE];

    // Skew unit output wires
    logic signed [DATA_WIDTH-1:0] a_row_skewed [ARRAY_SIZE];
    logic signed [DATA_WIDTH-1:0] b_col_skewed [ARRAY_SIZE];

    // Systolic core output matrix
    logic signed [ACC_WIDTH-1:0]  c_matrix_core [ARRAY_SIZE][ARRAY_SIZE];

    // Parallel Readout & Quantizer Wires
    logic signed [DATA_WIDTH-1:0] quant_dout_parallel [ARRAY_SIZE];
    logic [ARRAY_SIZE-1:0]        quant_valid_parallel;
    logic signed [ACC_WIDTH-1:0]  row_acc_delayed     [ARRAY_SIZE];

    // Readout 2D accumulator selection (Legacy single-element interface)
    logic signed [ACC_WIDTH-1:0]  quant_din_wire;
    assign quant_din_wire = c_matrix_core[ctrl_readout_r][ctrl_readout_c];

    // 1-Cycle Accumulator Pipeline Register to match Quantizer output latency
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (int c = 0; c < ARRAY_SIZE; c = c + 1) begin
                row_acc_delayed[c] <= '0;
            end
        end else begin
            for (int c = 0; c < ARRAY_SIZE; c = c + 1) begin
                row_acc_delayed[c] <= c_matrix_core[ctrl_readout_r][c];
            end
        end
    end

    // 1. Central FSM & Sequencer Controller
    gemm_controller #(
        .ARRAY_SIZE (ARRAY_SIZE),
        .MAX_K      (MAX_K)
    ) u_controller (
        .clk             (clk),
        .rst_n           (rst_n),
        .start           (start),
        .k_dim           (k_dim),
        .busy            (busy),
        .done            (done),
        .error           (error),
        .sys_en          (sys_en),
        .sys_clear_acc   (sys_clear_acc),
        .stream_en       (stream_en),
        .k_step          (k_step),
        .quant_in_en     (ctrl_quant_in_en),
        .readout_r       (ctrl_readout_r),
        .readout_c       (ctrl_readout_c),
        .readout_idx     (ctrl_readout_idx),
        .wr_acc_en       (ctrl_wr_acc_en),
        .wr_acc_addr     (ctrl_wr_acc_addr),
        .wr_row_en       (ctrl_wr_row_en),
        .wr_row_idx      (ctrl_wr_row_idx),
        .quant_out_valid (quant_valid_parallel[0]),
        .wr_int8_en      (ctrl_wr_int8_en),
        .wr_int8_addr    (ctrl_wr_int8_addr)
    );

    // 2. Weight Buffer A (Dual Legacy & Gen-2 Packed Write)
    matrix_buffer_a #(
        .ARRAY_SIZE (ARRAY_SIZE),
        .MAX_K      (MAX_K),
        .DATA_WIDTH (DATA_WIDTH),
        .ADDR_WIDTH (ADDR_A_WIDTH)
    ) u_buffer_a (
        .clk            (clk),
        .rst_n          (rst_n),
        .wr_en          (wr_a_en),
        .wr_addr        (wr_a_addr),
        .wr_data        (wr_a_data),
        .wr_packed_en   (wr_packed_a_en),
        .wr_packed_addr (wr_packed_a_addr),
        .wr_packed_data (wr_packed_a_data),
        .stream_en      (stream_en),
        .k_step         (k_step),
        .k_dim          (k_dim),
        .row_data_out   (a_row_raw)
    );

    // 3. Activation Buffer B (Dual Legacy & Gen-2 Packed Write)
    matrix_buffer_b #(
        .ARRAY_SIZE (ARRAY_SIZE),
        .MAX_K      (MAX_K),
        .DATA_WIDTH (DATA_WIDTH),
        .ADDR_WIDTH (ADDR_B_WIDTH)
    ) u_buffer_b (
        .clk            (clk),
        .rst_n          (rst_n),
        .wr_en          (wr_b_en),
        .wr_addr        (wr_b_addr),
        .wr_data        (wr_b_data),
        .wr_packed_en   (wr_packed_b_en),
        .wr_packed_addr (wr_packed_b_addr),
        .wr_packed_data (wr_packed_b_data),
        .stream_en      (stream_en),
        .k_step         (k_step),
        .k_dim          (k_dim),
        .col_data_out   (b_col_raw)
    );

    // 4. Systolic Skewing Pipeline Unit
    systolic_skew_unit #(
        .ARRAY_SIZE (ARRAY_SIZE),
        .DATA_WIDTH (DATA_WIDTH)
    ) u_skew_unit (
        .clk        (clk),
        .rst_n      (rst_n),
        .en         (sys_en),
        .clear_acc  (sys_clear_acc),
        .a_row_in   (a_row_raw),
        .b_col_in   (b_col_raw),
        .a_row_skew (a_row_skewed),
        .b_col_skew (b_col_skewed)
    );

    // 5. 2D Systolic Processing Mesh Core
    systolic_array_core #(
        .ARRAY_SIZE (ARRAY_SIZE),
        .DATA_WIDTH (DATA_WIDTH),
        .ACC_WIDTH  (ACC_WIDTH)
    ) u_systolic_core (
        .clk          (clk),
        .rst_n        (rst_n),
        .en           (sys_en),
        .clear_acc    (sys_clear_acc),
        .a_row_skew   (a_row_skewed),
        .b_col_skew   (b_col_skewed),
        .c_matrix_out (c_matrix_core)
    );

    // 6. Gen-2 Parallel Quantization & ReLU Units (8 parallel datapaths)
    genvar c_idx;
    generate
        for (c_idx = 0; c_idx < ARRAY_SIZE; c_idx = c_idx + 1) begin : gen_quantizers
            quantize_relu_unit #(
                .IN_WIDTH  (ACC_WIDTH),
                .OUT_WIDTH (DATA_WIDTH)
            ) u_quantizer_inst (
                .clk         (clk),
                .rst_n       (rst_n),
                .en          (ctrl_quant_in_en),
                .bypass_relu (bypass_relu),
                .shift_bits  (shift_bits),
                .din         (c_matrix_core[ctrl_readout_r][c_idx]),
                .dout        (quant_dout_parallel[c_idx]),
                .valid_out   (quant_valid_parallel[c_idx])
            );
        end
    endgenerate

    // 7. Output Matrix Buffer C (Dual Legacy & Gen-2 Parallel/Packed Ports)
    matrix_buffer_c #(
        .ARRAY_SIZE (ARRAY_SIZE),
        .DATA_WIDTH (DATA_WIDTH),
        .ACC_WIDTH  (ACC_WIDTH),
        .ADDR_WIDTH (ADDR_C_WIDTH)
    ) u_buffer_c (
        .clk                 (clk),
        .rst_n               (rst_n),
        .wr_acc_en           (ctrl_wr_acc_en),
        .wr_acc_addr         (ctrl_wr_acc_addr),
        .wr_acc_data         (quant_din_wire),
        .wr_int8_en          (ctrl_wr_int8_en),
        .wr_int8_addr        (ctrl_wr_int8_addr),
        .wr_int8_data        (quant_dout_parallel[0]),
        .wr_row_en           (ctrl_wr_row_en),
        .wr_row_idx          (ctrl_wr_row_idx),
        .wr_row_data_int8    (quant_dout_parallel),
        .wr_row_data_acc     (row_acc_delayed),
        .rd_addr             (rd_c_addr),
        .rd_data_int8        (rd_c_data),
        .rd_data_acc32       (rd_c_acc_data),
        .rd_packed_addr      (rd_c_packed_addr),
        .rd_data_packed_int8 (rd_c_packed_int8)
    );

endmodule
