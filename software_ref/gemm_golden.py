#!/usr/bin/env python3
"""
Script: gemm_golden.py
Pure-Python (Zero-Dependency) Golden Reference Model for INT8 Systolic Array GEMM Accelerator.
Generates parameterized matrix multiplications: C = A x B.
Matrix A: [M x K] in signed INT8 (-128 to 127)
Matrix B: [K x N] in signed INT8 (-128 to 127)
Computes C = A x B with INT32 accumulation.
Applies ReLU: max(0, x).
Applies Quantization: arithmetic shift right (>> shift_bits) + clamp to [0, 127].
Exports matrix_a.hex, matrix_b.hex, golden_acc_int32.hex, golden_output_int8.hex.
"""

import os
import random

def generate_test_vectors(array_size=4, k_dim=4, shift_bits=4, output_dir="./"):
    random.seed(42)
    os.makedirs(output_dir, exist_ok=True)

    M = array_size
    K = k_dim
    N = array_size

    print(f"[*] Generating Golden Reference for Matrix Dimension: [{M}x{K}] x [{K}x{N}]")

    # 1. Generate Matrix A (Weights) & Matrix B (Activations) in signed INT8 [-64, 63]
    A = [[random.randint(-32, 32) for _ in range(K)] for _ in range(M)]
    B = [[random.randint(-32, 32) for _ in range(N)] for _ in range(K)]

    # 2. Golden Integer Multiplication & Accumulation (INT32)
    C_acc = [[0 for _ in range(N)] for _ in range(M)]
    for i in range(M):
        for j in range(N):
            total = 0
            for k in range(K):
                total += A[i][k] * B[k][j]
            C_acc[i][j] = total

    # 3. Activation: ReLU
    C_relu = [[max(0, C_acc[i][j]) for j in range(N)] for i in range(M)]

    # 4. Quantization: Arithmetic Shift Right + Clamping to [0, 127]
    C_quant = [[0 for _ in range(N)] for _ in range(M)]
    for i in range(M):
        for j in range(N):
            scaled = C_relu[i][j] >> shift_bits
            clamped = min(127, max(0, scaled))
            C_quant[i][j] = clamped

    print("\n--- Matrix A (Weights INT8) ---")
    for row in A:
        print([f"{x:4d}" for x in row])

    print("\n--- Matrix B (Activations INT8) ---")
    for row in B:
        print([f"{x:4d}" for x in row])

    print("\n--- Golden Accumulation Result C (INT32) ---")
    for row in C_acc:
        print([f"{x:6d}" for x in row])

    print("\n--- Golden Post-ReLU & Quantized Output (INT8) ---")
    for row in C_quant:
        print([f"{x:4d}" for x in row])

    def to_hex_8bit(val):
        return f"{(val & 0xFF):02X}"

    def to_hex_32bit(val):
        return f"{(val & 0xFFFFFFFF):08X}"

    # Export Matrix A (Row-major)
    a_path = os.path.join(output_dir, "matrix_a.hex")
    with open(a_path, "w") as f:
        for row in A:
            for val in row:
                f.write(f"{to_hex_8bit(val)}\n")

    # Export Matrix B (Column-major or Row-major)
    b_path = os.path.join(output_dir, "matrix_b.hex")
    with open(b_path, "w") as f:
        for row in B:
            for val in row:
                f.write(f"{to_hex_8bit(val)}\n")

    # Export Golden INT32
    gold_acc_path = os.path.join(output_dir, "golden_acc_int32.hex")
    with open(gold_acc_path, "w") as f:
        for row in C_acc:
            for val in row:
                f.write(f"{to_hex_32bit(val)}\n")

    # Export Golden INT8
    gold_quant_path = os.path.join(output_dir, "golden_output_int8.hex")
    with open(gold_quant_path, "w") as f:
        for row in C_quant:
            for val in row:
                f.write(f"{to_hex_8bit(val)}\n")

    print(f"\n[+] Exported test vectors to '{output_dir}':")
    print(f"    - {a_path}")
    print(f"    - {b_path}")
    print(f"    - {gold_acc_path}")
    print(f"    - {gold_quant_path}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    generate_test_vectors(array_size=4, k_dim=4, shift_bits=4, output_dir=current_dir)
