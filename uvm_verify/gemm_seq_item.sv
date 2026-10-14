`timescale 1ns / 1ps

// ============================================================================
// Sequence Item: gemm_seq_item.sv
// Description: UVM Sequence Item representing one GEMM Matrix Operation.
// ============================================================================

import uvm_pkg::*;
`include "uvm_macros.svh"

class gemm_seq_item extends uvm_sequence_item;

    parameter ARRAY_SIZE = 4;
    parameter MAX_K      = 16;

    // Stimulus fields
    bit signed [7:0]  matrix_a[ARRAY_SIZE][MAX_K];
    bit signed [7:0]  matrix_b[MAX_K][ARRAY_SIZE];
    int               k_dim;
    bit               bypass_relu;
    bit [4:0]         shift_bits;

    // Response fields (captured from DUT Buffer C)
    bit signed [7:0]  matrix_c_out[ARRAY_SIZE][ARRAY_SIZE];
    bit signed [31:0] matrix_c_acc[ARRAY_SIZE][ARRAY_SIZE];

    // Golden model expected fields
    bit signed [31:0] golden_acc[ARRAY_SIZE][ARRAY_SIZE];
    bit signed [7:0]  golden_out[ARRAY_SIZE][ARRAY_SIZE];

    // Transaction metadata
    string            scenario_name;
    int               trans_id;

    `uvm_object_utils_begin(gemm_seq_item)
        `uvm_field_int(k_dim, UVM_ALL_ON)
        `uvm_field_int(bypass_relu, UVM_ALL_ON)
        `uvm_field_int(shift_bits, UVM_ALL_ON)
        `uvm_field_int(trans_id, UVM_ALL_ON)
        `uvm_field_string(scenario_name, UVM_ALL_ON)
    `uvm_object_utils_end

    function new(string name = "gemm_seq_item");
        super.new(name);
        k_dim = ARRAY_SIZE;
        bypass_relu = 0;
        shift_bits = 4;
        scenario_name = "DEFAULT";
    endfunction

    // Custom Constrained-Random Generator (Compatible with all ModelSim/Questa engines)
    function void generate_stimulus(int mode = 0);
        k_dim = ARRAY_SIZE;

        case (mode)
            0: begin // Uniform Random
                scenario_name = "UNIFORM_RANDOM";
                bypass_relu   = $urandom_range(0, 1);
                shift_bits    = $urandom_range(0, 8);
                for (int r = 0; r < ARRAY_SIZE; r++) begin
                    for (int k = 0; k < k_dim; k++) matrix_a[r][k] = $urandom_range(-128, 127);
                end
                for (int k = 0; k < k_dim; k++) begin
                    for (int c = 0; c < ARRAY_SIZE; c++) matrix_b[k][c] = $urandom_range(-128, 127);
                end
            end

            1: begin // Extreme Extrema (-128, +127)
                scenario_name = "EXTREME_CORNER_CASE";
                bypass_relu   = $urandom_range(0, 1);
                shift_bits    = 8;
                for (int r = 0; r < ARRAY_SIZE; r++) begin
                    for (int k = 0; k < k_dim; k++) matrix_a[r][k] = ($urandom_range(0, 1)) ? 8'sd127 : -8'sd128;
                end
                for (int k = 0; k < k_dim; k++) begin
                    for (int c = 0; c < ARRAY_SIZE; c++) matrix_b[k][c] = ($urandom_range(0, 1)) ? 8'sd127 : -8'sd128;
                end
            end

            2: begin // Saturation Clamping (+127 clamping test)
                scenario_name = "SATURATION_CLAMPING";
                bypass_relu   = 0;
                shift_bits    = 0; // No shift -> maximum accumulator overflow into +127
                for (int r = 0; r < ARRAY_SIZE; r++) begin
                    for (int k = 0; k < k_dim; k++) matrix_a[r][k] = $urandom_range(60, 127);
                end
                for (int k = 0; k < k_dim; k++) begin
                    for (int c = 0; c < ARRAY_SIZE; c++) matrix_b[k][c] = $urandom_range(60, 127);
                end
            end

            3: begin // Bypass ReLU Negative Preservation
                scenario_name = "BYPASS_RELU_NEGATIVE";
                bypass_relu   = 1;
                shift_bits    = 2;
                for (int r = 0; r < ARRAY_SIZE; r++) begin
                    for (int k = 0; k < k_dim; k++) matrix_a[r][k] = $urandom_range(-100, -10);
                end
                for (int k = 0; k < k_dim; k++) begin
                    for (int c = 0; c < ARRAY_SIZE; c++) matrix_b[k][c] = $urandom_range(10, 100);
                end
            end

            4: begin // Zero Matrix (Static Quiescence)
                scenario_name = "ZERO_MATRIX";
                bypass_relu   = 0;
                shift_bits    = 4;
                for (int r = 0; r < ARRAY_SIZE; r++) begin
                    for (int k = 0; k < k_dim; k++) matrix_a[r][k] = 8'sd0;
                end
                for (int k = 0; k < k_dim; k++) begin
                    for (int c = 0; c < ARRAY_SIZE; c++) matrix_b[k][c] = 8'sd0;
                end
            end

            default: begin // Identity Matrix A
                scenario_name = "IDENTITY_MATRIX";
                bypass_relu   = 0;
                shift_bits    = 0;
                for (int r = 0; r < ARRAY_SIZE; r++) begin
                    for (int k = 0; k < k_dim; k++) matrix_a[r][k] = (r == k) ? 8'sd1 : 8'sd0;
                end
                for (int k = 0; k < k_dim; k++) begin
                    for (int c = 0; c < ARRAY_SIZE; c++) matrix_b[k][c] = $urandom_range(1, 20);
                end
            end
        endcase

        compute_golden();
    endfunction

    // SystemVerilog Golden Model Predictor (Bit-True)
    function void compute_golden();
        int signed sum;
        int signed a_val;
        int signed b_val;
        int signed shifted;
        int signed relu_val;
        int signed clamped;

        for (int i = 0; i < ARRAY_SIZE; i++) begin
            for (int j = 0; j < ARRAY_SIZE; j++) begin
                // 1. MatMul Accumulation: sum(A[i][k] * B[k][j])
                sum = 0;
                for (int k = 0; k < k_dim; k++) begin
                    a_val = matrix_a[i][k];
                    b_val = matrix_b[k][j];
                    sum += a_val * b_val;
                end
                golden_acc[i][j] = sum;

                // 2. Arithmetic Right Shift
                shifted = sum >>> shift_bits;

                // 3. ReLU Activation
                if (bypass_relu)
                    relu_val = shifted;
                else
                    relu_val = (shifted < 0) ? 0 : shifted;

                // 4. Signed INT8 Saturation Clamping [-128, +127]
                if (relu_val > 127)
                    clamped = 127;
                else if (relu_val < -128)
                    clamped = -128;
                else
                    clamped = relu_val;

                golden_out[i][j] = clamped[7:0];
            end
        end
    endfunction

    function string convert2string();
        string s;
        s = $sformatf("[Tx #%0d | %s] K=%0d, Shift=%0d, Bypass=%0d | Sample A[0][0]=%0d, B[0][0]=%0d -> Out[0][0]=%0d (Gold=%0d)",
                      trans_id, scenario_name, k_dim, shift_bits, bypass_relu,
                      matrix_a[0][0], matrix_b[0][0], matrix_c_out[0][0], golden_out[0][0]);
        return s;
    endfunction

endclass : gemm_seq_item
