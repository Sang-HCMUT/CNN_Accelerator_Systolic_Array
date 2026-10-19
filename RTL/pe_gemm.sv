`timescale 1ns / 1ps

// Module: pe_gemm.sv
// Processing Element (PE) for INT8 Output-Stationary Systolic GEMM.
// Multiplies signed 8-bit A and signed 8-bit B (INT8 x INT8 -> INT16).
// Accumulates result in a 32-bit register (no overflow risk).
// Systolic propagation:
//   a_out registers a_in and passes to East neighbor.
//   b_out registers b_in and passes to South neighbor.

module pe_gemm #(
    parameter DATA_WIDTH = 8,
    parameter ACC_WIDTH  = 32
)(
    input  logic                          clk,
    input  logic                          rst_n,
    input  logic                          en,
    input  logic                          clear_acc,
    
    // Inputs from West and North
    input  logic signed [DATA_WIDTH-1:0]  a_in,
    input  logic signed [DATA_WIDTH-1:0]  b_in,
    
    // Outputs to East and South
    output logic signed [DATA_WIDTH-1:0]  a_out,
    output logic signed [DATA_WIDTH-1:0]  b_out,
    
    // Accumulated Result
    output logic signed [ACC_WIDTH-1:0]   c_acc
);

    logic signed [ACC_WIDTH-1:0] acc_reg;
    wire  signed [2*DATA_WIDTH-1:0] mult_result;

    // Signed 8-bit x 8-bit multiplication
    assign mult_result = a_in * b_in;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            a_out   <= '0;
            b_out   <= '0;
            acc_reg <= '0;
        end else if (clear_acc) begin
            a_out   <= '0;
            b_out   <= '0;
            acc_reg <= '0;
        end else if (en) begin
            a_out   <= a_in;
            b_out   <= b_in;
            acc_reg <= acc_reg + signed'(mult_result);
        end
    end

    assign c_acc = acc_reg;

endmodule
