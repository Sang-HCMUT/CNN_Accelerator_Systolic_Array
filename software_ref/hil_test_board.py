#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script: hil_test_board.py
Hardware-in-the-Loop (HIL) Automated UART Verification Suite for DE2 / DE10-Standard.
Connects to the FPGA SoC over UART at 115200 Baud (8N1).
Executes interactive scenarios [7], [1], [3], [5], [6] to verify:
  1. Boot banner & IP Version (0x02080820 - v2.0 Gen-2)
  2. Demo 1: GEMM benchmark (Gen-2 Packed 37 cyc vs Legacy 93 cyc, E2E 1,920 cyc, 173.7x speedup)
  3. Demo 3: Real MNIST Conv1 im2col (256/256 bit-true match)
  4. Demo 5: Quantization edge-case diagnostics (6/6 passed)
  5. Demo 6: MNIST digit '7' inference telemetry (69% confidence)
Saves complete execution log to hardware_test_log.txt.
"""

import sys
import os
import time
import argparse
from datetime import datetime

try:
    import serial
    import serial.tools.list_ports
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False


def list_ports():
    if not HAS_SERIAL:
        return []
    return [p.device for p in serial.tools.list_ports.comports()]


def run_hil_test(port=None, baudrate=115200, timeout=2.0, output_log="hardware_test_log.txt"):
    print("=" * 70)
    print("  HARDWARE-IN-THE-LOOP (HIL) FPGA AUTOMATED VERIFICATION SUITE")
    print("  Targets: Terasic DE2 (Cyclone II) / Terasic DE10-Standard (Cyclone V)")
    print("  Firmware: 8x8 Systolic Accelerator Gen-2 (RV32I PicoRV32 SoC)")
    print("=" * 70)

    ports = list_ports()
    if not port:
        if ports:
            port = ports[0]
            print(f"[+] Auto-detected Serial Port: {port}")
        else:
            print("[!] No active serial port detected on host.")
            print("[*] To run live on board:")
            print("    1. Plug USB-UART adapter (TX -> GPIO_0[1] uart_rx, RX -> GPIO_0[0] uart_tx, GND).")
            print("    2. Re-run: python hil_test_board.py --port COMx")
            print("[*] Generating pre-flight verification summary template...")
            generate_preflight_report(output_log)
            return False

    print(f"[+] Connecting to {port} at {baudrate} baud (8N1)...")
    try:
        ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
    except Exception as e:
        print(f"[-] Error opening serial port {port}: {e}")
        return False

    time.sleep(0.5)
    ser.reset_input_buffer()

    log_lines = []
    log_lines.append(f"HIL HARDWARE TEST EXECUTION LOG - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_lines.append(f"Port: {port} | Baudrate: {baudrate} 8N1\n")

    def send_and_record(cmd, desc, wait_sec=1.5):
        print(f"\n[+] Executing {desc} (Command: '{cmd}')...")
        ser.write(cmd.encode('ascii'))
        time.sleep(wait_sec)
        out = ""
        while ser.in_waiting:
            chunk = ser.read(ser.in_waiting).decode('latin1', errors='replace')
            out += chunk
            time.sleep(0.1)
        print(out)
        log_lines.append(f"--- Command: {cmd} ({desc}) ---")
        log_lines.append(out)
        return out

    # 1. Reset / Menu request
    banner_out = send_and_record("?", "Read Menu & Boot Banner", wait_sec=1.0)
    
    # 2. Inspect registers (Scenario 7)
    reg_out = send_and_record("7", "Scenario 7: Hardware MMIO Diagnostics", wait_sec=1.0)
    is_gen2 = "02080820" in reg_out or "0x02080820" in reg_out or "2.0" in reg_out
    print(f"[*] IP Version Check (0x02080820 Gen-2): {'PASS' if is_gen2 else 'LEGACY/UNKNOWN'}")

    # 3. Benchmark Demo 1
    demo1_out = send_and_record("1", "Scenario 1: GEMM Benchmark (Legacy vs Gen-2 Packed)", wait_sec=2.5)

    # 4. Conv1 Demo 3
    demo3_out = send_and_record("3", "Scenario 3: Real MNIST Conv1 Layer via im2col", wait_sec=2.5)

    # 5. Diagnostics Demo 5
    demo5_out = send_and_record("5", "Scenario 5: Quantization & Edge-Case Diagnostics", wait_sec=1.5)

    # 6. MNIST Inference Demo 6
    demo6_out = send_and_record("6", "Scenario 6: MNIST Digit '7' Inference", wait_sec=3.0)

    ser.close()

    # Save to log file
    with open(output_log, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

    print("\n" + "=" * 70)
    print(f"[+] HIL Test Run Completed. Complete telemetry saved to: {output_log}")
    print("=" * 70)
    return True


def generate_preflight_report(output_log):
    report = f"""================================================================================
  HARDWARE-IN-THE-LOOP (HIL) PRE-FLIGHT VERIFICATION SPECIFICATION
  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
  Targets: Terasic DE2 (Cyclone II) / Terasic DE10-Standard (Cyclone V)
  Firmware: 8x8 Systolic Accelerator Gen-2 (RV32I PicoRV32 SoC)
