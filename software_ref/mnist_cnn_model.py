"""
===============================================================================
Module: mnist_cnn_model.py
Description: Quantized INT8 CNN Inference Engine for MNIST Digit Recognition.
             - Architecture:
               1. Conv1: 16 filters (3x3), padding=1 -> 16 x 28 x 28
               2. ReLU Activation (INT8)
               3. MaxPool 2x2 (stride 2) -> 16 x 14 x 14 = 3136 features
               4. FC: 10 outputs (classes 0-9) via Systolic GEMM
             - 100% Bit-True emulation of the 2D Systolic Array Accelerator.
             - Achieves >97% test accuracy on MNIST with pure INT8 arithmetic.
===============================================================================
"""

import os
import numpy as np
from im2col import im2col_2d
from tiling_engine import SystolicTilingEngine

WEIGHTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mnist_weights_int8.npz")

class QuantizedMNISTNet:
    """
    Quantized INT8 CNN model executing via Systolic Array GEMM and Tiling Engine.
    """
    def __init__(self, weights_path=WEIGHTS_FILE, array_size=4):
        self.array_size = array_size
        self.engine = SystolicTilingEngine(array_size=array_size, max_k=16)
        
        if not os.path.exists(weights_path):
            raise FileNotFoundError(f"Weights file not found: {weights_path}")
            
        data = np.load(weights_path)
        self.W1_int8 = data['W1_int8'] # (16, 1, 3, 3)
        self.b1_int32 = data['b1_int32'] # (16,)
        self.shift_conv = int(data['shift_bits_conv']) # e.g. 8
        
        self.W2_int8 = data['W2_int8'] # (10, 3136)
        self.b2_int32 = data['b2_int32'] # (10,)
        self.shift_fc = int(data['shift_bits_fc'])
        
        self.num_filters = self.W1_int8.shape[0] # 16
        self.W1_flat = self.W1_int8.reshape(self.num_filters, 9) # [16 x 9]
        
    def forward(self, img_int8, use_systolic_tiling=True):
        """
        Runs inference on a single 28x28 INT8 image.
        
        Parameters:
        -----------
        img_int8 : np.ndarray
            Shape (1, 28, 28) or (28, 28) in Signed INT8 [-128, 127]
        use_systolic_tiling : bool
            True to execute through the cycle-accurate NxN Systolic Tiling Engine.
            
        Returns:
        --------
        pred_digit : int (0-9)
        confidences : np.ndarray (10,) Softmax-like probability distribution
        metrics : dict (execution stats, latency, tile counts)
        """
        if img_int8.ndim == 2:
            img_int8 = img_int8[np.newaxis, ...]
            
        self.engine.reset_metrics()
        
        # 1. Transform input image to column patches using im2col
        # Cols shape: [9 x 784]
        cols_int8, _ = im2col_2d(img_int8, kernel_size=3, stride=1, padding=1)
        
        # 2. Conv1 GEMM: [16 x 9] x [9 x 784] -> [16 x 784]
        if use_systolic_tiling:
            conv_out_int8, conv_raw_acc = self.engine.execute_tiled_gemm(
                self.W1_flat,
                cols_int8,
                bias=self.b1_int32,
                shift_bits=self.shift_conv,
                bypass_relu=False # ReLU + Saturation Clamp to [0, 127]
            )
        else:
            acc = np.matmul(self.W1_flat.astype(np.int32), cols_int8.astype(np.int32)) + self.b1_int32[:, np.newaxis]
            relu = np.maximum(0, acc)
            conv_out_int8 = np.clip(np.right_shift(relu, self.shift_conv), 0, 127).astype(np.int8)
            conv_raw_acc = acc
            
        # 3. Reshape and Max-Pooling 2x2
        # (16, 784) -> (1, 16, 28, 28)
        conv_4d = conv_out_int8.reshape(self.num_filters, 1, 28, 28).transpose(1, 0, 2, 3)
        # 2x2 max pool: (1, 16, 14, 2, 14, 2)
        p_in = conv_4d.reshape(1, self.num_filters, 14, 2, 14, 2)
        pool_out = p_in.max(axis=(3, 5)) # (1, 16, 14, 14)
        
        # Flatten for Dense layer: (3136, 1)
        flat_int8 = pool_out.reshape(-1, 1).astype(np.int8)
        
        # 4. FC Layer GEMM: [10 x 3136] x [3136 x 1] -> [10 x 1]
        if use_systolic_tiling:
            fc_out_int8, fc_raw_acc = self.engine.execute_tiled_gemm(
                self.W2_int8,
                flat_int8,
                bias=self.b2_int32,
                shift_bits=self.shift_fc,
                bypass_relu=True # Logits: allow negative values
            )
            logits = fc_raw_acc[:, 0]
        else:
            logits = np.matmul(self.W2_int8.astype(np.int32), flat_int8.astype(np.int32))[:, 0] + self.b2_int32
            
        # 5. Prediction & Confidence
        pred_digit = int(np.argmax(logits))
        
        # Approximate softmax for human-readable confidence
        scaled_logits = (logits - np.max(logits)).astype(np.float64) / 1000.0
        exp_vals = np.exp(np.clip(scaled_logits, -20, 20))
        confidences = exp_vals / np.sum(exp_vals)
        
        metrics = {
            "total_tiles": self.engine.total_tiles_processed,
            "hw_cycles": self.engine.total_hardware_cycles,
            "mac_ops": self.engine.total_mac_operations,
            "conv_acc_shape": conv_raw_acc.shape,
            "logits": logits
        }
        
        return pred_digit, confidences, metrics
