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
    int cnt_clamped_max = 0; // +127 clamped
    int cnt_clamped_zero = 0; // 0 clamped by ReLU

    function new(string name = "gemm_coverage", uvm_component parent = null);
        super.new(name, parent);
        drv_export = new("drv_export", this);
        mon_export = new("mon_export", this);
        for (int i = 0; i <= 8; i++) shift_bins[i] = 0;
    endfunction

    function void write_drv(gemm_seq_item t);
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
        // Track Output Saturation & Clamping from DUT Buffer C
        for (int r = 0; r < t.ARRAY_SIZE; r++) begin
            for (int c = 0; c < t.ARRAY_SIZE; c++) begin
                if (t.matrix_c_out[r][c] == 8'sd127) cnt_clamped_max++;
                if (t.matrix_c_out[r][c] == 8'sd0 && !t.bypass_relu) cnt_clamped_zero++;
            end
        end
    endfunction

    function void report_phase(uvm_phase phase);
        super.report_phase(phase);
        `uvm_info("COV", "--- Functional Coverage Summary ---", UVM_LOW)
        `uvm_info("COV", $sformatf("Matrix A: pos=%0d neg=%0d zero=%0d min(-128)=%0d max(+127)=%0d",
                                  cnt_positive_a, cnt_negative_a, cnt_zero_a, cnt_ext_min_a, cnt_ext_max_a), UVM_LOW)
        `uvm_info("COV", $sformatf("Matrix B: pos=%0d neg=%0d zero=%0d",
                                  cnt_positive_b, cnt_negative_b, cnt_zero_b), UVM_LOW)
        `uvm_info("COV", $sformatf("Activation/Quant: relu_on=%0d relu_bypass=%0d clamped_max=%0d clamped_zero=%0d",
                                  cnt_relu_on, cnt_relu_bypass, cnt_clamped_max, cnt_clamped_zero), UVM_LOW)
        `uvm_info("COV", $sformatf("Shift [0..8]: %0d, %0d, %0d, %0d, %0d, %0d, %0d, %0d, %0d",
                                  shift_bins[0], shift_bins[1], shift_bins[2], shift_bins[3],
                                  shift_bins[4], shift_bins[5], shift_bins[6], shift_bins[7], shift_bins[8]), UVM_LOW)
    endfunction

endclass : gemm_coverage
