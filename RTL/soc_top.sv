`timescale 1ns / 1ps

// Module: soc_top.sv
// Top-Level SoC integrating PicoRV32 RISC-V Soft CPU Core with:
//   - Parameterized INT8 Systolic Array GEMM Accelerator (AXI Slave)
//   - 32 KB Dual-Port / Single-Port Block RAM (Instruction + Data)
//   - UART / Console Output Peripheral
//   - AXI4-Lite Central Interconnect Crossbar

module soc_top #(
    parameter ARRAY_SIZE    = 4,
    parameter DATA_WIDTH    = 8,
    parameter ACC_WIDTH     = 32,
    parameter MEM_WORDS     = 4096,
    parameter MEM_INIT_FILE = "firmware.hex",
    parameter UART_CLKS_PER_BIT = 434
)(
    input  logic       clk,
    input  logic       rst_n,
    input  logic       uart_rx,
    output logic       uart_tx,
    output logic [6:0] hex0,
    output logic [6:0] hex1,
    output logic [9:0] ledr,
    output logic [7:0] ledg
);

    // Reset Synchronization: Asynchronous Assert, Synchronous Deassert (AASD)
    // Eliminates metastability & recovery/removal timing hazards on physical FPGA pushbutton
    logic rst_n_sync_1, rst_n_sync;
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rst_n_sync_1 <= 1'b0;
            rst_n_sync   <= 1'b0;
        end else begin
            rst_n_sync_1 <= 1'b1;
            rst_n_sync   <= rst_n_sync_1;
        end
    end

    // Master Bus Signals (CPU -> Interconnect)
    logic        trap;
    logic [31:0] cpu_axi_awaddr;
    logic [2:0]  cpu_axi_awprot;
    logic        cpu_axi_awvalid;
    logic        cpu_axi_awready;

    logic [31:0] cpu_axi_wdata;
    logic [3:0]  cpu_axi_wstrb;
    logic        cpu_axi_wvalid;
    logic        cpu_axi_wready;

    logic [1:0]  cpu_axi_bresp;
    logic        cpu_axi_bvalid;
    logic        cpu_axi_bready;

    logic [31:0] cpu_axi_araddr;
    logic [2:0]  cpu_axi_arprot;
    logic        cpu_axi_arvalid;
    logic        cpu_axi_arready;

    logic [31:0] cpu_axi_rdata;
    logic [1:0]  cpu_axi_rresp;
    logic        cpu_axi_rvalid;
    logic        cpu_axi_rready;

    // Slave 0 Signals: BRAM RAM (0x0000_0000)
    logic [31:0] s0_awaddr;
    logic [2:0]  s0_awprot;
    logic        s0_awvalid;
    logic        s0_awready;

    logic [31:0] s0_wdata;
    logic [3:0]  s0_wstrb;
    logic        s0_wvalid;
    logic        s0_wready;

    logic [1:0]  s0_bresp;
    logic        s0_bvalid;
    logic        s0_bready;

    logic [31:0] s0_araddr;
    logic [2:0]  s0_arprot;
    logic        s0_arvalid;
    logic        s0_arready;

    logic [31:0] s0_rdata;
    logic [1:0]  s0_rresp;
    logic        s0_rvalid;
    logic        s0_rready;

    // Slave 1 Signals: Systolic Accelerator (0x1000_0000)
    logic [31:0] s1_awaddr;
    logic [2:0]  s1_awprot;
    logic        s1_awvalid;
    logic        s1_awready;

    logic [31:0] s1_wdata;
    logic [3:0]  s1_wstrb;
    logic        s1_wvalid;
    logic        s1_wready;

    logic [1:0]  s1_bresp;
    logic        s1_bvalid;
    logic        s1_bready;

    logic [31:0] s1_araddr;
    logic [2:0]  s1_arprot;
    logic        s1_arvalid;
    logic        s1_arready;

    logic [31:0] s1_rdata;
    logic [1:0]  s1_rresp;
    logic        s1_rvalid;
    logic        s1_rready;

    // Slave 2 Signals: UART Peripheral (0x2000_0000)
    logic [31:0] s2_awaddr;
    logic [2:0]  s2_awprot;
    logic        s2_awvalid;
    logic        s2_awready;

    logic [31:0] s2_wdata;
    logic [3:0]  s2_wstrb;
    logic        s2_wvalid;
    logic        s2_wready;

    logic [1:0]  s2_bresp;
    logic        s2_bvalid;
    logic        s2_bready;

    logic [31:0] s2_araddr;
    logic [2:0]  s2_arprot;
    logic        s2_arvalid;
    logic        s2_arready;

    logic [31:0] s2_rdata;
    logic [1:0]  s2_rresp;
    logic        s2_rvalid;
    logic        s2_rready;

    // 1. PicoRV32 RISC-V CPU Core (AXI4-Lite Master)
    picorv32_axi #(
        .ENABLE_COUNTERS     (1),
        .ENABLE_COUNTERS64   (1),
        .ENABLE_REGS_16_31   (1),
        .ENABLE_REGS_DUALPORT(1),
        .TWO_STAGE_SHIFT     (1),
        .BARREL_SHIFTER      (1),
        .TWO_CYCLE_COMPARE   (0),
        .TWO_CYCLE_ALU       (0),
        .COMPRESSED_ISA      (0),
        .CATCH_MISALIGN      (1),
        .CATCH_ILLINSN       (1),
        .PROGADDR_RESET      (32'h0000_0000),
        .STACKADDR           (32'h0000_7FF0)
    ) u_cpu (
        .clk             (clk),
        .resetn          (rst_n_sync),
        .trap            (trap),

        // AXI4-Lite Master Interface
        .mem_axi_awvalid (cpu_axi_awvalid),
        .mem_axi_awready (cpu_axi_awready),
        .mem_axi_awaddr  (cpu_axi_awaddr),
        .mem_axi_awprot  (cpu_axi_awprot),

        .mem_axi_wvalid  (cpu_axi_wvalid),
        .mem_axi_wready  (cpu_axi_wready),
        .mem_axi_wdata   (cpu_axi_wdata),
        .mem_axi_wstrb   (cpu_axi_wstrb),

        .mem_axi_bvalid  (cpu_axi_bvalid),
        .mem_axi_bready  (cpu_axi_bready),

        .mem_axi_arvalid (cpu_axi_arvalid),
        .mem_axi_arready (cpu_axi_arready),
        .mem_axi_araddr  (cpu_axi_araddr),
        .mem_axi_arprot  (cpu_axi_arprot),

        .mem_axi_rvalid  (cpu_axi_rvalid),
        .mem_axi_rready  (cpu_axi_rready),
        .mem_axi_rdata   (cpu_axi_rdata),

        // Unused Co-Processor and IRQ
        .pcpi_valid      (),
        .pcpi_insn       (),
        .pcpi_rs1        (),
        .pcpi_rs2        (),
        .pcpi_wr         (1'b0),
        .pcpi_rd         (32'd0),
        .pcpi_wait       (1'b0),
        .pcpi_ready      (1'b0),
        .irq             (32'd0),
        .eoi             (),
        .trace_valid     (),
        .trace_data      ()
    );

    // 2. AXI4-Lite Central Interconnect Crossbar
    axi_interconnect u_interconnect (
        .clk            (clk),
        .rst_n          (rst_n_sync),

        // Master
        .s_axi_awaddr   (cpu_axi_awaddr),
        .s_axi_awprot   (cpu_axi_awprot),
        .s_axi_awvalid  (cpu_axi_awvalid),
        .s_axi_awready  (cpu_axi_awready),
        .s_axi_wdata    (cpu_axi_wdata),
        .s_axi_wstrb    (cpu_axi_wstrb),
        .s_axi_wvalid   (cpu_axi_wvalid),
        .s_axi_wready   (cpu_axi_wready),
        .s_axi_bresp    (cpu_axi_bresp),
        .s_axi_bvalid   (cpu_axi_bvalid),
        .s_axi_bready   (cpu_axi_bready),
        .s_axi_araddr   (cpu_axi_araddr),
        .s_axi_arprot   (cpu_axi_arprot),
        .s_axi_arvalid  (cpu_axi_arvalid),
        .s_axi_arready  (cpu_axi_arready),
        .s_axi_rdata    (cpu_axi_rdata),
        .s_axi_rresp    (cpu_axi_rresp),
        .s_axi_rvalid   (cpu_axi_rvalid),
        .s_axi_rready   (cpu_axi_rready),

        // Slave 0: BRAM RAM
        .m0_axi_awaddr  (s0_awaddr),
        .m0_axi_awprot  (s0_awprot),
        .m0_axi_awvalid (s0_awvalid),
        .m0_axi_awready (s0_awready),
        .m0_axi_wdata   (s0_wdata),
        .m0_axi_wstrb   (s0_wstrb),
        .m0_axi_wvalid  (s0_wvalid),
        .m0_axi_wready  (s0_wready),
        .m0_axi_bresp   (s0_bresp),
        .m0_axi_bvalid  (s0_bvalid),
        .m0_axi_bready  (s0_bready),
        .m0_axi_araddr  (s0_araddr),
        .m0_axi_arprot  (s0_arprot),
        .m0_axi_arvalid (s0_arvalid),
        .m0_axi_arready (s0_arready),
        .m0_axi_rdata   (s0_rdata),
        .m0_axi_rresp   (s0_rresp),
        .m0_axi_rvalid  (s0_rvalid),
        .m0_axi_rready  (s0_rready),

        // Slave 1: Systolic Accelerator
        .m1_axi_awaddr  (s1_awaddr),
        .m1_axi_awprot  (s1_awprot),
        .m1_axi_awvalid (s1_awvalid),
        .m1_axi_awready (s1_awready),
        .m1_axi_wdata   (s1_wdata),
        .m1_axi_wstrb   (s1_wstrb),
        .m1_axi_wvalid  (s1_wvalid),
        .m1_axi_wready  (s1_wready),
        .m1_axi_bresp   (s1_bresp),
        .m1_axi_bvalid  (s1_bvalid),
        .m1_axi_bready  (s1_bready),
        .m1_axi_araddr  (s1_araddr),
        .m1_axi_arprot  (s1_arprot),
        .m1_axi_arvalid (s1_arvalid),
        .m1_axi_arready (s1_arready),
        .m1_axi_rdata   (s1_rdata),
        .m1_axi_rresp   (s1_rresp),
        .m1_axi_rvalid  (s1_rvalid),
        .m1_axi_rready  (s1_rready),

        // Slave 2: UART Peripheral
        .m2_axi_awaddr  (s2_awaddr),
        .m2_axi_awprot  (s2_awprot),
        .m2_axi_awvalid (s2_awvalid),
        .m2_axi_awready (s2_awready),
        .m2_axi_wdata   (s2_wdata),
        .m2_axi_wstrb   (s2_wstrb),
        .m2_axi_wvalid  (s2_wvalid),
        .m2_axi_wready  (s2_wready),
        .m2_axi_bresp   (s2_bresp),
        .m2_axi_bvalid  (s2_bvalid),
        .m2_axi_bready  (s2_bready),
        .m2_axi_araddr  (s2_araddr),
        .m2_axi_arprot  (s2_arprot),
        .m2_axi_arvalid (s2_arvalid),
        .m2_axi_arready (s2_arready),
        .m2_axi_rdata   (s2_rdata),
        .m2_axi_rresp   (s2_rresp),
        .m2_axi_rvalid  (s2_rvalid),
        .m2_axi_rready  (s2_rready)
    );

    // 3. Slave 0: On-Chip Block RAM (32 KB)
    axi_ram #(
        .DATA_WIDTH     (32),
        .MEM_WORDS      (MEM_WORDS),
        .MEM_INIT_FILE  (MEM_INIT_FILE)
    ) u_bram (
        .clk          (clk),
        .rst_n        (rst_n_sync),

        .s_axi_awaddr (s0_awaddr),
        .s_axi_awprot (s0_awprot),
        .s_axi_awvalid(s0_awvalid),
        .s_axi_awready(s0_awready),

        .s_axi_wdata  (s0_wdata),
        .s_axi_wstrb  (s0_wstrb),
        .s_axi_wvalid (s0_wvalid),
        .s_axi_wready (s0_wready),

        .s_axi_bresp  (s0_bresp),
        .s_axi_bvalid (s0_bvalid),
        .s_axi_bready (s0_bready),

        .s_axi_araddr (s0_araddr),
        .s_axi_arprot (s0_arprot),
        .s_axi_arvalid(s0_arvalid),
        .s_axi_arready(s0_arready),

        .s_axi_rdata  (s0_rdata),
        .s_axi_rresp  (s0_rresp),
        .s_axi_rvalid (s0_rvalid),
        .s_axi_rready (s0_rready)
    );

    // 4. Slave 1: Systolic Array GEMM Accelerator
    logic accel_busy;
    logic accel_done;

    systolic_gemm_axi_lite #(
        .ARRAY_SIZE         (ARRAY_SIZE),
        .DATA_WIDTH         (DATA_WIDTH),
        .ACC_WIDTH          (ACC_WIDTH),
        .C_S_AXI_DATA_WIDTH (32),
        .C_S_AXI_ADDR_WIDTH (12)
    ) u_accelerator (
        .s_axi_aclk    (clk),
        .s_axi_aresetn (rst_n_sync),

        .s_axi_awaddr  (s1_awaddr[11:0]),
        .s_axi_awprot  (s1_awprot),
        .s_axi_awvalid (s1_awvalid),
        .s_axi_awready (s1_awready),

        .s_axi_wdata   (s1_wdata),
        .s_axi_wstrb   (s1_wstrb),
        .s_axi_wvalid  (s1_wvalid),
        .s_axi_wready  (s1_wready),

        .s_axi_bresp   (s1_bresp),
        .s_axi_bvalid  (s1_bvalid),
        .s_axi_bready  (s1_bready),

        .s_axi_araddr  (s1_araddr[11:0]),
        .s_axi_arprot  (s1_arprot),
        .s_axi_arvalid (s1_arvalid),
        .s_axi_arready (s1_arready),

        .s_axi_rdata   (s1_rdata),
        .s_axi_rresp   (s1_rresp),
        .s_axi_rvalid  (s1_rvalid),
        .s_axi_rready  (s1_rready),

        .core_busy_out (accel_busy),
        .core_done_out (accel_done)
    );

    // 5. Slave 2: UART / Console & Board Peripheral Controller
    // Hardware board interfaces
    logic [3:0] hex_digit_0;
    logic [3:0] hex_digit_1;
    logic [7:0] board_leds;
    logic       rx_valid_flag;

    // 7-Segment Displays for Terasic DE1
    seven_seg_decoder u_hex0 (
        .digit (hex_digit_0),
        .blank (1'b0),
        .seg   (hex0)
    );

    seven_seg_decoder u_hex1 (
        .digit (hex_digit_1),
        .blank (1'b0),
        .seg   (hex1)
    );

    // Board Status LEDs
    assign ledr[0]   = trap;
    assign ledr[1]   = accel_busy;
    assign ledr[9:2] = board_leds[7:0];

    assign ledg[0]   = accel_done;
    assign ledg[1]   = rx_valid_flag;
    assign ledg[7:2] = 6'b000000;

    axi_uart #(
        .CLKS_PER_BIT (UART_CLKS_PER_BIT)
    ) u_uart (
        .clk          (clk),
        .rst_n        (rst_n_sync),
        .uart_rx      (uart_rx),
        .uart_tx      (uart_tx),
        .hex_digit_0  (hex_digit_0),
        .hex_digit_1  (hex_digit_1),
        .board_leds   (board_leds),
        .rx_valid_flag(rx_valid_flag),

        .s_axi_awaddr (s2_awaddr),
        .s_axi_awprot (s2_awprot),
        .s_axi_awvalid(s2_awvalid),
        .s_axi_awready(s2_awready),

        .s_axi_wdata  (s2_wdata),
        .s_axi_wstrb  (s2_wstrb),
        .s_axi_wvalid (s2_wvalid),
        .s_axi_wready (s2_wready),

        .s_axi_bresp  (s2_bresp),
        .s_axi_bvalid (s2_bvalid),
        .s_axi_bready (s2_bready),

        .s_axi_araddr (s2_araddr),
        .s_axi_arprot (s2_arprot),
        .s_axi_arvalid(s2_arvalid),
        .s_axi_arready(s2_arready),

        .s_axi_rdata  (s2_rdata),
        .s_axi_rresp  (s2_rresp),
        .s_axi_rvalid (s2_rvalid),
        .s_axi_rready (s2_rready)
    );

endmodule
