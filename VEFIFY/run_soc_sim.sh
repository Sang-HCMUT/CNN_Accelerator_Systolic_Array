#!/bin/bash
# Shell script to run Phase 3 SoC Co-Simulation on Linux / Server
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo " [Linux/Server] Running Phase 3 SoC Co-Simulation"
echo "=========================================================="

# 1. Regenerate firmware if needed
if command -v python3 &>/dev/null; then
    echo "[1/2] Generating RISC-V firmware with Python Assembler..."
    python3 ../firmware/firmware_generator.py
elif command -v python &>/dev/null; then
    echo "[1/2] Generating RISC-V firmware with Python Assembler..."
    python ../firmware/firmware_generator.py
else
    echo "[WARN] Python not found, using existing firmware.hex..."
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
