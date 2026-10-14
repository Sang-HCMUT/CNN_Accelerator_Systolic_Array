`timescale 1ns / 1ps

// ============================================================================
// Tests: gemm_tests.sv
// Description: UVM Test Collection executing specific verification suites.
// ============================================================================

import uvm_pkg::*;
`include "uvm_macros.svh"

// ----------------------------------------------------------------------------
// Base Test Class
// ----------------------------------------------------------------------------
class gemm_base_test extends uvm_test;

    `uvm_component_utils(gemm_base_test)

    gemm_env env;

    function new(string name = "gemm_base_test", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        env = gemm_env::type_id::create("env", this);
    endfunction

    function void end_of_elaboration_phase(uvm_phase phase);
        super.end_of_elaboration_phase(phase);
        `uvm_info("BASE_TEST", "UVM testbench topology:", UVM_LOW)
        uvm_top.print_topology();
    endfunction

endclass : gemm_base_test

// ----------------------------------------------------------------------------
// 1. Directed Verification Test
// ----------------------------------------------------------------------------
class gemm_directed_test extends gemm_base_test;

    `uvm_component_utils(gemm_directed_test)

    function new(string name = "gemm_directed_test", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    task run_phase(uvm_phase phase);
        gemm_directed_seq seq;
        phase.raise_objection(this);
        `uvm_info("TEST", "Starting test: gemm_directed_test", UVM_LOW)
        seq = gemm_directed_seq::type_id::create("seq");
        seq.start(env.agt.sqr);
        #100;
        `uvm_info("TEST", "Completed test: gemm_directed_test", UVM_LOW)
        phase.drop_objection(this);
    endtask

endclass : gemm_directed_test

// ----------------------------------------------------------------------------
// 2. Constrained-Random Coverage Test
// ----------------------------------------------------------------------------
class gemm_random_test extends gemm_base_test;

    `uvm_component_utils(gemm_random_test)

    function new(string name = "gemm_random_test", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    task run_phase(uvm_phase phase);
        gemm_random_seq seq;
        phase.raise_objection(this);
        `uvm_info("TEST", "Starting test: gemm_random_test", UVM_LOW)
        seq = gemm_random_seq::type_id::create("seq");
        seq.num_transactions = 25; // 25 full 4x4 matrix multiplications
        seq.start(env.agt.sqr);
        #100;
        `uvm_info("TEST", "Completed test: gemm_random_test", UVM_LOW)
        phase.drop_objection(this);
    endtask

endclass : gemm_random_test

// ----------------------------------------------------------------------------
// 3. High-Stress Pipeline Test
// ----------------------------------------------------------------------------
class gemm_stress_test extends gemm_base_test;

    `uvm_component_utils(gemm_stress_test)

    function new(string name = "gemm_stress_test", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    task run_phase(uvm_phase phase);
        gemm_stress_seq seq;
        phase.raise_objection(this);
        `uvm_info("TEST", "Starting test: gemm_stress_test", UVM_LOW)
        seq = gemm_stress_seq::type_id::create("seq");
        seq.num_transactions = 50;
        seq.start(env.agt.sqr);
        #100;
        `uvm_info("TEST", "Completed test: gemm_stress_test", UVM_LOW)
        phase.drop_objection(this);
    endtask

endclass : gemm_stress_test
