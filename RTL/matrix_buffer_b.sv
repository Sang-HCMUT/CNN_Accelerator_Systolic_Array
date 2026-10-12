`timescale 1ns / 1ps

// ============================================================================
// Module: matrix_buffer_b.sv
// Description: Dedicated On-Chip Storage & Streaming Buffer for Input Matrix B.
//              - Supports Host random-access write port (row-major).
//              - Supports parallel systolic streaming read port (feeds all columns).
// ============================================================================

module matrix_buffer_b #(
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
    output logic signed [DATA_WIDTH-1:0]                  col_data_out [ARRAY_SIZE]
);

    localparam TOTAL_ENTRIES = ARRAY_SIZE * MAX_K;
    logic signed [DATA_WIDTH-1:0] ram [TOTAL_ENTRIES];

    // Host write logic
    always_ff @(posedge clk) begin
        if (wr_en) begin
            ram[wr_addr] <= wr_data;
        end
    end

    // Parallel streaming readout to systolic array columns
    always_comb begin
        for (int c = 0; c < ARRAY_SIZE; c = c + 1) begin
            if (stream_en && (k_step < k_dim)) begin
                col_data_out[c] = ram[k_step * ARRAY_SIZE + c];
            end else begin
                col_data_out[c] = '0;
            end
        end
    end

endmodule
