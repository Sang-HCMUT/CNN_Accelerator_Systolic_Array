#!/usr/bin/env python3
"""
Script: export_conv1_data.py
Extracts real MNIST CNN Conv1 layer weights, sample 0 image, and bit-true golden outputs
into a C header file for PicoRV32 SoC firmware acceleration.
"""

import os
import sys
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from mnist_dataset import get_mnist
from im2col import im2col_2d

def main():
    weights_path = os.path.join(CURRENT_DIR, "mnist_weights_int8.npz")
    data = np.load(weights_path)
    W1 = data['W1_int8'] # (16, 1, 3, 3)
    b1 = data['b1_int32'] # (16,)
    shift_conv = int(data['shift_bits_conv']) # 8

    # Flatten W1 to (16, 9)
    W1_flat = W1.reshape(16, 9)

    # Load MNIST Test Sample 0 (Digit 7)
    X_test, y_test = get_mnist(test_only=True)
    img_sample0 = X_test[0, 0] # (28, 28)
    label = int(y_test[0])

    print(f"Sample 0 Label: {label}")
    print(f"Image shape: {img_sample0.shape}, min: {img_sample0.min()}, max: {img_sample0.max()}")
    print(f"Conv1 Weights: shape {W1_flat.shape}, min: {W1_flat.min()}, max: {W1_flat.max()}")

    # im2col with padding=1
    cols, _ = im2col_2d(img_sample0[np.newaxis, ...], kernel_size=3, stride=1, padding=1) # (9, 784)

    # Full GEMM: [16 x 9] x [9 x 784] -> [16 x 784]
    acc_full = np.matmul(W1_flat.astype(np.int32), cols.astype(np.int32))
    relu_full = np.maximum(0, acc_full + b1[:, None])
    out_full = np.clip(np.right_shift(relu_full, shift_conv), 0, 127).astype(np.int8)

    # Benchmark: 16 filters x 16 patches (16 tiles of 4x4, K=9)
    # 4 filter groups (rows 0..3, 4..7, 8..11, 12..15)
    # 4 patch groups: let's select 16 patches from rows 7..10, cols 7..10 (active stroke region)
    # where stroke pixels of Digit 7 are prominent!
    selected_patch_indices = []
    for r in range(7, 11):
        for c in range(7, 11):
            selected_patch_indices.append(r * 28 + c)
    selected_patch_indices = np.array(selected_patch_indices, dtype=np.int32)

    cols_bench = cols[:, selected_patch_indices] # (9, 16)
    acc_bench = np.matmul(W1_flat.astype(np.int32), cols_bench.astype(np.int32)) # (16, 16)
    relu_bench = np.maximum(0, acc_bench + b1[:, None])
    out_bench = np.clip(np.right_shift(relu_bench, shift_conv), 0, 127).astype(np.int8)

    acc_sum_bench = int(np.sum(acc_bench))
    out_sum_bench = int(np.sum(out_bench))
    out_sum_full = int(np.sum(out_full))

    print(f"Benchmark 16x16: Acc Sum = {acc_sum_bench}, Quantized Out Sum = {out_sum_bench}")
    print(f"Full 16x784: Quantized Out Sum = {out_sum_full}")

    # Generate C header
    header_path = os.path.join(os.path.dirname(CURRENT_DIR), "firmware", "mnist_conv1_weights.h")
    with open(header_path, "w") as f:
        f.write("/*\n")
        f.write(" * Header: mnist_conv1_weights.h\n")
        f.write(" * Real Quantized INT8 Conv1 Layer Parameters for MNIST CNN.\n")
        f.write(" * Bit-true matching with Python reference model (97.06% accuracy).\n")
        f.write(" */\n\n")
        f.write("#ifndef MNIST_CONV1_WEIGHTS_H\n")
        f.write("#define MNIST_CONV1_WEIGHTS_H\n\n")
        f.write("#include <stdint.h>\n\n")

        # Conv1 Config
        f.write("#define CONV1_NUM_FILTERS  16\n")
        f.write("#define CONV1_KERNEL_SIZE  3\n")
        f.write("#define CONV1_KERNEL_ELEMS 9\n")
        f.write(f"#define CONV1_SHIFT_BITS   {shift_conv}\n\n")

        # Weights [16 x 9]
        f.write("// Conv1 Weights: 16 filters of 3x3 kernels (Signed INT8)\n")
        f.write("static const int8_t conv1_weights[144] = {\n")
        for i in range(16):
            row_str = ", ".join(f"{int(W1_flat[i, k]):4d}" for k in range(9))
            f.write(f"    {row_str},\n")
        f.write("};\n\n")

        # Biases [16]
        f.write("// Conv1 Biases: 16 filters (Signed INT32)\n")
        f.write("static const int32_t conv1_biases[16] = {\n    ")
        f.write(", ".join(f"{int(b1[i])}" for i in range(16)))
        f.write("\n};\n\n")

        # Benchmark 16 active patches indices
        f.write("// Benchmark Active Patches Indices (16 patches from rows 7..10, cols 7..10 of Digit 7)\n")
        f.write("static const uint16_t conv1_bench_patch_indices[16] = {\n    ")
        f.write(", ".join(f"{int(p)}" for p in selected_patch_indices))
        f.write("\n};\n\n")

        # Benchmark Golden Accumulators [16 x 16]
        f.write(f"#define CONV1_BENCH_ACC_SUM  {acc_sum_bench}\n")
        f.write(f"#define CONV1_BENCH_OUT_SUM  {out_sum_bench}\n")
        f.write(f"#define CONV1_FULL_OUT_SUM   {out_sum_full}\n\n")

        f.write("// Benchmark Golden INT8 Outputs [16 x 16]\n")
        f.write("static const int8_t conv1_bench_gold_out[256] = {\n")
        for r in range(16):
            row_str = ", ".join(f"{int(out_bench[r, c]):3d}" for c in range(16))
            f.write(f"    {row_str},\n")
        f.write("};\n\n")

        # Sample 0 Image (28x28 Signed INT8)
        f.write("// Real MNIST Test Sample 0 (Digit '7', 28x28 Signed INT8)\n")
        f.write("static const int8_t mnist_sample0_img28x28[784] = {\n")
        for r in range(28):
            row_str = ", ".join(f"{int(img_sample0[r, c]):4d}" for c in range(28))
            f.write(f"    {row_str},\n")
        f.write("};\n\n")

        f.write("#endif // MNIST_CONV1_WEIGHTS_H\n")

    print(f"Successfully generated {header_path}")

if __name__ == "__main__":
    main()
