#!/usr/bin/env python3
"""
===============================================================================
Script: uart_bridge.py
Description: Host PC to Terasic DE1 FPGA Communication Bridge for MNIST Inference.
             - Connects via RS-232 / USB-to-UART at 115200 Baud (8N1).
             - Streams 28x28 INT8 MNIST image tensors to the PicoRV32 SoC.
             - Captures UART TX console logs and hardware performance telemetry.
             - Includes interactive GUI Digit Drawer (Tkinter) and batch evaluation.
===============================================================================
"""

import os
import sys
import time
import argparse
import threading
import numpy as np

# Ensure software_ref directory is in Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

try:
    import serial
    import serial.tools.list_ports
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False

from mnist_dataset import get_mnist, render_ascii_digit
from mnist_cnn_model import QuantizedMNISTNet


def list_serial_ports():
    """List all available COM/TTY ports."""
    if not HAS_SERIAL:
        return []
    ports = serial.tools.list_ports.comports()
    return [(p.device, p.description) for p in ports]


class FPGAUartBridge:
    def __init__(self, port=None, baudrate=115200, timeout=2.0, mock=False):
        self.port_name = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.mock = mock
        self.ser = None

        if not self.mock and HAS_SERIAL:
            if not self.port_name:
                available = list_serial_ports()
                if available:
                    self.port_name = available[0][0]
                    print(f"[*] Auto-detected serial port: {self.port_name} ({available[0][1]})")
                else:
                    print("[!] No active COM ports detected. Falling back to MOCK mode.")
                    self.mock = True

        if not self.mock and HAS_SERIAL:
            try:
                self.ser = serial.Serial(self.port_name, baudrate=self.baudrate, timeout=self.timeout)
                print(f"[+] Connected to DE1 FPGA on {self.port_name} @ {self.baudrate} baud.")
            except Exception as e:
                print(f"[!] Failed to open serial port '{self.port_name}': {e}")
                print("[!] Switching to MOCK mode for offline emulation.")
                self.mock = True

    def send_image(self, img_array_28x28):
        """Send 28x28 INT8 image data (784 bytes) to FPGA."""
        flat_data = img_array_28x28.flatten().astype(np.int8)
        raw_bytes = flat_data.tobytes()

        if self.mock:
            # Emulate software reference execution
            time.sleep(0.05)
            model = QuantizedMNISTNet(array_size=4)
            pred_digit, confs, metrics = model.forward(img_array_28x28[np.newaxis, ...], use_systolic_tiling=True)
            mock_log = (
                f"\n[DE1 MOCK] Image Received: 784 bytes.\n"
                f"[DE1 MOCK] Triggering Systolic Array GEMM Pipeline...\n"
                f"[DE1 MOCK] Layer 1 CONV: 49 tiles, cycles: 28,420\n"
                f"[DE1 MOCK] Layer 2 DENSE: 64 tiles, cycles: 36,864\n"
                f"[DE1 MOCK] Predicted Digit: {pred_digit} (Confidence: {confs[pred_digit]*100:.1f}%)\n"
                f"[DE1 MOCK] Execution cycles: {metrics['hw_cycles']:,} (~{metrics['hw_cycles']/50e3:.2f} ms @ 50MHz)\n"
            )
            return pred_digit, mock_log

        # Real FPGA Hardware Transmission
        self.ser.reset_input_buffer()
        self.ser.write(raw_bytes)
        self.ser.flush()

        # Capture response
        start_time = time.time()
        response_lines = []
        pred_digit = None

        while (time.time() - start_time) < self.timeout:
            line = self.ser.readline().decode('latin-1', errors='replace')
            if line:
                response_lines.append(line)
                if "Predicted Digit:" in line:
                    try:
                        pred_digit = int(line.split("Predicted Digit:")[1].split()[0])
                    except Exception:
                        pass
                if "Hardware-Software Co-Simulation SUCCESS" in line or "Classification Complete" in line:
                    break

        full_log = "".join(response_lines)
        return pred_digit, full_log

    def monitor(self):
        """Stream continuous UART output from FPGA."""
        print(f"[*] Entering UART Monitor mode on {self.port_name or 'MOCK'}. Press Ctrl+C to exit.\n")
        if self.mock:
            print("[DE1 MOCK] === RISC-V PicoRV32 + CNN Accelerator SoC ===")
            print("[DE1 MOCK] Hardware ready. Waiting for input stream...")
            while True:
                time.sleep(1)
        else:
            try:
                while True:
                    if self.ser.in_waiting > 0:
                        char = self.ser.read(self.ser.in_waiting).decode('latin-1', errors='replace')
                        sys.stdout.write(char)
                        sys.stdout.flush()
                    time.sleep(0.01)
            except KeyboardInterrupt:
                print("\n[*] Exited Monitor mode.")

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()


