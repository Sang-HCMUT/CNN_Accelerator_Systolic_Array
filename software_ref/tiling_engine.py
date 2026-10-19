"""
Module: tiling_engine.py
Hardware-Aware Matrix Tiling Engine for 2D Systolic Array Accelerator.
Partitions arbitrarily large Matrix Multiplications [M x K] x [K x N]
into sub-tiles matching hardware ARRAY_SIZE (e.g., 4x4 or 8x8).
Emulates the hardware execution of each tile on the Systolic Core.
Accumulates partial sums across K-dimension.
Applies Bias addition, Arithmetic Scaling (>> shift_bits),
ReLU, and Saturation Clamping to INT8 [-128, 127].
Supports zero-padding for non-multiple matrix dimensions.
"""

import numpy as np

class SystolicTilingEngine:
    """
    Simulates the tiled execution of large GEMMs on an NxN Systolic Array.
    """
    def __init__(self, array_size=4, max_k=16, data_width=8, acc_width=32):
        self.array_size = array_size
        self.max_k = max_k
        self.data_width = data_width
        self.acc_width = acc_width
        
        # Performance tracking metrics
        self.total_tiles_processed = 0
        self.total_hardware_cycles = 0
        self.total_mac_operations  = 0
        
    def reset_metrics(self):
        self.total_tiles_processed = 0
        self.total_hardware_cycles = 0
        self.total_mac_operations  = 0

    def simulate_hardware_tile(self, A_tile, B_tile):
        """
        Cycle-accurate behavior of the Systolic Core for one ARRAY_SIZE x ARRAY_SIZE tile.
        A_tile: [ARRAY_SIZE x K_dim] in Signed INT8
        B_tile: [K_dim x ARRAY_SIZE] in Signed INT8
        Returns: C_acc [ARRAY_SIZE x ARRAY_SIZE] in Signed INT32
        """
        N = self.array_size
        K = A_tile.shape[1]
        
        # Verify dimensions
        assert A_tile.shape == (N, K), f"A_tile shape {A_tile.shape} != ({N}, {K})"
        assert B_tile.shape == (K, N), f"B_tile shape {B_tile.shape} != ({K}, {N})"
        
        # Systolic Accumulation (Exact INT32 math)
        C_acc = np.zeros((N, N), dtype=np.int32)
        for i in range(N):
            for j in range(N):
                acc = 0
                for k in range(K):
                    # INT8 x INT8 = INT16 multiplication
                    prod = int(A_tile[i, k]) * int(B_tile[k, j])
                    # INT32 Accumulation
                    acc += prod
                C_acc[i, j] = acc
                
        # Hardware latency calculation:
        # Latency = 1 (clear) + K (stream) + 2*ARRAY_SIZE (drain) + ARRAY_SIZE^2 (readout) + 2 (flush/done)
        tile_latency = 1 + K + 2 * N + N * N + 2
        
        self.total_tiles_processed += 1
        self.total_hardware_cycles += tile_latency
        self.total_mac_operations  += N * N * K
        
        return C_acc

    def execute_tiled_gemm(self, A, B, bias=None, shift_bits=4, bypass_relu=False):
        """
        Splits arbitrary [M x K] and [K x N] matrices into tiles and executes them.
        
        Parameters:
        -----------
        A : np.ndarray (M, K)
            Weights matrix in signed INT8
        B : np.ndarray (K, N)
            Activation/Patch matrix in signed INT8
        bias : np.ndarray (M,), optional
            Layer bias in signed INT32
        shift_bits : int
            Scaling arithmetic right shift
        bypass_relu : bool
            True to disable ReLU
            
        Returns:
        --------
        C_out : np.ndarray (M, N) in Signed INT8
        C_raw_acc : np.ndarray (M, N) in Signed INT32
        """
        M, K = A.shape
        K_b, N = B.shape
        assert K == K_b, f"Dimension mismatch: A shape ({M}, {K}) vs B shape ({K_b}, {N})"
        
        S = self.array_size
        
        # Calculate padded dimensions to multiples of ARRAY_SIZE
        M_pad = int(np.ceil(M / S)) * S
        N_pad = int(np.ceil(N / S)) * S
        
        # Pad matrices with zeros if dimensions are not exact multiples
        A_padded = np.zeros((M_pad, K), dtype=np.int8)
        A_padded[:M, :K] = A.astype(np.int8)
        
        B_padded = np.zeros((K, N_pad), dtype=np.int8)
        B_padded[:K, :N] = B.astype(np.int8)
        
        # Accumulator buffer for the padded output matrix (INT32)
        C_acc_padded = np.zeros((M_pad, N_pad), dtype=np.int32)
        
        # Tiling loops:
        # 1. Iterate over M-dimension tiles (rows of A)
        for i in range(0, M_pad, S):
            # 2. Iterate over N-dimension tiles (columns of B)
            for j in range(0, N_pad, S):
                tile_sum = np.zeros((S, S), dtype=np.int32)
                
                # 3. Iterate over K-dimension (depth) in chunks of at most max_k
                for k in range(0, K, self.max_k):
                    k_len = min(self.max_k, K - k)
                    
                    A_sub = A_padded[i:i+S, k:k+k_len]
                    B_sub = B_padded[k:k+k_len, j:j+S]
                    
                    sub_res = self.simulate_hardware_tile(A_sub, B_sub)
                    tile_sum += sub_res
                    
                C_acc_padded[i:i+S, j:j+S] = tile_sum
                
        # Crop back to original (M, N) dimension
        C_raw_acc = C_acc_padded[:M, :N].copy()
        
        # Post-Processing:
        # 1. Add bias (INT32)
        C_processed = C_raw_acc.copy()
        if bias is not None:
            C_processed = C_processed + bias[:, np.newaxis]
            
        # 2. ReLU Activation: max(0, x)
        if not bypass_relu:
            C_processed = np.maximum(0, C_processed)
            
        # 3. Arithmetic Shift Right (preserves sign if negative)
        C_scaled = np.right_shift(C_processed, shift_bits)
        
        # 4. Saturation Clamping to INT8 range
        if bypass_relu:
            C_out = np.clip(C_scaled, -128, 127).astype(np.int8)
        else:
            C_out = np.clip(C_scaled, 0, 127).astype(np.int8)
            
        return C_out, C_raw_acc


