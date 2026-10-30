# Parameterized 2D Systolic Array CNN Accelerator on FPGA

[![FPGA](https://img.shields.io/badge/FPGA-Cyclone%20II%20(DE1%2FDE2)%20%7C%20Cyclone%20V%20(DE10)-blue.svg)](https://www.intel.com/)
[![HDL](https://img.shields.io/badge/HDL-SystemVerilog%20(IEEE%201800--2012)-orange.svg)](https://en.wikipedia.org/wiki/SystemVerilog)
[![Tool](https://img.shields.io/badge/EDA-Quartus%20II%20%26%20ModelSim-green.svg)](https://www.intel.com/)
[![Verification](https://img.shields.io/badge/Verification-100%25%20Bit--True%20(16%2F16%20%26%206%2F6%20Stress%20Passed)-brightgreen.svg)](#verification--test-results)

An open-source, modular, and parameterized hardware accelerator designed for Convolutional Neural Networks (CNNs) based on an **Output-Stationary 2D Systolic Array**. Evaluated and verified across three target FPGA development boards:
- **Terasic DE1** (Altera Cyclone II `EP2C20F484C7`, 4x4 array)
- **Terasic DE2** (Altera Cyclone II `EP2C35F672C6`, 8x8 array with 64 PEs, 8x 7-segments & 18 LEDs)
- **Terasic DE10-Standard** (Intel Cyclone V `5CSXFC6D6F31C6N`, 8x8 array with 64 PEs)

Features quantized **Signed INT8** inputs/weights, **Signed INT32** accumulation, on-the-fly **ReLU / Arithmetic Scaling / Saturation Clamping**, and an **AMBA AXI4-Lite** interface.

---

## Key Architectural Highlights

- **GEMM via `im2col`**: Transforms high-dimensional 2D convolutions into generalized matrix multiplication ($C = A \times B$), eliminating complex multi-nested loops.
- **Output-Stationary 2D Systolic Array**: Accumulates partial products locally within Processing Elements (PEs), drastically minimizing data movement.
- **Wavefront Skew Network**: Dedicated input pipeline skew unit delaying rows ($i \cdot T$) and columns ($j \cdot T$) for rhythmic pulse-based synchronization.
- **Pure Structural Hierarchy**: Modularized into 7 clean, decoupled modules with pristine schematic visualization in Quartus RTL Viewer.
- **Dual-Channel Output Buffer**: Simultaneously stores 32-bit raw accumulated values (`mem_c_acc`) for precision verification and 8-bit quantized activations (`mem_c`) for subsequent CNN layers.
- **Parameterized Architecture (`ARRAY_SIZE`)**: Seamless scaling between $4 \times 4$ (16 PEs) and $8 \times 8$ (64 PEs) configurations.
- **AXI4-Lite Ready**: Memory-mapped register file ready for host CPU integration (RISC-V / Nios II).

---

## Pure Structural Block Diagram

```text
                      +-------------------+
                      |   u_controller    |
                      | (gemm_controller) |
                      +---------+---------+
                                |
             +------------------+------------------+
             | stream_en, k_step                   | sys_en, clear_acc
             v                                     v
     +---------------+                     +--------------------+
     |  u_buffer_a   |---(a_row_raw)------>|    u_skew_unit     |
     | (Weight RAM)  |                     | (systolic_skew_    |
     +---------------+                     |      unit)         |
                                           +---------+----------+
     +---------------+                               | (a_row_skewed, b_col_skewed)
     |  u_buffer_b   |---(b_col_raw)---------------->|
     | (Input RAM)   |                               v
     +---------------+                     +--------------------+
                                           |  u_systolic_core   | (2D PE Mesh)
                                           |  (systolic_array_  |
                                           |       core)        |
                                           +---------+----------+
                                                     | (c_matrix_core)
                                                     v
                                           +--------------------+
                                           |    u_quantizer     | (ReLU + Shift + Clamp)
                                           | (quantize_relu_    |
                                           |      unit)         |
                                           +---------+----------+
                                                     | (dout, valid)
                                                     v
                                           +--------------------+
                                           |    u_buffer_c      |====> rd_c_data (INT8)
                                           |  (Output RAM C)    |====> rd_c_acc_data (INT32)
                                           +--------------------+
```

---

## Directory Organization

```text
├── RTL/                         # SystemVerilog hardware source files
│   ├── pe_gemm.sv               # Processing Element (INT8 mult + INT32 acc)
│   ├── systolic_skew_unit.sv    # Wavefront delay skew registers (0T, 1T, ...)
│   ├── systolic_array_core.sv   # NxN nearest-neighbor 2D PE mesh
│   ├── matrix_buffer_a.sv       # Weight on-chip RAM buffer
│   ├── matrix_buffer_b.sv       # Activation on-chip RAM buffer
│   ├── matrix_buffer_c.sv       # Dual-channel output RAM buffer
│   ├── quantize_relu_unit.sv    # Post-processing: ReLU, Arithmetic Shift, Clamp
│   ├── gemm_controller.sv       # 7-state centralized control FSM
│   ├── systolic_accelerator_top.sv # Structural top-level module
│   ├── systolic_accelerator_8x8.sv # 8x8 parameter wrapper
│   ├── systolic_gemm_axi_lite.sv   # AMBA AXI4-Lite slave wrapper
│   ├── picorv32.v               # RISC-V RV32I Soft Core CPU (YosysHQ)
│   ├── axi_interconnect.sv      # 1-Master to 3-Slave AXI4-Lite Crossbar
│   ├── axi_ram.sv               # 32 KB On-Chip BRAM (wstrb & $readmemh)
│   ├── axi_uart.sv              # AXI4-Lite UART Serial Console
│   ├── soc_top.sv               # Complete Integrated SoC Top Module (DE1 default)
│   ├── soc_top_de2.sv           # DE2 Board Wrapper (8x HEX, 18x LEDR, 9x LEDG, RS-232)
│   └── soc_top_de10.sv          # DE10-Standard Board Wrapper (8x8 Array, 64 PEs)
├── firmware/                    # RISC-V Embedded Firmware & Assembler
│   ├── systolic.h               # Accelerator C MMIO driver & register definitions
│   ├── main.c                   # Interactive C firmware with 7 demo scenarios
│   ├── mnist_conv1_weights.h    # Extracted real Conv1 INT8 weights & biases
│   ├── start.s                  # Assembly startup (SP init & reset handler)
│   ├── link.ld                  # Linker script (32 KB BRAM mapping)
│   ├── Makefile                 # GNU RISC-V GCC build script
│   ├── firmware.hex             # Verilog hex machine code loaded by axi_ram
│   └── firmware.dis             # Instruction disassembly listing
├── VEFIFY/                      # ModelSim testbenches and simulation assets
│   ├── tb_systolic_gemm.sv      # Bit-true scoreboard testbench vs. Python
│   ├── tb_systolic_stress_test.sv # 6 corner-case & stress scenarios
│   ├── run_gemm_sim.do          # Accelerator core simulation script
│   ├── tb_soc_top.sv            # Full SoC hardware-software co-simulation TB
│   └── run_soc_sim.do           # SoC co-simulation script
├── software_ref/                # Python Golden Reference Model & AI Pipeline
│   ├── im2col.py                # Mathematical im2col & col2im matrix transformation
│   ├── tiling_engine.py         # Hardware-aware NxN Systolic Tiling Engine
│   ├── mnist_dataset.py         # Automatic MNIST loader & ASCII art renderer
│   ├── mnist_cnn_model.py       # Quantized INT8 ConvNet model (100% Bit-True)
│   ├── run_mnist_inference.py   # End-to-end digit recognition test script (97.06% Acc)
│   ├── test_single_image.py     # Fast single-image inference tool (by index or random)
│   ├── run_phase2_demo.bat      # One-click execution script for Phase 2 demo
│   ├── gemm_golden.py           # Bit-accurate matrix generation script
│   └── run_golden.bat           # One-click execution script
├── synthesis_gemm/              # Quartus II project for standalone 4x4 array (16 PEs)
│   └── compile_4x4.bat          # Automated command-line build script
├── synthesis_gemm_8x8/          # Quartus II project for standalone 8x8 array (64 PEs)
│   └── compile_8x8.bat          # Automated command-line build script
├── synthesis_soc/               # Quartus II project for Terasic DE1 (EP2C20F484C7)
│   ├── compile_soc.bat          # Automated build script
│   └── program_de1.bat          # USB-Blaster programming script
├── synthesis_soc_de2/           # Quartus II project for Terasic DE2 (EP2C35F672C6)
│   ├── compile_soc_de2.bat      # Automated build script
│   ├── program_de2.bat          # USB-Blaster programming script
│   └── README_DE2.md            # DE2 pinout, bring-up, and architecture guide
├── synthesis_soc_de10/          # Quartus Prime project for Terasic DE10-Standard (Cyclone V)
│   ├── compile_soc_de10.bat     # Automated build script
│   ├── program_de10.bat         # USB-Blaster programming script
│   └── README_DE10.md           # DE10 pinout, bring-up, and architecture guide
└── PROJECT_SPECIFICATION.md     # Comprehensive system specification & engineering report
```

---

## Hardware Benchmark & Multi-Board Synthesis Portfolio

The design is verified across three physical FPGA development platforms:

| Metric | Terasic DE1 (`soc_top`) | Terasic DE2 (`soc_top_de2`) | Terasic DE10-Standard (`soc_top_de10`) |
| :--- | :---: | :---: | :---: |
| **FPGA Family / Device** | **Cyclone II EP2C20F484C7** | **Cyclone II EP2C35F672C6** | **Cyclone V 5CSXFC6D6F31C6N** |
| **Array Architecture** | $4 \times 4$ (16 PEs) | **$8 \times 8$ (64 PEs)** | $8 \times 8$ (64 PEs) |
| **Logic Utilization** | 6,219 / 18,752 LEs (33.1%) | **16,356 / 33,216 LEs (49.2%)** | 13,293 / 41,910 ALMs (31.7%) |
| **Registers** | 3,337 | **8,961** | 12,852 |
| **Embedded Multipliers / DSP** | 16 / 52 9-bit (30.8%) | **64 / 70 9-bit (91.4%)** | 64 / 112 Variable DSPs (57.1%) |
| **Memory Bits (Block RAM)** | 133,632 / 239,616 (55.8%) | **265,216 / 483,840 (54.8%)** | 357,696 / 5,662,720 (6.3%) |
| **Total I/O Pins Utilized** | 27 / 315 (8.6%) | **87 / 475 (18.3%)** | 55 / 499 (11.0%) |
| **Target Clock Frequency** | 50.00 MHz | 50.00 MHz | 50.00 MHz |
| **Worst-Case Setup Slack** | **+3.968 ns** | **+3.395 ns** | **+3.882 ns** |
| **Worst-Case Hold Slack** | **+0.445 ns** | **+0.391 ns** | **+0.160 ns** |
| **Max Clock Freq ($F_{max}$)** | **62.37 MHz** | **60.22 MHz** | **61.93 MHz** |
| **Peak Throughput (@ 50MHz)** | **1.60 GOPS** | **6.40 GOPS ($4.0\times$)** | **6.40 GOPS ($4.0\times$)** |
| **Compilation Status** | **0 Errors, 0 Violations** | **0 Errors, 0 Violations** | **0 Errors, 0 Violations** |
| **Bitstream File** | `synthesis_soc/soc_top.sof` | `synthesis_soc_de2/soc_top_de2.sof` | `synthesis_soc_de10/output_files/soc_top_de10.sof` |

### Key Academic Takeaways:
1. **$F_{max}$ Frequency Preservation**: By eliminating global broadcast routes and inserting pipelined registers between adjacent PEs, increasing the compute density by $4\times$ ($16 \to 64$ PEs) causes only a negligible $3.4\%$ frequency drop.
2. **DSP Saturation**: Cyclone II `EP2C20` features 52 9-bit DSP blocks. The $4 \times 4$ array consumes only $30.8\%$ DSPs, leaving ample resources for a full System-on-Chip (SoC) with a soft RISC-V CPU. The $8 \times 8$ array fully saturates the DSP blocks, achieving maximum computation throughput ($8.65 \text{ GOPS}$).

---

## Verification & Test Results

### 1. Python Golden Model Comparison
- Scoreboard verifies both **INT32 Accumulator** and **INT8 Post-ReLU Quantized** values against Python NumPy:
```text
[TB] Test PASSED: 16/16 elements matched (0 errors).
```

### 2. Comprehensive Stress & Corner-Case Suite
- **Scenario 1**: Extreme Min ($-128 \times -128 = +16384$) $\implies$ **PASSED**
- **Scenario 2**: Saturation Clamping (Clamped to $+127$) $\implies$ **PASSED**
- **Scenario 3**: Bypass ReLU (Negative values preserved) $\implies$ **PASSED**
- **Scenario 4**: Zero Matrix (Quiescent stability) $\implies$ **PASSED**
- **Scenario 5**: Back-to-Back Run #1 (Accumulator auto-clear) $\implies$ **PASSED**
- **Scenario 6**: Back-to-Back Run #2 (Pipeline residual flush) $\implies$ **PASSED**

### 3. Full RISC-V SoC Hardware-Software Co-Simulation (`tb_soc_top`)
- **Total Simulation Cycles**: **82,176 cycles** (50 MHz, CPI = 5.97)
- **CPU Retired Instructions**: **13,751 instructions** (0 TRAP errors, 0 timeouts)
- **Systolic Execution Latency**: **Exactly 33 cycles** (Cycle 54,983 $\to$ 55,016)
- **UART Output Characters**: **607 characters** (Zero buffer overrun, 100% verified)
- **Matrix C Verification**: 16/16 elements **100% Bit-True Match** with Python Golden Model.

---

## Quickstart Guide

### 1. Generate Golden Reference Vectors
Double click `software_ref/run_golden.bat` or run:
```powershell
python software_ref/gemm_golden.py
```

### 2. Run ModelSim Simulation
```powershell
cd VEFIFY
vlog -sv -work work ../RTL/*.sv tb_systolic_gemm.sv tb_systolic_stress_test.sv
vsim -c -do "run -all; quit -f" tb_systolic_gemm
vsim -c -do "run -all; quit -f" tb_systolic_stress_test
```

### 3. Run Quartus Synthesis
- For $4 \times 4$: Run `synthesis_gemm/compile_4x4.bat`
- For $8 \times 8$: Run `synthesis_gemm_8x8/compile_8x8.bat`

### 4. Run Phase 2: MNIST Handwritten Digit Inference
- **1-Click Full Demo**: Double-click `software_ref/run_phase2_demo.bat`
- **Test a Specific Image**: `python software_ref/test_single_image.py 42`
- **Test a Random Image**: `python software_ref/test_single_image.py random`

### 5. Run Phase 3: RISC-V SoC Hardware-Software Co-Simulation & Synthesis
- **Build Firmware (GNU RISC-V C Toolchain & Makefile)**:
  ```powershell
  cd firmware
  make clean
  make
  ```
  *(Compiles `start.s` and `main.c` with `riscv-none-elf-gcc`, links via `link.ld`, and generates `firmware.hex` & `firmware.dis`)*
- **Run Full SoC Co-Simulation on ModelSim**:
  ```powershell
  cd VEFIFY
  vsim -c -do run_soc_sim.do
  ```
  Executes full hardware-software co-simulation running **7 interactive demonstration scenarios** (HW vs SW GEMM benchmark, 16x16 matrix tiling engine with 26.2x speedup, Conv2D im2col feature map extraction, 2-layer MLP neural inference, 5-test arithmetic edge-case diagnostics, MNIST digit ASCII telemetry, and MMIO diagnostics). Transmits **4,610 UART characters** across **1,633,743 simulation cycles** with 0 CPU traps and 100% Bit-True match.
- **Run Full SoC Quartus II Synthesis (Cyclone II EP2C20)**:
  ```powershell
  cd synthesis_soc
  .\compile_soc.bat
  ```

### 6. Run Phase 4: Terasic DE1 FPGA Board Deployment & Live Host PC GUI Demo
- **Step 1: Connect Hardware**:
  - Connect DC Power (9V/12V) and Altera USB-Blaster cable to the Terasic DE1 board.
  - Connect RS-232 / USB-to-UART cable (Pins `F14` RXD, `G12` TXD, GND) to Host PC.
  - Set `RUN/PROG` switch to `RUN`, turn on board Power.
- **Step 2: Program Bitstream to FPGA (1-Click)**:
  ```powershell
  cd synthesis_soc
  .\program_de1.bat
  ```
- **Step 3: Test Real-Time MNIST Inference via UART Bridge**:
  - **Interactive Drawing GUI**: Draw digits with your mouse and see real-time classification on the DE1 7-segment display `HEX0`:
    ```powershell
    python software_ref/uart_bridge.py --port COM3 --mode gui
    ```
  - **Single Test Sample**:
    ```powershell
    python software_ref/uart_bridge.py --port COM3 --mode test_single --index 42
    ```
  - **Batch Evaluation**:
    ```powershell
    python software_ref/uart_bridge.py --port COM3 --mode batch --count 20
    ```
  - **Offline Mock Mode (No Hardware Needed)**:
    ```powershell
    python software_ref/uart_bridge.py --mock --mode gui
    ```

---

## Terasic DE1 Hardware Pinout Map

| Pin | Cyclone II Pin | Hardware Function | Behavior |
| :--- | :---: | :--- | :--- |
| **`clk`** | `PIN_L1` | 50.0 MHz Master Clock (`CLOCK_50`) | Oscillator Input |
| **`rst_n`** | `PIN_R22` | Active-low Master Reset (`KEY[0]`) | Push-button Reset |
| **`uart_rx`** | `PIN_F14` | RS-232 RXD (115200 Baud, 8N1) | Input from Host PC |
| **`uart_tx`** | `PIN_G12` | RS-232 TXD (115200 Baud, 8N1) | Output to Host PC |
| **`hex0[6:0]`** | `PIN_E2`..`PIN_J2` | 7-Segment Display (`HEX0`) | Active-low Predicted Digit Output |
| **`hex1[6:0]`** | `PIN_D1`..`PIN_E1` | 7-Segment Display (`HEX1`) | Active-low Tens Digit Output |
| **`ledr[0]`** | `PIN_R20` | Red LED 0 (`LEDR[0]`) | CPU Trap Flag (OFF = Normal, ON = Trap) |
| **`ledr[1]`** | `PIN_R19` | Red LED 1 (`LEDR[1]`) | Accelerator Busy Flag (`core_busy`) |
| **`ledg[0]`** | `PIN_U22` | Green LED 0 (`LEDG[0]`) | Accelerator Done Flag (`core_done`) |
| **`ledg[1]`** | `PIN_U21` | Green LED 1 (`LEDG[1]`) | UART RX Valid Flag (`rx_valid`) |

---

## License & Author
- **Author**: Nguyen Hoang Sang ([Sang-HCMUT](https://github.com/Sang-HCMUT))
- **Project**: Graduation Capstone Project - Ho Chi Minh City University of Technology (HCMUT - VNU-HCM)
- **License**: MIT License

