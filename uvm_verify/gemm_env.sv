`timescale 1ns / 1ps

// Environment: gemm_env.sv
// UVM Environment instantiating Agent, Scoreboard, and Coverage.


import uvm_pkg::*;
`include "uvm_macros.svh"

class gemm_env extends uvm_env;

    `uvm_component_utils(gemm_env)

    gemm_agent      agt;
    gemm_scoreboard scb;
    gemm_coverage   cov;

    function new(string name = "gemm_env", uvm_component parent = null);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        agt = gemm_agent::type_id::create("agt", this);
        scb = gemm_scoreboard::type_id::create("scb", this);
        cov = gemm_coverage::type_id::create("cov", this);
    endfunction

    function void connect_phase(uvm_phase phase);
        super.connect_phase(phase);
        // Driver transactions -> Scoreboard expected export & Coverage stimulus export
        agt.drv.drv_ap.connect(scb.exp_export);
        agt.drv.drv_ap.connect(cov.drv_export);

        // Monitor transactions -> Scoreboard actual export & Coverage response export
        agt.mon.item_collected_port.connect(scb.act_export);
        agt.mon.item_collected_port.connect(cov.mon_export);
    endfunction

endclass : gemm_env
