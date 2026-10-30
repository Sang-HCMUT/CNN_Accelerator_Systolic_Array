# Terasic DE2 Board Synthesis & Bring-Up Guide

This directory contains the Quartus II 13.0 SP1 project configuration, timing constraints, and programming scripts for deploying the RISC-V SoC with INT8 Systolic GEMM Accelerator on the **Terasic DE2 Development and Education Board**.

---

## 1. Target Hardware Specifications

| Parameter | Specification |
| :--- | :--- |
| **FPGA Board** | Terasic DE2 Development & Education Board |
| **Target Device** | Altera Cyclone II **EP2C35F672C6** |
| **Systolic Array Size** | **$8 \times 8$ (64 Processing Elements)** |
| **Logic Elements (LEs)**| **16,356 / 33,216 (49.2%)** |
| **Registers** | **8,961 / 33,216 (27.0%)** |
| **M4K RAM Blocks** | 105 (483,840 RAM bits) — **265,216 bits used (54.8%)** |
| **Embedded Multipliers**| 35 (up to 70 9x9 multipliers) — **64 / 70 used (91.4%)** |
| **Primary Clock** | 50.000 MHz Oscillator (`PIN_N2`, `CLOCK_50`) |
| **Worst-Case Slack (@ 50MHz)**| **+3.395 ns** (Setup), **+0.391 ns** (Hold) |
| **Maximum Frequency ($F_{max}$)**| **60.22 MHz** ($T_{clk} = 16.605 \text{ ns}$) |
| **Peak Throughput (@ 50MHz)**| **6.40 GOPS** (3.20 GMAC/s) |
| **Reset Input** | Pushbutton `KEY[0]` (`PIN_G26`, Active-Low) |
| **UART Interface** | Onboard RS-232 DB9 Connector (MAX232 transceiver) |
| **Display Outputs** | 8x 7-Segment Displays (`HEX0`..`HEX7`) |
| **LED Indicators** | 18x Red LEDs (`LEDR[17:0]`), 9x Green LEDs (`LEDG[8:0]`) |
| **Synthesis Tool** | Altera Quartus II 13.0 SP1 (64-bit) |

---

## 2. Pin Assignments Summary

All pin assignments are extracted from the official `DE2_pin_assignments.csv`:

### Clock & Reset
- **System Clock (50 MHz)**: `clk` -> `PIN_N2` (3.3-V LVTTL)
- **Active-Low Reset**: `rst_n` -> `PIN_G26` (`KEY[0]`, 3.3-V LVTTL)

### RS-232 UART Serial Port
- **Receive (RX)**: `uart_rx` -> `PIN_C25` (`UART_RXD`)
- **Transmit (TX)**: `uart_tx` -> `PIN_B25` (`UART_TXD`)
- **Baud Rate**: 115,200 baud (50 MHz / 434 clock cycles per bit)

### 7-Segment Displays (`HEX0`..`HEX7`)
- **HEX0 (AI Prediction Units Digit)**:
  `AF10` (0), `AB12` (1), `AC12` (2), `AD11` (3), `AE11` (4), `V14` (5), `V13` (6)
- **HEX1 (AI Prediction Tens Digit)**:
  `V20` (0), `V21` (1), `W21` (2), `Y22` (3), `AA24` (4), `AA23` (5), `AB24` (6)
- **HEX2..HEX7**: Blanked (`7'b111_1111`)

### LED Diagnostics
- **LEDR[0]**: CPU Trap Error (Lit = fatal CPU halt / unhandled exception)
- **LEDR[1]**: Systolic Accelerator Busy
- **LEDR[9:2]**: Firmware Register Diagnostics (`REG_LEDS`)
- **LEDR[16:10]**: Reserved (Tied to GND)
- **LEDR[17]**: 1 Hz Heartbeat Monitor (blinks every 0.5s to show clock is alive)
- **LEDG[0]**: Accelerator Tile Done pulse
- **LEDG[1]**: UART RX Valid flag
- **LEDG[7:2]**: Internal diagnostics
- **LEDG[8]**: 1 Hz Green Heartbeat Monitor

---

## 3. Compilation & FPGA Programming

### Step 1: Synthesis & Timing Analysis
Run the batch build script in a Command Prompt or terminal:
```cmd
cd synthesis_soc_de2
compile_soc_de2.bat
```
This executes:
1. `quartus_map` - Analysis & RTL elaboration
2. `quartus_fit` - Placement, routing & I/O assignment
3. `quartus_asm` - Bitstream generation (`soc_top_de2.sof`)
4. `quartus_sta` - TimeQuest STA verification against 50 MHz constraint

### Step 2: Programming the DE2 Board
1. Connect the USB-Blaster cable between the PC and the DE2 **USB BLASTER** port.
2. Turn on DE2 board power (Blue pushbutton).
3. Set the **RUN/PROG** toggle switch on the DE2 board to **RUN**.
4. Run:
```cmd
program_de2.bat
```
5. Open your terminal emulator (e.g. PuTTY or minicom) at **115,200 baud, 8-N-1** on the connected COM port to interact with the firmware demo suite.
