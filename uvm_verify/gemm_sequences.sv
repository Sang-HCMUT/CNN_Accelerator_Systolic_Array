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

        `uvm_info("SEQ", "Executing directed sequence (6 transactions)...", UVM_LOW)

        for (int mode = 0; mode <= 5; mode++) begin
            req = gemm_seq_item::type_id::create($sformatf("dir_item_%0d", mode));
            start_item(req);
            req.trans_id = mode + 1;
            req.generate_stimulus(mode);
            finish_item(req);
        end

        `uvm_info("SEQ", "Directed sequence complete.", UVM_LOW)
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
