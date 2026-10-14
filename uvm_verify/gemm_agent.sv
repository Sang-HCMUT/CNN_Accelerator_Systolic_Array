`timescale 1ns / 1ps

// ============================================================================
// Agent: gemm_agent.sv
// Description: UVM Agent encapsulating Driver, Monitor and Sequencer.
// ============================================================================

import uvm_pkg::*;
`include "uvm_macros.svh"

class gemm_agent extends uvm_agent;

    `uvm_component_utils(gemm_agent)

    gemm_sequencer sqr;
    gemm_driver    drv;
    gemm_monitor   mon;

    function new(string name = "gemm_agent", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        mon = gemm_monitor::type_id::create("mon", this);
        if (get_is_active() == UVM_ACTIVE) begin
            sqr = gemm_sequencer::type_id::create("sqr", this);
            drv = gemm_driver::type_id::create("drv", this);
        end
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        if (get_is_active() == UVM_ACTIVE) begin
            drv.seq_item_port.connect(sqr.seq_item_export);
        end
    endfunction

endclass : gemm_agent
