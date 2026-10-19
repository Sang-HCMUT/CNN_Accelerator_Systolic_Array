"""
Module: im2col.py
Mathematical im2col (Image to Column) & col2im Engine for Systolic Array GEMM Accelerator.
Converts high-dimensional 2D convolutions into GEMM (C = A x B).
Matrix A (Weights): [C_out x (C_in * K_h * K_w)]
Matrix B (Patches): [(C_in * K_h * K_w) x (H_out * W_out)]
Output Matrix C:    [C_out x (H_out * W_out)]
Pure NumPy (Zero-Dependency), fully vectorized and bit-accurate.
"""

import numpy as np

def im2col_2d(input_tensor, kernel_size, stride=1, padding=0):
    """
    Transforms an input feature map into column patches for GEMM.
    
    Parameters:
    -----------
    input_tensor : np.ndarray
        Shape (N, C_in, H, W) or (C_in, H, W)
    kernel_size : int or tuple (K_h, K_w)
        Dimensions of the convolution filter
    stride : int or tuple (S_h, S_w)
        Stride of the sliding window
    padding : int or tuple (P_h, P_w)
        Zero-padding added to both sides of input
        
    Returns:
    --------
    cols : np.ndarray
        2D Matrix of shape [(C_in * K_h * K_w), (N * H_out * W_out)]
    out_shape : tuple
        (N, C_in, H_out, W_out) spatial shape information
    """
    # Normalize 3D tensor (C, H, W) to 4D (1, C, H, W)
    if input_tensor.ndim == 3:
        input_tensor = input_tensor[np.newaxis, ...]
        
    N, C_in, H, W = input_tensor.shape
    
    if isinstance(kernel_size, int):
        Kh, Kw = kernel_size, kernel_size
    else:
        Kh, Kw = kernel_size
        
    if isinstance(stride, int):
        Sh, Sw = stride, stride
    else:
        Sh, Sw = stride
        
    if isinstance(padding, int):
        Ph, Pw = padding, padding
    else:
        Ph, Pw = padding
        
    # Calculate output dimensions
    H_out = (H + 2 * Ph - Kh) // Sh + 1
    W_out = (W + 2 * Pw - Kw) // Sw + 1
    
    assert H_out > 0 and W_out > 0, f"Invalid output shape: H_out={H_out}, W_out={W_out}"
    
    # Apply zero-padding
    if Ph > 0 or Pw > 0:
        padded = np.pad(
            input_tensor,
            ((0, 0), (0, 0), (Ph, Ph), (Pw, Pw)),
            mode='constant',
            constant_values=0
        )
    else:
        padded = input_tensor

    # Extract patches
    # Each patch has size (C_in, Kh, Kw) -> flattened to (C_in * Kh * Kw)
    cols = np.zeros((C_in * Kh * Kw, N * H_out * W_out), dtype=input_tensor.dtype)
    
    col_idx = 0
    for n in range(N):
        for i in range(H_out):
            h_start = i * Sh
            h_end = h_start + Kh
            for j in range(W_out):
                w_start = j * Sw
                w_end = w_start + Kw
                patch = padded[n, :, h_start:h_end, w_start:w_end]
                cols[:, col_idx] = patch.reshape(-1)
                col_idx += 1
                
    return cols, (N, C_in, H_out, W_out)


def col2im_2d(cols, out_shape, C_out):
    """
    Reshapes the GEMM result matrix C back into a 4D output feature map tensor.
    
    Parameters:
    -----------
    cols : np.ndarray
        Shape [C_out, (N * H_out * W_out)]
    out_shape : tuple
        (N, C_in, H_out, W_out)
    C_out : int
        Number of output channels (filters)
        
    Returns:
    --------
    output_tensor : np.ndarray
        Shape (N, C_out, H_out, W_out)
    """
    N, _, H_out, W_out = out_shape
    output_tensor = cols.reshape(C_out, N, H_out, W_out)
    # Transpose back to (N, C_out, H_out, W_out)
    output_tensor = np.transpose(output_tensor, (1, 0, 2, 3))
    return output_tensor


