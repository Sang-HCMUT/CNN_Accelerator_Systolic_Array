`timescale 1ns / 1ps

// Module: matrix_buffer_c.sv
// Dedicated On-Chip Storage for Output Matrix C.
// Stores INT8 Quantized/ReLU activations and INT32 raw high-precision accumulators.
// Dual write channels:
//   1. Synchronous INT32 accumulator channel (from core during readout).
//   2. Synchronous INT8 activation channel (from quantizer when valid).
// Host read port for downstream layers / CPU bus.

module matrix_buffer_c #(
    parameter ARRAY_SIZE = 8,
    parameter DATA_WIDTH = 8,
    parameter ACC_WIDTH  = 32,
    parameter ADDR_WIDTH = $clog2(ARRAY_SIZE * ARRAY_SIZE)
)(
    input  logic                                          clk,
    input  logic                                          rst_n,
    
    // Channel 1: Write INT32 Accumulator (Legacy Single-Element)
    input  logic                                          wr_acc_en,
    input  logic [ADDR_WIDTH-1:0]                         wr_acc_addr,
    input  logic signed [ACC_WIDTH-1:0]                   wr_acc_data,
    
    // Channel 2: Write INT8 Quantized Activation (Legacy Single-Element)
    input  logic                                          wr_int8_en,
    input  logic [ADDR_WIDTH-1:0]                         wr_int8_addr,
    input  logic signed [DATA_WIDTH-1:0]                  wr_int8_data,

    // Gen-2 Parallel Row Write Interface (8 parallel quantizers & accumulators)
    input  logic                                          wr_row_en,
    input  logic [$clog2(ARRAY_SIZE)-1:0]                 wr_row_idx,
    input  logic signed [DATA_WIDTH-1:0]                  wr_row_data_int8 [ARRAY_SIZE],
    input  logic signed [ACC_WIDTH-1:0]                   wr_row_data_acc  [ARRAY_SIZE],
    
    // Host Read Interface (Legacy Single-Element)
    input  logic [ADDR_WIDTH-1:0]                         rd_addr,
    output logic signed [DATA_WIDTH-1:0]                  rd_data_int8,
    output logic signed [ACC_WIDTH-1:0]                   rd_data_acc32,

    // Host Gen-2 Packed 4-INT8 Read Interface
    input  logic [ADDR_WIDTH-3:0]                         rd_packed_addr,
    output logic [31:0]                                   rd_data_packed_int8
);

    localparam TOTAL_C = ARRAY_SIZE * ARRAY_SIZE;

    logic signed [DATA_WIDTH-1:0] mem_c     [TOTAL_C];
    logic signed [ACC_WIDTH-1:0]  mem_c_acc [TOTAL_C];

    // Channel 1 synchronous write (Accumulators)
    always_ff @(posedge clk) begin
        if (wr_row_en) begin
            for (int c = 0; c < ARRAY_SIZE; c = c + 1) begin
                mem_c_acc[wr_row_idx * ARRAY_SIZE + c] <= wr_row_data_acc[c];
            end
        end else if (wr_acc_en) begin
            mem_c_acc[wr_acc_addr] <= wr_acc_data;
        end
    end

    // Channel 2 synchronous write (Quantized INT8)
    always_ff @(posedge clk) begin
        if (wr_row_en) begin
            for (int c = 0; c < ARRAY_SIZE; c = c + 1) begin
                mem_c[wr_row_idx * ARRAY_SIZE + c] <= wr_row_data_int8[c];
            end
        end else if (wr_int8_en) begin
            mem_c[wr_int8_addr] <= wr_int8_data;
        end
    end

    // Host asynchronous / registered readout
    assign rd_data_int8  = mem_c[rd_addr];
    assign rd_data_acc32 = mem_c_acc[rd_addr];

    // Host Gen-2 packed 4-INT8 readout (little-endian byte ordering)
    assign rd_data_packed_int8 = {
        mem_c[{rd_packed_addr, 2'b11}],
        mem_c[{rd_packed_addr, 2'b10}],
        mem_c[{rd_packed_addr, 2'b01}],
        mem_c[{rd_packed_addr, 2'b00}]
    };

endmodule
