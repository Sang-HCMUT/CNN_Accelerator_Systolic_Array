`timescale 1ns / 1ps

// Driver: gemm_driver.sv
// UVM Driver translating GEMM sequence items to pin-level interface.


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
        vif.drv_cb.start       <= 1'b0;
        vif.drv_cb.wr_a_en     <= 1'b0;
        vif.drv_cb.wr_b_en     <= 1'b0;
        vif.drv_cb.rd_c_addr   <= '0;
        vif.drv_cb.k_dim       <= 4;
        vif.drv_cb.bypass_relu <= 1'b0;
        vif.drv_cb.shift_bits  <= '0;

        // Wait for reset deassertion
        @(posedge vif.rst_n);
        @(vif.drv_cb);

        forever begin
            seq_item_port.get_next_item(req);

            // Wait until DUT is ready (not busy)
            while (vif.drv_cb.busy) @(vif.drv_cb);

            // 1. Write Matrix A into on-chip Buffer A (Row-major)
            for (int r = 0; r < req.ARRAY_SIZE; r++) begin
                for (int k = 0; k < req.k_dim; k++) begin
                    vif.drv_cb.wr_a_en   <= 1'b1;
                    vif.drv_cb.wr_a_addr <= r * req.k_dim + k;
                    vif.drv_cb.wr_a_data <= req.matrix_a[r][k];
                    @(vif.drv_cb);
                end
            end
            vif.drv_cb.wr_a_en <= 1'b0;
            @(vif.drv_cb);

            // 2. Write Matrix B into on-chip Buffer B (Row-major)
            for (int k = 0; k < req.k_dim; k++) begin
                for (int c = 0; c < req.ARRAY_SIZE; c++) begin
                    vif.drv_cb.wr_b_en   <= 1'b1;
                    vif.drv_cb.wr_b_addr <= k * req.ARRAY_SIZE + c;
                    vif.drv_cb.wr_b_data <= req.matrix_b[k][c];
                    @(vif.drv_cb);
                end
            end
            vif.drv_cb.wr_b_en <= 1'b0;
            @(vif.drv_cb);

            // 3. Configure GEMM Parameters
            vif.drv_cb.k_dim       <= req.k_dim;
            vif.drv_cb.bypass_relu <= req.bypass_relu;
            vif.drv_cb.shift_bits  <= req.shift_bits;

            // 4. Pulse START
            vif.drv_cb.start <= 1'b1;
            @(vif.drv_cb);
            vif.drv_cb.start <= 1'b0;

            `uvm_info("DRIVER", $sformatf("Dispatched GEMM Tx #%0d (%s)", req.trans_id, req.scenario_name), UVM_HIGH)

            // Mid-computation Fault Injection: Asynchronous Reset Test
            if (req.inject_mid_reset) begin
                `uvm_info("DRIVER", $sformatf("Injecting mid-flight reset after %0d cycles during computation...", req.reset_after_cycles), UVM_LOW)
                repeat (req.reset_after_cycles) @(vif.drv_cb);
                vif.rst_n <= 1'b0;
                repeat (3) @(vif.drv_cb);
                vif.rst_n <= 1'b1;
                @(vif.drv_cb);
                `uvm_info("DRIVER", "Mid-flight reset deasserted. Accelerator core restored to IDLE.", UVM_LOW)
                seq_item_port.item_done();
                continue;
            end

            drv_ap.write(req);

            // 5. Wait for accelerator core computation to complete
            @(vif.drv_cb);
            while (vif.drv_cb.busy) @(vif.drv_cb);

            // 6. Host Readback: Driver drives rd_c_addr sequentially for all elements
            for (int r = 0; r < req.ARRAY_SIZE; r++) begin
                for (int c = 0; c < req.ARRAY_SIZE; c++) begin
                    vif.drv_cb.rd_c_addr <= r * req.ARRAY_SIZE + c;
                    @(vif.drv_cb);
                end
            end
            @(vif.drv_cb);

            seq_item_port.item_done();
        end
    endtask

endclass : gemm_driver
