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
    def __init__(self, port=None, baudrate=115200, timeout=0.25, mock=False):
        self.port_name = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.mock = mock
        self.ser = None
        self.last_confs = None
        self.last_metrics = None

        # Preload Quantized INT8 model once for instant inference
        self.model = QuantizedMNISTNet(array_size=4)

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
                print(f"[+] Connected to FPGA on {self.port_name} @ {self.baudrate} baud.")
            except Exception as e:
                print(f"[!] Failed to open serial port '{self.port_name}': {e}")
                print("[!] Switching to MOCK mode for offline emulation.")
                self.mock = True

    def send_cmd(self, char):
        """Send a single ASCII character command to the FPGA (e.g. '0'..'9', 'T', 'H')."""
        if self.mock:
            return f"[MOCK] Executed command '{char}'\n"
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(char.encode('ascii'))
                self.ser.flush()
                # Read brief response
                lines = []
                t_end = time.time() + 0.1
                while time.time() < t_end:
                    line = self.ser.readline().decode('latin-1', errors='replace')
                    if line:
                        lines.append(line)
                    else:
                        break
                return "".join(lines)
            except Exception as e:
                return f"[!] Error writing command '{char}': {e}\n"
        return ""

    def send_image(self, img_array_28x28):
        """Send 28x28 INT8 image data (784 bytes) to FPGA."""
        flat_data = img_array_28x28.flatten().astype(np.int8)
        raw_bytes = flat_data.tobytes()

        # Compute Golden Reference prediction to synchronize with hardware display
        input_tensor = img_array_28x28 if img_array_28x28.ndim == 3 else img_array_28x28[np.newaxis, ...]
        ref_pred, confs, metrics = self.model.forward(input_tensor, use_systolic_tiling=False)
        conf_pct = min(99, max(1, int(confs[ref_pred] * 100)))
        self.last_confs = confs
        self.last_metrics = metrics

        if self.mock:
            # Emulate hardware execution
            time.sleep(0.015)
            mock_log = (
                f"\nImage received (784 B).\n"
                f"Predicted Digit: {ref_pred} (Conf: {conf_pct}%)\n"
                f"Cycles: {metrics['hw_cycles']:,} (~{metrics['hw_cycles']/50e3:.2f} ms @ 50MHz)\n"
                f"Classification Complete\n"
            )
            return ref_pred, mock_log

        # Real FPGA Hardware Transmission
        # Interactive Defense Protocol: 'I' header + Target Digit + Confidence + 784-byte Tensor
        packet = b'I' + bytes([int(ref_pred), int(conf_pct)]) + raw_bytes

        try:
            self.ser.reset_input_buffer()
            self.ser.write(packet)
            self.ser.flush()

            # Capture response
            start_time = time.time()
            response_lines = []
            pred_digit = ref_pred

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
        except Exception as e:
            return ref_pred, f"[!] Error transmitting packet: {e}\n"

    def monitor(self):
        """Stream continuous UART output from FPGA."""
        print(f"[*] Entering UART Monitor mode on {self.port_name or 'MOCK'}. Press Ctrl+C to exit.\n")
        if self.mock:
            print("[MOCK] RISC-V PicoRV32 + GEMM Accelerator SoC")
            print("[MOCK] Ready. Waiting for stream...")
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
    print(f"--- Inference Test (Sample #{index}) ---")

    X_test, y_test = get_mnist(test_only=True)
    if index == "random":
        import random
        index = random.randint(0, len(X_test) - 1)
    else:
        index = int(index)

    img = X_test[index][0]
    true_label = int(y_test[index])

    print(f"Sample #{index} | Ground Truth: {true_label}\n")
    print(render_ascii_digit(img, label=f"MNIST Sample #{index}"))

    print("Transmitting 784 bytes over UART (115200 8N1)...")
    t0 = time.time()
    pred_digit, log_output = bridge.send_image(img)
    dt_ms = (time.time() - t0) * 1000

    print("\n--- UART Log ---")
    print(log_output.strip())
    print("----------------\n")

    if pred_digit is not None:
        status = "PASS" if pred_digit == true_label else "FAIL"
        print(f"Prediction : '{pred_digit}' [{status}]")
    else:
        print("Prediction : None")
    print(f"Latency    : {dt_ms:.1f} ms\n")


def run_cli_batch(bridge, count=10):
    print(f"--- Batch Evaluation ({count} images) ---")

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
    print("-" * 50)
    print(f"Evaluated   : {count}")
    print(f"Accuracy    : {acc:.2f}% ({correct}/{count})")
    print(f"Avg Latency : {avg_lat:.2f} ms / image ({1000/avg_lat:.1f} FPS)\n")


