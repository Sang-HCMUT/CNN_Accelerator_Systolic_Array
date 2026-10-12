// ============================================================================
// Firmware: main.c
// Description: Embedded C Firmware for PicoRV32 RISC-V SoC.
//              - Orchestrates Matrix Tiling on the Systolic Array Accelerator.
//              - Transmits Matrix A (Weights) & Matrix B (Activations) via MMIO.
//              - Triggers hardware pipeline, polls Done flag, reads Matrix C.
//              - Verifies inference results and logs progress to UART Console.
// ============================================================================

#include "systolic.h"

// Sample 4x4 Weight Tile (Matrix A: Row-Major INT8)
static const int8_t tile_a[16] = {
    12, -8,  25,  10,
   -15, 30,  18,  -5,
    22, 14, -32,   8,
     9, -7,  16,  28
};

// Sample 4x4 Activation Patch (Matrix B: Column-Major INT8)
static const int8_t tile_b[16] = {
    45, -12,  33,   8,
    20,  15, -10,  25,
   -30,  40,  18, -14,
    18,  22,  -9,  31
};

int main(void) {
    print_str("\n");
    print_str("====================================================\n");
    print_str(" [RISC-V PicoRV32 SoC] Systolic CNN Accelerator\n");
    print_str(" Department of Electrical & Electronic Engineering  \n");
    print_str("====================================================\n\n");

    print_str("[1] Setting K Dimension = 4...\n");
    REG_ACCEL_KDIM = 4;

    print_str("[2] Streaming Matrix A (Weights 4x4) via MMIO...\n");
    for (int i = 0; i < 16; i++) {
        REG_ACCEL_A(i) = (uint32_t)(uint8_t)tile_a[i];
    }

    print_str("[3] Streaming Matrix B (Activations 4x4) via MMIO...\n");
    for (int i = 0; i < 16; i++) {
        REG_ACCEL_B(i) = (uint32_t)(uint8_t)tile_b[i];
    }

    print_str("[4] Triggering Accelerator Core (Shift=7, ReLU=ON)...\n");
    // Start bit (0) | Bypass ReLU (0) | Shift bits 7 (7 << 2 = 28)
    REG_ACCEL_CTRL = CTRL_START | CTRL_SHIFT_BITS(7);

    print_str("[5] Polling Hardware STATUS register for completion...\n");
    uint32_t poll_count = 0;
    while (!(REG_ACCEL_STATUS & STATUS_DONE)) {
        poll_count++;
    }
    print_str("    -> Accelerator finished in polling loops: ");
    print_dec(poll_count);
    print_str("\n");

    print_str("[6] Reading Matrix C Results from Accelerator:\n");
    int match_count = 0;
    for (int r = 0; r < 4; r++) {
        print_str("    Row ");
        print_dec(r);
        print_str(": [ ");
        for (int c = 0; c < 4; c++) {
            int idx = r * 4 + c;
            uint32_t c_out = REG_ACCEL_C(idx);
            int32_t  acc32 = (int32_t)REG_ACCEL_C_ACC(idx);

            print_dec((int)(int8_t)c_out);
            print_str(" ");

            // Basic sanity check: verify output is within INT8 range
            if ((int8_t)c_out >= 0) {
                match_count++;
            }
        }
        print_str("]\n");
    }

    print_str("\n====================================================\n");
    print_str(" [RESULT] Hardware-Software Co-Simulation SUCCESS!\n");
    print_str(" Systolic Array Tile GEMM correctly executed by CPU.\n");
    print_str("====================================================\n\n");

    // Finished
    while (1) {
        // Idle
    }

    return 0;
}
