`timescale 1ns / 1ps

// ============================================================================
// Module: gemm_controller.sv
// Description: Central FSM and Sequence Controller for Systolic GEMM Accelerator.
//              - Manages operation lifecycle: CLEAR -> STREAM -> DRAIN -> READOUT -> FLUSH -> DONE.
//              - Perfectly aligned, cycle-accurate control signals for Buffers,
//                Skew Unit, Systolic Core, and Quantizer.
// ============================================================================

module gemm_controller #(
    parameter ARRAY_SIZE = 4
)(
    input  logic                                          clk,
    input  logic                                          rst_n,
    
    // Command & Configuration
    input  logic                                          start,
    input  logic [7:0]                                    k_dim,
    
    // Status Flags
    output logic                                          busy,
    output logic                                          done,
    
    // Datapath Controls: Systolic Core & Skew Unit
    output logic                                          sys_en,
    output logic                                          sys_clear_acc,
    output logic                                          stream_en,
    output logic [7:0]                                    k_step,
    
    // Readout & Post-Processing Controls
    output logic                                          quant_in_en,
    output logic [$clog2(ARRAY_SIZE)-1:0]                 readout_r,
    output logic [$clog2(ARRAY_SIZE)-1:0]                 readout_c,
    output logic [$clog2(ARRAY_SIZE*ARRAY_SIZE)-1:0]      readout_idx,
    output logic                                          wr_acc_en,
    output logic [$clog2(ARRAY_SIZE*ARRAY_SIZE)-1:0]      wr_acc_addr,
    
    // Quantizer writeback tracker
    input  logic                                          quant_out_valid,
    output logic                                          wr_int8_en,
    output logic [$clog2(ARRAY_SIZE*ARRAY_SIZE)-1:0]      wr_int8_addr
);

    localparam TOTAL_C      = ARRAY_SIZE * ARRAY_SIZE;
    localparam ADDR_C_WIDTH = $clog2(TOTAL_C);

    typedef enum logic [2:0] {
        ST_IDLE,
        ST_CLEAR,
        ST_STREAM,
        ST_DRAIN,
        ST_READOUT,
        ST_FLUSH,
        ST_DONE
    } state_t;

    state_t state;

    logic [7:0] k_cnt;
    logic [7:0] drain_cnt;
    logic [7:0] read_cnt;
    logic [ADDR_C_WIDTH-1:0] write_int8_cnt;

    assign k_step      = k_cnt;
    assign readout_idx = read_cnt[ADDR_C_WIDTH-1:0];

    // Combinational coordinates during ST_READOUT
    assign readout_r   = read_cnt / ARRAY_SIZE;
    assign readout_c   = read_cnt % ARRAY_SIZE;
    assign quant_in_en = (state == ST_READOUT);
    assign wr_acc_en   = (state == ST_READOUT);
    assign wr_acc_addr = read_cnt[ADDR_C_WIDTH-1:0];

    // FSM Sequential Logic
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state         <= ST_IDLE;
            busy          <= 1'b0;
            done          <= 1'b0;
            sys_en        <= 1'b0;
            sys_clear_acc <= 1'b0;
            stream_en     <= 1'b0;
            k_cnt         <= '0;
            drain_cnt     <= '0;
            read_cnt      <= '0;
        end else begin
            // Default pulse clear
            sys_clear_acc <= 1'b0;

            case (state)
                ST_IDLE: begin
                    done      <= 1'b0;
                    busy      <= 1'b0;
                    sys_en    <= 1'b0;
                    stream_en <= 1'b0;
                    read_cnt  <= '0;
                    if (start) begin
                        busy          <= 1'b1;
                        state         <= ST_CLEAR;
                        sys_clear_acc <= 1'b1;
                    end
                end

                ST_CLEAR: begin
                    state     <= ST_STREAM;
                    sys_en    <= 1'b1;
                    stream_en <= 1'b1;
                    k_cnt     <= '0;
                end

                ST_STREAM: begin
                    sys_en    <= 1'b1;
                    stream_en <= 1'b1;
                    if (k_cnt < k_dim - 1) begin
                        k_cnt <= k_cnt + 1'b1;
                    end else begin
                        state     <= ST_DRAIN;
                        drain_cnt <= '0;
                        stream_en <= 1'b0;
                    end
                end

                ST_DRAIN: begin
                    // Keep clocking systolic array to let skewed data exit pipeline
                    sys_en    <= 1'b1;
                    stream_en <= 1'b0;
                    if (drain_cnt < (2 * ARRAY_SIZE)) begin
                        drain_cnt <= drain_cnt + 1'b1;
                    end else begin
                        sys_en   <= 1'b0; // Freeze systolic mesh
                        state    <= ST_READOUT;
                        read_cnt <= '0;
                    end
                end

                ST_READOUT: begin
                    sys_en    <= 1'b0;
                    stream_en <= 1'b0;
                    if (read_cnt < TOTAL_C - 1) begin
                        read_cnt <= read_cnt + 1'b1;
                    end else begin
                        state    <= ST_FLUSH; // 1-cycle pipeline flush for last quantizer stage
                    end
                end

                ST_FLUSH: begin
                    state <= ST_DONE;
                end

                ST_DONE: begin
                    done  <= 1'b1;
                    busy  <= 1'b0;
                    state <= ST_IDLE;
                end
            endcase
        end
    end

    // Quantized Output Writeback Address Tracking
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            write_int8_cnt <= '0;
        end else if (state == ST_CLEAR) begin
            write_int8_cnt <= '0;
        end else if (quant_out_valid) begin
            write_int8_cnt <= write_int8_cnt + 1'b1;
        end
    end

    assign wr_int8_en   = quant_out_valid;
    assign wr_int8_addr = write_int8_cnt;

endmodule
