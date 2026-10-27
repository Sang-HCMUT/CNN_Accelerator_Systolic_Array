`timescale 1ns / 1ps

// Coverage Subscriber: gemm_coverage.sv
// UVM Functional Coverage collector tracking stimulus diversity.


import uvm_pkg::*;
`include "uvm_macros.svh"

`uvm_analysis_imp_decl(_drv)
`uvm_analysis_imp_decl(_mon)

class gemm_coverage extends uvm_component;

    `uvm_component_utils(gemm_coverage)

    uvm_analysis_imp_drv #(gemm_seq_item, gemm_coverage) drv_export;
    uvm_analysis_imp_mon #(gemm_seq_item, gemm_coverage) mon_export;

    // Coverage statistics counters (ModelSim ASE license-safe)
    int cnt_positive_a  = 0;
    int cnt_negative_a  = 0;
    int cnt_zero_a      = 0;
    int cnt_ext_min_a   = 0; // -128
    int cnt_ext_max_a   = 0; // +127

    int cnt_positive_b  = 0;
    int cnt_negative_b  = 0;
    int cnt_zero_b      = 0;

    int cnt_relu_on     = 0;
    int cnt_relu_bypass = 0;

    int shift_bins[9]; // shift 0..8

    // Rigorous Post-Processing / Clamping & Saturation Bins:
    int cnt_true_sat_pos   = 0; // Positive saturation: (scaled > +127) clamped to +127
    int cnt_true_sat_neg   = 0; // Negative saturation: bypass_relu && (scaled < -128) clamped to -128
    int cnt_true_relu_zero = 0; // ReLU zero clamp: !bypass_relu && (din < 0) clamped to 0
    int cnt_true_linear    = 0; // Linear passthrough: in-range, no clamping needed

    // K-Dimension Coverage [1..16]
    int cnt_k_min  = 0; // K = 1
    int cnt_k_mid  = 0; // K = 2..15
    int cnt_k_max  = 0; // K = 16
    int k_bins[17];     // Per-K counters

    function new(string name = "gemm_coverage", uvm_component parent = null);
        super.new(name, parent);
        drv_export = new("drv_export", this);
        mon_export = new("mon_export", this);
        for (int i = 0; i <= 8; i++) shift_bins[i] = 0;
        for (int i = 0; i <= 16; i++) k_bins[i] = 0;
    endfunction

    function void write_drv(gemm_seq_item t);
        // Track K dimension distribution
        if (t.k_dim >= 1 && t.k_dim <= 16) k_bins[t.k_dim]++;
        if (t.k_dim == 1)       cnt_k_min++;
        else if (t.k_dim == 16) cnt_k_max++;
        else                    cnt_k_mid++;

        // Track ReLU configuration
        if (t.bypass_relu) cnt_relu_bypass++;
        else               cnt_relu_on++;

        // Track shift bits
        if (t.shift_bits <= 8) shift_bins[t.shift_bits]++;

        // Track Matrix A operand distribution
        for (int r = 0; r < t.ARRAY_SIZE; r++) begin
            for (int k = 0; k < t.k_dim; k++) begin
                if (t.matrix_a[r][k] == -8'sd128) cnt_ext_min_a++;
                if (t.matrix_a[r][k] == 8'sd127)  cnt_ext_max_a++;
                if (t.matrix_a[r][k] == 8'sd0)    cnt_zero_a++;
                else if (t.matrix_a[r][k] > 0)    cnt_positive_a++;
                else                              cnt_negative_a++;
            end
        end

        // Track Matrix B operand distribution
        for (int k = 0; k < t.k_dim; k++) begin
            for (int c = 0; c < t.ARRAY_SIZE; c++) begin
                if (t.matrix_b[k][c] == 8'sd0)    cnt_zero_b++;
                else if (t.matrix_b[k][c] > 0)    cnt_positive_b++;
                else                              cnt_negative_b++;
            end
        end
    endfunction

    function void write_mon(gemm_seq_item t);
        // Track True Output Saturation, Clamping, and Linear Passthrough
        for (int r = 0; r < t.ARRAY_SIZE; r++) begin
            for (int c = 0; c < t.ARRAY_SIZE; c++) begin
                int signed din = t.matrix_c_acc[r][c];
                int signed relu_val = (t.bypass_relu) ? din : ((din > 0) ? din : 0);
                int signed scaled_val = relu_val >>> t.shift_bits;

                // 1. True Positive Saturation Clamp: pre-clamp > 127 clamped down to +127
                if (scaled_val > 127 && t.matrix_c_out[r][c] == 8'sd127) begin
                    cnt_true_sat_pos++;
                end

                // 2. True Negative Saturation Clamp: bypass_relu and pre-clamp < -128 clamped up to -128
                if (t.bypass_relu && scaled_val < -128 && t.matrix_c_out[r][c] == -8'sd128) begin
                    cnt_true_sat_neg++;
                end

                // 3. True ReLU Zero Clamping: negative accumulator explicitly clipped to 0
                if (!t.bypass_relu && din < 0 && t.matrix_c_out[r][c] == 8'sd0) begin
                    cnt_true_relu_zero++;
                end

                // 4. True Linear Passthrough: in-range value passes through un-clamped
                if ((!t.bypass_relu && din >= 0 && scaled_val <= 127 && t.matrix_c_out[r][c] == scaled_val[7:0]) ||
                    (t.bypass_relu && scaled_val >= -128 && scaled_val <= 127 && t.matrix_c_out[r][c] == scaled_val[7:0])) begin
                    cnt_true_linear++;
                end
            end
        end
    endfunction

    function void report_phase(uvm_phase phase);
        int hit_bins = 0;
        real cov_pct = 0.0;
        super.report_phase(phase);

        // 1. Matrix A operands (5 bins)
        if (cnt_positive_a > 0) hit_bins++;
        if (cnt_negative_a > 0) hit_bins++;
        if (cnt_zero_a > 0)     hit_bins++;
        if (cnt_ext_min_a > 0)  hit_bins++;
        if (cnt_ext_max_a > 0)  hit_bins++;

        // 2. Matrix B operands (3 bins)
        if (cnt_positive_b > 0) hit_bins++;
        if (cnt_negative_b > 0) hit_bins++;
        if (cnt_zero_b > 0)     hit_bins++;

        // 3. Activation & Bypass modes (2 bins)
        if (cnt_relu_on > 0)     hit_bins++;
        if (cnt_relu_bypass > 0) hit_bins++;

        // 4. Shift scale sweep [0..8] (9 bins)
        for (int i = 0; i <= 8; i++) begin
            if (shift_bins[i] > 0) hit_bins++;
        end

        // 5. True Post-Processing & Saturation (4 bins)
        if (cnt_true_sat_pos > 0)   hit_bins++;
        if (cnt_true_sat_neg > 0)   hit_bins++;
        if (cnt_true_relu_zero > 0) hit_bins++;
        if (cnt_true_linear > 0)    hit_bins++;

        // 6. K-Dimension space [1..16] (16 bins)
        for (int k = 1; k <= 16; k++) begin
            if (k_bins[k] > 0) hit_bins++;
        end

        cov_pct = (real'(hit_bins) / 39.0) * 100.0;

        `uvm_info("COV", "==================================================================", UVM_LOW)
        `uvm_info("COV", "                 FUNCTIONAL COVERAGE CLOSURE REPORT               ", UVM_LOW)
        `uvm_info("COV", "==================================================================", UVM_LOW)
        `uvm_info("COV", $sformatf("Matrix A [5 bins]    : pos=%0d neg=%0d zero=%0d min(-128)=%0d max(+127)=%0d",
                                  cnt_positive_a, cnt_negative_a, cnt_zero_a, cnt_ext_min_a, cnt_ext_max_a), UVM_LOW)
        `uvm_info("COV", $sformatf("Matrix B [3 bins]    : pos=%0d neg=%0d zero=%0d",
                                  cnt_positive_b, cnt_negative_b, cnt_zero_b), UVM_LOW)
        `uvm_info("COV", $sformatf("Activation [2 bins]  : relu_on=%0d relu_bypass=%0d",
                                  cnt_relu_on, cnt_relu_bypass), UVM_LOW)
        `uvm_info("COV", $sformatf("Shift [0..8] [9 bins]: s0:%0d, s1:%0d, s2:%0d, s3:%0d, s4:%0d, s5:%0d, s6:%0d, s7:%0d, s8:%0d",
                                  shift_bins[0], shift_bins[1], shift_bins[2], shift_bins[3],
                                  shift_bins[4], shift_bins[5], shift_bins[6], shift_bins[7], shift_bins[8]), UVM_LOW)
        `uvm_info("COV", $sformatf("Clamping [4 bins]    : sat_pos(+127)=%0d, sat_neg(-128)=%0d, relu_zero=%0d, linear_pass=%0d",
                                  cnt_true_sat_pos, cnt_true_sat_neg, cnt_true_relu_zero, cnt_true_linear), UVM_LOW)
        `uvm_info("COV", $sformatf("K-Dim [1..16] [16 b] : min(K=1)=%0d max(K=16)=%0d mid(2..15)=%0d",
                                  cnt_k_min, cnt_k_max, cnt_k_mid), UVM_LOW)
        `uvm_info("COV", "------------------------------------------------------------------", UVM_LOW)
        `uvm_info("COV", $sformatf("TOTAL COVERAGE SCORE : %0d / 39 Target Bins Covered ( %0.2f%% )",
                                  hit_bins, cov_pct), UVM_LOW)
        if (hit_bins == 39) begin
            `uvm_info("COV", "COVERAGE VERDICT     : [COVERAGE CLOSURE ACHIEVED (100.00%)]", UVM_LOW)
        end else begin
            `uvm_info("COV", $sformatf("COVERAGE VERDICT     : [IN PROGRESS - %0d bins remaining]", 39 - hit_bins), UVM_LOW)
        end
        `uvm_info("COV", "==================================================================", UVM_LOW)

        // Machine-readable bit vector for regression cumulative coverage aggregation
        `uvm_info("COV_DATA", $sformatf("BINS_A:%0d,%0d,%0d,%0d,%0d",
            (cnt_positive_a>0), (cnt_negative_a>0), (cnt_zero_a>0), (cnt_ext_min_a>0), (cnt_ext_max_a>0)), UVM_LOW)
        `uvm_info("COV_DATA", $sformatf("BINS_B:%0d,%0d,%0d",
            (cnt_positive_b>0), (cnt_negative_b>0), (cnt_zero_b>0)), UVM_LOW)
        `uvm_info("COV_DATA", $sformatf("BINS_RELU:%0d,%0d",
            (cnt_relu_on>0), (cnt_relu_bypass>0)), UVM_LOW)
        `uvm_info("COV_DATA", $sformatf("BINS_SHIFT:%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d",
            (shift_bins[0]>0), (shift_bins[1]>0), (shift_bins[2]>0), (shift_bins[3]>0),
            (shift_bins[4]>0), (shift_bins[5]>0), (shift_bins[6]>0), (shift_bins[7]>0), (shift_bins[8]>0)), UVM_LOW)
        `uvm_info("COV_DATA", $sformatf("BINS_CLAMP:%0d,%0d,%0d,%0d",
            (cnt_true_sat_pos>0), (cnt_true_sat_neg>0), (cnt_true_relu_zero>0), (cnt_true_linear>0)), UVM_LOW)
        `uvm_info("COV_DATA", $sformatf("BINS_K:%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d",
            (k_bins[1]>0), (k_bins[2]>0), (k_bins[3]>0), (k_bins[4]>0),
            (k_bins[5]>0), (k_bins[6]>0), (k_bins[7]>0), (k_bins[8]>0),
            (k_bins[9]>0), (k_bins[10]>0), (k_bins[11]>0), (k_bins[12]>0),
            (k_bins[13]>0), (k_bins[14]>0), (k_bins[15]>0), (k_bins[16]>0)), UVM_LOW)
    endfunction

endclass : gemm_coverage
