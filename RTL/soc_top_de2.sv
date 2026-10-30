`timescale 1ns / 1ps

// ============================================================================
// Module: soc_top_de2.sv
// Target: Terasic DE2 Development & Education Board (Altera Cyclone II EP2C35F672C6)
// Top-Level Board Wrapper adapting the RISC-V SoC Systolic CNN Accelerator.
//
// Hardware Features & Mappings:
//   - Systolic Array Size: 8x8 = 64 PEs (64 Embedded 9-bit Multipliers)
//   - Clock:  50 MHz Crystal Oscillator on PIN_N2 (CLOCK_50)
//   - Reset:  KEY[0] Active-Low Pushbutton on PIN_G26 (with AASD synchronizer inside soc_top)
//   - UART:   Dedicated RS-232 Transceiver DB9 Port
//             UART_RXD on PIN_C25 (from Host PC / USB-Serial)
//             UART_TXD on PIN_B25 (to Host PC / USB-Serial)
//   - 7-Seg:  HEX0..HEX7 (8 active-low 7-segment displays)
//             HEX0: Units digit of AI prediction
//             HEX1: Tens digit of AI prediction
//             HEX2..HEX7: Blanked (tied to 7'b1111111)
//   - LEDs:   LEDR[17:0] (18 Red LEDs)
//               LEDR[0]   : CPU Trap Error (should remain OFF)
//               LEDR[1]   : Systolic Array Computing (Busy)
//               LEDR[9:2] : Firmware Diagnostics / Register Map LEDs
//               LEDR[15:10]: Reserved (Tied to 0)
//               LEDR[16]  : 8x8 Mode Indicator (Always ON = 64 PEs active)
//               LEDR[17]  : 1 Hz Heartbeat Monitor (alive indicator)
//             LEDG[8:0] (9 Green LEDs)
//               LEDG[0]   : Systolic Array Tile Done
//               LEDG[1]   : UART RX Valid Activity
//               LEDG[7:2] : Diagnostic status
//               LEDG[8]   : 1 Hz Heartbeat Monitor (synchronized with LEDR[17])
// ============================================================================

module soc_top_de2 #(
    parameter ARRAY_SIZE        = 8,         // 8x8 = 64 PEs (Mapped to 64/70 DSP blocks on EP2C35)
    parameter DATA_WIDTH        = 8,
    parameter ACC_WIDTH         = 32,
    parameter MEM_WORDS         = 8192,      // 32 KB Main BRAM
    parameter MEM_INIT_FILE     = "firmware.hex",
    parameter UART_CLKS_PER_BIT = 434
)(
    // Clock & Pushbutton Reset
    input  logic        clk,         // 50 MHz Oscillator (CLOCK_50: PIN_N2)
    input  logic        rst_n,       // Pushbutton KEY[0] Active-Low (PIN_G26)

    // RS-232 Serial Port
    input  logic        uart_rx,     // UART_RXD (PIN_C25)
    output logic        uart_tx,     // UART_TXD (PIN_B25)

    // 8x 7-Segment Displays (Active-Low: 0 = Lit, 1 = Blank)
    output logic [6:0]  hex0,        // Units digit of classification (PIN_AF10, ...)
    output logic [6:0]  hex1,        // Tens digit of classification (PIN_V20, ...)
    output logic [6:0]  hex2,        // Blanked
    output logic [6:0]  hex3,        // Blanked
    output logic [6:0]  hex4,        // Blanked
    output logic [6:0]  hex5,        // Blanked
    output logic [6:0]  hex6,        // Blanked
    output logic [6:0]  hex7,        // Blanked

    // 18x Red LEDs
    output logic [17:0] ledr,

    // 9x Green LEDs
    output logic [8:0]  ledg
);

    // Internal bus wires between wrapper and core SoC
    logic [9:0] soc_ledr;
    logic [7:0] soc_ledg;

    // ------------------------------------------------------------------------
    // 1 Hz Heartbeat Counter (at 50 MHz system clock)
    // Blinks LEDR[17] and LEDG[8] every 0.5s (1 Hz cycle) to visually confirm
    // that the clock network is operating and the board is actively running.
    // ------------------------------------------------------------------------
    logic [25:0] hb_cnt;
    logic        heartbeat;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            hb_cnt    <= 26'd0;
            heartbeat <= 1'b0;
        end else begin
            if (hb_cnt == 26'd24_999_999) begin
                hb_cnt    <= 26'd0;
                heartbeat <= ~heartbeat;
            end else begin
                hb_cnt <= hb_cnt + 26'd1;
            end
        end
    end

    // ------------------------------------------------------------------------
    // SoC Core Instantiation (8x8 = 64 PEs Systolic Array)
    // ------------------------------------------------------------------------
    soc_top #(
        .ARRAY_SIZE        (ARRAY_SIZE),
        .DATA_WIDTH        (DATA_WIDTH),
        .ACC_WIDTH         (ACC_WIDTH),
        .MEM_WORDS         (MEM_WORDS),
        .MEM_INIT_FILE     (MEM_INIT_FILE),
        .UART_CLKS_PER_BIT (UART_CLKS_PER_BIT)
    ) u_soc_core (
        .clk     (clk),
        .rst_n   (rst_n),
        .uart_rx (uart_rx),
        .uart_tx (uart_tx),
        .hex0    (hex0),
        .hex1    (hex1),
        .ledr    (soc_ledr),
        .ledg    (soc_ledg)
    );

    // ------------------------------------------------------------------------
    // Peripheral Routing & Blanking
    // ------------------------------------------------------------------------
    // Turn off unused 7-segment displays (active-low 1111111)
    assign hex2 = 7'b111_1111;
    assign hex3 = 7'b111_1111;
    assign hex4 = 7'b111_1111;
    assign hex5 = 7'b111_1111;
    assign hex6 = 7'b111_1111;
    assign hex7 = 7'b111_1111;

    // Red LED Mapping
    assign ledr[9:0]   = soc_ledr[9:0];
    assign ledr[15:10] = 6'b000_000;
    assign ledr[16]    = 1'b1;          // Indicator: 8x8 Mode Active (64 PEs)
    assign ledr[17]    = heartbeat;

    // Green LED Mapping
    assign ledg[7:0]   = soc_ledg[7:0];
    assign ledg[8]     = heartbeat;

endmodule