def run_cli_test_single(bridge, index=42):
    print("=" * 65)
    print("   TERASIC DE1 FPGA UART HARDWARE INFERENCE DEMO")
    print("=" * 65)

    X_test, y_test = get_mnist(test_only=True)
    if index == "random":
        import random
        index = random.randint(0, len(X_test) - 1)
    else:
        index = int(index)

    img = X_test[index][0]
    true_label = int(y_test[index])

    print(f"\n[*] Sample #{index} | Ground Truth Label: {true_label}\n")
    print(render_ascii_digit(img, label=f"MNIST Test Image #{index}"))

    print("[*] Streaming 784 bytes over UART (115200 Baud, 8N1)...")
    t0 = time.time()
    pred_digit, log_output = bridge.send_image(img)
    dt_ms = (time.time() - t0) * 1000

    print("\n--- [FPGA UART CONSOLE OUTPUT] ---")
    print(log_output.strip())
    print("----------------------------------\n")

    if pred_digit is not None:
        status = "CORRECT" if pred_digit == true_label else "MISMATCH"
        print(f"[RESULT] Predicted Digit : '{pred_digit}' ({status})")
    else:
        print(f"[RESULT] Prediction completed (Raw log captured).")
    print(f"[BENCHMARK] Total Roundtrip Latency: {dt_ms:.1f} ms\n")


def run_cli_batch(bridge, count=10):
    print("=" * 65)
    print(f"   TERASIC DE1 FPGA BATCH EVALUATION ({count} IMAGES)")
    print("=" * 65)

    X_test, y_test = get_mnist(test_only=True)
    count = min(count, len(X_test))

    correct = 0
    latencies = []

    for i in range(count):
        img = X_test[i][0]
        lbl = int(y_test[i])

        t0 = time.time()
        pred, _ = bridge.send_image(img)
        dt = (time.time() - t0) * 1000
        latencies.append(dt)

        is_corr = (pred == lbl)
        if is_corr:
            correct += 1
        mark = "OK" if is_corr else "ERR"
        print(f"[{i+1:02d}/{count:02d}] True: {lbl} | Pred: {pred} | Latency: {dt:5.1f} ms | [{mark}]")

    acc = (correct / count) * 100
    avg_lat = np.mean(latencies)
    print("-" * 65)
    print(f"Total Evaluated : {count}")
    print(f"FPGA Accuracy   : {acc:.2f}% ({correct}/{count})")
    print(f"Average Latency : {avg_lat:.2f} ms / image ({1000/avg_lat:.1f} FPS)")
    print("=" * 65 + "\n")


