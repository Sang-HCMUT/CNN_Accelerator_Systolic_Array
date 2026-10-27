#!/usr/bin/env python3
"""
Multi-Seed UVM Regression Suite for Systolic GEMM Accelerator.
Executes randomized verification iterations across multiple random seeds,
aggregates cumulative functional coverage across all seeds, verifies
protocol/temporal SVA assertions, and generates reproducible failure scripts.
"""

import os
import sys
import time
import argparse
import subprocess
from pathlib import Path

# Ensure UTF-8 output on Windows terminal
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

VSIM_EXE = r"C:\13.0sp1\modelsim_ase\win32aloem\vsim.exe"
UVM_DIR  = Path(__file__).resolve().parent
FAIL_DIR = UVM_DIR / "regression_failures"


def parse_args():
    parser = argparse.ArgumentParser(description="Multi-Seed GEMM UVM Regression Runner")
    parser.add_argument("--test", default="gemm_random_test", help="UVM test name (default: gemm_random_test)")
    parser.add_argument("--seeds", type=int, default=10, help="Number of random seeds to execute (default: 10)")
    parser.add_argument("--start-seed", type=int, default=1001, help="Starting seed integer (default: 1001)")
    parser.add_argument("--array-size", type=int, default=4, choices=[4, 8], help="Systolic array size (4 or 8)")
    return parser.parse_args()


def run_single_seed(seed, test_name, array_size):
    start_time = time.time()
    tcl_cmd = f"set UVM_TEST {test_name}; set SEED_VAL {seed}; set ARRAY_SIZE {array_size}; do run_uvm.do"
    cmd = [VSIM_EXE, "-c", "-do", tcl_cmd]

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(UVM_DIR),
            capture_output=True,
            text=True,
            timeout=120
        )
        elapsed = time.time() - start_time
        output = proc.stdout

        # Analyze verification criteria
        passed_scoreboard = ("Status: PASSED" in output) and ("Failed: 0" in output)
        zero_uvm_errors   = ("UVM_ERROR :    0" in output) or ("UVM_ERROR : 0" in output)
        no_sva_violations = ("[SVA" not in output or "Error" not in output)

        is_success = passed_scoreboard and zero_uvm_errors and no_sva_violations

        # Extract transaction and coverage summary
        total_tx = "?"
        cov_score = "?"
        bins_a = set()
        bins_b = set()
        bins_relu = set()
        bins_shift = set()
        bins_clamp = set()
        bins_k = set()

        for line in output.splitlines():
            if "Total:" in line and "Passed:" in line:
                total_tx = line.strip().split("|")[0].replace("UVM_INFO", "").strip()
            if "TOTAL COVERAGE SCORE" in line:
                cov_score = line.split(":")[-1].strip()
            if "BINS_A:" in line:
                vals = line.split("BINS_A:")[-1].strip().split(",")
                for idx, v in enumerate(vals):
                    if v == "1": bins_a.add(idx)
            if "BINS_B:" in line:
                vals = line.split("BINS_B:")[-1].strip().split(",")
                for idx, v in enumerate(vals):
                    if v == "1": bins_b.add(idx)
            if "BINS_RELU:" in line:
                vals = line.split("BINS_RELU:")[-1].strip().split(",")
                for idx, v in enumerate(vals):
                    if v == "1": bins_relu.add(idx)
            if "BINS_SHIFT:" in line:
                vals = line.split("BINS_SHIFT:")[-1].strip().split(",")
                for idx, v in enumerate(vals):
                    if v == "1": bins_shift.add(idx)
            if "BINS_CLAMP:" in line:
                vals = line.split("BINS_CLAMP:")[-1].strip().split(",")
                for idx, v in enumerate(vals):
                    if v == "1": bins_clamp.add(idx)
            if "BINS_K:" in line:
                vals = line.split("BINS_K:")[-1].strip().split(",")
                for idx, v in enumerate(vals):
                    if v == "1": bins_k.add(idx + 1)

        sva_bypassed = ("vsim-8311" in output)

        return {
            "seed": seed,
            "success": is_success,
            "elapsed": elapsed,
            "total_tx": total_tx,
            "cov_score": cov_score,
            "sva_bypassed": sva_bypassed,
            "bins_a": bins_a,
            "bins_b": bins_b,
            "bins_relu": bins_relu,
            "bins_shift": bins_shift,
            "bins_clamp": bins_clamp,
            "bins_k": bins_k,
            "log": output
        }

    except subprocess.TimeoutExpired:
        return {
            "seed": seed,
            "success": False,
            "elapsed": 120.0,
            "total_tx": "TIMEOUT",
            "cov_score": "N/A",
            "bins_a": set(),
            "bins_b": set(),
            "bins_relu": set(),
            "bins_shift": set(),
            "bins_clamp": set(),
            "bins_k": set(),
            "log": "ERROR: Simulation timed out after 120 seconds!"
        }


