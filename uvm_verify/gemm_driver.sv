`timescale 1ns / 1ps

// ============================================================================
// Driver: gemm_driver.sv
// Description: UVM Driver translating GEMM sequence items to pin-level interface.
// ============================================================================

import uvm_pkg::*;
`include "uvm_macros.svh"

class gemm_driver extends uvm_driver #(gemm_seq_item);

    `uvm_component_utils(gemm_driver)

    virtual gemm_if vif;
    uvm_analysis_port #(gemm_seq_item) drv_ap;

    function new(string name = "gemm_driver", uvm_component parent = null);
        super.new(name, parent);
        drv_ap = new("drv_ap", this);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        if (!uvm_config_db#(virtual gemm_if)::get(this, "", "vif", vif)) begin
            `uvm_fatal("DRIVER", "Virtual interface vif not found in config_db!")
        end
    endfunction

    task run_phase(uvm_phase phase);
        // Initial signal states
        vif.start       <= 0;
        vif.wr_a_en     <= 0;
        vif.wr_b_en     <= 0;
        vif.rd_c_addr   <= 0;
        vif.k_dim       <= 4;
        vif.bypass_relu <= 0;
        vif.shift_bits  <= 0;

        // Wait for reset deassertion
        @(posedge vif.rst_n);
        @(posedge vif.clk);

        forever begin
            seq_item_port.get_next_item(req);

            // Wait until DUT is ready (not busy)
            while (vif.busy) @(posedge vif.clk);

            // 1. Write Matrix A into on-chip Buffer A (Row-major)
            for (int r = 0; r < req.ARRAY_SIZE; r++) begin
                for (int k = 0; k < req.k_dim; k++) begin
                    @(posedge vif.clk);
                    vif.wr_a_en   <= 1'b1;
                    vif.wr_a_addr <= r * req.k_dim + k;
                    vif.wr_a_data <= req.matrix_a[r][k];
                end
            end
            @(posedge vif.clk);
            vif.wr_a_en <= 1'b0;

            // 2. Write Matrix B into on-chip Buffer B (Row-major)
            for (int k = 0; k < req.k_dim; k++) begin
                for (int c = 0; c < req.ARRAY_SIZE; c++) begin
                    @(posedge vif.clk);
                    vif.wr_b_en   <= 1'b1;
                    vif.wr_b_addr <= k * req.ARRAY_SIZE + c;
                    vif.wr_b_data <= req.matrix_b[k][c];
                end
            end
            @(posedge vif.clk);
            vif.wr_b_en <= 1'b0;

            // 3. Configure GEMM Parameters
            vif.k_dim       <= req.k_dim;
            vif.bypass_relu <= req.bypass_relu;
            vif.shift_bits  <= req.shift_bits;

            // 4. Pulse START
            @(posedge vif.clk);
            vif.start <= 1'b1;
            @(posedge vif.clk);
            vif.start <= 1'b0;

            `uvm_info("DRIVER", $sformatf("Dispatched GEMM Tx #%0d (%s)", req.trans_id, req.scenario_name), UVM_HIGH)
            drv_ap.write(req);

            // 5. Wait for accelerator core computation to complete
            @(posedge vif.clk);
            while (vif.busy) @(posedge vif.clk);

            // 6. Wait for monitor to finish reading Buffer C
            repeat (req.ARRAY_SIZE * req.ARRAY_SIZE + 2) @(posedge vif.clk);

            seq_item_port.item_done();
        end
    endtask

endclass : gemm_driver
