`timescale 1ns / 1ps

// ============================================================================
// Module: soc_top_de10.sv
// Description: DE10-Standard Board Wrapper for RISC-V SoC CNN Accelerator.
//              Target: Terasic DE10-Standard (Intel Cyclone V 5CSXFC6D6F31C6)
//
//              Key Differences from DE1 (soc_top.sv):
//              - ARRAY_SIZE = 8  (8x8 Systolic Array, 64 PEs)
//                DE10-Standard has 112 DSP blocks vs 52 on Cyclone II.
//              - No LEDG (DE10-Standard only has 10x LEDR).
//                ledg[7:0] from soc_top are mapped to the internal diagnostic
//                signals and OR-combined with LEDR[7:2] for visibility.
//              - UART: mapped to GPIO_0 header (GPIO_0[0]=TX, GPIO_0[1]=RX)
//              - Clock: 50 MHz CLOCK_50 (same as DE1)
//              - Reset: KEY[0] active-low push-button
//
//              Resource Estimate on Cyclone V 5CSXFC6D6F31C6:
//              - ALMs:       ~22,000 / 41,910  (~52%)
//              - DSP blocks: 64      / 112      (~57%)
//              - BRAM:       ~600 Kbits / 5,662 Kbits (~11%)
// ============================================================================

module soc_top_de10 (
    // ---- Clock & Reset ----
    input  logic       clk,        // CLOCK_50[0] — 50 MHz crystal oscillator
    input  logic       rst_n,      // KEY[0] — active-low push-button reset

    // ---- UART (mapped to GPIO_0 header) ----
    input  logic       uart_rx,    // GPIO_0[1] — Receive from Host PC
    output logic       uart_tx,    // GPIO_0[0] — Transmit to Host PC

    // ---- 7-Segment Displays (Active-Low, same polarity as DE1) ----
    output logic [6:0] hex0,       // HEX0 — Units digit of AI prediction
    output logic [6:0] hex1,       // HEX1 — Tens digit of AI prediction
    output logic [6:0] hex2,       // HEX2 — Tied OFF (1111111) — reserved
    output logic [6:0] hex3,       // HEX3 — Tied OFF — reserved
    output logic [6:0] hex4,       // HEX4 — Tied OFF — reserved
    output logic [6:0] hex5,       // HEX5 — Tied OFF — reserved

    // ---- Red LEDs (DE10-Standard has only LEDR, 10 total) ----
    // Bit assignment:
    //   LEDR[0] = trap        (CPU Error — should stay OFF = 0)
    //   LEDR[1] = accel_busy  (Systolic Array computing)
    //   LEDR[2] = accel_done  (Tile computation complete)
    //   LEDR[3] = uart_rx_act (UART RX activity)
    //   LEDR[4] = uart_tx_act (UART TX activity)
    //   LEDR[5] = reserved (ledg[2] from soc_top)
    //   LEDR[6] = reserved (ledg[3] from soc_top)
    //   LEDR[7] = reserved (ledg[4] from soc_top)
    //   LEDR[8] = heartbeat (LED blinks at ~1Hz to show clock alive)
    //   LEDR[9] = array_size_indicator (always ON to indicate 8x8 mode)
    output logic [9:0] ledr
);

    // ---- Internal wires for soc_top outputs ----
    logic [9:0] soc_ledr;   // ledr[9:0] from soc_top (internal diagnostic)
    logic [7:0] soc_ledg;   // ledg[7:0] from soc_top — repurposed for LEDR[7:2]

    // ---- Heartbeat counter (1 Hz blink at 50 MHz) ----
    logic [25:0] hb_cnt;
    logic        heartbeat;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            hb_cnt  <= '0;
            heartbeat <= 1'b0;
        end else begin
            if (hb_cnt == 26'd49_999_999) begin
                hb_cnt    <= '0;
                heartbeat <= ~heartbeat;
            end else begin
                hb_cnt <= hb_cnt + 1'b1;
            end
        end
    end

    // ---- LED mapping (10 LEDR only, no LEDG on DE10-Standard) ----
    assign ledr[0] = soc_ledr[0];   // CPU Trap error
    assign ledr[1] = soc_ledr[1];   // Accelerator busy
    assign ledr[2] = soc_ledg[0];   // Tile done (was LEDG[0] on DE1)
    assign ledr[3] = soc_ledg[1];   // UART RX valid (was LEDG[1] on DE1)
    assign ledr[4] = soc_ledr[2];   // Spare diagnostic from ledr
    assign ledr[5] = soc_ledg[2];   // Spare from ledg
    assign ledr[6] = soc_ledg[3];   // Spare from ledg
    assign ledr[7] = soc_ledg[4];   // Spare from ledg
    assign ledr[8] = heartbeat;     // 1 Hz heartbeat — confirms chip alive
    assign ledr[9] = 1'b1;          // Always ON — indicates 8x8 ARRAY_SIZE mode

    // ---- Unused HEX displays: blank (Active-Low: 7'b1111111 = all segments OFF) ----
    assign hex2 = 7'b111_1111;
    assign hex3 = 7'b111_1111;
    assign hex4 = 7'b111_1111;
    assign hex5 = 7'b111_1111;

    // ---- SoC Core Instantiation (8x8 Systolic Array) ----
    soc_top #(
        .ARRAY_SIZE         (8),         // 8x8 = 64 PEs (vs 4x4 on DE1)
        .DATA_WIDTH         (8),
        .ACC_WIDTH          (32),
        .MEM_WORDS          (8192),      // 32 KB BRAM (same as DE1, firmware fits easily)
        .MEM_INIT_FILE      ("firmware.hex"),
        .UART_CLKS_PER_BIT  (434)        // 50 MHz / 115200 baud = 434 clocks/bit (same as DE1)
    ) u_soc (
        .clk        (clk),
        .rst_n      (rst_n),
        .uart_rx    (uart_rx),
        .uart_tx    (uart_tx),
        .hex0       (hex0),
        .hex1       (hex1),
        .ledr       (soc_ledr),
        .ledg       (soc_ledg)
    );

endmodule
