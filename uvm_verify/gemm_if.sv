`timescale 1ns / 1ps

// Interface: gemm_if.sv
// SystemVerilog Virtual Interface for Systolic GEMM Accelerator DUT.


`ifndef ARRAY_SIZE
    `define ARRAY_SIZE 4
`endif
`ifndef MAX_K
    `define MAX_K 16
`endif

interface gemm_if #(
    parameter ARRAY_SIZE = `ARRAY_SIZE,
    parameter DATA_WIDTH = 8,
    parameter ACC_WIDTH  = 32,
    parameter MAX_K      = `MAX_K
)(
    input logic clk
);

    localparam ADDR_A_WIDTH = $clog2(ARRAY_SIZE * MAX_K);
    localparam ADDR_B_WIDTH = $clog2(ARRAY_SIZE * MAX_K);
    localparam ADDR_C_WIDTH = $clog2(ARRAY_SIZE * ARRAY_SIZE);

    // Reset
    logic rst_n;

    // Command & Control
    logic start;
    logic [7:0] k_dim;
    logic bypass_relu;
    logic [4:0] shift_bits;
    logic done;
    logic busy;

    // Host Write Buffer A
    logic wr_a_en;
    logic [ADDR_A_WIDTH-1:0] wr_a_addr;
    logic signed [DATA_WIDTH-1:0] wr_a_data;

    // Host Write Buffer B
    logic wr_b_en;
    logic [ADDR_B_WIDTH-1:0] wr_b_addr;
    logic signed [DATA_WIDTH-1:0] wr_b_data;

    // Host Read Buffer C
    logic [ADDR_C_WIDTH-1:0] rd_c_addr;
    logic signed [DATA_WIDTH-1:0] rd_c_data;
    logic signed [ACC_WIDTH-1:0]  rd_c_acc_data;

    // Clocking block for driver
    clocking drv_cb @(posedge clk);
        default input #1ns output #1ns;
        output start;
        output k_dim;
        output bypass_relu;
        output shift_bits;
        output wr_a_en, wr_a_addr, wr_a_data;
        output wr_b_en, wr_b_addr, wr_b_data;
        output rd_c_addr;
        input  done, busy;
        input  rd_c_data, rd_c_acc_data;
    endclocking

    // Clocking block for monitor
    clocking mon_cb @(posedge clk);
        default input #1ns output #1ns;
        input rst_n;
        input start;
        input k_dim;
        input bypass_relu;
        input shift_bits;
        input done, busy;
        input wr_a_en, wr_a_addr, wr_a_data;
        input wr_b_en, wr_b_addr, wr_b_data;
        input rd_c_addr;
        input rd_c_data, rd_c_acc_data;
    endclocking

    // =========================================================================
    // SYSTEMVERILOG PROTOCOL, TIMING & TEMPORAL ASSERTIONS (SVA)
    // =========================================================================
    logic start_d;
    logic done_d;
    int   compute_timer;
    int   expected_latency;
    logic tracking_latency;

    // 1a. Asynchronous Reset Clearance: Allow 1ps delta for DUT NBA reset to settle
    always @(negedge rst_n) begin
        #1ps;
        if (!rst_n && $time > 0) begin
            chk_async_reset_clear: assert (busy === 1'b0 && done === 1'b0)
                else $error("[SVA-PROC] Reset Violation: busy or done active after asynchronous reset assertion at time %0t!", $time);
        end
    end

    // 1b. Procedural Reset Quiescence Check (Active across ALL simulators including ModelSim ASE)
    always @(posedge clk) begin
        if (!rst_n && $time > 0) begin
            chk_reset_quiescence_proc: assert (busy === 1'b0 && done === 1'b0)
                else $error("[SVA-PROC] Reset Violation: Core not quiescent during active reset at time %0t!", $time);
        end
    end

    // 1c. Concurrent SVA Property (Formal IEEE 1800 assertion for QuestaSim / EDA sign-off)
    chk_reset_quiescence_sva: assert property (@(posedge clk) !rst_n |-> (busy === 1'b0 && done === 1'b0))
        else $error("[SVA-CONCURRENT] Reset Violation: Core not quiescent during active reset at time %0t!", $time);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            start_d          <= 1'b0;
            done_d           <= 1'b0;
            compute_timer    <= 0;
            expected_latency <= 0;
            tracking_latency <= 1'b0;
        end else begin
            start_d <= start;
            done_d  <= done;

            // 2. Pulse Width Checks: START & DONE must be exactly 1 cycle
            if (start_d && start) begin
                chk_start_pulse_width: assert (1'b0)
                    else $error("[SVA-TEMPORAL] Protocol Error: START held high > 1 cycle at time %0t!", $time);
            end

            if (done_d && done) begin
                chk_done_pulse_width: assert (1'b0)
                    else $error("[SVA-TEMPORAL] Protocol Error: DONE held high > 1 cycle at time %0t!", $time);
            end

            // 3. No START when BUSY
            chk_no_start_busy: assert (!(start && busy))
                else $error("[SVA] Protocol Violation: START pulse asserted while accelerator is BUSY at time %0t!", $time);

            // 4. No buffer writes while computing
            chk_no_write_busy: assert (!(busy && (wr_a_en || wr_b_en)))
                else $error("[SVA] Memory Hazard: Host write attempted to Buffer A/B during active computation at time %0t!", $time);

            // 5. Valid K dimension range [1..MAX_K]
            chk_k_dim_valid: assert (!(start && (k_dim < 1 || k_dim > MAX_K)))
                else $error("[SVA] Parameter Error: k_dim=%0d outside valid range [1..%0d] at time %0t!", k_dim, MAX_K, $time);

            // 6. Deterministic FSM Latency & Deadline Tracker: Latency = K + 2*N + N^2 + 5
            if (start && !busy) begin
                tracking_latency <= 1'b1;
                compute_timer    <= 1;
                expected_latency <= k_dim + 2 * ARRAY_SIZE + ARRAY_SIZE * ARRAY_SIZE + 5;
            end else if (tracking_latency) begin
                compute_timer <= compute_timer + 1;
                if (done) begin
                    tracking_latency <= 1'b0;
                    chk_exact_latency: assert (compute_timer == expected_latency)
                        else $error("[SVA-TIMING] Latency Mismatch: Expected %0d cycles for K=%0d, N=%0d, but DONE arrived at cycle %0d!",
                                    expected_latency, k_dim, ARRAY_SIZE, compute_timer);
                end else if (compute_timer > expected_latency + 10) begin
                    tracking_latency <= 1'b0;
                    chk_done_deadline: assert (1'b0)
                        else $error("[SVA-TIMING] Deadline Violation: Core timed out after %0d cycles (Deadline was %0d)!",
                                    compute_timer, expected_latency);
                end
            end
        end
    end

endinterface : gemm_if
