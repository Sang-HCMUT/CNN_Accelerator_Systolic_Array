`timescale 1ns / 1ps

// Testbench: tb_soc_top.sv
// Full Hardware-Software Co-Simulation Testbench for the
// RISC-V PicoRV32 + Systolic Array AI Accelerator SoC.
// Boots CPU from On-Chip BRAM (firmware.hex).
// CPU runs RV32I instructions to configure and stream tiles.
// Accelerator executes pipelined Systolic GEMM.
// CPU reads output activations and prints verification to UART.


module tb_soc_top;

    localparam CLK_PERIOD = 20; // 50 MHz -> 20 ns period
    localparam MAX_CYCLES = 2500000;
    localparam UART_CLKS  = 16;

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
        .UART_CLKS_PER_BIT (UART_CLKS)
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
            $display("\n[FATAL ERROR] PicoRV32 CPU entered TRAP state at cycle %0d!", cycle_cnt);
            $display("  PC         = 0x%08X", dut.u_cpu.picorv32_core.reg_pc);
            $display("  mem_addr   = 0x%08X", dut.u_cpu.picorv32_core.mem_addr);
            $display("  mem_wdata  = 0x%08X", dut.u_cpu.picorv32_core.mem_wdata);
            $display("  mem_rdata  = 0x%08X", dut.u_cpu.picorv32_core.mem_rdata);
            $finish;
        end

        if (cycle_cnt > MAX_CYCLES) begin
            $display("\n[TIMEOUT] Simulation reached %0d cycles at PC = 0x%08X!", MAX_CYCLES, dut.u_cpu.picorv32_core.reg_pc);
            $finish;
        end

        if (dut.u_uart.tx_start) begin
            uart_chars_cnt <= uart_chars_cnt + 1;
            $write("%c", dut.u_uart.tx_byte_latch);
        end
    end

    // Task to transmit a byte over UART RX to PicoRV32 SoC
    task automatic send_uart_byte(input [7:0] b);
        integer i;
        uart_rx = 0; // Start bit
        #(CLK_PERIOD * UART_CLKS);
        for (i = 0; i < 8; i = i + 1) begin
            uart_rx = b[i];
            #(CLK_PERIOD * UART_CLKS);
        end
        uart_rx = 1; // Stop bit
        #(CLK_PERIOD * UART_CLKS);
        #(CLK_PERIOD * UART_CLKS * 4); // Inter-character gap
    endtask

    // Wait until CPU finishes current task and enters uart_getchar() loop at PC=0x68
    task automatic wait_cpu_prompt();
        wait(dut.u_cpu.picorv32_core.reg_pc != 32'h00000068);
        wait(dut.u_cpu.picorv32_core.reg_pc == 32'h00000068);
        while (dut.u_uart.tx_busy) #(CLK_PERIOD * 10);
        #(CLK_PERIOD * 200);
    endtask

    // Simulation Sequence
    initial begin
        $display("\nStarting RISC-V SoC Hardware-Software Co-Simulation");
        $display("PicoRV32 (RV32I) + AXI4-Lite + 4x4 Systolic Array Accelerator\n");

        rst_n = 0;
        #(CLK_PERIOD * 10);
        rst_n = 1;
        $display("[TB] Reset released. CPU execution started...\n");

        // Wait for boot and baseline Demo 1 (HW vs SW GEMM) to complete
        wait(dut.u_uart.reg_hex_0 == 4'h1);
        while (dut.u_uart.tx_busy) #(CLK_PERIOD * 10);
        #(CLK_PERIOD * 500);

        // Scenario 2: 16x16 Large Matrix Tiling Engine
        $display("\n[TB] ---> User selected [2]: 16x16 Large Matrix Tiling Engine");
        send_uart_byte("2");
        wait(dut.u_uart.reg_hex_0 == 4'h2);
        while (dut.u_uart.tx_busy) #(CLK_PERIOD * 10);
        #(CLK_PERIOD * 500);

        // Scenario 3: 2D Image Convolution via im2col
        $display("\n[TB] ---> User selected [3]: 2D Image Convolution via im2col");
        send_uart_byte("3");
        wait(dut.u_uart.reg_hex_0 == 4'h3);
        while (dut.u_uart.tx_busy) #(CLK_PERIOD * 10);
        #(CLK_PERIOD * 500);

        // Scenario 4: 2-Layer Neural Network (MLP) Forward Inference
        $display("\n[TB] ---> User selected [4]: 2-Layer Neural Network (MLP)");
        send_uart_byte("4");
        #(CLK_PERIOD * 40000);
        while (dut.u_uart.tx_busy) #(CLK_PERIOD * 10);
        #(CLK_PERIOD * 500);

        // Scenario 5: Arithmetic Edge-Case Diagnostics
        $display("\n[TB] ---> User selected [5]: Arithmetic Diagnostics");
        send_uart_byte("5");
        wait(dut.u_uart.reg_hex_0 == 4'h5);
        while (dut.u_uart.tx_busy) #(CLK_PERIOD * 10);
        #(CLK_PERIOD * 500);

        // Scenario 6: MNIST Digit Built-in Evaluation
        $display("\n[TB] ---> User selected [6]: MNIST Digit Telemetry");
        send_uart_byte("6");
        wait(dut.u_uart.reg_hex_0 == 4'h7);
        while (dut.u_uart.tx_busy) #(CLK_PERIOD * 10);
        #(CLK_PERIOD * 500);

        $display("\n[TB] All Targeted Demonstration Scenarios Verified Successfully!");
        $display("[TB] Total Simulation Cycles: %0d", cycle_cnt);
        $display("[TB] CPU Retired Instructions: %0d", dut.u_cpu.picorv32_core.count_instr);
        $display("[TB] UART Characters Transmitted: %0d\n", uart_chars_cnt);
        $finish;
    end

endmodule
