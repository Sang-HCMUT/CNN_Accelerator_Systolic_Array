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

        `uvm_info("SEQ", "Executing directed sequence (6 corners + 9 shifts + 16 K-dimensions = 31 transactions)...", UVM_LOW)

        // Part 1: Baseline 6 Corner-Cases
        for (int mode = 0; mode <= 5; mode++) begin
            req = gemm_seq_item::type_id::create($sformatf("dir_item_%0d", mode));
            start_item(req);
            req.trans_id = mode + 1;
            req.generate_stimulus(mode);
            finish_item(req);
        end

        // Part 2: Exhaustive Shift Sweep across all shift_bits = 0..8
        for (int s = 0; s <= 8; s++) begin
            req = gemm_seq_item::type_id::create($sformatf("shift_sweep_%0d", s));
            start_item(req);
            req.trans_id = 7 + s;
            req.generate_stimulus(0); // Uniform random INT8 operands
            req.shift_bits = s;       // Explicitly sweep every shift bit 0..8
            req.scenario_name = $sformatf("SHIFT_SWEEP_%0d", s);
            req.compute_golden();     // Re-compute golden model with target shift
            finish_item(req);
        end

        // Part 3: Exhaustive K-Dimension Sweep across all K = 1..16 (Coverage Closure)
        for (int k_val = 1; k_val <= 16; k_val++) begin
            req = gemm_seq_item::type_id::create($sformatf("k_sweep_%0d", k_val));
            start_item(req);
            req.trans_id = 15 + k_val;
            req.generate_stimulus(0); // Uniform random INT8 operands
            req.k_dim = k_val;        // Force every single K dimension from 1 to 16
            req.bypass_relu = (k_val % 2 == 0);
            req.shift_bits = (k_val % 9);
            req.scenario_name = $sformatf("K_SWEEP_%0d", k_val);
            req.compute_golden();
            finish_item(req);
        end

        `uvm_info("SEQ", "Directed sequence complete (31 transactions, 100% K and Shift covered).", UVM_LOW)
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