# Self-test when run directly
if __name__ == "__main__":
    print("=" * 60)
    print("Testing Systolic Tiling Engine (Arbitrary Matrix Scaling)...")
    print("=" * 60)
    
    np.random.seed(123)
    
    # Large non-power-of-2 matrix test:
    # M = 10 (filters), K = 18 (C_in*Kh*Kw), N = 25 (patches)
    # Hardware ARRAY_SIZE = 4x4
    M, K, N = 10, 18, 25
    A = np.random.randint(-16, 16, size=(M, K)).astype(np.int8)
    B = np.random.randint(-16, 16, size=(K, N)).astype(np.int8)
    bias = np.random.randint(-50, 50, size=(M,)).astype(np.int32)
    
    engine = SystolicTilingEngine(array_size=4, max_k=16)
    tiled_out, tiled_acc = engine.execute_tiled_gemm(A, B, bias=bias, shift_bits=3, bypass_relu=False)
    
    # Compute Golden Full-Matrix Multiplication
    gold_acc = np.matmul(A.astype(np.int32), B.astype(np.int32))
    gold_with_bias = gold_acc + bias[:, np.newaxis]
    gold_relu = np.maximum(0, gold_with_bias)
    gold_scaled = np.right_shift(gold_relu, 3)
    gold_out = np.clip(gold_scaled, 0, 127).astype(np.int8)
    
    diff_acc = np.max(np.abs(tiled_acc - gold_acc))
    diff_out = np.max(np.abs(tiled_out - gold_out))
    
    print(f"[*] Input Dimensions: A[{M}x{K}] x B[{K}x{N}] -> C[{M}x{N}]")
    print(f"[*] Hardware Tile Size: {engine.array_size}x{engine.array_size} PEs")
    print(f"[*] Total Sub-Tiles Processed: {engine.total_tiles_processed}")
    print(f"[*] Total Emulated Clock Cycles: {engine.total_hardware_cycles}")
    print(f"[*] Total MAC Operations: {engine.total_mac_operations}")
    print(f"[*] Diff on Accumulation (INT32): {diff_acc}")
    print(f"[*] Diff on Quantized Output (INT8): {diff_out}")
    
    if diff_acc == 0 and diff_out == 0:
        print("\n>>> [SUCCESS] Tiling Engine is 100% BIT-TRUE MATCH with Full Matrix GEMM! <<<")
    else:
        print("\n>>> [FAIL] Difference detected! <<<")
