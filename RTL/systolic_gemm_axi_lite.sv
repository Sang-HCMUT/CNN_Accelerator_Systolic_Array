`timescale 1ns / 1ps

// ============================================================================
// Module: systolic_gemm_axi_lite.sv
// Description: AXI4-Lite Slave Interface Wrapper for the Parameterized
//              INT8 Systolic Array GEMM Accelerator.
//              Enables direct MMIO control from RISC-V or Nios II Host CPU.
// ============================================================================

module systolic_gemm_axi_lite #(
    parameter ARRAY_SIZE = 4,
    parameter DATA_WIDTH = 8,
    parameter ACC_WIDTH  = 32,
    parameter C_S_AXI_DATA_WIDTH = 32,
    parameter C_S_AXI_ADDR_WIDTH = 12
)(
    input  logic                                  s_axi_aclk,
    input  logic                                  s_axi_aresetn,

    // Write Address Channel
    input  logic [C_S_AXI_ADDR_WIDTH-1:0]         s_axi_awaddr,
    input  logic [2:0]                            s_axi_awprot,
    input  logic                                  s_axi_awvalid,
    output logic                                  s_axi_awready,

    // Write Data Channel
    input  logic [C_S_AXI_DATA_WIDTH-1:0]         s_axi_wdata,
    input  logic [(C_S_AXI_DATA_WIDTH/8)-1:0]     s_axi_wstrb,
    input  logic                                  s_axi_wvalid,
    output logic                                  s_axi_wready,

    // Write Response Channel
    output logic [1:0]                            s_axi_bresp,
    output logic                                  s_axi_bvalid,
    input  logic                                  s_axi_bready,

    // Read Address Channel
    input  logic [C_S_AXI_ADDR_WIDTH-1:0]         s_axi_araddr,
    input  logic [2:0]                            s_axi_arprot,
    input  logic                                  s_axi_arvalid,
    output logic                                  s_axi_arready,

    // Read Data Channel
    output logic [C_S_AXI_DATA_WIDTH-1:0]         s_axi_rdata,
    output logic [1:0]                            s_axi_rresp,
    output logic                                  s_axi_rvalid,
    input  logic                                  s_axi_rready
);

    wire rst_n = s_axi_aresetn;

    // Registers:
    // 0x000: Control (bit 0: Start, bit 1: Bypass ReLU, bit [6:2]: shift_bits)
    // 0x004: Status  (bit 0: Done, bit 1: Busy)
    // 0x008: K_DIM   (Dimension K)
    // 0x100 - 0x1FC: Matrix A Buffer
    // 0x200 - 0x2FC: Matrix B Buffer
    // 0x300 - 0x3FC: Matrix C Output Buffer
    logic [31:0] control_reg;
    logic [31:0] status_reg;
    logic [7:0]  k_dim_reg;

    logic [C_S_AXI_ADDR_WIDTH-1:0] axi_awaddr;
    logic [C_S_AXI_ADDR_WIDTH-1:0] axi_araddr;

    // Accelerator core interface wires
    logic        core_start;
    logic        core_done;
    logic        core_busy;

    logic                                     core_wr_a_en;
    logic [$clog2(ARRAY_SIZE*16)-1:0]         core_wr_a_addr;
    logic signed [DATA_WIDTH-1:0]             core_wr_a_data;

    logic                                     core_wr_b_en;
    logic [$clog2(ARRAY_SIZE*16)-1:0]         core_wr_b_addr;
    logic signed [DATA_WIDTH-1:0]             core_wr_b_data;

    logic [$clog2(ARRAY_SIZE*ARRAY_SIZE)-1:0] core_rd_c_addr;
    logic signed [DATA_WIDTH-1:0]             core_rd_c_data;
    logic signed [ACC_WIDTH-1:0]              core_rd_c_acc;

    // AXI Write State Machine
    always_ff @(posedge s_axi_aclk or negedge rst_n) begin
        if (!rst_n) begin
            s_axi_awready <= 1'b0;
            s_axi_wready  <= 1'b0;
            s_axi_bvalid  <= 1'b0;
            s_axi_bresp   <= 2'b00;
            axi_awaddr    <= '0;
            control_reg   <= '0;
            status_reg    <= '0;
            k_dim_reg     <= 8'd4;
            core_start    <= 1'b0;
            core_wr_a_en  <= 1'b0;
            core_wr_b_en  <= 1'b0;
        end else begin
            core_start   <= 1'b0;
            core_wr_a_en <= 1'b0;
            core_wr_b_en <= 1'b0;

            if (core_done) status_reg[0] <= 1'b1;
            status_reg[1] <= core_busy;

            // AW Handshake
            if (~s_axi_awready && s_axi_awvalid && s_axi_wvalid) begin
                s_axi_awready <= 1'b1;
                axi_awaddr    <= s_axi_awaddr;
            end else begin
                s_axi_awready <= 1'b0;
            end

            // W Handshake
            if (~s_axi_wready && s_axi_wvalid && s_axi_awvalid) begin
                s_axi_wready <= 1'b1;
            end else begin
                s_axi_wready <= 1'b0;
            end

            // Write Operation
            if (s_axi_awready && s_axi_wready) begin
                s_axi_bvalid <= 1'b1;
                s_axi_bresp  <= 2'b00;

                if (axi_awaddr == 12'h000) begin
                    control_reg <= s_axi_wdata;
                    if (s_axi_wdata[0]) begin
                        core_start     <= 1'b1;
                        status_reg[0]  <= 1'b0; // Clear done
                    end
                end else if (axi_awaddr == 12'h008) begin
                    k_dim_reg <= s_axi_wdata[7:0];
                end else if (axi_awaddr >= 12'h100 && axi_awaddr < 12'h200) begin
                    core_wr_a_en   <= 1'b1;
                    core_wr_a_addr <= (axi_awaddr - 12'h100) >> 2;
                    core_wr_a_data <= s_axi_wdata[DATA_WIDTH-1:0];
                end else if (axi_awaddr >= 12'h200 && axi_awaddr < 12'h300) begin
                    core_wr_b_en   <= 1'b1;
                    core_wr_b_addr <= (axi_awaddr - 12'h200) >> 2;
                    core_wr_b_data <= s_axi_wdata[DATA_WIDTH-1:0];
                end
            end else if (s_axi_bvalid && s_axi_bready) begin
                s_axi_bvalid <= 1'b0;
            end
        end
    end

    // AXI Read State Machine
    always_ff @(posedge s_axi_aclk or negedge rst_n) begin
        if (!rst_n) begin
            s_axi_arready <= 1'b0;
            s_axi_rvalid  <= 1'b0;
            s_axi_rresp   <= 2'b00;
            s_axi_rdata   <= '0;
            axi_araddr    <= '0;
            core_rd_c_addr <= '0;
        end else begin
            if (~s_axi_arready && s_axi_arvalid) begin
                s_axi_arready <= 1'b1;
                axi_araddr    <= s_axi_araddr;
            end else begin
                s_axi_arready <= 1'b0;
            end

            if (s_axi_arready && s_axi_arvalid && ~s_axi_rvalid) begin
                s_axi_rvalid <= 1'b1;
                s_axi_rresp  <= 2'b00;

                if (axi_araddr == 12'h000) begin
                    s_axi_rdata <= control_reg;
                end else if (axi_araddr == 12'h004) begin
                    s_axi_rdata <= status_reg;
                end else if (axi_araddr == 12'h008) begin
                    s_axi_rdata <= {24'd0, k_dim_reg};
                end else if (axi_araddr >= 12'h300 && axi_araddr < 12'h400) begin
                    core_rd_c_addr <= (axi_araddr - 12'h300) >> 2;
                    s_axi_rdata    <= {24'd0, core_rd_c_data};
                end else begin
                    s_axi_rdata <= 32'd0;
                end
            end else if (s_axi_rvalid && s_axi_rready) begin
                s_axi_rvalid <= 1'b0;
            end
        end
    end

    // Accelerator Core Instance
    systolic_accelerator_top #(
        .ARRAY_SIZE (ARRAY_SIZE),
        .DATA_WIDTH (DATA_WIDTH),
        .ACC_WIDTH  (ACC_WIDTH)
    ) core_inst (
        .clk           (s_axi_aclk),
        .rst_n         (rst_n),
        .start         (core_start),
        .k_dim         (k_dim_reg),
        .bypass_relu   (control_reg[1]),
        .shift_bits    (control_reg[6:2]),
        .done          (core_done),
        .busy          (core_busy),
        .wr_a_en       (core_wr_a_en),
        .wr_a_addr     (core_wr_a_addr),
        .wr_a_data     (core_wr_a_data),
        .wr_b_en       (core_wr_b_en),
        .wr_b_addr     (core_wr_b_addr),
        .wr_b_data     (core_wr_b_data),
        .rd_c_addr     (core_rd_c_addr),
        .rd_c_data     (core_rd_c_data),
        .rd_c_acc_data (core_rd_c_acc)
    );

endmodule