def conv2d_im2col(input_tensor, weights, bias=None, stride=1, padding=0):
    """
    Full 2D Convolution implemented via im2col and Matrix Multiplication (GEMM).
    
    Parameters:
    -----------
    input_tensor : np.ndarray
        Shape (N, C_in, H, W)
    weights : np.ndarray
        Shape (C_out, C_in, Kh, Kw)
    bias : np.ndarray, optional
        Shape (C_out,)
        
    Returns:
    --------
    output_tensor : np.ndarray
        Shape (N, C_out, H_out, W_out)
    """
    C_out, C_in, Kh, Kw = weights.shape
    
    # 1. Transform weights to 2D matrix A [C_out x (C_in * Kh * Kw)]
    A = weights.reshape(C_out, -1)
    
    # 2. Transform input feature map to 2D matrix B [(C_in * Kh * Kw) x (N * H_out * W_out)]
    B, out_shape = im2col_2d(input_tensor, (Kh, Kw), stride=stride, padding=padding)
    
    # 3. Compute GEMM: C = A @ B
    C = np.matmul(A, B)
    
    # 4. Add bias if present
    if bias is not None:
        C = C + bias[:, np.newaxis]
        
    # 5. Reshape to 4D tensor (N, C_out, H_out, W_out)
    output_tensor = col2im_2d(C, out_shape, C_out)
    return output_tensor, A, B, C


def direct_conv2d_reference(input_tensor, weights, bias=None, stride=1, padding=0):
    """
    Direct spatial convolution loop used as a golden reference to test im2col correctness.
    """
    if input_tensor.ndim == 3:
        input_tensor = input_tensor[np.newaxis, ...]
        
    N, C_in, H, W = input_tensor.shape
    C_out, _, Kh, Kw = weights.shape
    
    if isinstance(stride, int):
        Sh, Sw = stride, stride
    else:
        Sh, Sw = stride
        
    if isinstance(padding, int):
        Ph, Pw = padding, padding
    else:
        Ph, Pw = padding
        
    H_out = (H + 2 * Ph - Kh) // Sh + 1
    W_out = (W + 2 * Pw - Kw) // Sw + 1
    
    if Ph > 0 or Pw > 0:
        padded = np.pad(
            input_tensor,
            ((0, 0), (0, 0), (Ph, Ph), (Pw, Pw)),
            mode='constant',
            constant_values=0
        )
    else:
        padded = input_tensor
        
    out = np.zeros((N, C_out, H_out, W_out), dtype=input_tensor.dtype)
    
    for n in range(N):
        for cout in range(C_out):
            for i in range(H_out):
                h_start = i * Sh
                h_end = h_start + Kh
                for j in range(W_out):
                    w_start = j * Sw
                    w_end = w_start + Kw
                    patch = padded[n, :, h_start:h_end, w_start:w_end]
                    val = np.sum(patch * weights[cout])
                    if bias is not None:
                        val += bias[cout]
                    out[n, cout, i, j] = val
                    
    return out


# Self-test when run directly
if __name__ == "__main__":
    print("=" * 60)
    print("Testing im2col & col2im Mathematical Correctness...")
    print("=" * 60)
    
    np.random.seed(42)
    
    # Test case: 1 image, 2 input channels, 6x6 spatial dimension
    # 4 output filters, 3x3 kernel, stride=1, padding=1
    test_img = np.random.randint(-10, 10, size=(1, 2, 6, 6)).astype(np.int32)
    test_w   = np.random.randint(-5, 5, size=(4, 2, 3, 3)).astype(np.int32)
    test_b   = np.random.randint(-2, 2, size=(4,)).astype(np.int32)
    
    conv_im2col_out, A, B, C = conv2d_im2col(test_img, test_w, test_b, stride=1, padding=1)
    conv_direct_out = direct_conv2d_reference(test_img, test_w, test_b, stride=1, padding=1)
    
    diff = np.max(np.abs(conv_im2col_out - conv_direct_out))
    
    print(f"[*] Input shape:   {test_img.shape}")
    print(f"[*] Weights shape: {test_w.shape}")
    print(f"[*] Matrix A (Weights Flat):  {A.shape} -> [C_out x (C_in*Kh*Kw)]")
    print(f"[*] Matrix B (Patches Flat):  {B.shape} -> [(C_in*Kh*Kw) x (H_out*W_out)]")
    print(f"[*] Matrix C (GEMM Result):   {C.shape} -> [C_out x (H_out*W_out)]")
    print(f"[*] Output Feature Map shape: {conv_im2col_out.shape}")
    print(f"[*] Maximum absolute difference: {diff}")
    
    if diff == 0:
        print("\n>>> [SUCCESS] im2col is 100% BIT-TRUE MATCH with Direct Convolution! <<<")
    else:
        print("\n>>> [FAIL] Difference detected! <<<")
