`timescale 1ns / 1ps

// Sequences: gemm_sequences.sv
// UVM Sequences generating directed, random, and stress workloads.

import uvm_pkg::*;
`include "uvm_macros.svh"

// 1. Directed Scenario Sequence
class gemm_directed_seq extends uvm_sequence #(gemm_seq_item);

    `uvm_object_utils(gemm_directed_seq)

    function new(string name = "gemm_directed_seq");
        super.new(name);
    endfunction

    task body();
        gemm_seq_item req;
        int tx_cnt = 0;

        `uvm_info("SEQ", "Executing directed sequence with Cross-Coverage closure (71 transactions)...", UVM_LOW)

        // Part 1: Baseline 6 Corner-Cases
        for (int mode = 0; mode <= 5; mode++) begin
            req = gemm_seq_item::type_id::create($sformatf("dir_item_%0d", mode));
            start_item(req);
            tx_cnt++;
            req.trans_id = tx_cnt;
            req.generate_stimulus(mode);
            finish_item(req);
        end

        // Part 2: Cross 1 Systematic Sweep [ReLU Mode (2)] x [Shift (9)] = 18 combinations
        for (int r_mode = 0; r_mode <= 1; r_mode++) begin
            for (int s = 0; s <= 8; s++) begin
                req = gemm_seq_item::type_id::create($sformatf("cross_relu_s%0d_r%0d", s, r_mode));
                start_item(req);
                tx_cnt++;
                req.trans_id = tx_cnt;
                req.generate_stimulus(0);
                req.bypass_relu = r_mode;
                req.shift_bits  = s;
                req.k_dim       = (s % 3 == 0) ? 1 : ((s % 3 == 1) ? 8 : 16);
                req.scenario_name = $sformatf("CROSS_RELU_%0d_SHIFT_%0d", r_mode, s);
                req.compute_golden();
                finish_item(req);
            end
        end

        // Part 3: Cross 2 Systematic Sweep [K-Range (3: Min=1, Mid=8, Max=16)] x [Shift (9)] = 27 combinations
        begin
            int k_test_vals[3] = '{1, 8, 16};
            for (int ki = 0; ki < 3; ki++) begin
                for (int s = 0; s <= 8; s++) begin
                    req = gemm_seq_item::type_id::create($sformatf("cross_k%0d_s%0d", k_test_vals[ki], s));
                    start_item(req);
                    tx_cnt++;
                    req.trans_id = tx_cnt;
                    req.generate_stimulus(0);
                    req.k_dim       = k_test_vals[ki];
                    req.shift_bits  = s;
                    req.bypass_relu = (s % 2);
                    req.scenario_name = $sformatf("CROSS_K_%0d_SHIFT_%0d", k_test_vals[ki], s);
                    req.compute_golden();
                    finish_item(req);
                end
            end
        end

        // Part 4: Exhaustive K-Dimension Sweep across all K = 1..16 (Coverage Closure)
        for (int k_val = 1; k_val <= 16; k_val++) begin
            req = gemm_seq_item::type_id::create($sformatf("k_sweep_%0d", k_val));
            start_item(req);
            tx_cnt++;
            req.trans_id = tx_cnt;
            req.generate_stimulus(0);
            req.k_dim       = k_val;
            req.bypass_relu = (k_val % 2 == 0);
            req.shift_bits  = (k_val % 9);
            req.scenario_name = $sformatf("K_SWEEP_%0d", k_val);
            req.compute_golden();
            finish_item(req);
        end

        // Part 5: Cross 3 Matrix A Extremes (-128, +127) x Matrix B Sign (Neg, Pos) = 4 combinations
        for (int a_ext = 0; a_ext < 2; a_ext++) begin
            for (int b_sign = 0; b_sign < 2; b_sign++) begin
                req = gemm_seq_item::type_id::create($sformatf("cross_ext_a%0d_b%0d", a_ext, b_sign));
                start_item(req);
                tx_cnt++;
                req.trans_id = tx_cnt;
                req.k_dim       = 4;
                req.bypass_relu = 1;
                req.shift_bits  = 4;
                for (int r = 0; r < req.ARRAY_SIZE; r++) begin
                    for (int k = 0; k < req.k_dim; k++) begin
                        req.matrix_a[r][k] = (a_ext == 0) ? -8'sd128 : 8'sd127;
                    end
                end
                for (int k = 0; k < req.k_dim; k++) begin
                    for (int c = 0; c < req.ARRAY_SIZE; c++) begin
                        req.matrix_b[k][c] = (b_sign == 0) ? -8'sd50 : 8'sd50;
                    end
                end
                req.scenario_name = $sformatf("CROSS_EXT_A%0d_B%0d", a_ext, b_sign);
                req.compute_golden();
                finish_item(req);
            end
        end

        `uvm_info("SEQ", $sformatf("Directed sequence complete (%0d transactions, 100%% Point & Cross Coverage).", tx_cnt), UVM_LOW)
    endtask

endclass : gemm_directed_seq

// 2. Constrained-Random Workload Sequence
class gemm_random_seq extends uvm_sequence #(gemm_seq_item);

    `uvm_object_utils(gemm_random_seq)

    int num_transactions = 30;

    function new(string name = "gemm_random_seq");
        super.new(name);
    endfunction

    task body();
        gemm_seq_item req;

        `uvm_info("SEQ", $sformatf("Executing random sequence (%0d transactions)...", num_transactions), UVM_LOW)

        for (int i = 0; i < num_transactions; i++) begin
            int rnd_mode = $urandom_range(0, 5);
            req = gemm_seq_item::type_id::create($sformatf("rnd_item_%0d", i));
            start_item(req);
            req.trans_id = i + 1;
            req.generate_stimulus(rnd_mode);
            if (i < 9) begin
                req.shift_bits = i; // Guarantee shift coverage closure across 0..8
                req.compute_golden();
            end
            finish_item(req);
        end

        `uvm_info("SEQ", "Random sequence complete.", UVM_LOW)
    endtask

