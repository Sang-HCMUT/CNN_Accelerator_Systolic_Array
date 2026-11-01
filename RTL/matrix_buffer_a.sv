`timescale 1ns / 1ps

// Module: matrix_buffer_a.sv
// Dedicated On-Chip Storage & Streaming Buffer for Weight Matrix A.
// Supports Host random-access write port (row-major).
// Supports parallel systolic streaming read port (feeds all rows).

module matrix_buffer_a #(
    parameter ARRAY_SIZE = 8,
    parameter MAX_K      = 16,
    parameter DATA_WIDTH = 8,
    parameter ADDR_WIDTH = $clog2(ARRAY_SIZE * MAX_K)
)(
    input  logic                                          clk,
    input  logic                                          rst_n,
    
    // Host Write Interface (Legacy Single-Byte)
    input  logic                                          wr_en,
    input  logic [ADDR_WIDTH-1:0]                         wr_addr,
    input  logic signed [DATA_WIDTH-1:0]                  wr_data,
    
    // Host Gen-2 Packed 4-INT8 Write Interface
    input  logic                                          wr_packed_en,
    input  logic [ADDR_WIDTH-3:0]                         wr_packed_addr,
    input  logic [31:0]                                   wr_packed_data,
    
    // Systolic Streaming Interface
    input  logic                                          stream_en,
    input  logic [7:0]                                    k_step,
    input  logic [7:0]                                    k_dim,
    output logic signed [DATA_WIDTH-1:0]                  row_data_out [ARRAY_SIZE]
);

    localparam TOTAL_ENTRIES = ARRAY_SIZE * MAX_K;
    logic signed [DATA_WIDTH-1:0] ram [TOTAL_ENTRIES];

    // Host write logic (Supports legacy single-byte and Gen-2 packed 4-byte writes)
    always_ff @(posedge clk) begin
        if (wr_en) begin
            ram[wr_addr] <= wr_data;
        end else if (wr_packed_en) begin
            ram[{wr_packed_addr, 2'b00}] <= wr_packed_data[7:0];
            ram[{wr_packed_addr, 2'b01}] <= wr_packed_data[15:8];
            ram[{wr_packed_addr, 2'b10}] <= wr_packed_data[23:16];
            ram[{wr_packed_addr, 2'b11}] <= wr_packed_data[31:24];
        end
    end

    // Parallel streaming readout to systolic array rows (with hardware bounds protection)
    always_comb begin
        for (int r = 0; r < ARRAY_SIZE; r = r + 1) begin
            int read_idx;
            read_idx = r * k_dim + k_step;
            if (stream_en && (k_step < k_dim) && (k_dim <= MAX_K) && (read_idx < TOTAL_ENTRIES)) begin
                row_data_out[r] = ram[read_idx];
            end else begin
                row_data_out[r] = '0;
            end
        end
    end

endmodule
