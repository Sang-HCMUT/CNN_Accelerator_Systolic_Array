`timescale 1ns / 1ps

// Module: systolic_array_gemm.sv
// Fully Parameterized 2D Systolic Array (ARRAY_SIZE x ARRAY_SIZE)
// Wrapper combining systolic_skew_unit and systolic_array_core.
// Maintains compatibility with existing top-level interfaces.

module systolic_array_gemm #(
    parameter ARRAY_SIZE = 4,  // Number of PEs per row/col
    parameter DATA_WIDTH = 8,  // INT8 operands
    parameter ACC_WIDTH  = 32  // INT32 accumulator
)(
    input  logic                                          clk,
    input  logic                                          rst_n,
    input  logic                                          en,
    input  logic                                          clear_acc,
    
    // Matrix Inputs (Unskewed, raw row/col vectors)
    input  logic signed [DATA_WIDTH-1:0]                  a_row_in [ARRAY_SIZE],
    input  logic signed [DATA_WIDTH-1:0]                  b_col_in [ARRAY_SIZE],
    
    // Full 2D Accumulated Matrix Output
    output logic signed [ACC_WIDTH-1:0]                   c_matrix_out [ARRAY_SIZE][ARRAY_SIZE]
);

    logic signed [DATA_WIDTH-1:0] a_skewed [ARRAY_SIZE];
    logic signed [DATA_WIDTH-1:0] b_skewed [ARRAY_SIZE];

    // 1. Skew Unit
    systolic_skew_unit #(
        .ARRAY_SIZE (ARRAY_SIZE),
        .DATA_WIDTH (DATA_WIDTH)
    ) u_skew (
        .clk        (clk),
        .rst_n      (rst_n),
        .en         (en),
        .clear_acc  (clear_acc),
        .a_row_in   (a_row_in),
        .b_col_in   (b_col_in),
        .a_row_skew (a_skewed),
        .b_col_skew (b_skewed)
    );

    // 2. 2D Core Mesh
    systolic_array_core #(
        .ARRAY_SIZE (ARRAY_SIZE),
        .DATA_WIDTH (DATA_WIDTH),
        .ACC_WIDTH  (ACC_WIDTH)
    ) u_core (
        .clk          (clk),
        .rst_n        (rst_n),
        .en           (en),
        .clear_acc    (clear_acc),
        .a_row_skew   (a_skewed),
        .b_col_skew   (b_skewed),
        .c_matrix_out (c_matrix_out)
    );

endmodule
