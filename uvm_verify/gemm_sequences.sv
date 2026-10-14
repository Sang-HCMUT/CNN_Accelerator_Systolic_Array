`timescale 1ns / 1ps

// ============================================================================
// Sequences: gemm_sequences.sv
// Description: UVM Sequences generating directed, random and stress workloads.
// ============================================================================

import uvm_pkg::*;
`include "uvm_macros.svh"

// ----------------------------------------------------------------------------
// 1. Directed Scenario Sequence
// ----------------------------------------------------------------------------
class gemm_directed_seq extends uvm_sequence #(gemm_seq_item);

    `uvm_object_utils(gemm_directed_seq)

    function new(string name = "gemm_directed_seq");
        super.new(name);
    endfunction

    task body();
        gemm_seq_item req;

        `uvm_info("SEQUENCE", "Executing Directed 6-Scenario GEMM Suite...", UVM_LOW)

        for (int mode = 0; mode <= 5; mode++) begin
            req = gemm_seq_item::type_id::create($sformatf("dir_item_%0d", mode));
            start_item(req);
            req.trans_id = mode + 1;
            req.generate_stimulus(mode);
            finish_item(req);
        end

        `uvm_info("SEQUENCE", "Directed Scenario Suite Complete (6/6 Dispatched).", UVM_LOW)
    endtask

endclass : gemm_directed_seq

// ----------------------------------------------------------------------------
// 2. Constrained-Random Workload Sequence
// ----------------------------------------------------------------------------
class gemm_random_seq extends uvm_sequence #(gemm_seq_item);

    `uvm_object_utils(gemm_random_seq)

    int num_transactions = 30;

    function new(string name = "gemm_random_seq");
        super.new(name);
    endfunction

    task body();
        gemm_seq_item req;

        `uvm_info("SEQUENCE", $sformatf("Launching Constrained-Random GEMM Suite (%0d transactions)...", num_transactions), UVM_LOW)

        for (int i = 0; i < num_transactions; i++) begin
            int rnd_mode = $urandom_range(0, 5);
            req = gemm_seq_item::type_id::create($sformatf("rnd_item_%0d", i));
            start_item(req);
            req.trans_id = i + 1;
            req.generate_stimulus(rnd_mode);
            finish_item(req);
        end

        `uvm_info("SEQUENCE", $sformatf("Random GEMM Suite Complete (%0d transactions dispatched).", num_transactions), UVM_LOW)
    endtask

endclass : gemm_random_seq

// ----------------------------------------------------------------------------
// 3. High-Stress Back-to-Back Workload Sequence
// ----------------------------------------------------------------------------
class gemm_stress_seq extends uvm_sequence #(gemm_seq_item);

    `uvm_object_utils(gemm_stress_seq)

    int num_transactions = 60;

    function new(string name = "gemm_stress_seq");
        super.new(name);
    endfunction

    task body();
        gemm_seq_item req;

        `uvm_info("SEQUENCE", $sformatf("Launching High-Stress Back-to-Back Suite (%0d transactions)...", num_transactions), UVM_LOW)

        for (int i = 0; i < num_transactions; i++) begin
            int rnd_mode = (i % 2 == 0) ? 1 : 2; // Alternate between extremes and saturation
            req = gemm_seq_item::type_id::create($sformatf("stress_item_%0d", i));
            start_item(req);
            req.trans_id = i + 1;
            req.generate_stimulus(rnd_mode);
            finish_item(req);
        end

        `uvm_info("SEQUENCE", $sformatf("Stress GEMM Suite Complete (%0d transactions dispatched).", num_transactions), UVM_LOW)
    endtask

endclass : gemm_stress_seq
