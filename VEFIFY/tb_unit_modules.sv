`timescale 1ns / 1ps

// ==============================================================================
// Testbench: tb_unit_modules.sv
// Comprehensive Unit-Level Hardware Verification Suite for Systolic CNN Accelerator
// Verifies individual hardware modules with bit-true assertions & waveform tracing:
//   [UNIT 1] Processing Element (pe_gemm)
//   [UNIT 2] Systolic Skew Unit (systolic_skew_unit - 8x8)
//   [UNIT 3] Hardware Quantization & ReLU Unit (quantize_relu_unit)
//   [UNIT 4] On-Chip Matrix Storage Buffers (matrix_buffer_a, b, c)
//   [UNIT 5] Active-Low 7-Segment Decoder (seven_seg_decoder)
//   [UNIT 6] Central GEMM FSM Controller (gemm_controller)
//   [UNIT 7] 2D Systolic Processing Mesh Core (systolic_array_core - 8x8 = 64 PEs)
// ==============================================================================

module tb_unit_modules;

    localparam CLK_PERIOD = 20; // 50 MHz
    logic clk;
    logic rst_n;

    // Clock generator
    initial begin
        clk = 0;
        forever #(CLK_PERIOD / 2) clk = ~clk;
    end

    // Test tracking counters
    int total_tests  = 0;
    int passed_tests = 0;
    int failed_tests = 0;

    // Macro for assertions
    `define CHECK(cond, msg) \
        total_tests++; \
        if (cond) begin \
            passed_tests++; \
            $display("[PASS] %s", msg); \
        end else begin \
            failed_tests++; \
            $display("[FAIL @ %0t ns] %s", $time, msg); \
        end

    // ==========================================================================
    // UNIT 1: Processing Element (pe_gemm)
    // ==========================================================================
    logic                       pe_en;
    logic                       pe_clear_acc;
    logic signed [7:0]          pe_a_in, pe_b_in;
    logic signed [7:0]          pe_a_out, pe_b_out;
    logic signed [31:0]         pe_c_acc;

    pe_gemm #(
        .DATA_WIDTH(8),
        .ACC_WIDTH(32)
    ) u_pe (
        .clk        (clk),
        .rst_n      (rst_n),
        .en         (pe_en),
        .clear_acc  (pe_clear_acc),
        .a_in       (pe_a_in),
        .b_in       (pe_b_in),
        .a_out      (pe_a_out),
        .b_out      (pe_b_out),
        .c_acc      (pe_c_acc)
    );

    // ==========================================================================
    // UNIT 2: Systolic Skew Unit (systolic_skew_unit - 8x8)
    // ==========================================================================
    localparam N = 8;
    logic                       skew_en;
    logic                       skew_clear;
    logic signed [7:0]          skew_a_in [N];
    logic signed [7:0]          skew_b_in [N];
    logic signed [7:0]          skew_a_out[N];
    logic signed [7:0]          skew_b_out[N];

    systolic_skew_unit #(
        .ARRAY_SIZE(N),
        .DATA_WIDTH(8)
    ) u_skew (
        .clk        (clk),
        .rst_n      (rst_n),
        .en         (skew_en),
        .clear_acc  (skew_clear),
        .a_row_in   (skew_a_in),
        .b_col_in   (skew_b_in),
        .a_row_skew (skew_a_out),
        .b_col_skew (skew_b_out)
    );

    // ==========================================================================
    // UNIT 3: Quantization & ReLU Unit (quantize_relu_unit)
    // ==========================================================================
    logic                       q_en;
    logic                       q_bypass_relu;
    logic [4:0]                 q_shift_bits;
    logic signed [31:0]         q_din;
    logic signed [7:0]          q_dout;
    logic                       q_valid_out;

    quantize_relu_unit #(
        .IN_WIDTH(32),
        .OUT_WIDTH(8)
    ) u_quant (
        .clk         (clk),
        .rst_n       (rst_n),
        .en          (q_en),
        .bypass_relu (q_bypass_relu),
        .shift_bits  (q_shift_bits),
        .din         (q_din),
        .dout        (q_dout),
        .valid_out   (q_valid_out)
    );

    // ==========================================================================
    // UNIT 4: On-Chip Matrix Storage Buffers (matrix_buffer_a, b, c)
    // ==========================================================================
    logic                       buf_a_wr_en;
    logic [6:0]                 buf_a_wr_addr;
    logic signed [7:0]          buf_a_wr_data;
    logic                       buf_a_stream_en;
    logic [7:0]                 buf_a_k_step, buf_a_k_dim;
    logic signed [7:0]          buf_a_row_out [N];

    matrix_buffer_a #(
        .ARRAY_SIZE(N),
        .MAX_K(16),
        .DATA_WIDTH(8)
    ) u_buf_a (
        .clk         (clk),
        .rst_n       (rst_n),
        .wr_en       (buf_a_wr_en),
        .wr_addr     (buf_a_wr_addr),
        .wr_data     (buf_a_wr_data),
        .stream_en   (buf_a_stream_en),
        .k_step      (buf_a_k_step),
        .k_dim       (buf_a_k_dim),
        .row_data_out(buf_a_row_out)
    );

    logic                       buf_b_wr_en;
    logic [6:0]                 buf_b_wr_addr;
    logic signed [7:0]          buf_b_wr_data;
    logic                       buf_b_stream_en;
    logic [7:0]                 buf_b_k_step, buf_b_k_dim;
    logic signed [7:0]          buf_b_col_out [N];

    matrix_buffer_b #(
        .ARRAY_SIZE(N),
        .MAX_K(16),
        .DATA_WIDTH(8)
    ) u_buf_b (
        .clk         (clk),
        .rst_n       (rst_n),
        .wr_en       (buf_b_wr_en),
        .wr_addr     (buf_b_wr_addr),
        .wr_data     (buf_b_wr_data),
        .stream_en   (buf_b_stream_en),
        .k_step      (buf_b_k_step),
        .k_dim       (buf_b_k_dim),
        .col_data_out(buf_b_col_out)
    );

    logic                       buf_c_wr_acc_en;
    logic [5:0]                 buf_c_wr_acc_addr;
    logic signed [31:0]         buf_c_wr_acc_data;
    logic                       buf_c_wr_int8_en;
    logic [5:0]                 buf_c_wr_int8_addr;
    logic signed [7:0]          buf_c_wr_int8_data;
    logic [5:0]                 buf_c_rd_addr;
    logic signed [7:0]          buf_c_rd_data_int8;
    logic signed [31:0]         buf_c_rd_data_acc32;

    matrix_buffer_c #(
        .ARRAY_SIZE(N),
        .DATA_WIDTH(8),
        .ACC_WIDTH(32)
    ) u_buf_c (
        .clk          (clk),
        .rst_n        (rst_n),
        .wr_acc_en    (buf_c_wr_acc_en),
        .wr_acc_addr  (buf_c_wr_acc_addr),
        .wr_acc_data  (buf_c_wr_acc_data),
        .wr_int8_en   (buf_c_wr_int8_en),
        .wr_int8_addr (buf_c_wr_int8_addr),
        .wr_int8_data (buf_c_wr_int8_data),
        .rd_addr      (buf_c_rd_addr),
        .rd_data_int8 (buf_c_rd_data_int8),
        .rd_data_acc32(buf_c_rd_data_acc32)
    );

    // ==========================================================================
    // UNIT 5: Active-Low 7-Segment Decoder (seven_seg_decoder)
    // ==========================================================================
    logic [3:0] dec_digit;
    logic       dec_blank;
    logic [6:0] dec_seg;

    seven_seg_decoder u_dec (
        .digit(dec_digit),
        .blank(dec_blank),
        .seg  (dec_seg)
    );

    // ==========================================================================
    // UNIT 6: Central GEMM FSM Controller (gemm_controller)
    // ==========================================================================
    logic                       ctrl_start;
    logic [7:0]                 ctrl_k_dim;
    logic                       ctrl_busy;
    logic                       ctrl_done;
    logic                       ctrl_error;
    logic                       ctrl_sys_en;
    logic                       ctrl_sys_clear_acc;
    logic                       ctrl_stream_en;
    logic [7:0]                 ctrl_k_step;
    logic                       ctrl_quant_in_en;
    logic [$clog2(N)-1:0]       ctrl_readout_r, ctrl_readout_c;
    logic [$clog2(N*N)-1:0]     ctrl_readout_idx;
    logic                       ctrl_wr_acc_en;
    logic [$clog2(N*N)-1:0]     ctrl_wr_acc_addr;
    logic                       ctrl_quant_out_valid;
    logic                       ctrl_wr_int8_en;
    logic [$clog2(N*N)-1:0]     ctrl_wr_int8_addr;

    gemm_controller #(
        .ARRAY_SIZE(N),
        .MAX_K(16)
    ) u_ctrl (
        .clk             (clk),
        .rst_n           (rst_n),
        .start           (ctrl_start),
        .k_dim           (ctrl_k_dim),
        .busy            (ctrl_busy),
        .done            (ctrl_done),
        .error           (ctrl_error),
        .sys_en          (ctrl_sys_en),
        .sys_clear_acc   (ctrl_sys_clear_acc),
        .stream_en       (ctrl_stream_en),
        .k_step          (ctrl_k_step),
        .quant_in_en     (ctrl_quant_in_en),
        .readout_r       (ctrl_readout_r),
        .readout_c       (ctrl_readout_c),
        .readout_idx     (ctrl_readout_idx),
        .wr_acc_en       (ctrl_wr_acc_en),
        .wr_acc_addr     (ctrl_wr_acc_addr),
        .quant_out_valid (ctrl_quant_out_valid),
        .wr_int8_en      (ctrl_wr_int8_en),
        .wr_int8_addr    (ctrl_wr_int8_addr)
    );

    // ==========================================================================
    // UNIT 7: 2D Systolic Processing Mesh Core (systolic_array_core - 8x8)
    // ==========================================================================
    logic                       core_en;
    logic                       core_clear_acc;
    logic signed [7:0]          core_a_row_skew [N];
    logic signed [7:0]          core_b_col_skew [N];
    logic signed [31:0]         core_c_matrix_out [N][N];

    systolic_array_core #(
        .ARRAY_SIZE(N),
        .DATA_WIDTH(8),
        .ACC_WIDTH(32)
    ) u_core (
        .clk         (clk),
        .rst_n       (rst_n),
        .en          (core_en),
        .clear_acc   (core_clear_acc),
        .a_row_skew  (core_a_row_skew),
        .b_col_skew  (core_b_col_skew),
        .c_matrix_out(core_c_matrix_out)
    );

    // ==========================================================================
    // MAIN VERIFICATION PROCEDURE
    // ==========================================================================
    initial begin
        $dumpfile("unit_modules_waveform.vcd");
        $dumpvars(0, tb_unit_modules);

        $display("================================================================================");
        $display("  STARTING COMPREHENSIVE UNIT-LEVEL HARDWARE VERIFICATION SUITE");
        $display("  Architecture: 8x8 INT8 Output-Stationary Systolic Neural Accelerator");
        $display("================================================================================");

        // Global Reset Initialization
        rst_n = 0;
        pe_en = 0; pe_clear_acc = 0; pe_a_in = 0; pe_b_in = 0;
        skew_en = 0; skew_clear = 0;
        for (int k = 0; k < N; k++) begin
            skew_a_in[k] = 0; skew_b_in[k] = 0;
            core_a_row_skew[k] = 0; core_b_col_skew[k] = 0;
        end
        q_en = 0; q_bypass_relu = 0; q_shift_bits = 0; q_din = 0;
        buf_a_wr_en = 0; buf_a_wr_addr = 0; buf_a_wr_data = 0;
        buf_a_stream_en = 0; buf_a_k_step = 0; buf_a_k_dim = 8;
        buf_b_wr_en = 0; buf_b_wr_addr = 0; buf_b_wr_data = 0;
        buf_b_stream_en = 0; buf_b_k_step = 0; buf_b_k_dim = 8;
        buf_c_wr_acc_en = 0; buf_c_wr_acc_addr = 0; buf_c_wr_acc_data = 0;
        buf_c_wr_int8_en = 0; buf_c_wr_int8_addr = 0; buf_c_wr_int8_data = 0;
        buf_c_rd_addr = 0;
        dec_digit = 0; dec_blank = 0;
        ctrl_start = 0; ctrl_k_dim = 8; ctrl_quant_out_valid = 0;
        core_en = 0; core_clear_acc = 0;

        repeat (5) @(posedge clk);
        rst_n = 1;
        @(negedge clk);

        // ----------------------------------------------------------------------
        // [UNIT 1] PE GEMM VERIFICATION
        // ----------------------------------------------------------------------
        $display("\n>>> [UNIT 1] Processing Element (pe_gemm.sv) Unit Tests...");
        
        @(negedge clk);
        pe_clear_acc = 1;
        @(posedge clk); #1;
        `CHECK(pe_c_acc == 0, "PE Clear Accumulator Check");

        @(negedge clk);
        pe_clear_acc = 0;

        // MAC 1: 5 * 10 = 50
        pe_en = 1; pe_a_in = 8'sd5; pe_b_in = 8'sd10;
        @(posedge clk); #1;
        `CHECK(pe_c_acc == 50, "PE MAC: 5 * 10 = 50");
        `CHECK(pe_a_out == 5 && pe_b_out == 10, "PE Systolic Pass-Through a_out/b_out");

        // MAC 2: Accumulate -4 * 7 = -28 -> acc = 50 - 28 = 22
        @(negedge clk);
        pe_a_in = -8'sd4; pe_b_in = 8'sd7;
        @(posedge clk); #1;
        `CHECK(pe_c_acc == 22, "PE MAC: 50 + (-4 * 7) = 22");

        // MAC 3: Maximum positive extremes: 127 * 127 = 16,129 -> acc = 22 + 16,129 = 16,151
        @(negedge clk);
        pe_a_in = 8'sd127; pe_b_in = 8'sd127;
        @(posedge clk); #1;
        `CHECK(pe_c_acc == 16151, "PE Extreme Positive MAC: 127 * 127");

        // MAC 4: Maximum negative asymmetry: (-128) * (-128) = 16,384 -> acc = 16,151 + 16,384 = 32,535
        @(negedge clk);
        pe_a_in = -8'sd128; pe_b_in = -8'sd128;
        @(posedge clk); #1;
        `CHECK(pe_c_acc == 32535, "PE Negative Asymmetry MAC: (-128) * (-128)");

        // MAC 5: Cross-sign extreme: (-128) * 127 = -16,256 -> acc = 32,535 - 16,256 = 16,279
        @(negedge clk);
        pe_a_in = -8'sd128; pe_b_in = 8'sd127;
        @(posedge clk); #1;
        `CHECK(pe_c_acc == 16279, "PE Cross Sign Extreme MAC: (-128) * 127");

        // Test 1.3: Enable gating
        @(negedge clk);
        pe_en = 0; pe_a_in = 8'sd100; pe_b_in = 8'sd100;
        @(posedge clk); #1;
        `CHECK(pe_c_acc == 16279, "PE Enable Gating: Accumulator holds state when en=0");

        // ----------------------------------------------------------------------
        // [UNIT 2] SYSTOLIC SKEW UNIT VERIFICATION (8x8)
        // ----------------------------------------------------------------------
        $display("\n>>> [UNIT 2] Systolic Skew Unit (systolic_skew_unit.sv) Unit Tests...");
        @(negedge clk);
        skew_en = 1;
        skew_clear = 1;
        @(posedge clk); #1;
        @(negedge clk);
        skew_clear = 0;

        // Apply a pulse of unique values across rows 0..7 at cycle T0
        for (int r = 0; r < N; r++) skew_a_in[r] = 8'sd10 + r;
        
        #1;
        `CHECK(skew_a_out[0] == 10, "Skew Row 0 (0T delay) instant pass-through");

        @(posedge clk); #1;
        `CHECK(skew_a_out[1] == 11, "Skew Row 1 (1T delay) registered output");

        @(negedge clk);
        for (int r = 0; r < N; r++) skew_a_in[r] = 8'sd0;

        for (int step = 2; step < N; step++) begin
            @(posedge clk); #1;
            `CHECK(skew_a_out[step] == 10 + step, $sformatf("Skew Row %0d (%0dT delay) wavefront verified", step, step));
        end

        // ----------------------------------------------------------------------
        // [UNIT 3] QUANTIZATION & RELU UNIT VERIFICATION
        // ----------------------------------------------------------------------
        $display("\n>>> [UNIT 3] Hardware Quantization & ReLU (quantize_relu_unit.sv) Unit Tests...");
        @(negedge clk);
        q_en = 1;

        // Test 3.1: Positive number with shift_bits = 7 (Scale factor 128)
        q_bypass_relu = 0;
        q_shift_bits  = 5'd7;
        q_din         = 32'sd1280; // 1280 >> 7 = 10
        @(posedge clk); #1;
        `CHECK(q_dout == 8'sd10, "Quantization Scale: 1280 >> 7 = 10");

        // Test 3.2: ReLU clipping negative number
        @(negedge clk);
        q_bypass_relu = 0;
        q_shift_bits  = 5'd7;
        q_din         = -32'sd1280; // Negative with ReLU -> 0
        @(posedge clk); #1;
        `CHECK(q_dout == 8'sd0, "ReLU Activation: Negative input clipped to 0");

        // Test 3.3: Bypass ReLU preserving negative number
        @(negedge clk);
        q_bypass_relu = 1;
        q_shift_bits  = 5'd7;
        q_din         = -32'sd1280; // -1280 >>> 7 = -10
        @(posedge clk); #1;
        `CHECK(q_dout == -8'sd10, "Bypass ReLU: Signed negative value preserved (-10)");

        // Test 3.4: Positive saturation clamp (> 127 clamped to +127)
        @(negedge clk);
        q_bypass_relu = 1;
        q_shift_bits  = 5'd0;
        q_din         = 32'sd5000;
        @(posedge clk); #1;
        `CHECK(q_dout == 8'sd127, "Positive Saturation: 5000 clamped to +127");

        // Test 3.5: Negative saturation clamp (< -128 clamped to -128)
        @(negedge clk);
        q_bypass_relu = 1;
        q_shift_bits  = 5'd0;
        q_din         = -32'sd5000;
        @(posedge clk); #1;
        `CHECK(q_dout == -8'sd128, "Negative Saturation: -5000 clamped to -128");

        // ----------------------------------------------------------------------
        // [UNIT 4] MATRIX BUFFERS VERIFICATION (A, B, C)
        // ----------------------------------------------------------------------
        $display("\n>>> [UNIT 4] On-Chip Matrix Storage Buffers (A, B, C) Unit Tests...");

        // Buffer A: Write row 0..7 for K=0
        for (int r = 0; r < N; r++) begin
            @(negedge clk);
            buf_a_wr_en = 1;
            buf_a_wr_addr = r * 8 + 0;
            buf_a_wr_data = 8'sd20 + r;
        end
        @(negedge clk);
        buf_a_wr_en = 0;

        buf_a_stream_en = 1;
        buf_a_k_step = 0;
        buf_a_k_dim  = 8;
        #1;
        for (int r = 0; r < N; r++) begin
            `CHECK(buf_a_row_out[r] == 20 + r, $sformatf("Buffer A Parallel Readout Row %0d", r));
        end

        // Buffer B: Write col 0..7 for K=0
        for (int c = 0; c < N; c++) begin
            @(negedge clk);
            buf_b_wr_en = 1;
            buf_b_wr_addr = 0 * N + c;
            buf_b_wr_data = 8'sd30 + c;
        end
        @(negedge clk);
        buf_b_wr_en = 0;

        buf_b_stream_en = 1;
        buf_b_k_step = 0;
        buf_b_k_dim  = 8;
        #1;
        for (int c = 0; c < N; c++) begin
            `CHECK(buf_b_col_out[c] == 30 + c, $sformatf("Buffer B Parallel Readout Col %0d", c));
        end

        // Buffer C dual write/read (INT8 and INT32 accumulated)
        @(negedge clk);
        buf_c_wr_acc_en = 1;
        buf_c_wr_acc_addr = 6'd15;
        buf_c_wr_acc_data = 32'sd999999;
        buf_c_wr_int8_en = 1;
        buf_c_wr_int8_addr = 6'd15;
        buf_c_wr_int8_data = 8'sd77;
        @(posedge clk); #1;
        @(negedge clk);
        buf_c_wr_acc_en = 0;
        buf_c_wr_int8_en = 0;

        buf_c_rd_addr = 6'd15;
        #1;
        `CHECK(buf_c_rd_data_int8 == 8'sd77, "Buffer C INT8 Readout at addr 15");
        `CHECK(buf_c_rd_data_acc32 == 32'sd999999, "Buffer C INT32 Accumulator Readout at addr 15");

        // ----------------------------------------------------------------------
        // [UNIT 5] 7-SEGMENT DECODER VERIFICATION
        // ----------------------------------------------------------------------
        $display("\n>>> [UNIT 5] Active-Low 7-Segment Display Decoder Unit Tests...");
        
        dec_blank = 1; dec_digit = 4'h0;
        #1;
        `CHECK(dec_seg == 7'b1111111, "Decoder Blanking (All Segments OFF)");

        dec_blank = 0;
        dec_digit = 4'h0; #1;
        `CHECK(dec_seg == 7'b1000000, "Decoder Digit 0 -> 7'b1000000 (0x40)");

        dec_digit = 4'h7; #1;
        `CHECK(dec_seg == 7'b1111000, "Decoder Digit 7 -> 7'b1111000 (0x78)");

        dec_digit = 4'h8; #1;
        `CHECK(dec_seg == 7'b0000000, "Decoder Digit 8 -> 7'b0000000 (0x00)");

        dec_digit = 4'hF; #1;
        `CHECK(dec_seg == 7'b0001110, "Decoder Digit F -> 7'b0001110 (0x0E)");

        // ----------------------------------------------------------------------
        // [UNIT 6] GEMM FSM CONTROLLER VERIFICATION
        // ----------------------------------------------------------------------
        $display("\n>>> [UNIT 6] Central GEMM FSM Controller (gemm_controller.sv) Unit Tests...");

        // Test 6.1: Invalid K dimension guardband rejection (K=0)
        @(negedge clk);
        ctrl_k_dim = 8'd0;
        ctrl_start = 1;
        @(posedge clk); #1;
        `CHECK(ctrl_error == 1 && ctrl_done == 1 && ctrl_busy == 0, "Controller Guardband: Reject K=0");
        @(negedge clk);
        ctrl_start = 0;
        @(posedge clk); #1;

        // Test 6.2: Invalid K dimension guardband rejection (K=25 > MAX_K)
        @(negedge clk);
        ctrl_k_dim = 8'd25;
        ctrl_start = 1;
        @(posedge clk); #1;
        `CHECK(ctrl_error == 1 && ctrl_done == 1, "Controller Guardband: Reject K > MAX_K");
        @(negedge clk);
        ctrl_start = 0;
        @(posedge clk); #1;

        // Test 6.3: Valid FSM lifecycle execution (K=8)
        @(negedge clk);
        ctrl_k_dim = 8'd8;
        ctrl_start = 1;
        @(posedge clk); #1;
        @(negedge clk);
        ctrl_start = 0;

        `CHECK(ctrl_busy == 1 && ctrl_error == 0, "Controller FSM Transition to BUSY state");

        // Wait until controller completes full cycle and pulses done
        fork : wait_ctrl_done
            begin
                @(posedge ctrl_done); #1;
                `CHECK(ctrl_done == 1 && ctrl_busy == 0, "Controller FSM Full Cycle to DONE state");
            end
            begin
                repeat (200) @(posedge clk);
                `CHECK(1'b0, "Controller FSM Timeout waiting for done");
            end
        join_any
        disable wait_ctrl_done;

        // ----------------------------------------------------------------------
        // [UNIT 7] 2D SYSTOLIC ARRAY CORE VERIFICATION (8x8 = 64 PEs)
        // ----------------------------------------------------------------------
        $display("\n>>> [UNIT 7] 2D Systolic Array Core (systolic_array_core.sv - 64 PEs) Unit Tests...");

        @(negedge clk);
        core_clear_acc = 1;
        core_en = 0;
        @(posedge clk); #1;
        @(negedge clk);
        core_clear_acc = 0;

        // Verify all 64 accumulators are zero
        begin
            int zero_cnt;
            zero_cnt = 0;
            for (int r = 0; r < N; r++) begin
                for (int c = 0; c < N; c++) begin
                    if (core_c_matrix_out[r][c] == 0) zero_cnt++;
                end
            end
            `CHECK(zero_cnt == 64, "Systolic Array Core: All 64 PEs cleared to 0");
        end

        // Step 1: Feed input A=[1..1] across all rows, B=[2..2] across all cols
        @(negedge clk);
        core_en = 1;
        for (int k = 0; k < N; k++) begin
            core_a_row_skew[k] = 8'sd1;
            core_b_col_skew[k] = 8'sd2;
        end
        @(posedge clk); #1;

        // PE(0,0) receives a_row_skew[0]=1 and b_col_skew[0]=2 immediately!
        // At 1st posedge clk, PE(0,0) accumulator becomes: 0 + 1 * 2 = 2
        `CHECK(core_c_matrix_out[0][0] == 2, "Systolic Core PE(0,0) First Cycle Compute: 1 * 2 = 2");

        // Clock cycle 2: a_out from PE(0,0) propagates to PE(0,1), b_out propagates to PE(1,0)
        @(posedge clk); #1;
        `CHECK(core_c_matrix_out[0][1] == 2, "Systolic Core PE(0,1) Horizontal Propagation");
        `CHECK(core_c_matrix_out[1][0] == 2, "Systolic Core PE(1,0) Vertical Propagation");

        // ----------------------------------------------------------------------
        // FINAL SUMMARY REPORT
        // ----------------------------------------------------------------------
        repeat (10) @(posedge clk);
        $display("\n================================================================================");
        $display("  UNIT-LEVEL HARDWARE VERIFICATION SUMMARY REPORT");
        $display("================================================================================");
        $display("  Total Unit Checks Executed : %0d", total_tests);
        $display("  Passed Checks              : %0d", passed_tests);
        $display("  Failed Checks              : %0d", failed_tests);
        if (failed_tests == 0) begin
            $display("  VERIFICATION RESULT        : >>> 100%% PASSED (0 ERRORS) <<<");
        end else begin
            $display("  VERIFICATION RESULT        : >>> FAILED (%0d ERRORS) <<<", failed_tests);
        end
        $display("================================================================================\n");

        $finish;
    end

endmodule
