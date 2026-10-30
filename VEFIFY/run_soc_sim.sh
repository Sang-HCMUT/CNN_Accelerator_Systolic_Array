#!/bin/bash
# Shell script to run Phase 3 SoC Co-Simulation on Linux / Server
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo " [Linux/Server] Running Phase 3 SoC Co-Simulation"
echo "=========================================================="

# 1. Compile firmware using RISC-V GCC toolchain if needed
if command -v riscv-none-elf-gcc &>/dev/null && command -v make &>/dev/null; then
    echo "[1/2] Compiling RISC-V C firmware with GCC toolchain..."
    make -C ../firmware
    cp ../firmware/firmware.hex ./firmware.hex
else
    echo "[INFO] Using existing firmware.hex..."
fi

# 2. Run ModelSim / QuestaSim in command-line mode
echo "[2/2] Running ModelSim simulation..."
if command -v vsim &>/dev/null; then
    vsim -c -do run_soc_sim.do
else
    echo "[ERROR] 'vsim' not found in PATH."
    echo "Please source your EDA environment (e.g., 'module load modelsim' or 'module load questasim')."
    exit 1
fi