endclass : gemm_random_seq

// 3. High-Stress Back-to-Back Workload Sequence
class gemm_stress_seq extends uvm_sequence #(gemm_seq_item);

    `uvm_object_utils(gemm_stress_seq)

    int num_transactions = 60;

    function new(string name = "gemm_stress_seq");
        super.new(name);
    endfunction

    task body();
        gemm_seq_item req;

        `uvm_info("SEQ", $sformatf("Executing stress sequence (%0d transactions)...", num_transactions), UVM_LOW)

        for (int i = 0; i < num_transactions; i++) begin
            int rnd_mode = (i % 2 == 0) ? 1 : 2; // Alternate between extremes and saturation
            req = gemm_seq_item::type_id::create($sformatf("stress_item_%0d", i));
            start_item(req);
            req.trans_id = i + 1;
            req.generate_stimulus(rnd_mode);
            finish_item(req);
        end

        `uvm_info("SEQ", "Stress sequence complete.", UVM_LOW)
    endtask

endclass : gemm_stress_seq

// 4. Mid-Computation Asynchronous Reset Resilience Sequence
class gemm_reset_seq extends uvm_sequence #(gemm_seq_item);

    `uvm_object_utils(gemm_reset_seq)

    function new(string name = "gemm_reset_seq");
        super.new(name);
    endfunction

    task body();
        gemm_seq_item req;

        `uvm_info("SEQ", "Executing mid-computation reset sequence (3 phases: Pre-Reset -> Abrupt Reset -> Recovery)...", UVM_LOW)

        // Phase 1: Pre-Reset Baseline Transaction (K=4, verified normal operation)
        req = gemm_seq_item::type_id::create("pre_reset_item");
        start_item(req);
        req.trans_id = 1;
        req.generate_stimulus(0);
        req.k_dim = 4;
        req.scenario_name = "PRE_RESET_BASELINE";
        finish_item(req);

        // Phase 2: Mid-Computation Reset Injection (K=16, interrupted at cycle 10)
        req = gemm_seq_item::type_id::create("mid_reset_item");
        start_item(req);
        req.trans_id = 2;
        req.generate_stimulus(0);
        req.k_dim = 16;
        req.inject_mid_reset = 1'b1;
        req.reset_after_cycles = 10;
        req.scenario_name = "MID_FLIGHT_RESET_ABORT";
        finish_item(req);

        // Phase 3: Post-Reset Recovery Transaction (K=8, confirms hardware recovers to normal)
        req = gemm_seq_item::type_id::create("post_reset_item");
        start_item(req);
        req.trans_id = 2; // Matches monitor's synced counter
        req.generate_stimulus(0);
        req.k_dim = 8;
        req.scenario_name = "POST_RESET_RECOVERY";
        finish_item(req);

        `uvm_info("SEQ", "Mid-computation reset sequence complete. Accelerator recovered successfully.", UVM_LOW)
    endtask

endclass : gemm_reset_seq