def launch_gui_drawer(bridge):
    """Launch interactive Tkinter 28x28 digit drawing pad."""
    try:
        import tkinter as tk
        from tkinter import messagebox
    except ImportError:
        print("[!] Tkinter not available in this Python environment.")
        return

    root = tk.Tk()
    root.title("Terasic DE1 - AI Digit Recognition GUI")
    root.resizable(False, False)

    grid_size = 28
    cell_px = 12
    canvas_dim = grid_size * cell_px
    pixels = np.zeros((grid_size, grid_size), dtype=np.float32)

    def paint(event):
        x, y = event.x // cell_px, event.y // cell_px
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nx, ny = x + dx, y + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                    weight = 1.0 if (dx == 0 and dy == 0) else 0.5
                    pixels[ny, nx] = min(1.0, pixels[ny, nx] + weight)
                    intensity = int(pixels[ny, nx] * 255)
                    hex_color = f"#{intensity:02x}{intensity:02x}{intensity:02x}"
                    canvas.create_rectangle(nx * cell_px, ny * cell_px,
                                            (nx + 1) * cell_px, (ny + 1) * cell_px,
                                            fill=hex_color, outline=hex_color)

    def clear():
        pixels.fill(0.0)
        canvas.delete("all")
        canvas.create_rectangle(0, 0, canvas_dim, canvas_dim, fill="black")
        lbl_result.config(text="Prediction: - | Confidence: -")

    def send_to_fpga():
        # Scale to [-128, 127] INT8
        img_int8 = ((pixels * 255.0) - 128.0).astype(np.int8)
        pred, log = bridge.send_image(img_int8)
        if pred is not None:
            lbl_result.config(text=f"Predicted Digit: {pred} | DE1 HEX0 Output: '{pred}'", fg="#00FF66")
        else:
            lbl_result.config(text="Executed | Check DE1 HEX0 / Terminal", fg="#FFCC00")
        txt_log.delete("1.0", tk.END)
        txt_log.insert(tk.END, log)

    header = tk.Label(root, text="Terasic DE1 FPGA - Live AI Digit Recognition", font=("Consolas", 14, "bold"), bg="#1E1E2E", fg="#FFFFFF")
    header.pack(fill=tk.X, padx=10, pady=5)

    canvas = tk.Canvas(root, width=canvas_dim, height=canvas_dim, bg="black", cursor="crosshair")
    canvas.pack(padx=10, pady=5)
    canvas.bind("<B1-Motion>", paint)
    canvas.bind("<Button-1>", paint)

    btn_frame = tk.Frame(root)
    btn_frame.pack(fill=tk.X, padx=10, pady=5)

    btn_send = tk.Button(btn_frame, text="⚡ Send to DE1 FPGA", font=("Consolas", 11, "bold"), bg="#007ACC", fg="white", command=send_to_fpga)
    btn_send.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

    btn_clear = tk.Button(btn_frame, text="🗑️ Clear", font=("Consolas", 11), bg="#D9534F", fg="white", command=clear)
    btn_clear.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=2)

    lbl_result = tk.Label(root, text="Prediction: - | Confidence: -", font=("Consolas", 12, "bold"), fg="#00CCFF", bg="#1E1E2E")
    lbl_result.pack(fill=tk.X, padx=10, pady=5)

    txt_log = tk.Text(root, height=8, width=50, bg="#11111B", fg="#A6ADC8", font=("Consolas", 9))
    txt_log.pack(padx=10, pady=5)
    txt_log.insert(tk.END, "[*] Ready. Draw a digit above with mouse and click 'Send to DE1 FPGA'.\n")

    root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="Terasic DE1 FPGA UART Inference Bridge")
    parser.add_argument("--port", type=str, default=None, help="COM Port name (e.g. COM3 or /dev/ttyUSB0)")
    parser.add_argument("--baud", type=int, default=115200, help="Baudrate (default 115200)")
    parser.add_argument("--mode", type=str, choices=["test_single", "batch", "monitor", "gui", "list_ports"],
                        default="test_single", help="Operation mode")
    parser.add_argument("--index", type=str, default="42", help="Image index for test_single ('random' or int)")
    parser.add_argument("--count", type=int, default=10, help="Batch evaluation count")
    parser.add_argument("--mock", action="store_true", help="Run in mock emulation mode (no physical FPGA needed)")

    args = parser.parse_args()

    if args.mode == "list_ports":
        ports = list_serial_ports()
        print("\nAvailable Serial Ports:")
        if ports:
            for p, d in ports:
                print(f"  - {p}: {d}")
        else:
            print("  (None found)")
        print()
        return

    bridge = FPGAUartBridge(port=args.port, baudrate=args.baud, mock=args.mock)

    try:
        if args.mode == "test_single":
            run_cli_test_single(bridge, index=args.index)
        elif args.mode == "batch":
            run_cli_batch(bridge, count=args.count)
        elif args.mode == "monitor":
            bridge.monitor()
        elif args.mode == "gui":
            launch_gui_drawer(bridge)
    finally:
        bridge.close()


if __name__ == "__main__":
    main()
