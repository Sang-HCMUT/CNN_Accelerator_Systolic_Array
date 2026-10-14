`timescale 1ns / 1ps

// ============================================================================
// Sequencer: gemm_sequencer.sv
// Description: UVM Sequencer routing sequence items to the driver.
// ============================================================================

import uvm_pkg::*;
`include "uvm_macros.svh"

class gemm_sequencer extends uvm_sequencer #(gemm_seq_item);

    `uvm_component_utils(gemm_sequencer)

    function new(string name = "gemm_sequencer", uvm_component parent = null);
        super.new(name, parent);
    endfunction

endclass : gemm_sequencer
