#!/bin/bash
# Shell script to run Phase 2 MNIST Demo on Linux / Server
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if command -v python3 &>/dev/null; then
    python3 run_mnist_inference.py
else
    python run_mnist_inference.py
fi
