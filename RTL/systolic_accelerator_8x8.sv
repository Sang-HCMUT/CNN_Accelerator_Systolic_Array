`timescale 1ns / 1ps

// Module: systolic_accelerator_8x8.sv
// Fixed 8x8 Systolic Accelerator Top-Level Wrapper for 
// Synthesis and Benchmarking on Altera Cyclone II / Cyclone V FPGA.

module systolic_accelerator_8x8 (
    input  logic                                          clk,
    input  logic                                          rst_n,
    
    // Command & Status
    input  logic                                          start,
    input  logic [7:0]                                    k_dim,
    input  logic                                          bypass_relu,
    input  logic [4:0]                                    shift_bits,
    output logic                                          done,
    output logic                                          busy,
    
    // Host Write Interface for Matrix A (Row-major, 8 x 16 max = 128 elements)
    input  logic                                          wr_a_en,
    input  logic [6:0]                                    wr_a_addr,
    input  logic signed [7:0]                             wr_a_data,
    
    // Host Write Interface for Matrix B (Row-major, 16 x 8 max = 128 elements)
    input  logic                                          wr_b_en,
    input  logic [6:0]                                    wr_b_addr,
    input  logic signed [7:0]                             wr_b_data,
    
    // Host Read Interface for Output Matrix C (Row-major, 8 x 8 = 64 elements)
    input  logic [5:0]                                    rd_c_addr,
    output logic signed [7:0]                             rd_c_data,
    output logic signed [31:0]                            rd_c_acc_data
);

    systolic_accelerator_top #(
        .ARRAY_SIZE (8),
        .DATA_WIDTH (8),
        .ACC_WIDTH  (32)
    ) u_core (
        .clk           (clk),
        .rst_n         (rst_n),
        .start         (start),
        .k_dim         (k_dim),
        .bypass_relu   (bypass_relu),
        .shift_bits    (shift_bits),
        .done          (done),
        .busy          (busy),
        .wr_a_en       (wr_a_en),
        .wr_a_addr     (wr_a_addr),
        .wr_a_data     (wr_a_data),
        .wr_b_en       (wr_b_en),
        .wr_b_addr     (wr_b_addr),
        .wr_b_data     (wr_b_data),
        .rd_c_addr     (rd_c_addr),
        .rd_c_data     (rd_c_data),
        .rd_c_acc_data (rd_c_acc_data)
    );

endmodule
