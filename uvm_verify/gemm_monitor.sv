`timescale 1ns / 1ps

// ============================================================================
// Monitor: gemm_monitor.sv
// Description: UVM Monitor capturing output results from DUT Buffer C.
// ============================================================================

import uvm_pkg::*;
`include "uvm_macros.svh"

class gemm_monitor extends uvm_monitor;

    `uvm_component_utils(gemm_monitor)

    virtual gemm_if vif;
    uvm_analysis_port #(gemm_seq_item) item_collected_port;

    int mon_trans_cnt = 0;

    function new(string name = "gemm_monitor", uvm_component parent = null);
        super.new(name, parent);
        item_collected_port = new("item_collected_port", this);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        if (!uvm_config_db#(virtual gemm_if)::get(this, "", "vif", vif)) begin
            `uvm_fatal("MONITOR", "Virtual interface vif not found in config_db!")
        end
    endfunction

    task run_phase(uvm_phase phase);
        gemm_seq_item trans;

        @(posedge vif.rst_n);

        forever begin
            // 1. Wait for START signal
            @(posedge vif.clk);
            if (vif.start) begin
                mon_trans_cnt++;
                trans = gemm_seq_item::type_id::create($sformatf("trans_%0d", mon_trans_cnt));
                trans.trans_id     = mon_trans_cnt;
                trans.k_dim        = vif.k_dim;
                trans.bypass_relu  = vif.bypass_relu;
                trans.shift_bits   = vif.shift_bits;

                // 2. Wait for DONE from accelerator core
                while (!vif.done) @(posedge vif.clk);

                // 3. Read back all ARRAY_SIZE x ARRAY_SIZE elements from Buffer C
                for (int r = 0; r < trans.ARRAY_SIZE; r++) begin
                    for (int c = 0; c < trans.ARRAY_SIZE; c++) begin
                        vif.rd_c_addr <= r * trans.ARRAY_SIZE + c;
                        @(posedge vif.clk);
                        // Buffer C registered readout
                        trans.matrix_c_out[r][c] = vif.rd_c_data;
                        trans.matrix_c_acc[r][c] = vif.rd_c_acc_data;
                    end
                end

                `uvm_info("MONITOR", $sformatf("Captured completed GEMM Tx #%0d from Buffer C", trans.trans_id), UVM_HIGH)

                // 4. Broadcast to Scoreboard & Coverage Subscribers
                item_collected_port.write(trans);
            end
        end
    endtask

endclass : gemm_monitor
