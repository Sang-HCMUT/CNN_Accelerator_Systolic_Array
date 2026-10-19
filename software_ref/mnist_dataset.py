"""
Module: mnist_dataset.py
Fast & Zero-Dependency MNIST Dataset Loader and Visualizer.
Downloads official MNIST dataset from reliable mirrors.
Caches locally in software_ref/data/mnist/.
Parses binary IDX format into NumPy arrays.
Provides terminal ASCII-art visualization for handwritten digits.
"""

import os
import gzip
import struct
import urllib.request
import numpy as np

MNIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "mnist")

URLS = {
    "train_images": "https://ossci-datasets.s3.amazonaws.com/mnist/train-images-idx3-ubyte.gz",
    "train_labels": "https://ossci-datasets.s3.amazonaws.com/mnist/train-labels-idx1-ubyte.gz",
    "test_images":  "https://ossci-datasets.s3.amazonaws.com/mnist/t10k-images-idx3-ubyte.gz",
    "test_labels":  "https://ossci-datasets.s3.amazonaws.com/mnist/t10k-labels-idx1-ubyte.gz",
}

BACKUP_URLS = {
    "train_images": "https://storage.googleapis.com/cvdf-datasets/mnist/train-images-idx3-ubyte.gz",
    "train_labels": "https://storage.googleapis.com/cvdf-datasets/mnist/train-labels-idx1-ubyte.gz",
    "test_images":  "https://storage.googleapis.com/cvdf-datasets/mnist/t10k-images-idx3-ubyte.gz",
    "test_labels":  "https://storage.googleapis.com/cvdf-datasets/mnist/t10k-labels-idx1-ubyte.gz",
}

def download_file(url, backup_url, dest_path):
    if os.path.exists(dest_path):
        return
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    filename = os.path.basename(dest_path)
    print(f"[*] Downloading {filename}...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response, open(dest_path, 'wb') as out_file:
            out_file.write(response.read())
    except Exception as e:
        print(f"[!] Primary URL failed ({e}), trying backup...")
        req = urllib.request.Request(backup_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response, open(dest_path, 'wb') as out_file:
            out_file.write(response.read())
    print(f"[+] Downloaded {filename} ({os.path.getsize(dest_path)} bytes).")

def load_images(filepath):
    with gzip.open(filepath, 'rb') as f:
        magic, num_images, rows, cols = struct.unpack('>IIII', f.read(16))
        assert magic == 2051, f"Invalid magic number {magic} in {filepath}"
        buf = f.read(num_images * rows * cols)
        data = np.frombuffer(buf, dtype=np.uint8).reshape(num_images, 1, rows, cols)
        return data

def load_labels(filepath):
    with gzip.open(filepath, 'rb') as f:
        magic, num_items = struct.unpack('>II', f.read(8))
        assert magic == 2049, f"Invalid magic number {magic} in {filepath}"
        buf = f.read(num_items)
        labels = np.frombuffer(buf, dtype=np.uint8)
        return labels

def get_mnist(test_only=False):
    """
    Returns (X_test, y_test) or (X_train, y_train, X_test, y_test).
    Images are normalized to range [-128, 127] signed INT8 for the accelerator.
    """
    os.makedirs(MNIST_DIR, exist_ok=True)
    
    test_img_path = os.path.join(MNIST_DIR, "t10k-images-idx3-ubyte.gz")
    test_lbl_path = os.path.join(MNIST_DIR, "t10k-labels-idx1-ubyte.gz")
    
    download_file(URLS["test_images"], BACKUP_URLS["test_images"], test_img_path)
    download_file(URLS["test_labels"], BACKUP_URLS["test_labels"], test_lbl_path)
    
    X_test = load_images(test_img_path)
    y_test = load_labels(test_lbl_path)
    
    # Scale from [0, 255] uint8 to [-128, 127] int8 (zero-point centered at 128)
    X_test_int8 = (X_test.astype(np.int16) - 128).astype(np.int8)
    
    if test_only:
        return X_test_int8, y_test
        
    train_img_path = os.path.join(MNIST_DIR, "train-images-idx3-ubyte.gz")
    train_lbl_path = os.path.join(MNIST_DIR, "train-labels-idx1-ubyte.gz")
    
    download_file(URLS["train_images"], BACKUP_URLS["train_images"], train_img_path)
    download_file(URLS["train_labels"], BACKUP_URLS["train_labels"], train_lbl_path)
    
    X_train = load_images(train_img_path)
    y_train = load_labels(train_lbl_path)
    X_train_int8 = (X_train.astype(np.int16) - 128).astype(np.int8)
    
    return X_train_int8, y_train, X_test_int8, y_test

def render_ascii_digit(image_2d, label=None):
    """
    Renders a 28x28 grayscale image as terminal ASCII art.
    """
    # Normalize to 0..255 for display
    if image_2d.dtype == np.int8:
        display_img = (image_2d.astype(np.int16) + 128).astype(np.uint8)
    else:
        display_img = image_2d
        
    chars = " .:-=+*#%@"
    header = f"--- Handwritten Digit: {label} ---" if label is not None else "--- Handwritten Digit ---"
    lines = [header]
    # Downsample spatially by taking 28x28 and printing every row, 2 chars per col for aspect ratio
    for r in range(0, 28, 1):
        line = ""
        for c in range(0, 28, 1):
            val = display_img[r, c]
            char_idx = int(val / 256.0 * len(chars))
            line += chars[min(len(chars)-1, char_idx)] * 2
        lines.append(line)
    lines.append("-" * len(header))
    return "\n".join(lines)


if __name__ == "__main__":
    print("Testing MNIST Loader...")
    X_test, y_test = get_mnist(test_only=True)
    print(f"[+] Loaded {len(X_test)} MNIST test samples. Shape: {X_test.shape}")
    print(f"[*] Showing first 3 test samples:\n")
    for idx in range(3):
        print(render_ascii_digit(X_test[idx, 0], label=y_test[idx]))
        print()
