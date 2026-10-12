#!/bin/bash
# Shell script to run Quartus II Synthesis on Linux / Server
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo " [Linux/Server] Running Quartus II Synthesis for SoC Top"
echo "=========================================================="

if ! command -v quartus_map &>/dev/null; then
    echo "[ERROR] 'quartus_map' not found in PATH."
    echo "Please load your Quartus environment (e.g. export PATH=\$QUARTUS_ROOTDIR/bin:\$PATH)."
    exit 1
fi

echo "[1/4] Running Analysis & Synthesis (quartus_map)..."
quartus_map soc_top

echo "[2/4] Running Fitter (quartus_fit)..."
quartus_fit soc_top

echo "[3/4] Running Assembler (quartus_asm)..."
quartus_asm soc_top

echo "[4/4] Running TimeQuest Timing Analyzer (quartus_sta)..."
quartus_sta soc_top

echo "=========================================================="
echo " Synthesis Completed Successfully!"
echo " Check soc_top.fit.summary and soc_top.sta.rpt for metrics."
echo "=========================================================="
