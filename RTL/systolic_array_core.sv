`timescale 1ns / 1ps

// ============================================================================
// Module: systolic_array_core.sv
// Description: Core 2D Processing Mesh of Processing Elements (ARRAY_SIZE x ARRAY_SIZE).
//              - Receives pre-skewed inputs from systolic_skew_unit.
//              - Pure nearest-neighbor interconnections between adjacent PEs.
//              - Displays as a pristine 2D grid in Quartus RTL Viewer.
// ============================================================================

module systolic_array_core #(
    parameter ARRAY_SIZE = 4,  // Number of PEs per row/col
    parameter DATA_WIDTH = 8,  // INT8 operands
    parameter ACC_WIDTH  = 32  // INT32 accumulator
)(
    input  logic                                          clk,
    input  logic                                          rst_n,
    input  logic                                          en,
    input  logic                                          clear_acc,
    
    // Pre-skewed inputs from systolic_skew_unit
    input  logic signed [DATA_WIDTH-1:0]                  a_row_skew   [ARRAY_SIZE],
    input  logic signed [DATA_WIDTH-1:0]                  b_col_skew   [ARRAY_SIZE],
    
    // 2D Output Accumulator Matrix
    output logic signed [ACC_WIDTH-1:0]                   c_matrix_out [ARRAY_SIZE][ARRAY_SIZE]
);

    // Horizontal and vertical forwarding wires between PEs
    logic signed [DATA_WIDTH-1:0] a_wire [ARRAY_SIZE][ARRAY_SIZE];
    logic signed [DATA_WIDTH-1:0] b_wire [ARRAY_SIZE][ARRAY_SIZE];

    genvar i, j;
    generate
        for (i = 0; i < ARRAY_SIZE; i = i + 1) begin : pe_row
            for (j = 0; j < ARRAY_SIZE; j = j + 1) begin : pe_col
                
                // Horizontal input to PE(i, j): from left neighbor or array input
                wire signed [DATA_WIDTH-1:0] pe_a_in = (j == 0) ? a_row_skew[i] : a_wire[i][j-1];
                
                // Vertical input to PE(i, j): from top neighbor or array input
                wire signed [DATA_WIDTH-1:0] pe_b_in = (i == 0) ? b_col_skew[j] : b_wire[i-1][j];

                pe_gemm #(
                    .DATA_WIDTH (DATA_WIDTH),
                    .ACC_WIDTH  (ACC_WIDTH)
                ) pe_inst (
                    .clk       (clk),
                    .rst_n     (rst_n),
                    .en        (en),
                    .clear_acc (clear_acc),
                    .a_in      (pe_a_in),
                    .b_in      (pe_b_in),
                    .a_out     (a_wire[i][j]),
                    .b_out     (b_wire[i][j]),
                    .c_acc     (c_matrix_out[i][j])
                );
            end
        end
    endgenerate

endmodule
