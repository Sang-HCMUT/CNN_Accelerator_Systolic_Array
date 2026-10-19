`timescale 1ns / 1ps

// Module: matrix_buffer_a.sv
// Dedicated On-Chip Storage & Streaming Buffer for Weight Matrix A.
// Supports Host random-access write port (row-major).
// Supports parallel systolic streaming read port (feeds all rows).

module matrix_buffer_a #(
    parameter ARRAY_SIZE = 4,
    parameter MAX_K      = 16,
    parameter DATA_WIDTH = 8,
    parameter ADDR_WIDTH = $clog2(ARRAY_SIZE * MAX_K)
)(
    input  logic                                          clk,
    input  logic                                          rst_n,
    
    // Host Write Interface
    input  logic                                          wr_en,
    input  logic [ADDR_WIDTH-1:0]                         wr_addr,
    input  logic signed [DATA_WIDTH-1:0]                  wr_data,
    
    // Systolic Streaming Interface
    input  logic                                          stream_en,
    input  logic [7:0]                                    k_step,
    input  logic [7:0]                                    k_dim,
    output logic signed [DATA_WIDTH-1:0]                  row_data_out [ARRAY_SIZE]
);

    localparam TOTAL_ENTRIES = ARRAY_SIZE * MAX_K;
    logic signed [DATA_WIDTH-1:0] ram [TOTAL_ENTRIES];

    // Host write logic
    always_ff @(posedge clk) begin
        if (wr_en) begin
            ram[wr_addr] <= wr_data;
        end
    end

    // Parallel streaming readout to systolic array rows
    always_comb begin
        for (int r = 0; r < ARRAY_SIZE; r = r + 1) begin
            if (stream_en && (k_step < k_dim)) begin
                row_data_out[r] = ram[r * k_dim + k_step];
            end else begin
                row_data_out[r] = '0;
            end
        end
    end

endmodule
