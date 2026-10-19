`timescale 1ns / 1ps

// Module: quantize_relu_unit.sv
// Post-Processing Unit for Systolic GEMM.
// ReLU Activation: max(0, x) (optional bypass).
// Arithmetic Shift Right (Scale): configurable shift_bits.
// Saturation / Clamping: clamps value into INT8 range [-128, 127] or [0, 127] after ReLU.

module quantize_relu_unit #(
    parameter IN_WIDTH  = 32,
    parameter OUT_WIDTH = 8
)(
    input  logic                          clk,
    input  logic                          rst_n,
    input  logic                          en,
    input  logic                          bypass_relu,
    input  logic [4:0]                    shift_bits,
    
    // Inputs (from Accumulator)
    input  logic signed [IN_WIDTH-1:0]    din,
    
    // Outputs (Quantized INT8)
    output logic signed [OUT_WIDTH-1:0]   dout,
    output logic                          valid_out
);

    // 1. ReLU
    logic signed [IN_WIDTH-1:0] relu_data;
    always_comb begin
        if (bypass_relu) begin
            relu_data = din;
        end else begin
            relu_data = (din > 0) ? din : '0;
        end
    end

    // 2. Scaling (Arithmetic Shift Right)
    wire signed [IN_WIDTH-1:0] scaled_data = relu_data >>> shift_bits;

    // 3. Saturation & Clamping to 8-bit range [-128, 127]
    logic signed [OUT_WIDTH-1:0] clamped_data;
    always_comb begin
        if (scaled_data > 32'sd127) begin
            clamped_data = 8'sd127;
        end else if (scaled_data < -32'sd128) begin
            clamped_data = -8'sd128;
        end else begin
            clamped_data = scaled_data[OUT_WIDTH-1:0];
        end
    end

    // Registered output
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            dout      <= '0;
            valid_out <= 1'b0;
        end else begin
            dout      <= clamped_data;
            valid_out <= en;
        end
    end

endmodule