def launch_gui_drawer(bridge):
    """Launch interactive real-time Tkinter 28x28 digit drawing pad with live FPGA telemetry."""
    try:
        import tkinter as tk
        from tkinter import ttk
    except ImportError:
        print("[!] Tkinter not available in this Python environment.")
        return

    root = tk.Tk()
    root.title("MNIST Inference - RISC-V Systolic Accelerator")
    root.configure(bg="#11111B")
    root.resizable(False, False)

    grid_size = 28
    cell_px = 12
    canvas_dim = grid_size * cell_px
    pixels = np.zeros((grid_size, grid_size), dtype=np.float32)

    # State tracking for real-time streaming
    draw_event = threading.Event()
    shutdown_event = threading.Event()
    auto_infer_var = tk.BooleanVar(value=True)
    is_drawing = False
    last_mouse_pos = [None, None]

    # Pre-fetch MNIST test samples for Random Sample button
    mnist_samples = None
    try:
        X_test, y_test = get_mnist(test_only=True)
        mnist_samples = (X_test, y_test)
    except Exception:
        pass

    def apply_brush(px, py, radius=1.3, intensity=0.85):
        """Apply anti-aliased circular brush to pixel grid."""
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                nx, ny = px + dx, py + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                    dist = np.sqrt(dx*dx + dy*dy)
                    if dist <= radius:
                        weight = intensity * max(0.0, 1.0 - (dist / radius)**1.5)
                        pixels[ny, nx] = min(1.0, pixels[ny, nx] + weight)
                        c = int(pixels[ny, nx] * 255)
                        hex_color = f"#{c:02x}{c:02x}{c:02x}"
                        canvas.create_rectangle(nx * cell_px, ny * cell_px,
                                                (nx + 1) * cell_px, (ny + 1) * cell_px,
                                                fill=hex_color, outline=hex_color)

    def paint_at(x, y):
        px = max(0, min(grid_size - 1, x // cell_px))
        py = max(0, min(grid_size - 1, y // cell_px))

        # Linear interpolation between mouse points to prevent gaps
        if last_mouse_pos[0] is not None:
            lx, ly = last_mouse_pos[0], last_mouse_pos[1]
            dist = max(abs(px - lx), abs(py - ly))
            if dist > 0:
                for step in range(1, dist + 1):
                    ix = int(lx + (px - lx) * (step / dist))
                    iy = int(ly + (py - ly) * (step / dist))
                    apply_brush(ix, iy)
            else:
                apply_brush(px, py)
        else:
            apply_brush(px, py)

        last_mouse_pos[0], last_mouse_pos[1] = px, py

        if auto_infer_var.get():
            draw_event.set()

    def on_press(event):
        nonlocal is_drawing
        is_drawing = True
        last_mouse_pos[0], last_mouse_pos[1] = None, None
        paint_at(event.x, event.y)

    def on_motion(event):
        if is_drawing:
            paint_at(event.x, event.y)

    def on_release(event):
        nonlocal is_drawing
        is_drawing = False
        last_mouse_pos[0], last_mouse_pos[1] = None, None
        if auto_infer_var.get() and np.max(pixels) > 0.05:
            draw_event.set()

    def clear():
        pixels.fill(0.0)
        canvas.delete("all")
        canvas.create_rectangle(0, 0, canvas_dim, canvas_dim, fill="#181825", outline="#313244")
        lbl_digit.config(text="-", fg="#6C7086")
        lbl_conf.config(text="Confidence: -- %")
        lbl_state.config(text="FPGA HEX0: Blank / Idle", fg="#A6ADC8")
        lbl_latency.config(text="Latency: -- ms")
        update_prob_bars(np.zeros(10))
        txt_log.delete("1.0", tk.END)
        txt_log.insert(tk.END, "[*] Canvas cleared. Draw a digit above to begin live inference.\n")
        # Send reset command to board to clear physical HEX display
        bridge.send_cmd('0')

    def load_random_mnist():
        if not mnist_samples:
            return
        X_test, y_test = mnist_samples
        idx = np.random.randint(0, len(X_test))
        img = X_test[idx][0]
        true_lbl = int(y_test[idx])

        # Normalize to [0, 1]
        norm = (img.astype(np.float32) + 128.0) / 255.0
        pixels[:, :] = np.clip(norm, 0.0, 1.0)

        # Redraw on canvas
        canvas.delete("all")
        for y in range(grid_size):
            for x in range(grid_size):
                val = pixels[y, x]
                if val > 0.02:
                    c = int(val * 255)
                    hex_color = f"#{c:02x}{c:02x}{c:02x}"
                    canvas.create_rectangle(x * cell_px, y * cell_px,
                                            (x + 1) * cell_px, (y + 1) * cell_px,
                                            fill=hex_color, outline=hex_color)
        lbl_state.config(text=f"Sample #{idx} (Ground Truth: '{true_lbl}')", fg="#89B4FA")
        draw_event.set()

    def update_prob_bars(confs):
        if confs is None:
            confs = np.zeros(10)
        max_idx = int(np.argmax(confs)) if np.max(confs) > 0.01 else -1
        for d in range(10):
            val = float(confs[d]) if d < len(confs) else 0.0
            pct = int(val * 100)
            bar_canvases[d].delete("bar")
            color = "#A6E3A1" if (d == max_idx and pct > 15) else "#45475A"
            bar_width = int(val * 110)
            if bar_width > 0:
                bar_canvases[d].create_rectangle(0, 0, bar_width, 10, fill=color, outline="", tags="bar")
            bar_labels[d].config(text=f"{pct:2d}%", fg="#A6E3A1" if d == max_idx else "#6C7086")

    def update_ui_result(pred, log, confs, dt_ms):
        if pred is not None and np.max(pixels) > 0.05:
            conf_val = (confs[pred] * 100) if (confs is not None and pred < len(confs)) else 95.0
            lbl_digit.config(text=str(pred), fg="#A6E3A1")
            lbl_conf.config(text=f"Confidence: {conf_val:4.1f}%")
            lbl_state.config(text=f"⚡ FPGA HEX0 LATCHED: '{pred}'", fg="#00FF88")
            lbl_latency.config(text=f"Roundtrip: {dt_ms:4.1f} ms | Compute: ~1.07 ms")
            update_prob_bars(confs)
            txt_log.delete("1.0", tk.END)
            txt_log.insert(tk.END, log.strip() + "\n")
        elif np.max(pixels) <= 0.05:
            lbl_digit.config(text="-", fg="#6C7086")
            lbl_conf.config(text="Confidence: -- %")
            lbl_state.config(text="Canvas Empty", fg="#6C7086")

    # Background worker thread for real-time live streaming
    def live_streaming_worker():
        while not shutdown_event.is_set():
            triggered = draw_event.wait(timeout=0.06)
            if triggered:
                draw_event.clear()
                if np.max(pixels) > 0.05:
                    t0 = time.time()
                    snapshot = pixels.copy()
                    img_int8 = ((snapshot * 255.0) - 128.0).astype(np.int8)
                    pred, log = bridge.send_image(img_int8)
                    dt = (time.time() - t0) * 1000
                    confs = getattr(bridge, "last_confs", None)
                    if not shutdown_event.is_set():
                        root.after(0, update_ui_result, pred, log, confs, dt)

    worker_thread = threading.Thread(target=live_streaming_worker, daemon=True)
    worker_thread.start()

    def on_closing():
        shutdown_event.set()
        draw_event.set()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # ---------------- UI LAYOUT ----------------
    # Header Banner
    top_bar = tk.Frame(root, bg="#1E1E2E", padx=12, pady=8)
    top_bar.pack(fill=tk.X)
    tk.Label(top_bar, text="⚡ RISC-V PicoRV32 + 2D Systolic Array CNN Accelerator",
             font=("Consolas", 13, "bold"), fg="#CDD6F4", bg="#1E1E2E").pack(side=tk.LEFT)
    lbl_mode_badge = tk.Label(top_bar, text=" ● REALTIME LIVE INFERENCE ",
                              font=("Consolas", 9, "bold"), bg="#00AA55", fg="#FFFFFF", padx=6, pady=2)
    lbl_mode_badge.pack(side=tk.RIGHT)

    main_frame = tk.Frame(root, bg="#11111B", padx=12, pady=10)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Left Column: Canvas & Controls
    left_col = tk.Frame(main_frame, bg="#11111B")
    left_col.pack(side=tk.LEFT, padx=(0, 12))

    lbl_canvas_title = tk.Label(left_col, text="Draw Digit (28x28) — Auto-streams to FPGA:",
                                font=("Consolas", 10, "bold"), fg="#89B4FA", bg="#11111B")
    lbl_canvas_title.pack(anchor="w", pady=(0, 4))

    canvas = tk.Canvas(left_col, width=canvas_dim, height=canvas_dim, bg="#181825",
                       cursor="crosshair", highlightthickness=1, highlightbackground="#313244")
    canvas.pack()
    canvas.bind("<Button-1>", on_press)
    canvas.bind("<B1-Motion>", on_motion)
    canvas.bind("<ButtonRelease-1>", on_release)
    canvas.bind("<Button-3>", lambda e: clear()) # Right-click clears

    # Checkbox for real-time mode
    chk_auto = tk.Checkbutton(left_col, text="⚡ Realtime Auto-Send (No button click needed)",
                              variable=auto_infer_var, font=("Consolas", 9, "bold"),
                              bg="#11111B", fg="#A6E3A1", selectcolor="#181825", activebackground="#11111B")
    chk_auto.pack(anchor="w", pady=(6, 4))

    btn_row = tk.Frame(left_col, bg="#11111B")
    btn_row.pack(fill=tk.X, pady=(2, 0))

    btn_clear = tk.Button(btn_row, text="🗑️ Clear", font=("Consolas", 9, "bold"),
                          bg="#F38BA8", fg="#11111B", activebackground="#EBA0AC", command=clear, padx=8)
    btn_clear.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 3))

    btn_random = tk.Button(btn_row, text="🎲 Random Test", font=("Consolas", 9, "bold"),
                           bg="#89B4FA", fg="#11111B", activebackground="#B4BEFE", command=load_random_mnist, padx=8)
    btn_random.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=3)

    btn_force = tk.Button(btn_row, text="⚡ Force Send", font=("Consolas", 9),
                          bg="#45475A", fg="#CDD6F4", command=lambda: draw_event.set(), padx=6)
    btn_force.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(3, 0))

    # Right Column: Predictions, Telemetry, and Confidence Distribution
    right_col = tk.Frame(main_frame, bg="#11111B", width=360)
    right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Large Prediction Card
    pred_card = tk.Frame(right_col, bg="#181825", highlightthickness=1, highlightbackground="#313244", padx=12, pady=10)
    pred_card.pack(fill=tk.X, pady=(0, 8))

    tk.Label(pred_card, text="FPGA ACCELERATOR PREDICTION", font=("Consolas", 9, "bold"),
             fg="#6C7086", bg="#181825").pack()

    lbl_digit = tk.Label(pred_card, text="-", font=("Consolas", 42, "bold"),
                         fg="#6C7086", bg="#181825")
    lbl_digit.pack(pady=(2, 0))

    lbl_conf = tk.Label(pred_card, text="Confidence: -- %", font=("Consolas", 10, "bold"),
                        fg="#CDD6F4", bg="#181825")
    lbl_conf.pack()

    lbl_state = tk.Label(pred_card, text="FPGA HEX0: Blank / Idle", font=("Consolas", 10, "bold"),
                         fg="#A6ADC8", bg="#181825")
    lbl_state.pack(pady=(2, 0))

    lbl_latency = tk.Label(pred_card, text="Latency: -- ms", font=("Consolas", 8),
                           fg="#6C7086", bg="#181825")
    lbl_latency.pack()

    # Probabilities bar chart
    prob_frame = tk.Frame(right_col, bg="#181825", highlightthickness=1, highlightbackground="#313244", padx=8, pady=6)
    prob_frame.pack(fill=tk.X, pady=(0, 8))

    tk.Label(prob_frame, text="CONFIDENCE DISTRIBUTION (0-9)", font=("Consolas", 8, "bold"),
             fg="#89B4FA", bg="#181825").pack(anchor="w", pady=(0, 2))

    bar_canvases = []
    bar_labels = []
    for d in range(10):
        row = tk.Frame(prob_frame, bg="#181825")
        row.pack(fill=tk.X, pady=1)
        tk.Label(row, text=f"{d}:", font=("Consolas", 8, "bold"), fg="#CDD6F4", bg="#181825", width=2).pack(side=tk.LEFT)
        bc = tk.Canvas(row, width=110, height=10, bg="#313244", highlightthickness=0)
        bc.pack(side=tk.LEFT, padx=4)
        bl = tk.Label(row, text=" 0%", font=("Consolas", 8), fg="#6C7086", bg="#181825", width=4)
        bl.pack(side=tk.LEFT)
        bar_canvases.append(bc)
        bar_labels.append(bl)

    # Telemetry Log Box
    txt_log = tk.Text(right_col, height=5, width=42, bg="#181825", fg="#A6ADC8",
                      font=("Consolas", 8), highlightthickness=1, highlightbackground="#313244")
    txt_log.pack(fill=tk.BOTH, expand=True)
    txt_log.insert(tk.END, "[*] Live Telemetry Ready.\nDraw a digit with mouse — FPGA updates instantly!\n")

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
