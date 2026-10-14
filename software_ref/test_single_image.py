#!/usr/bin/env python3
"""
===============================================================================
Script: test_single_image.py
Description: Fast single-image inference tool for MNIST on Systolic Accelerator.
             Usage:
                 python software_ref/test_single_image.py [image_index]
             Example:
                 python software_ref/test_single_image.py 42
                 python software_ref/test_single_image.py random
===============================================================================
"""

import os
import sys
import random
import numpy as np

# Ensure software_ref directory is in Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from mnist_dataset import get_mnist, render_ascii_digit
from mnist_cnn_model import QuantizedMNISTNet

def test_single_image(index=42):
    X_test, y_test = get_mnist(test_only=True)
    total_samples = len(X_test)

    if isinstance(index, str) and index.lower() == "random":
        index = random.randint(0, total_samples - 1)
    else:
        try:
            index = int(index)
        except ValueError:
            index = 42

    if index < 0 or index >= total_samples:
        print(f"[!] Index {index} out of range (0 - {total_samples - 1}). Defaulting to 42.")
        index = 42

    img = X_test[index]
    lbl = int(y_test[index])

    print(f"--- Inference Test (Sample #{index}) ---")
    print(f"Sample #{index} / {total_samples} | Ground Truth: {lbl}\n")
    print(render_ascii_digit(img[0], label=f"MNIST Sample #{index}"))

    # Load Model with 4x4 Systolic Array
    model = QuantizedMNISTNet(array_size=4)

    # Run inference through Tiling Engine
    pred_digit, confidences, metrics = model.forward(img, use_systolic_tiling=True)
    ideal_pred, _, _ = model.forward(img, use_systolic_tiling=False)

    is_correct = (pred_digit == lbl)
    is_bit_true = (pred_digit == ideal_pred)

    status_str = "MATCH" if is_correct else "MISMATCH"
    bit_true_str = "(Bit-True)" if is_bit_true else "(Diff)"

    print("-" * 50)
    print(f"Prediction   : {pred_digit} [{status_str}] {bit_true_str}")
    print(f"Confidence   : {confidences[pred_digit] * 100:.1f}%")
    print(f"Ground Truth : {lbl}")
    print(f"Tiles        : {metrics['total_tiles']} (4x4)")
    print(f"Cycles       : {metrics['hw_cycles']:,} (~{metrics['hw_cycles']/50e3:.2f} ms @ 50MHz)")
    print(f"MACs         : {metrics['mac_ops']:,}")
    print("-" * 50 + "\n")

if __name__ == "__main__":
    idx_arg = 42
    if len(sys.argv) > 1:
        idx_arg = sys.argv[1]
    test_single_image(idx_arg)