def main():
    args = parse_args()

    print("==================================================================")
    print("      SYSTOLIC GEMM UVM MULTI-SEED REGRESSION TEST SUITE        ")
    print("==================================================================")
    print(f"Target Accelerator Core : {args.array_size}x{args.array_size} Systolic Mesh")
    print(f"UVM Test Selected       : {args.test}")
    print(f"Number of Seeds         : {args.seeds}")
    print(f"Starting Seed           : {args.start_seed}")
    print("==================================================================")

    results = []
    pass_cnt = 0
    fail_cnt = 0

    # Sets for Cumulative Coverage across all seeds
    cum_a     = set()
    cum_b     = set()
    cum_relu  = set()
    cum_shift = set()
    cum_clamp = set()
    cum_k     = set()

    FAIL_DIR.mkdir(exist_ok=True)

    for i in range(args.seeds):
        seed = args.start_seed + i
        print(f"[{i+1:02d}/{args.seeds:02d}] Executing Seed {seed:05d} ... ", end="", flush=True)

        res = run_single_seed(seed, args.test, args.array_size)
        results.append(res)

        # Merge coverage
        cum_a.update(res.get("bins_a", set()))
        cum_b.update(res.get("bins_b", set()))
        cum_relu.update(res.get("bins_relu", set()))
        cum_shift.update(res.get("bins_shift", set()))
        cum_clamp.update(res.get("bins_clamp", set()))
        cum_k.update(res.get("bins_k", set()))

        if res["success"]:
            pass_cnt += 1
            print(f"[PASSED] ({res['elapsed']:.1f}s) | Cov: {res['cov_score']}")
        else:
            fail_cnt += 1
            print(f"[FAILED] ({res['elapsed']:.1f}s) - Failure logged!")

            # Save failing log
            log_path = FAIL_DIR / f"failure_seed_{seed}.log"
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(res["log"])

            # Save standalone reproducer batch script
            reproduce_bat = FAIL_DIR / f"reproduce_seed_{seed}.bat"
            with open(reproduce_bat, "w", encoding="utf-8") as f:
                f.write(f'@echo off\n')
                f.write(f'cd /d "{UVM_DIR}"\n')
                f.write(f'"{VSIM_EXE}" -c -do "set UVM_TEST {args.test}; set SEED_VAL {seed}; set ARRAY_SIZE {args.array_size}; do run_uvm.do"\n')
                f.write(f'pause\n')

    print("\n==================================================================")
    print("                    REGRESSION SUMMARY REPORT                     ")
    print("==================================================================")
    pass_rate = (pass_cnt / args.seeds) * 100.0
    print(f"Total Seeds Run      : {args.seeds}")
    print(f"Passed Seeds         : {pass_cnt}")
    print(f"Failed Seeds         : {fail_cnt}")
    print(f"Overall Pass Rate    : {pass_rate:.2f}%")
    print("==================================================================")

    # Cumulative Coverage Across All Seeds
    cum_total = (len(cum_a) + len(cum_b) + len(cum_relu) +
                 len(cum_shift) + len(cum_clamp) + len(cum_k))
    cum_pct = (cum_total / 39.0) * 100.0
    print("             CUMULATIVE MULTI-SEED COVERAGE SUMMARY               ")
    print("==================================================================")
    print(f"Matrix A Operands (5 bins)     : {len(cum_a)}/5 covered")
    print(f"Matrix B Operands (3 bins)     : {len(cum_b)}/3 covered")
    print(f"Activation Modes  (2 bins)     : {len(cum_relu)}/2 covered")
    print(f"Shift Scales      (9 bins)     : {len(cum_shift)}/9 covered")
    print(f"Clamping / Saturation (4 bins) : {len(cum_clamp)}/4 covered")
    print(f"K-Dimensions      (16 bins)    : {len(cum_k)}/16 covered")
    print("------------------------------------------------------------------")
    print(f"Cumulative Target Bins Covered : {cum_total} / 39 ( {cum_pct:.2f}% )")
    print("==================================================================")

    sva_bypassed_any = any(r.get("sva_bypassed", False) for r in results)

    if fail_cnt == 0:
        print(f"[VERDICT] REGRESSION SUITE: All {pass_cnt}/{args.seeds} executed seeds PASSED (0 Scoreboard Mismatches, 0 Procedural Errors)")
        if sva_bypassed_any:
            print("         [NOTE: SIMULATOR CAPABILITY DISCLOSURE]")
            print("         * Warning vsim-8311 detected: Simulator is ModelSim ASE (Concurrent SVA disabled by license).")
            print("         * Active Enforcement: Full Procedural Assertions, Clocking Block Timing, and Bit-True Scoreboard.")
            print("         * Formal SVA Sign-Off: Requires QuestaSim, Synopsys VCS, or Cadence Xcelium for concurrent properties.")
        print(f"         (Pass rate reflects tested seeds; Cumulative Feature Coverage reached {cum_pct:.2f}% across 39 target bins)")
        sys.exit(0)
    else:
        print(f"[VERDICT] REGRESSION SUITE FAILED ({fail_cnt}/{args.seeds} seeds encountered errors)")
        print(f"         Reproducers and failure logs saved to: {FAIL_DIR}")
        sys.exit(1)


if __name__ == "__main__":
    main()
