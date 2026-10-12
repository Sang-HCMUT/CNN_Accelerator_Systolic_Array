`timescale 1ns / 1ps

// ============================================================================
// Testbench: tb_soc_top.sv
// Description: Full Hardware-Software Co-Simulation Testbench for the
//              RISC-V PicoRV32 + Systolic Array AI Accelerator SoC.
//              - Boots CPU from On-Chip BRAM (firmware.hex).
//              - CPU runs RV32I instructions to configure and stream tiles.
//              - Accelerator executes pipelined Systolic GEMM.
//              - CPU reads output activations and prints verification to UART.
// ============================================================================

module tb_soc_top;

    localparam CLK_PERIOD = 20; // 50 MHz -> 20 ns period
    localparam MAX_CYCLES = 200000;

    logic clk;
    logic rst_n;
    logic trap;
    logic       uart_rx;
    logic [6:0] hex0;
    logic [6:0] hex1;
    logic [9:0] ledr;
    logic [7:0] ledg;

    // Clock Generation
    initial begin
        clk = 0;
        forever #(CLK_PERIOD / 2) clk = ~clk;
    end

    // Default idle for uart_rx
    initial uart_rx = 1'b1;

    // DUT Instantiation
    soc_top #(
        .ARRAY_SIZE        (4),
        .DATA_WIDTH        (8),
        .ACC_WIDTH         (32),
        .MEM_WORDS         (8192),
        .MEM_INIT_FILE     ("firmware.hex"),
        .UART_CLKS_PER_BIT (2)
    ) dut (
        .clk     (clk),
        .rst_n   (rst_n),
        .uart_rx (uart_rx),
        .uart_tx (uart_tx),
        .hex0    (hex0),
        .hex1    (hex1),
        .ledr    (ledr),
        .ledg    (ledg)
    );

    // Cycle Counter & Watchdog
    integer cycle_cnt = 0;
    integer uart_chars_cnt = 0;

    always @(posedge clk) begin
        cycle_cnt <= cycle_cnt + 1;

        if (dut.u_accelerator.core_start) $display("\n[TB-ACCEL] core_start pulsed at cycle %0d!", cycle_cnt);
        if (dut.u_accelerator.core_done)  $display("\n[TB-ACCEL] core_done pulsed at cycle %0d!", cycle_cnt);

        if (ledr[0]) begin
            $display("\n=======================================================");
            $display("[FATAL ERROR] PicoRV32 CPU entered TRAP state at cycle %0d!", cycle_cnt);
            $display("  PC         = 0x%08X", dut.u_cpu.picorv32_core.reg_pc);
            $display("  mem_addr   = 0x%08X", dut.u_cpu.picorv32_core.mem_addr);
            $display("  mem_wdata  = 0x%08X", dut.u_cpu.picorv32_core.mem_wdata);
            $display("  mem_rdata  = 0x%08X", dut.u_cpu.picorv32_core.mem_rdata);
            $display("=======================================================\n");
            $finish;
        end

        if (cycle_cnt > MAX_CYCLES) begin
            $display("\n=======================================================");
            $display("[TIMEOUT] Simulation reached %0d cycles at PC = 0x%08X!", MAX_CYCLES, dut.u_cpu.picorv32_core.reg_pc);
            $display("=======================================================\n");
            $finish;
        end

        if (dut.u_uart.tx_start) begin
            uart_chars_cnt <= uart_chars_cnt + 1;
            $write("%c", dut.u_uart.tx_byte_latch);
        end
    end

    // Simulation Sequence
    initial begin
        $display("\n=================================================================");
        $display("  STARTING PHASE 3: RISC-V SoC HARDWARE-SOFTWARE CO-SIMULATION");
        $display("  Architecture: PicoRV32 (RV32I) + AXI4-Lite + 4x4 Systolic Array");
        $display("=================================================================\n");

        rst_n = 0;
        #(CLK_PERIOD * 10);
        rst_n = 1;
        $display("[TB] Reset released. CPU execution started...\n");

        // Wait for CPU to reach halt address (0x18C)
        wait(dut.u_cpu.picorv32_core.reg_pc == 32'h0000018C);

        // Allow final UART character shift-out
        #(CLK_PERIOD * 50);

        $display("\n[TB] Hardware-Software Co-Simulation Completed Successfully!");
        $display("[TB] Total Simulation Cycles: %0d", cycle_cnt);
        $display("[TB] CPU Retired Instructions: %0d", dut.u_cpu.picorv32_core.count_instr);
        $display("[TB] UART Characters Transmitted: %0d", uart_chars_cnt);
        $display("=================================================================\n");
        $finish;
    end

endmodule
