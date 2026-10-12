# Parameterized 2D Systolic Array CNN Accelerator on FPGA

[![FPGA](https://img.shields.io/badge/FPGA-Altera%20Cyclone%20II%20EP2C20-blue.svg)](https://www.intel.com/)
[![HDL](https://img.shields.io/badge/HDL-SystemVerilog%20(IEEE%201800--2012)-orange.svg)](https://en.wikipedia.org/wiki/SystemVerilog)
[![Tool](https://img.shields.io/badge/EDA-Quartus%20II%20%26%20ModelSim-green.svg)](https://www.intel.com/)
[![Verification](https://img.shields.io/badge/Verification-100%25%20Bit--True%20(16%2F16%20%26%206%2F6%20Stress%20Passed)-brightgreen.svg)](#verification--test-results)

An open-source, modular, and parameterized hardware accelerator designed for Convolutional Neural Networks (CNNs) based on an **Output-Stationary 2D Systolic Array**. Optimized for low-cost FPGA platforms (such as the Altera Cyclone II on Terasic DE1), featuring quantized **Signed INT8** inputs/weights, **Signed INT32** accumulation, on-the-fly **ReLU / Arithmetic Scaling / Saturation Clamping**, and an **AMBA AXI4-Lite** interface.

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
│   └── soc_top.sv               # Complete Integrated SoC Top Module
├── firmware/                    # RISC-V Embedded Firmware & Assembler
│   ├── systolic.h               # Accelerator C MMIO driver & register definitions
│   ├── main.c                   # C firmware application
│   ├── start.s                  # Assembly startup (SP init & reset handler)
│   ├── link.ld                  # Linker script (32 KB BRAM mapping)
│   ├── Makefile                 # GNU RISC-V GCC build script
│   ├── firmware_generator.py    # Standalone pure Python RV32I assembler
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
├── synthesis_gemm/              # Quartus II project for 4x4 configuration (16 PEs)
│   └── compile_4x4.bat          # Automated command-line build script
├── synthesis_gemm_8x8/          # Quartus II project for 8x8 configuration (64 PEs)
│   └── compile_8x8.bat          # Automated command-line build script
├── synthesis_soc/               # Quartus II project for complete RISC-V SoC system
│   └── compile_soc.bat          # Automated command-line build script for SoC
└── PROJECT_SPECIFICATION.md     # Comprehensive system specification & engineering report
```

---

## Hardware Benchmark (Altera Cyclone II EP2C20F484C7)

Compiled with **Quartus II 64-Bit 13.0 SP1** and analyzed via **TimeQuest Timing Analyzer**:

| Metric | $4 \times 4$ Standalone Array | $8 \times 8$ Standalone Array | Full RISC-V SoC (`soc_top`) |
| :--- | :---: | :---: | :---: |
| **Logic Elements (LEs)** | **4,323 / 18,752 (23.1%)** | **15,567 / 18,752 (83.0%)** | **6,219 / 18,752 (33.1%)** |
| - *Combinational Functions* | 3,412 (18.2%) | 13,211 (70.5%) | 5,539 (29.5%) |
| - *Dedicated Logic Registers* | 2,473 (13.2%) | 8,012 (42.7%) | 3,337 (17.8%) |
| **Embedded Multipliers (9-bit)** | **16 / 52 (30.8%)** | **52 / 52 (100.0% - Saturated)** | **16 / 52 (30.8%)** |
| **Memory Bits (Block RAM)** | **512 / 239,616 (< 1%)** | **1,024 / 239,616 (< 1%)** | **133,632 / 239,616 (55.8%)** |
| **Total I/O Pins** | 93 / 315 (29.5%) | 97 / 315 (30.8%) | **4 / 315 (1.3%)** |
| **Max Frequency $F_{max}$ (Slow 85°C)** | **70.00 MHz** ($T_{clk} = 14.29 \text{ ns}$) | **67.60 MHz** ($T_{clk} = 14.79 \text{ ns}$) | **60.00 MHz** ($T_{clk} = 16.67 \text{ ns}$) |
| **Max Frequency $F_{max}$ (Fast 0°C)** | **186.04 MHz** ($T_{clk} = 5.37 \text{ ns}$) | **184.74 MHz** ($T_{clk} = 5.41 \text{ ns}$) | **162.33 MHz** ($T_{clk} = 6.16 \text{ ns}$) |
| **Worst-Case Slack @ 50 MHz** | **+5.714 ns** | **+5.207 ns** | **+3.331 ns (Zero Violation)** |
| **Compilation Status** | **0 Errors (Passed)** | **0 Errors (Passed)** | **0 Errors (Passed)** |

### Key Academic Takeaways:
1. **$F_{max}$ Frequency Preservation**: By eliminating global broadcast routes and inserting pipelined registers between adjacent PEs, increasing the compute density by $4\times$ ($16 \to 64$ PEs) causes only a negligible $3.4\%$ frequency drop.
2. **DSP Saturation**: Cyclone II `EP2C20` features 52 9-bit DSP blocks. The $4 \times 4$ array consumes only $30.8\%$ DSPs, leaving ample resources for a full System-on-Chip (SoC) with a soft RISC-V CPU. The $8 \times 8$ array fully saturates the DSP blocks, achieving maximum computation throughput ($8.65 \text{ GOPS}$).

---

## Verification & Test Results

### 1. Python Golden Model Comparison
- Scoreboard verifies both **INT32 Accumulator** and **INT8 Post-ReLU Quantized** values against Python NumPy:
```text
VERIFICATION RESULT: ALL 16 ELEMENTS PASSED (0 ERRORS)!
100% BIT-FOR-BIT MATCH WITH PYTHON GOLDEN MODEL!
```

### 2. Comprehensive Stress & Corner-Case Suite
- **Scenario 1**: Extreme Min ($-128 \times -128 = +16384$) $\implies$ **PASSED**
- **Scenario 2**: Saturation Clamping (Clamped to $+127$) $\implies$ **PASSED**
- **Scenario 3**: Bypass ReLU (Negative values preserved) $\implies$ **PASSED**
- **Scenario 4**: Zero Matrix (Quiescent stability) $\implies$ **PASSED**
- **Scenario 5**: Back-to-Back Run #1 (Accumulator auto-clear) $\implies$ **PASSED**
- **Scenario 6**: Back-to-Back Run #2 (Pipeline residual flush) $\implies$ **PASSED**

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

### 5. Run Phase 3: RISC-V SoC Hardware-Software Co-Simulation
- **Compile Firmware (Pure Python RV32I Assembler)**:
  ```powershell
  python firmware/firmware_generator.py
  ```
- **Run Full SoC Co-Simulation on ModelSim**:
  ```powershell
  cd VEFIFY
  vsim -c -do run_soc_sim.do
  ```
  Observes CPU booting from BRAM (`0x0000_0000`), configuring the Systolic GEMM Accelerator via AXI4-Lite (`0x1000_0000`), executing GEMM tile calculations in 33 hardware cycles, and streaming verified results out via UART (`0x2000_0000`).

---

## License & Author
- **Author**: Nguyen Hoang Sang ([Sang-HCMUT](https://github.com/Sang-HCMUT))
- **Project**: Graduation Capstone Project - Ho Chi Minh City University of Technology (HCMUT - VNU-HCM)
- **License**: MIT License
