`timescale 1ns / 1ps

// Interface: gemm_if.sv
// SystemVerilog Virtual Interface for Systolic GEMM Accelerator DUT.


interface gemm_if #(
    parameter ARRAY_SIZE = 4,
    parameter DATA_WIDTH = 8,
    parameter ACC_WIDTH  = 32,
    parameter MAX_K      = 16
)(
    input logic clk
);

    localparam ADDR_A_WIDTH = $clog2(ARRAY_SIZE * MAX_K);
    localparam ADDR_B_WIDTH = $clog2(ARRAY_SIZE * MAX_K);
    localparam ADDR_C_WIDTH = $clog2(ARRAY_SIZE * ARRAY_SIZE);

    // Reset
    logic rst_n;

    // Command & Control
    logic start;
    logic [7:0] k_dim;
    logic bypass_relu;
    logic [4:0] shift_bits;
    logic done;
    logic busy;

    // Host Write Buffer A
    logic wr_a_en;
    logic [ADDR_A_WIDTH-1:0] wr_a_addr;
    logic signed [DATA_WIDTH-1:0] wr_a_data;

    // Host Write Buffer B
    logic wr_b_en;
    logic [ADDR_B_WIDTH-1:0] wr_b_addr;
    logic signed [DATA_WIDTH-1:0] wr_b_data;

    // Host Read Buffer C
    logic [ADDR_C_WIDTH-1:0] rd_c_addr;
    logic signed [DATA_WIDTH-1:0] rd_c_data;
    logic signed [ACC_WIDTH-1:0]  rd_c_acc_data;

    // Clocking block for driver
    clocking drv_cb @(posedge clk);
        default input #1ns output #1ns;
        output rst_n;
        output start;
        output k_dim;
        output bypass_relu;
        output shift_bits;
        output wr_a_en, wr_a_addr, wr_a_data;
        output wr_b_en, wr_b_addr, wr_b_data;
        output rd_c_addr;
        input  done, busy;
        input  rd_c_data, rd_c_acc_data;
    endclocking

    // Clocking block for monitor
    clocking mon_cb @(posedge clk);
        default input #1ns output #1ns;
        input rst_n;
        input start;
        input k_dim;
        input bypass_relu;
        input shift_bits;
        input done, busy;
        input wr_a_en, wr_a_addr, wr_a_data;
        input wr_b_en, wr_b_addr, wr_b_data;
        input rd_c_addr;
        input rd_c_data, rd_c_acc_data;
    endclocking

endinterface : gemm_if
