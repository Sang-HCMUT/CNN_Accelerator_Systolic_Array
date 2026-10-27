`timescale 1ns / 1ps

// Top-Level Testbench: tb_top.sv
// UVM Top Module instantiating DUT, Interface, and starting UVM test.


import uvm_pkg::*;
`include "uvm_macros.svh"
import gemm_pkg::*;

`ifndef ARRAY_SIZE
    `define ARRAY_SIZE 4
`endif
`ifndef MAX_K
    `define MAX_K 16
`endif

module tb_top;

    parameter ARRAY_SIZE = `ARRAY_SIZE;
    parameter DATA_WIDTH = 8;
    parameter ACC_WIDTH  = 32;
    parameter MAX_K      = `MAX_K;

    // Clock generation: 50 MHz (Period = 20 ns)
    logic clk;
    initial begin
        clk = 0;
        forever #10 clk = ~clk;
    end

    // Interface instantiation
    gemm_if #(
        .ARRAY_SIZE (ARRAY_SIZE),
        .DATA_WIDTH (DATA_WIDTH),
        .ACC_WIDTH  (ACC_WIDTH),
        .MAX_K      (MAX_K)
    ) vif (clk);

    // Device Under Test (DUT): Structural 2D Systolic GEMM Accelerator
    systolic_accelerator_top #(
        .ARRAY_SIZE (ARRAY_SIZE),
        .DATA_WIDTH (DATA_WIDTH),
        .ACC_WIDTH  (ACC_WIDTH),
        .MAX_K      (MAX_K)
    ) dut (
        .clk            (clk),
        .rst_n          (vif.rst_n),
        .start          (vif.start),
        .k_dim          (vif.k_dim),
        .bypass_relu    (vif.bypass_relu),
        .shift_bits     (vif.shift_bits),
        .done           (vif.done),
        .busy           (vif.busy),
        .wr_a_en        (vif.wr_a_en),
        .wr_a_addr      (vif.wr_a_addr),
        .wr_a_data      (vif.wr_a_data),
        .wr_b_en        (vif.wr_b_en),
        .wr_b_addr      (vif.wr_b_addr),
        .wr_b_data      (vif.wr_b_data),
        .rd_c_addr      (vif.rd_c_addr),
        .rd_c_data      (vif.rd_c_data),
        .rd_c_acc_data  (vif.rd_c_acc_data)
    );

    // Reset generation in separate initial block
    initial begin
        vif.rst_n = 1'b0;
        #40;
        @(posedge clk);
        vif.rst_n = 1'b1;
    end

    // UVM launch at Time 0
    initial begin
        // Register virtual interface in UVM Configuration Database
        uvm_config_db#(virtual gemm_if)::set(null, "*", "vif", vif);

        // Start UVM phase execution at simulation time 0
        run_test();
    end

endmodule : tb_top
