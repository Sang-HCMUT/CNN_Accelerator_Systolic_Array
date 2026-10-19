`timescale 1ns / 1ps

// Module: systolic_skew_unit.sv
// Dedicated Input Skewing Pipeline Registers for 2D Systolic Array.
// Row i of Matrix A is delayed by i cycles (0T, 1T, 2T, ...).
// Column j of Matrix B is delayed by j cycles (0T, 1T, 2T, ...).

module systolic_skew_unit #(
    parameter ARRAY_SIZE = 4,
    parameter DATA_WIDTH = 8
)(
    input  logic                                          clk,
    input  logic                                          rst_n,
    input  logic                                          en,
    input  logic                                          clear_acc,
    
    // Raw Unskewed Inputs from Buffers
    input  logic signed [DATA_WIDTH-1:0]                  a_row_in   [ARRAY_SIZE],
    input  logic signed [DATA_WIDTH-1:0]                  b_col_in   [ARRAY_SIZE],
    
    // Skewed Outputs to Systolic Array Core
    output logic signed [DATA_WIDTH-1:0]                  a_row_skew [ARRAY_SIZE],
    output logic signed [DATA_WIDTH-1:0]                  b_col_skew [ARRAY_SIZE]
);

    genvar i, j;
    generate
        // Skewing for Matrix A (Row i delayed by i cycles)
        for (i = 0; i < ARRAY_SIZE; i = i + 1) begin : gen_skew_a
            if (i == 0) begin
                assign a_row_skew[0] = a_row_in[0];
            end else begin
                logic signed [DATA_WIDTH-1:0] delay_pipe [i];
                always_ff @(posedge clk or negedge rst_n) begin
                    if (!rst_n) begin
                        for (int k = 0; k < i; k = k + 1) delay_pipe[k] <= '0;
                    end else if (clear_acc) begin
                        for (int k = 0; k < i; k = k + 1) delay_pipe[k] <= '0;
                    end else if (en) begin
                        delay_pipe[0] <= a_row_in[i];
                        for (int k = 1; k < i; k = k + 1) begin
                            delay_pipe[k] <= delay_pipe[k-1];
                        end
                    end
                end
                assign a_row_skew[i] = delay_pipe[i-1];
            end
        end

        // Skewing for Matrix B (Col j delayed by j cycles)
        for (j = 0; j < ARRAY_SIZE; j = j + 1) begin : gen_skew_b
            if (j == 0) begin
                assign b_col_skew[0] = b_col_in[0];
            end else begin
                logic signed [DATA_WIDTH-1:0] delay_pipe [j];
                always_ff @(posedge clk or negedge rst_n) begin
                    if (!rst_n) begin
                        for (int k = 0; k < j; k = k + 1) delay_pipe[k] <= '0;
                    end else if (clear_acc) begin
                        for (int k = 0; k < j; k = k + 1) delay_pipe[k] <= '0;
                    end else if (en) begin
                        delay_pipe[0] <= b_col_in[j];
                        for (int k = 1; k < j; k = k + 1) begin
                            delay_pipe[k] <= delay_pipe[k-1];
                        end
                    end
                end
                assign b_col_skew[j] = delay_pipe[j-1];
            end
        end
    endgenerate

endmodule
