`timescale 1ns / 1ps

// ============================================================================
// Module: matrix_buffer_c.sv
// Description: Dedicated On-Chip Storage for Output Matrix C.
//              - Stores INT8 Quantized/ReLU activations.
//              - Stores INT32 raw high-precision accumulators.
//              - Dual write channels:
//                1. Synchronous INT32 accumulator channel (from core during readout).
//                2. Synchronous INT8 activation channel (from quantizer when valid).
//              - Host read port for downstream layers / CPU bus.
// ============================================================================

module matrix_buffer_c #(
    parameter ARRAY_SIZE = 4,
    parameter DATA_WIDTH = 8,
    parameter ACC_WIDTH  = 32,
    parameter ADDR_WIDTH = $clog2(ARRAY_SIZE * ARRAY_SIZE)
)(
    input  logic                                          clk,
    input  logic                                          rst_n,
    
    // Channel 1: Write INT32 Accumulator
    input  logic                                          wr_acc_en,
    input  logic [ADDR_WIDTH-1:0]                         wr_acc_addr,
    input  logic signed [ACC_WIDTH-1:0]                   wr_acc_data,
    
    // Channel 2: Write INT8 Quantized Activation
    input  logic                                          wr_int8_en,
    input  logic [ADDR_WIDTH-1:0]                         wr_int8_addr,
    input  logic signed [DATA_WIDTH-1:0]                  wr_int8_data,
    
    // Host Read Interface
    input  logic [ADDR_WIDTH-1:0]                         rd_addr,
    output logic signed [DATA_WIDTH-1:0]                  rd_data_int8,
    output logic signed [ACC_WIDTH-1:0]                   rd_data_acc32
);

    localparam TOTAL_C = ARRAY_SIZE * ARRAY_SIZE;

    logic signed [DATA_WIDTH-1:0] mem_c     [TOTAL_C];
    logic signed [ACC_WIDTH-1:0]  mem_c_acc [TOTAL_C];

    // Channel 1 synchronous write
    always_ff @(posedge clk) begin
        if (wr_acc_en) begin
            mem_c_acc[wr_acc_addr] <= wr_acc_data;
        end
    end

    // Channel 2 synchronous write
    always_ff @(posedge clk) begin
        if (wr_int8_en) begin
            mem_c[wr_int8_addr] <= wr_int8_data;
        end
    end

    // Host asynchronous / registered readout
    assign rd_data_int8  = mem_c[rd_addr];
    assign rd_data_acc32 = mem_c_acc[rd_addr];

endmodule