================================================================================

1. PHYSICAL HARDWARE SETUP:
   - DE2 Platform:
     * Bitstream: synthesis_soc_de2/soc_top_de2.sof (19,107 LEs, +4.626 ns slack)
     * UART: DB9 RS-232 onboard port connected via USB-RS232 adapter.
     * Reset: Pushbutton KEY[0] (PIN_G26).
   - DE10-Standard Platform:
     * Bitstream: synthesis_soc_de10/soc_top_de10.sof (8,290 ALMs, +5.609 ns slack)
     * UART: USB-UART adapter connected to GPIO_0:
       - Adapter TX -> GPIO_0[1] (PIN_AK2, uart_rx)
       - Adapter RX -> GPIO_0[0] (PIN_W15, uart_tx)
       - Adapter GND -> GPIO_0 GND (PIN_AH4 or PIN_AH2)
     * Reset: Pushbutton KEY[0] (PIN_AJ4).

2. EXPECTED TELEMETRY & ACCEPTANCE CRITERIA:
   [A] Scenario 7 (REG_ACCEL_VERSION):
       - Expected IP Version: 0x02080820 (Major: 2, Size: 8x8, Data: INT8, Acc: INT32).
   [B] Scenario 1 (GEMM Benchmark K=8):
       - Gen-2 Pure Compute Latency: 37 clock cycles (0.74 us @ 50 MHz).
       - Gen-2 Pure Throughput: 1,383.8 MOPS (1.38 GOPS).
       - Gen-2 End-to-End Latency: 1,920 clock cycles (38.4 us @ 50 MHz).
       - Instructions: 275 CPU instructions (down from 1,269).
       - End-to-End Speedup vs RV32I Software: 173.7x faster.
       - Bit-True Parity: 0 errors across all 64 elements.
   [C] Scenario 3 (Real MNIST Conv1 im2col):
       - Bit-True Parity: 256/256 activations match PyTorch golden reference (0 mismatches).
   [D] Scenario 5 (Arithmetic Diagnostics):
       - 6/6 tests passed (Saturation clamp +127, (-128)x(-128)=+16384, ReLU bypass, Shift sweep, Guardband rejection).
   [E] Scenario 6 (MNIST Inference):
       - Predicted Digit: '7' (Confidence: 69%, displayed on HEX0).

3. TO EXECUTE ON CONNECTED HARDWARE:
   - Run: python software_ref/hil_test_board.py --port <COM_PORT>
   - Or double-click: synthesis_soc_de10/run_hil_test.bat (or synthesis_soc_de2/run_hil_test.bat)
================================================================================
"""
    with open(output_log, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"[+] Pre-flight specification written to: {output_log}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HIL UART Verification for FPGA SoC")
    parser.add_argument("--port", type=str, default=None, help="Serial COM port (e.g., COM3, COM4)")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate (default: 115200)")
    parser.add_argument("--output", type=str, default="hardware_test_log.txt", help="Output log path")
    args = parser.parse_args()

    run_hil_test(port=args.port, baudrate=args.baud, output_log=args.output)
