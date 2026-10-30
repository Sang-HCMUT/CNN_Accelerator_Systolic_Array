# Parameterized 2D Systolic Array CNN Accelerator SoC on Multi-FPGA

[![FPGA](https://img.shields.io/badge/FPGA-Cyclone%20II%20(DE1%2FDE2)%20%7C%20Cyclone%20V%20(DE10)-007acc.svg?style=flat-square&logo=intel)](https://www.intel.com/)
[![HDL](https://img.shields.io/badge/HDL-SystemVerilog%20(IEEE%201800--2012)-orange.svg?style=flat-square)](https://en.wikipedia.org/wiki/SystemVerilog)
[![Interconnect](https://img.shields.io/badge/Bus-AMBA%20AXI4--Lite-red.svg?style=flat-square)](https://www.arm.com/architecture/system-architectures/amba)
[![CPU Core](https://img.shields.io/badge/CPU-RISC--V%20(PicoRV32%20RV32I)-brightgreen.svg?style=flat-square)](https://github.com/YosysHQ/picorv32)
[![UVM](https://img.shields.io/badge/Verification-UVM%201.1c%20(100%25%20Cross--Coverage)-blueviolet.svg?style=flat-square)](#4-uvm-functional-cross-coverage-closure-10000)
[![Timing](https://img.shields.io/badge/Timing-Timing%20Closure%20Met%20(TNS%20%3D%200.000)-success.svg?style=flat-square)](#multi-platform-fpga-synthesis-portfolio)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)

An industrial-grade, modular, and fully parameterized hardware accelerator System-on-Chip (SoC) tailored for Convolutional Neural Network (CNN) edge inference. Designed with an **Output-Stationary 2D Systolic Array**, an **AMBA AXI4-Lite** central interconnect, and an embedded **PicoRV32 RISC-V (RV32I)** soft-core CPU. 

Validated, timing-closed, and deployable across three Altera/Intel FPGA development platforms:
1. **Terasic DE1** (`EP2C20F484C7`, $4 \times 4$ array, 16 PEs)
2. **Terasic DE2** (`EP2C35F672C6`, $8 \times 8$ array with 64 PEs, 8x 7-segments & 18 LEDs)
3. **Terasic DE10-Standard** (`5CSXFC6D6F31C6N`, $8 \times 8$ array with 64 PEs)

---

## Table of Contents

- [Architectural Highlights](#architectural-highlights)
- [System Architecture & Block Diagram](#system-architecture--block-diagram)
- [SoC Memory Map & Register Specifications](#soc-memory-map--register-specifications)
- [Multi-Platform FPGA Synthesis Portfolio](#multi-platform-fpga-synthesis-portfolio)
- [Embedded Firmware & 7 Demo Scenarios](#embedded-firmware--7-demo-scenarios)
- [Verification Framework & UVM Coverage Closure](#verification-framework--uvm-coverage-closure)
- [Directory Structure](#directory-structure)
- [Quickstart Guide](#quickstart-guide)
- [FPGA Hardware Pinout Maps](#fpga-hardware-pinout-maps)
- [Academic Context & Author](#academic-context--author)

---

## Architectural Highlights

- **Generalized Matrix Multiplication (GEMM) via `im2col`**:
  Translates multi-dimensional 2D convolutions into hardware-friendly matrix multiplication ($C = A \times B$), flattening complex nested loops into streaming dot-products.
- **Output-Stationary 2D Systolic Array**:
  Accumulates partial products locally inside each Processing Element (PE), eliminating global accumulator wire routing and slashing internal memory bandwidth pressure.
- **Wavefront Skew Synchronization Network**:
  Hardware skew unit delays row activations ($i \cdot T$) and column weights ($j \cdot T$) with zero CPU overhead to sustain rhythmic, continuous dataflow.
- **Pipelined Post-Processing Unit**:
  Integrated on-the-fly **Quantized ReLU activation**, multi-scale arithmetic right-shifting ($2^{-0} \dots 2^{-8}$), and symmetric two's-complement saturation clamping ($-128 \dots +127$).
- **Dual-Channel Output Buffering**:
  Simultaneously stores both 32-bit raw unquantized accumulators (`mem_c_acc`) for precision verification/residual analysis and 8-bit quantized activations (`mem_c`) for subsequent neural network layers.
- **Hardware Performance Profiling & Version ID Registers**:
  Dedicated hardware cycle counter (`REG_ACCEL_CYCLES`) measuring pure systolic array execution and IP version register (`REG_ACCEL_VERSION`) encoding array dimensions, precision, and version ID.
- **Pure Native GNU Toolchain**:
  Bare-metal RISC-V C firmware built directly with `riscv-none-elf-gcc`, `link.ld`, and `objcopy -O verilog` without reliance on Python wrapper generators.
- **Zero-Warning RTL & 100% UVM Cross-Coverage**:
  Strict industrial coding standards adhering to zero synthesis/linting warnings and 100% functional cross-coverage closure under IEEE 1800 SystemVerilog UVM 1.1c.

---

## System Architecture & Block Diagram

```text
 +----------------------------------------------------------------------------------------------------+
 |                                        RISC-V SoC TOP LEVEL                                        |
 |                                                                                                    |
 |  +-----------------------+                    AMBA AXI4-LITE INTERCONNECT                          |
 |  |    PicoRV32 CPU       |                              (1M to 3S)                                 |
 |  |     (RV32I Core)      |=====[AXI Master]=================+==================+                   |
 |  +-----------------------+                                  |                  |                   |
 |              | Interrupts / Traps                            |                  |                   |
 |              v                                               v                  v                   |
 |       [STATUS / LEDS]                             +------------------+  +------------------+       |
 |                                                   |    On-Chip BRAM  |  |    UART Core     |       |
 |                                                   |  (32 KB Boot/FW) |  | (115200 Baud)    |       |
 |                                                   +------------------+  +------------------+       |
 |                                                                                 |                  |
 |                                                                                 v                  |
 |                                                                           [HOST PC GUI]            |
 |                                                                                                    |
 |===================================[AXI-Lite Slave Interface]=======================================|
 |                                                                                                    |
 |                       +-----------------------------------------------+                            |
 |                       |           systolic_gemm_axi_lite              |                            |
 |                       |   (Control, Status, Profiler, Tile Buffers)   |                            |
 |                       +-----------------------+-----------------------+                            |
 |                                               |                                                    |
 |                                               v                                                    |
 |                       +-----------------------------------------------+                            |
 |                       |           systolic_accelerator_top            |                            |
 |                       |                                               |                            |
 |                       |  +-----------------+     +-----------------+  |                            |
 |                       |  | Matrix Buffer A |     | Matrix Buffer B |  |                            |
 |                       |  |  (Weights INT8) |     | (Inputs INT8)   |  |                            |
 |                       |  +--------+--------+     +--------+--------+  |                            |
 |                       |           |                       |           |                            |
 |                       |           v                       v           |                            |
 |                       |  +-----------------------------------------+  |                            |
 |                       |  |           systolic_skew_unit            |  |                            |
 |                       |  |    (Wavefront Pipelined Delay Rows/Cols)|  |                            |
 |                       |  +--------------------+--------------------+  |                            |
 |                       |                       |                       |                            |
 |                       |                       v                       |                            |
 |                       |  +-----------------------------------------+  |                            |
 |                       |  |           systolic_array_core           |  |                            |
 |                       |  |       (NxN Processing Element Mesh)     |  |                            |
 |                       |  +--------------------+--------------------+  |                            |
 |                       |                       | (INT32 Accumulators)  |                            |
 |                       |                       v                       |                            |
 |                       |  +-----------------------------------------+  |                            |
 |                       |  |           quantize_relu_unit            |  |                            |
 |                       |  |       (ReLU + Multi-Scale Shift + Clamp)|  |                            |
 |                       |  +--------------------+--------------------+  |                            |
 |                       |                       |                       |                            |
 |                       |                       v                       |                            |
 |                       |  +-----------------------------------------+  |                            |
 |                       |  |            Matrix Buffer C              |  |                            |
 |                       |  |   (Dual: INT8 Quantized & INT32 Acc)    |  |                            |
 |                       |  +-----------------------------------------+  |                            |
 |                       +-----------------------------------------------+                            |
 +----------------------------------------------------------------------------------------------------+
```

---

## SoC Memory Map & Register Specifications

The SoC uses a unified 32-bit flat memory-mapped architecture:

| Base Address Range | Peripheral / Device | Description |
| :--- | :--- | :--- |
| `0x0000_0000 - 0x0000_7FFF` | **AXI On-Chip BRAM (32 KB)** | Firmware Instructions & Static Data (`firmware.hex`) |
| `0x1000_0000 - 0x1000_00FF` | **Systolic Accelerator Control** | Control, Status, Dimensions, Hardware Profiling |
| `0x1000_0100 - 0x1000_01FF` | **Matrix A Buffer (Weights)** | Memory-Mapped Input Weights (Word-aligned, INT8) |
| `0x1000_0200 - 0x1000_02FF` | **Matrix B Buffer (Activations)** | Memory-Mapped Input Activations (Word-aligned, INT8) |
| `0x1000_0300 - 0x1000_03FF` | **Matrix C Buffer (Quantized Out)** | Post-ReLU Quantized Activations (Word-aligned, INT8) |
| `0x1000_0400 - 0x1000_04FF` | **Matrix C Accumulator (Raw Out)** | Raw 32-bit Accumulator Output (Word-aligned, INT32) |
| `0x2000_0000 - 0x2000_000F` | **UART & Board I/O** | TX/RX FIFOs, Status, 7-Segment displays, LEDs |

### Accelerator MMIO Register Map (`ACCEL_BASE = 0x1000_0000`)

| Offset | Register Name | Access | Bitfields & Descriptions |
| :--- | :--- | :---: | :--- |
| `0x000` | `REG_ACCEL_CTRL` | R/W | `[0]`: `START` (Pulse 1 to launch computation)<br/>`[1]`: `BYPASS_RELU` (1 = Linear bypass, 0 = Active ReLU)<br/>`[6:2]`: `SHIFT_BITS` (Arithmetic right-shift: $0 \dots 8$) |
| `0x004` | `REG_ACCEL_STATUS` | RO | `[0]`: `DONE` (1 = Computation finished & buffers ready)<br/>`[1]`: `BUSY` (1 = Core computation in progress) |
| `0x008` | `REG_ACCEL_KDIM` | R/W | `[7:0]`: Inner dot-product dimension $K$ ($1 \le K \le 16$) |
| `0x00C` | `REG_ACCEL_CYCLES` | RO | `[31:0]`: **Hardware Execution Cycle Counter** (counts exact clock cycles from `core_start` to `core_done`) |
| `0x010` | `REG_ACCEL_VERSION` | RO | `[31:24]`: Major/Minor Version (`0x01`)<br/>`[23:16]`: Array Size $N$ (`0x04` for $4\times4$, `0x08` for $8\times8$)<br/>`[15:8]`: Input Data Width (`0x08` = INT8)<br/>`[7:0]`: Accumulator Width (`0x20` = INT32) |

---

## Multi-Platform FPGA Synthesis Portfolio

The design is synthesized, fully placed-and-routed, and timing-closed across three physical FPGA development platforms:

| Metric | Terasic DE1 (`soc_top`) | Terasic DE2 (`soc_top_de2`) | Terasic DE10-Standard (`soc_top_de10`) |
| :--- | :---: | :---: | :---: |
| **FPGA Family / Device** | **Cyclone II EP2C20F484C7** | **Cyclone II EP2C35F672C6** | **Cyclone V 5CSXFC6D6F31C6N** |
| **Technology Node** | 90 nm TSMC | 90 nm TSMC | 28 nm TSMC Low-Power |
| **Array Architecture** | $4 \times 4$ (16 PEs) | **$8 \times 8$ (64 PEs)** | $8 \times 8$ (64 PEs) |
| **Logic Utilization** | 6,368 / 18,752 LEs (34.0%) | **16,356 / 33,216 LEs (49.2%)** | 13,293 / 41,910 ALMs (31.7%) |
| **Dedicated Logic Registers** | 3,365 registers | **8,987 registers** | 12,852 registers |
| **DSP / Embedded Multipliers** | 16 / 52 9-bit (30.8%) | **64 / 70 9-bit (91.4%)** | 64 / 112 Variable DSPs (57.1%) |
| **Total Memory Bits (BRAM)** | 134,144 / 239,616 (56.0%) | **265,216 / 483,840 (54.8%)** | 357,696 / 5,662,720 (6.3%) |
| **Target Clock Frequency** | 50.00 MHz (20.0 ns) | 50.00 MHz (20.0 ns) | 50.00 MHz (20.0 ns) |
| **Setup Slack (Slow Model)** | **+4.144 ns** | **+4.858 ns** | **+3.882 ns** |
| **Hold Slack (Slow Model)** | **+0.445 ns** | **+0.391 ns** | **+0.160 ns** |
| **Max Frequency ($F_{max}$)** | **63.07 MHz** | **66.04 MHz** | **61.93 MHz** |
| **Timing Violations (TNS)** | **0.000 ns (Closure Met)** | **0.000 ns (Closure Met)** | **0.000 ns (Closure Met)** |
| **Peak Throughput (@ 50MHz)** | **1.60 GOPS** | **6.40 GOPS ($4.0\times$)** | **6.40 GOPS ($4.0\times$)** |
| **Programming Bitstream** | `synthesis_soc/soc_top.sof` | `synthesis_soc_de2/soc_top_de2.sof` | `synthesis_soc_de10/output_files/soc_top_de10.sof` |

---

## Embedded Firmware & 7 Demo Scenarios

The firmware operates as an interactive real-time operating console over UART (115200 Baud, 8N1). It includes 7 fully functional diagnostic and inference suites:

```text
====================================================================
RISC-V SoC & Systolic Array Accelerator Demonstration Suite
Graduation Thesis Project - Dual Platform DE1 / DE2 / DE10
====================================================================

Available Scenarios:
  [1] Hardware vs Software GEMM Benchmark & Speedup Analysis
  [2] 16x16 Large Matrix GEMM Tiling Engine (Multi-Tile K=16)
  [3] Real MNIST Conv1 Layer via Systolic GEMM (im2col + Tiling)
  [4] 2-Layer Neural Network (MLP) Forward Inference (FC1 -> FC2)
  [5] Arithmetic Edge-Case & Quantization Diagnostics Suite
  [6] MNIST Digit Inference Telemetry (Built-in Sample)
  [7] Hardware Peripherals & MMIO Register Diagnostics
  [0-9] Direct Set HEX0 display
  [I] Receive Live MNIST Image Tensor (Host PC)
  [M] / [?] Show Menu
```

### Scenario Breakdown

1. **Demo 1: Hardware vs Software GEMM Benchmark**:
   - Calculates $C = \text{ReLU}((A \times B) \gg 7)$ on $4 \times 4$ matrices ($K=4$).
   - Demonstrates a **15.2x acceleration speedup** of Systolic Hardware Core over the software CPU computation.
2. **Demo 2: 16x16 Large Matrix Tiling Engine**:
   - Hardware-aware 2D tiling partitioning a $16 \times 16$ GEMM into 16 sub-matrix tiles ($K=16$).
   - Demonstrates a **16.1x speedup** (Hardware: 180,893 cycles vs. Software CPU: 2,924,592 cycles).
3. **Demo 3: Real MNIST Conv1 Layer via im2col**:
   - Convolves real MNIST $28 \times 28$ image data with 16 trained $3 \times 3$ filters across 16 spatial patches.
   - Verifies **256 activations** against PyTorch golden references with **0 bit mismatches** (Acc Checksum = 26,450, Out Checksum = 3,865).
4. **Demo 4: 2-Layer MLP Forward Inference**:
   - Architecture: Input [16] $\to$ FC1 ($16 \times 16$) + ReLU $\to$ FC2 ($16 \times 4$) $\to$ Class Logits [4].
   - Correctly identifies Class 0 as winner with total inference latency of 125,833 cycles (~2.51 ms @ 50MHz).
5. **Demo 5: Arithmetic Diagnostics & Corner-Case Suite**:
   - 5/5 robustness tests passed:
     * `[5A]` Positive Saturation Clamping (+127)
     * `[5B]` $(-128) \times (-128) = +16384$ Arithmetic Precision
     * `[5C]` ReLU Negative Clamping to Zero ($-10000 \to 0$)
     * `[5D]` ReLU Bypass Mode Signed Retention ($-40 \to -40$)
     * `[5E]` Multi-Scale Shift Sweep (shifts 4, 6, 8)
6. **Demo 6: MNIST Digit Telemetry (Digit '7')**:
   - ASCII visualizer of receptive field, streaming 12 systolic tiles ($K=16$).
   - Output: Class 7 logit = **9,793 (Winner)** with 69% confidence score, display on `HEX0 = '7'`.
7. **Demo 7: Hardware Peripherals & MMIO Profiler Diagnostics**:
   - Inspects `REG_ACCEL_STATUS`, `REG_ACCEL_CYCLES`, and `REG_ACCEL_VERSION`.
   - Triggers automated visual animations across 7-Segment Displays (`HEX0-HEX7`) and LEDs.

---

## Verification Framework & UVM Coverage Closure

### 1. Functional Verification Architecture
The verification environment is designed around industry standards with SystemVerilog UVM 1.1c:

```text
               +-------------------------------------------------------+
               |                    gemm_env                           |
               |                                                       |
               |  +--------------------+        +--------------------+ |
               |  |     gemm_agent     |        |   gemm_coverage    | |
               |  |                    |        |  (88 Target Bins)  | |
               |  |  +--------------+  |        +---------^----------+ |
               |  |  | gemm_seqr    |  |                  |            |
               |  |  +-------+------+  |                  | (mon_exp)  |
               |  |          |         |                  |            |
               |  |  +-------v------+  |        +---------+----------+ |
               |  |  | gemm_driver  |  |        |  gemm_scoreboard   | |
               |  |  +-------+------+  |=======>| (Bit-True Predict) | |
               |  |          |         | (drv)  +---------^----------+ |
               |  |  +-------v------+  |                  |            |
               |  |  | gemm_monitor |  |------------------+            |
               |  |  +-------+------+  |                               |
               |  +----------|---------+                               |
               +-------------|-----------------------------------------+
                             | (gemm_if Interface with Clocking Blocks)
                             v
               +-------------------------------------------------------+
               |              DUT: systolic_accelerator_top            |
               +-------------------------------------------------------+
```

### 2. UVM Functional Cross-Coverage Closure: 100.00%

The testbench measures stimulus quality through **39 Point Coverage Bins** and **49 Industrial Cross-Coverage Bins**:

```text
==================================================================
                 FUNCTIONAL COVERAGE CLOSURE REPORT               
==================================================================
Matrix A [5 bins]    : pos=894 neg=854 zero=576 min(-128)=72 max(+127)=69
Matrix B [3 bins]    : pos=925 neg=843 zero=556
Activation [2 bins]  : relu_on=36 relu_bypass=35
Shift [0..8] [9 bins]: s0:8, s1:7, s2:8, s3:7, s4:13, s5:7, s6:7, s7:7, s8:7
Clamping [4 bins]    : sat_pos(+127)=404, sat_neg(-128)=192, relu_zero=249, linear_pass=291
K-Dim [1..16] [16 b] : min(K=1)=17 max(K=16)=17 mid(2..15)=37
------------------------------------------------------------------
                 CROSS-COVERAGE CLOSURE MATRIX                    
------------------------------------------------------------------
Cross 1: [ReLU x Shift]      : 18 / 18 Bins Covered
  ReLU_ON     x Shift[0..8]  : [7, 2, 5, 2, 7, 2, 5, 2, 4]
  ReLU_BYPASS x Shift[0..8]  : [1, 5, 3, 5, 6, 5, 2, 5, 3]
Cross 2: [K-Range x Shift]   : 27 / 27 Bins Covered
  K_MIN (K=1)  x Shift[0..8] : [3, 2, 2, 3, 1, 1, 3, 1, 1]
  K_MID (2..15)x Shift[0..8] : [4, 4, 3, 3, 11, 3, 3, 4, 2]
  K_MAX (K=16) x Shift[0..8] : [1, 1, 3, 1, 1, 3, 1, 2, 4]
Cross 3: [Extremes A x B Sign]: 4 / 4 Bins Covered
  A(-128) x B(Neg): 8 | A(-128) x B(Pos): 8 | A(+127) x B(Neg): 8 | A(+127) x B(Pos): 8
------------------------------------------------------------------
POINT COVERAGE SCORE : 39 / 39 Target Bins Covered ( 100.00% )
CROSS COVERAGE SCORE : 49 / 49 Target Bins Covered ( 100.00% )
COMBINED SCORE       : 88 / 88 Total Bins Covered  ( 100.00% )
COVERAGE VERDICT     : [100.00% FULL INDUSTRIAL CLOSURE ACHIEVED]
Scoreboard Summary   : Total: 71 | Passed: 71 | Failed: 0
UVM_ERROR : 0, UVM_FATAL : 0
==================================================================
```

### 3. Full SoC Hardware-Software Co-Simulation (`tb_soc_top.sv`)
- **Total Simulation Time**: 45,833,650 ns (**2,291,682 clock cycles**).
- **CPU Retired Instructions**: **351,826 instructions** (0 TRAP, 0 pipeline stalls).
- **UART Output Stream**: **5,342 characters** received with 100% parity against golden output.

---

## Directory Structure

```text
├── RTL/                         # SystemVerilog hardware RTL source files
│   ├── pe_gemm.sv               # Processing Element (INT8 multiplier + INT32 accumulator)
│   ├── systolic_skew_unit.sv    # Wavefront delay skew registers (0T, 1T, ...)
│   ├── systolic_array_core.sv   # NxN nearest-neighbor 2D PE mesh
│   ├── matrix_buffer_a.sv       # Weight on-chip RAM buffer
│   ├── matrix_buffer_b.sv       # Activation on-chip RAM buffer
│   ├── matrix_buffer_c.sv       # Dual-channel output RAM buffer (INT8 + INT32)
│   ├── quantize_relu_unit.sv    # ReLU, Multi-Scale Shift, Saturation Clamping
│   ├── gemm_controller.sv       # Centralized control FSM (7 states)
│   ├── systolic_accelerator_top.sv # Top-level accelerator core module
│   ├── systolic_gemm_axi_lite.sv   # AMBA AXI4-Lite slave wrapper & Profiler
│   ├── picorv32.v               # RISC-V RV32I Soft Core CPU (YosysHQ)
│   ├── axi_interconnect.sv      # 1-Master to 3-Slave AXI4-Lite Crossbar
│   ├── axi_ram.sv               # 32 KB On-Chip BRAM with byte strobe ($readmemh)
│   ├── axi_uart.sv              # AXI4-Lite UART Serial Controller
│   ├── seven_seg_decoder.sv     # 7-Segment Hexadecimal Display Decoder
│   ├── soc_top.sv               # Complete Integrated SoC Top (DE1 Board)
│   ├── soc_top_de2.sv           # Complete Integrated SoC Top (DE2 Board, 8x8 Array)
│   ├── soc_top_de10.sv          # Complete Integrated SoC Top (DE10-Standard, 8x8 Array)
│   └── firmware.hex             # Synchronized boot firmware machine code
├── firmware/                    # RISC-V Embedded Bare-Metal C Firmware
│   ├── systolic.h               # Accelerator MMIO driver, cycle counters, math helpers
│   ├── main.c                   # Interactive firmware console (7 demo scenarios)
│   ├── mnist_conv1_weights.h    # Pre-trained Conv1 INT8 weights & biases
│   ├── mnist_weights.h          # Full MNIST weights for inference
│   ├── start.s                  # Startup assembly code (stack pointer init, crt0)
│   ├── link.ld                  # Linker script (32 KB BRAM mapping)
│   ├── Makefile                 # Native GNU GCC build script (0 warnings)
│   ├── firmware.hex             # Verilog hex format machine code
│   └── firmware.dis             # Complete assembly disassembly listing
├── uvm_verify/                  # IEEE 1800 SystemVerilog UVM 1.1c Verification Suite
│   ├── tb_top.sv                # UVM Top-level testbench
│   ├── gemm_if.sv               # Interface with clocking blocks and SVA assertions
│   ├── gemm_pkg.sv              # Package imports
│   ├── gemm_seq_item.sv         # Sequence item with constrained randomization & golden model
│   ├── gemm_sequences.sv        # Directed, random, stress, and cross-coverage sequences
│   ├── gemm_driver.sv           # Pipelined driver driving AXI-like transactions
│   ├── gemm_monitor.sv          # Output monitor checking DUT responses
│   ├── gemm_scoreboard.sv       # Bit-true scoreboard comparing against expected results
│   ├── gemm_coverage.sv         # 88-bin Functional Point & Cross-Coverage collector
│   ├── gemm_env.sv              # UVM environment container
│   ├── gemm_tests.sv            # Test library (directed, random, stress, reset)
│   ├── run_uvm.bat              # Command-line runner for single UVM test
│   ├── run_uvm.do               # ModelSim TCL compilation and execution script
│   └── run_regression.py        # Multi-seed regression runner with failure reproduction
├── VEFIFY/                      # ModelSim RTL Simulation Testbenches
│   ├── tb_soc_top.sv            # Full SoC Co-Simulation testbench
│   ├── tb_systolic_gemm.sv      # Standalone accelerator scoreboard testbench
│   ├── tb_systolic_stress_test.sv # Standalone 6-scenario stress testbench
│   ├── run_soc_sim.do           # ModelSim co-simulation script
│   ├── run_gemm_sim.do          # ModelSim standalone testbench script
│   ├── run_stress_sim.do        # ModelSim stress testbench script
│   ├── run_code_coverage.do     # ModelSim RTL code coverage script (+cover=bcesf)
│   └── run_code_coverage.bat    # Windows launcher for code coverage analysis
├── software_ref/                # Python Golden Reference Models & Deployment Tools
│   ├── mnist_cnn_model.py       # PyTorch quantized INT8 CNN model (97.06% accuracy)
│   ├── export_conv1_data.py     # Weights and feature map extraction tool
│   ├── im2col.py                # Mathematical im2col & col2im transformation
│   ├── tiling_engine.py         # Hardware-aware 2D tiling partitioning engine
│   ├── uart_bridge.py           # Real-time Host PC GUI & UART serial bridge
│   └── gemm_golden.py           # Bit-accurate matrix generation script
├── synthesis_soc/               # Quartus II Synthesis Project for Terasic DE1 (EP2C20)
│   ├── compile_soc.bat          # Automated command-line build script
│   ├── program_de1.bat          # USB-Blaster programming script
│   ├── soc_top.qpf / .qsf / .sdc# Quartus project files & SDC timing constraints
│   └── soc_top.sof              # Compiled FPGA bitstream file
├── synthesis_soc_de2/           # Quartus II Synthesis Project for Terasic DE2 (EP2C35, 8x8)
│   ├── compile_soc_de2.bat      # Automated command-line build script
│   ├── program_de2.bat          # USB-Blaster programming script
│   ├── soc_top_de2.qpf/.qsf/.sdc# Quartus project files & SDC timing constraints
│   ├── soc_top_de2.sof          # Compiled FPGA bitstream file (64 PEs)
│   └── README_DE2.md            # DE2 detailed architecture & pinout documentation
└── synthesis_soc_de10/          # Quartus Prime Synthesis Project for Terasic DE10-Standard
    ├── compile_soc_de10.bat     # Automated command-line build script
    ├── program_de10.bat         # USB-Blaster programming script
    └── README_DE10.md           # DE10-Standard detailed pinout documentation
```

---

## Quickstart Guide

### 1. Build Firmware (GNU RISC-V Toolchain)
Requires `riscv-none-elf-gcc` on your system path:
```powershell
cd firmware
make clean
make
```

### 2. Run Full SoC Co-Simulation on ModelSim
```powershell
cd VEFIFY
C:\13.0sp1\modelsim_ase\win32aloem\vsim.exe -c -do run_soc_sim.do
```

### 3. Run UVM 1.1c Functional Verification & Coverage
```powershell
cd uvm_verify
.\run_uvm.bat gemm_directed_test
```
To run multi-seed regression (e.g. 10 seeds):
```powershell
python run_regression.py --seeds 10 --test gemm_random_test
```

### 4. Synthesize Bitstream on Quartus II
- **Terasic DE1** ($4 \times 4$ Array, Cyclone II EP2C20):
  ```powershell
  cd synthesis_soc
  .\compile_soc.bat
  ```
- **Terasic DE2** ($8 \times 8$ Array, Cyclone II EP2C35):
  ```powershell
  cd synthesis_soc_de2
  .\compile_soc_de2.bat
  ```
- **Terasic DE10-Standard** ($8 \times 8$ Array, Cyclone V):
  ```powershell
  cd synthesis_soc_de10
  .\compile_soc_de10.bat
  ```

### 5. Deploy on Board & Launch Host PC GUI
1. Connect USB-Blaster and RS-232 / USB-UART cable to the FPGA board.
2. Program the bitstream:
   ```powershell
   cd synthesis_soc     # or synthesis_soc_de2
   .\program_de1.bat    # or .\program_de2.bat
   ```
3. Launch the interactive real-time handwriting drawing GUI:
   ```powershell
   python software_ref/uart_bridge.py --port COM3 --mode gui
   ```

---

## FPGA Hardware Pinout Maps

### Terasic DE1 (`EP2C20F484C7`)
| Signal | Pin | Function |
| :--- | :---: | :--- |
| `clk` | `PIN_L1` | 50.0 MHz Oscillator Input (`CLOCK_50`) |
| `rst_n` | `PIN_R22` | Active-Low Reset (`KEY[0]`) |
| `uart_rx` | `PIN_F14` | RS-232 RXD (115200 Baud) |
| `uart_tx` | `PIN_G12` | RS-232 TXD (115200 Baud) |
| `hex0[6:0]` | `PIN_E2`..`PIN_J2` | 7-Segment Display 0 (Predicted Class) |
| `hex1[6:0]` | `PIN_D1`..`PIN_E1` | 7-Segment Display 1 (Tens Class) |
| `ledr[0]` | `PIN_R20` | CPU Trap Alert Flag |
| `ledr[1]` | `PIN_R19` | Accelerator Core Busy Flag |
| `ledg[0]` | `PIN_U22` | Accelerator Core Done Flag |

### Terasic DE2 (`EP2C35F672C6`)
| Signal | Pin | Function |
| :--- | :---: | :--- |
| `clk` | `PIN_N2` | 50.0 MHz Oscillator Input (`CLOCK_50`) |
| `rst_n` | `PIN_G26` | Active-Low Reset (`KEY[0]`) |
| `uart_rx` | `PIN_C25` | RS-232 UART RXD |
| `uart_tx` | `PIN_B25` | RS-232 UART TXD |
| `hex0[6:0]`..`hex7[6:0]` | 8 Displays | Multi-digit Telemetry & Class Display |
| `ledr[17:0]` | 18 Red LEDs | One-hot Class & Trap Monitoring |
| `ledg[8:0]` | 9 Green LEDs | Status Flags (`core_busy`, `core_done`, `uart_rx`) |

---

## Academic Context & Author

- **Author**: Nguyen Hoang Sang ([Sang-HCMUT](https://github.com/Sang-HCMUT))
- **Project**: Graduation Capstone Project (Đồ án tốt nghiệp Kỹ sư)
- **Institution**: Ho Chi Minh City University of Technology (HCMUT - VNU-HCM)
- **Faculty**: Faculty of Electrical & Electronics Engineering
- **Specialization**: Integrated Circuit (IC) Design & Embedded Systems
- **License**: MIT License
