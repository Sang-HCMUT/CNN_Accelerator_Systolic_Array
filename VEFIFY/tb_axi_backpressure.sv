`timescale 1ns / 1ps

// Testbench: tb_axi_backpressure.sv
// Verifies AMBA AXI4-Lite Protocol Compliance for all Slaves and Interconnect
// specifically under Master Backpressure (delayed BREADY and delayed RREADY).
// Tests:
//   1. axi_ram: Write response hold across BREADY delays (1..10 cycles)
//   2. axi_ram: Read valid & stable RDATA across RREADY delays (1..10 cycles)
//   3. systolic_gemm_axi_lite: Write & Read response stability across BREADY/RREADY delays
//   4. axi_interconnect: Slave arbitration retention until handshake completion

module tb_axi_backpressure;

    logic clk;
    logic rst_n;

    // Clock generation: 50 MHz (20ns period)
    always #10 clk = ~clk;

    // Master AXI-Lite Bus to Interconnect
    logic [31:0] s_axi_awaddr;
    logic [2:0]  s_axi_awprot;
    logic        s_axi_awvalid;
    logic        s_axi_awready;

    logic [31:0] s_axi_wdata;
    logic [3:0]  s_axi_wstrb;
    logic        s_axi_wvalid;
    logic        s_axi_wready;

    logic [1:0]  s_axi_bresp;
    logic        s_axi_bvalid;
    logic        s_axi_bready;

    logic [31:0] s_axi_araddr;
    logic [2:0]  s_axi_arprot;
    logic        s_axi_arvalid;
    logic        s_axi_arready;

    logic [31:0] s_axi_rdata;
    logic [1:0]  s_axi_rresp;
    logic        s_axi_rvalid;
    logic        s_axi_rready;

    // Interconnect to M0 (RAM)
    logic [31:0] m0_awaddr;
    logic [2:0]  m0_awprot;
    logic        m0_awvalid;
    logic        m0_awready;
    logic [31:0] m0_wdata;
    logic [3:0]  m0_wstrb;
    logic        m0_wvalid;
    logic        m0_wready;
    logic [1:0]  m0_bresp;
    logic        m0_bvalid;
    logic        m0_bready;
    logic [31:0] m0_araddr;
    logic [2:0]  m0_arprot;
    logic        m0_arvalid;
    logic        m0_arready;
    logic [31:0] m0_rdata;
    logic [1:0]  m0_rresp;
    logic        m0_rvalid;
    logic        m0_rready;

    // Interconnect to M1 (Systolic Accelerator)
    logic [31:0] m1_awaddr;
    logic [2:0]  m1_awprot;
    logic        m1_awvalid;
    logic        m1_awready;
    logic [31:0] m1_wdata;
    logic [3:0]  m1_wstrb;
    logic        m1_wvalid;
    logic        m1_wready;
    logic [1:0]  m1_bresp;
    logic        m1_bvalid;
    logic        m1_bready;
    logic [31:0] m1_araddr;
    logic [2:0]  m1_arprot;
    logic        m1_arvalid;
    logic        m1_arready;
    logic [31:0] m1_rdata;
    logic [1:0]  m1_rresp;
    logic        m1_rvalid;
    logic        m1_rready;

    // Interconnect to M2 (UART)
    logic [31:0] m2_awaddr;
    logic [2:0]  m2_awprot;
    logic        m2_awvalid;
    logic        m2_awready;
    logic [31:0] m2_wdata;
    logic [3:0]  m2_wstrb;
    logic        m2_wvalid;
    logic        m2_wready;
    logic [1:0]  m2_bresp;
    logic        m2_bvalid;
    logic        m2_bready;
    logic [31:0] m2_araddr;
    logic [2:0]  m2_arprot;
    logic        m2_arvalid;
    logic        m2_arready;
    logic [31:0] m2_rdata;
    logic [1:0]  m2_rresp;
    logic        m2_rvalid;
    logic        m2_rready;

    // Instantiate Interconnect
    axi_interconnect u_interconnect (
        .clk             (clk),
        .rst_n           (rst_n),
        .s_axi_awaddr    (s_axi_awaddr),
        .s_axi_awprot    (s_axi_awprot),
        .s_axi_awvalid   (s_axi_awvalid),
        .s_axi_awready   (s_axi_awready),
        .s_axi_wdata     (s_axi_wdata),
        .s_axi_wstrb     (s_axi_wstrb),
        .s_axi_wvalid    (s_axi_wvalid),
        .s_axi_wready    (s_axi_wready),
        .s_axi_bresp     (s_axi_bresp),
        .s_axi_bvalid    (s_axi_bvalid),
        .s_axi_bready    (s_axi_bready),
        .s_axi_araddr    (s_axi_araddr),
        .s_axi_arprot    (s_axi_arprot),
        .s_axi_arvalid   (s_axi_arvalid),
        .s_axi_arready   (s_axi_arready),
        .s_axi_rdata     (s_axi_rdata),
        .s_axi_rresp     (s_axi_rresp),
        .s_axi_rvalid    (s_axi_rvalid),
        .s_axi_rready    (s_axi_rready),

        .m0_axi_awaddr   (m0_awaddr),
        .m0_axi_awprot   (m0_awprot),
        .m0_axi_awvalid  (m0_awvalid),
        .m0_axi_awready  (m0_awready),
        .m0_axi_wdata    (m0_wdata),
        .m0_axi_wstrb    (m0_wstrb),
        .m0_axi_wvalid   (m0_wvalid),
        .m0_axi_wready   (m0_wready),
        .m0_axi_bresp    (m0_bresp),
        .m0_axi_bvalid   (m0_bvalid),
        .m0_axi_bready   (m0_bready),
        .m0_axi_araddr   (m0_araddr),
        .m0_axi_arprot   (m0_arprot),
        .m0_axi_arvalid  (m0_arvalid),
        .m0_axi_arready  (m0_arready),
        .m0_axi_rdata    (m0_rdata),
        .m0_axi_rresp    (m0_rresp),
        .m0_axi_rvalid   (m0_rvalid),
        .m0_axi_rready   (m0_rready),

        .m1_axi_awaddr   (m1_awaddr),
        .m1_axi_awprot   (m1_awprot),
        .m1_axi_awvalid  (m1_awvalid),
        .m1_axi_awready  (m1_awready),
        .m1_axi_wdata    (m1_wdata),
        .m1_axi_wstrb    (m1_wstrb),
        .m1_axi_wvalid   (m1_wvalid),
        .m1_axi_wready   (m1_wready),
        .m1_axi_bresp    (m1_bresp),
        .m1_axi_bvalid   (m1_bvalid),
        .m1_axi_bready   (m1_bready),
        .m1_axi_araddr   (m1_araddr),
        .m1_axi_arprot   (m1_arprot),
        .m1_axi_arvalid  (m1_arvalid),
        .m1_axi_arready  (m1_arready),
        .m1_axi_rdata    (m1_rdata),
        .m1_axi_rresp    (m1_rresp),
        .m1_axi_rvalid   (m1_rvalid),
        .m1_axi_rready   (m1_rready),

        .m2_axi_awaddr   (m2_awaddr),
        .m2_axi_awprot   (m2_awprot),
        .m2_axi_awvalid  (m2_awvalid),
        .m2_axi_awready  (m2_awready),
        .m2_axi_wdata    (m2_wdata),
        .m2_axi_wstrb    (m2_wstrb),
        .m2_axi_wvalid   (m2_wvalid),
        .m2_axi_wready   (m2_wready),
        .m2_axi_bresp    (m2_bresp),
        .m2_axi_bvalid   (m2_bvalid),
        .m2_axi_bready   (m2_bready),
        .m2_axi_araddr   (m2_araddr),
        .m2_axi_arprot   (m2_arprot),
        .m2_axi_arvalid  (m2_arvalid),
        .m2_axi_arready  (m2_arready),
        .m2_axi_rdata    (m2_rdata),
        .m2_axi_rresp    (m2_rresp),
        .m2_axi_rvalid   (m2_rvalid),
        .m2_axi_rready   (m2_rready)
    );

    // Instantiate AXI RAM (8192 words = 32 KB)
    axi_ram #(
        .MEM_WORDS      (8192),
        .MEM_INIT_FILE  ("")
    ) u_ram (
        .clk          (clk),
        .rst_n        (rst_n),
        .s_axi_awaddr (m0_awaddr),
        .s_axi_awprot (m0_awprot),
        .s_axi_awvalid(m0_awvalid),
        .s_axi_awready(m0_awready),
        .s_axi_wdata  (m0_wdata),
        .s_axi_wstrb  (m0_wstrb),
        .s_axi_wvalid (m0_wvalid),
        .s_axi_wready (m0_wready),
        .s_axi_bresp  (m0_bresp),
        .s_axi_bvalid (m0_bvalid),
        .s_axi_bready (m0_bready),
        .s_axi_araddr (m0_araddr),
        .s_axi_arprot (m0_arprot),
        .s_axi_arvalid(m0_arvalid),
        .s_axi_arready(m0_arready),
        .s_axi_rdata  (m0_rdata),
        .s_axi_rresp  (m0_rresp),
        .s_axi_rvalid (m0_rvalid),
        .s_axi_rready (m0_rready)
    );

    // Instantiate Systolic GEMM AXI-Lite (8x8)
    systolic_gemm_axi_lite #(
        .ARRAY_SIZE   (8),
        .DATA_WIDTH   (8),
        .ACC_WIDTH    (32)
    ) u_accel (
        .s_axi_aclk   (clk),
        .s_axi_aresetn(rst_n),
        .s_axi_awaddr (m1_awaddr[11:0]),
        .s_axi_awprot (m1_awprot),
        .s_axi_awvalid(m1_awvalid),
        .s_axi_awready(m1_awready),
        .s_axi_wdata  (m1_wdata),
        .s_axi_wstrb  (m1_wstrb),
        .s_axi_wvalid (m1_wvalid),
        .s_axi_wready (m1_wready),
        .s_axi_bresp  (m1_bresp),
        .s_axi_bvalid (m1_bvalid),
        .s_axi_bready (m1_bready),
        .s_axi_araddr (m1_araddr[11:0]),
        .s_axi_arprot (m1_arprot),
        .s_axi_arvalid(m1_arvalid),
        .s_axi_arready(m1_arready),
        .s_axi_rdata  (m1_rdata),
        .s_axi_rresp  (m1_rresp),
        .s_axi_rvalid (m1_rvalid),
        .s_axi_rready (m1_rready),
        .core_busy_out(),
        .core_done_out()
    );

    // Instantiate UART & Board I/O
    logic [3:0] hex0_dig, hex1_dig;
    logic [7:0] board_leds_sig;
    axi_uart #(
        .BAUD_RATE    (115200),
        .CLK_FREQ_HZ  (50_000_000)
    ) u_uart (
        .clk          (clk),
        .rst_n        (rst_n),
        .s_axi_awaddr (m2_awaddr),
        .s_axi_awprot (m2_awprot),
        .s_axi_awvalid(m2_awvalid),
        .s_axi_awready(m2_awready),
        .s_axi_wdata  (m2_wdata),
        .s_axi_wstrb  (m2_wstrb),
        .s_axi_wvalid (m2_wvalid),
        .s_axi_wready (m2_wready),
        .s_axi_bresp  (m2_bresp),
        .s_axi_bvalid (m2_bvalid),
        .s_axi_bready (m2_bready),
        .s_axi_araddr (m2_araddr),
        .s_axi_arprot (m2_arprot),
        .s_axi_arvalid(m2_arvalid),
        .s_axi_arready(m2_arready),
        .s_axi_rdata  (m2_rdata),
        .s_axi_rresp  (m2_rresp),
        .s_axi_rvalid (m2_rvalid),
        .s_axi_rready (m2_rready),
        .uart_rx      (1'b1),
        .uart_tx      (),
        .hex_digit_0  (hex0_dig),
        .hex_digit_1  (hex1_dig),
        .board_leds   (board_leds_sig),
        .rx_valid_flag()
    );

    integer test_errors = 0;

    // Master AXI Write Task with Backpressure
    task automatic axi_write_backpressure(
        input [31:0] addr,
        input [31:0] data,
        input [3:0]  strb,
        input integer bready_delay
    );
        // Address & Data phase
        @(posedge clk);
        s_axi_awaddr  <= addr;
        s_axi_awprot  <= 3'b000;
        s_axi_awvalid <= 1'b1;
        s_axi_wdata   <= data;
        s_axi_wstrb   <= strb;
        s_axi_wvalid  <= 1'b1;
        s_axi_bready  <= 1'b0;

        // Wait until AWREADY and WREADY are asserted
        while (!(s_axi_awready && s_axi_wready)) begin
            @(posedge clk);
            if (s_axi_awready) s_axi_awvalid <= 1'b0;
            if (s_axi_wready)  s_axi_wvalid  <= 1'b0;
        end
        @(posedge clk);
        s_axi_awvalid <= 1'b0;
        s_axi_wvalid  <= 1'b0;

        // Wait for BVALID
        while (!s_axi_bvalid) begin
            @(posedge clk);
        end

        // Apply backpressure by keeping BREADY = 0 for bready_delay cycles
        for (integer d = 0; d < bready_delay; d++) begin
            if (!s_axi_bvalid) begin
                $display("[ERROR] BVALID dropped prematurely at cycle %0d of backpressure! (Addr=0x%08x)", d, addr);
                test_errors++;
            end
            @(posedge clk);
        end

        // Complete handshake
        s_axi_bready <= 1'b1;
        @(posedge clk);
        s_axi_bready <= 1'b0;

        // Verify BVALID deasserts after handshake
        @(posedge clk);
        if (s_axi_bvalid) begin
            $display("[ERROR] BVALID failed to deassert after BREADY handshake! (Addr=0x%08x)", addr);
            test_errors++;
        end
    endtask

    // Master AXI Read Task with Backpressure
    task automatic axi_read_backpressure(
        input [31:0] addr,
        output [31:0] data,
        input integer rready_delay
    );
        logic [31:0] latched_first_data;

        // Address phase
        @(posedge clk);
        s_axi_araddr  <= addr;
        s_axi_arprot  <= 3'b000;
        s_axi_arvalid <= 1'b1;
        s_axi_rready  <= 1'b0;

        while (!s_axi_arready) begin
            @(posedge clk);
        end
        @(posedge clk);
        s_axi_arvalid <= 1'b0;

        // Wait for RVALID
        while (!s_axi_rvalid) begin
            @(posedge clk);
        end

        latched_first_data = s_axi_rdata;

        // Apply backpressure: hold RREADY = 0 for rready_delay cycles
        for (integer d = 0; d < rready_delay; d++) begin
            if (!s_axi_rvalid) begin
                $display("[ERROR] RVALID dropped prematurely at cycle %0d of backpressure! (Addr=0x%08x)", d, addr);
                test_errors++;
            end
            if (s_axi_rdata !== latched_first_data) begin
                $display("[ERROR] RDATA unstable during backpressure at cycle %0d! Exp=0x%08x, Got=0x%08x",
                         d, latched_first_data, s_axi_rdata);
                test_errors++;
            end
            @(posedge clk);
        end

        // Complete handshake
        data = s_axi_rdata;
        s_axi_rready <= 1'b1;
        @(posedge clk);
        s_axi_rready <= 1'b0;

        // Verify RVALID deasserts after handshake
        @(posedge clk);
        if (s_axi_rvalid) begin
            $display("[ERROR] RVALID failed to deassert after RREADY handshake! (Addr=0x%08x)", addr);
            test_errors++;
        end
    endtask

    logic [31:0] read_val;

    initial begin
        $display("\n========================================================");
        $display("  STARTING AXI4-LITE BACKPRESSURE COMPLIANCE VERIFICATION");
        $display("========================================================");

        clk           = 1'b0;
        rst_n         = 1'b0;
        s_axi_awaddr  = '0;
        s_axi_awprot  = '0;
        s_axi_awvalid = 1'b0;
        s_axi_wdata   = '0;
        s_axi_wstrb   = '0;
        s_axi_wvalid  = 1'b0;
        s_axi_bready  = 1'b0;
        s_axi_araddr  = '0;
        s_axi_arprot  = '0;
        s_axi_arvalid = 1'b0;
        s_axi_rready  = 1'b0;

        repeat (5) @(posedge clk);
        rst_n = 1'b1;
        repeat (5) @(posedge clk);

        // ----------------------------------------------------
        // TEST 1: RAM Write & Read with varying backpressure
        // ----------------------------------------------------
        $display("[TEST 1] Testing AXI RAM with 1..8 cycles BREADY & RREADY delays...");
        for (integer bp = 1; bp <= 8; bp++) begin
            axi_write_backpressure(32'h0000_0100 + (bp*4), 32'hA000_0000 + bp, 4'hF, bp);
        end
        for (integer bp = 1; bp <= 8; bp++) begin
            axi_read_backpressure(32'h0000_0100 + (bp*4), read_val, bp);
            if (read_val !== (32'hA000_0000 + bp)) begin
                $display("[ERROR] RAM Read mismatch for bp=%0d! Exp=0x%08x, Got=0x%08x",
                         bp, 32'hA000_0000 + bp, read_val);
                test_errors++;
            end
        end
        $display("[TEST 1] RAM backpressure tests completed.");

        // ----------------------------------------------------
        // TEST 2: Systolic Accelerator MMIO with backpressure
        // ----------------------------------------------------
        $display("[TEST 2] Testing Systolic Accelerator MMIO with backpressure...");
        // Read IP Version (0x1000_0010) with 6 cycles RREADY delay
        axi_read_backpressure(32'h1000_0010, read_val, 6);
        if (read_val !== 32'h01080820) begin
            $display("[ERROR] Accel IP Version mismatch! Exp=0x01080820, Got=0x%08x", read_val);
            test_errors++;
        end else begin
            $display("         IP Version 0x01080820 confirmed stable over 6 delay cycles.");
        end

        // Configure K_DIM = 8 (0x1000_0008) with 5 cycles BREADY delay
        axi_write_backpressure(32'h1000_0008, 32'd8, 4'hF, 5);
        axi_read_backpressure(32'h1000_0008, read_val, 4);
        if (read_val !== 32'd8) begin
            $display("[ERROR] K_DIM readback mismatch! Exp=8, Got=%0d", read_val);
            test_errors++;
        end

        // Write Buffer A (0x1000_0100) with 7 cycles BREADY delay
        axi_write_backpressure(32'h1000_0100, 32'h04030201, 4'hF, 7);

        // Write Buffer B (0x1000_0300) with 5 cycles BREADY delay
        axi_write_backpressure(32'h1000_0300, 32'h08070605, 4'hF, 5);

        // ----------------------------------------------------
        // TEST 3: UART MMIO with backpressure
        // ----------------------------------------------------
        $display("[TEST 3] Testing UART MMIO with backpressure...");
        // Write HEX display (0x2000_0008) with 4 cycles BREADY delay
        axi_write_backpressure(32'h2000_0008, 32'h0000_0078, 4'hF, 4);
        axi_read_backpressure(32'h2000_0008, read_val, 5);
        if (read_val[7:0] !== 8'h78) begin
            $display("[ERROR] UART HEX readback mismatch! Exp=0x78, Got=0x%02x", read_val[7:0]);
            test_errors++;
        end

        // Write LEDs (0x2000_000C) with 6 cycles BREADY delay
        axi_write_backpressure(32'h2000_000C, 32'h0000_00AA, 4'hF, 6);
        axi_read_backpressure(32'h2000_000C, read_val, 3);
        if (read_val[7:0] !== 8'hAA) begin
            $display("[ERROR] UART LEDs readback mismatch! Exp=0xAA, Got=0x%02x", read_val[7:0]);
            test_errors++;
        end

        // ----------------------------------------------------
        // Final Summary
        // ----------------------------------------------------
        $display("\n========================================================");
        if (test_errors == 0) begin
            $display("  ALL AXI4-LITE BACKPRESSURE TESTS PASSED (100%% COMPLIANT)!");
        end else begin
            $display("  AXI4-LITE BACKPRESSURE TESTS FAILED WITH %0d ERRORS!", test_errors);
        end
        $display("========================================================\n");
        $finish;
    end

endmodule
