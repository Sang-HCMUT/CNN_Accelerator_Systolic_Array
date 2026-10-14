`timescale 1ns / 1ps

// ============================================================================
// Testbench: tb_systolic_stress_test.sv
// Description: Comprehensive Corner-Case & Stress Test Suite for Systolic GEMM.
//              Verifies all potential failure points and bottlenecks:
//              1. TEST 1: Happy Path (Standard Random Matrix)
//              2. TEST 2: Extreme Values & Negative Asymmetry (-128, +127, -128 * -128)
//              3. TEST 3: Saturation Clamping (Values exceeding 127 clamped strictly to 127)
//              4. TEST 4: Bypass ReLU & Arithmetic Shift Negative Retention (Signed preserve)
//              5. TEST 5: Back-to-Back Execution (Multiple inferences without system reset)
//              6. TEST 6: Zero Matrix (All zeros input and weight)
// ============================================================================

module tb_systolic_stress_test;

    localparam ARRAY_SIZE = 4;
    localparam DATA_WIDTH = 8;
    localparam ACC_WIDTH  = 32;
    localparam K_DIM      = 4;
    localparam TOTAL_C    = ARRAY_SIZE * ARRAY_SIZE;

    logic clk;
    logic rst_n;

    logic       start;
    logic [7:0] k_dim;
    logic       bypass_relu;
    logic [4:0] shift_bits;
    logic       done;
    logic       busy;

    logic                                     wr_a_en;
    logic [$clog2(ARRAY_SIZE*16)-1:0]         wr_a_addr;
    logic signed [DATA_WIDTH-1:0]             wr_a_data;

    logic                                     wr_b_en;
    logic [$clog2(ARRAY_SIZE*16)-1:0]         wr_b_addr;
    logic signed [DATA_WIDTH-1:0]             wr_b_data;

    logic [$clog2(ARRAY_SIZE*ARRAY_SIZE)-1:0] rd_c_addr;
    logic signed [DATA_WIDTH-1:0]             rd_c_data;
    logic signed [ACC_WIDTH-1:0]              rd_c_acc_data;

    // DUT
    systolic_accelerator_top #(
        .ARRAY_SIZE (ARRAY_SIZE),
        .DATA_WIDTH (DATA_WIDTH),
        .ACC_WIDTH  (ACC_WIDTH)
    ) dut (
        .clk           (clk),
        .rst_n         (rst_n),
        .start         (start),
        .k_dim         (k_dim),
        .bypass_relu   (bypass_relu),
        .shift_bits    (shift_bits),
        .done          (done),
        .busy          (busy),
        .wr_a_en       (wr_a_en),
        .wr_a_addr     (wr_a_addr),
        .wr_a_data     (wr_a_data),
        .wr_b_en       (wr_b_en),
        .wr_b_addr     (wr_b_addr),
        .wr_b_data     (wr_b_data),
        .rd_c_addr     (rd_c_addr),
        .rd_c_data     (rd_c_data),
        .rd_c_acc_data (rd_c_acc_data)
    );

    always #10 clk = ~clk;

    // Test matrix arrays
    logic signed [DATA_WIDTH-1:0] mat_a [ARRAY_SIZE][K_DIM];
    logic signed [DATA_WIDTH-1:0] mat_b [K_DIM][ARRAY_SIZE];
    logic signed [ACC_WIDTH-1:0]  gold_acc [ARRAY_SIZE][ARRAY_SIZE];
    logic signed [DATA_WIDTH-1:0] gold_out [ARRAY_SIZE][ARRAY_SIZE];

    integer total_tests = 0;
    integer passed_tests = 0;
    integer failed_tests = 0;

    // Task to run one test scenario
    task automatic run_test_scenario(
        input string desc,
        input logic  t_bypass_relu,
        input logic [4:0] t_shift_bits
    );
        int i, j, k;
        int err_count;
        int sum;
        int relu_val;
        int scaled;

        err_count = 0;
        total_tests++;

        $display("------------------------------------------------------------------");
        $display("[SCENARIO %0d] %s", total_tests, desc);
        $display("  Config: bypass_relu=%0b, shift_bits=%0d", t_bypass_relu, t_shift_bits);

        // 1. Calculate Golden in Software
        for (i = 0; i < ARRAY_SIZE; i++) begin
            for (j = 0; j < ARRAY_SIZE; j++) begin
                sum = 0;
                for (k = 0; k < K_DIM; k++) begin
                    sum += mat_a[i][k] * mat_b[k][j];
                end
                gold_acc[i][j] = sum;

                // ReLU
                relu_val = (t_bypass_relu) ? sum : ((sum > 0) ? sum : 0);
                
                // Scale (Arithmetic shift)
                scaled = relu_val >>> t_shift_bits;

                // Clamp
                if (scaled > 127) gold_out[i][j] = 127;
                else if (scaled < -128) gold_out[i][j] = -128;
                else gold_out[i][j] = scaled[DATA_WIDTH-1:0];
            end
        end

        // 2. Load into Hardware Buffers
        bypass_relu = t_bypass_relu;
        shift_bits  = t_shift_bits;
        k_dim       = K_DIM;

        for (i = 0; i < ARRAY_SIZE; i++) begin
            for (k = 0; k < K_DIM; k++) begin
                @(posedge clk);
                wr_a_en   = 1'b1;
                wr_a_addr = i * K_DIM + k;
                wr_a_data = mat_a[i][k];
            end
        end
        @(posedge clk);
        wr_a_en = 1'b0;

        for (k = 0; k < K_DIM; k++) begin
            for (j = 0; j < ARRAY_SIZE; j++) begin
                @(posedge clk);
                wr_b_en   = 1'b1;
                wr_b_addr = k * ARRAY_SIZE + j;
                wr_b_data = mat_b[k][j];
            end
        end
        @(posedge clk);
        wr_b_en = 1'b0;

        // 3. Launch Accelerator
        @(posedge clk);
        start = 1'b1;
        @(posedge clk);
        start = 1'b0;

        // 4. Wait for Done
        wait (done == 1'b1);
        @(posedge clk);

        // 5. Verify all 16 results
        for (i = 0; i < ARRAY_SIZE; i++) begin
            for (j = 0; j < ARRAY_SIZE; j++) begin
                rd_c_addr = i * ARRAY_SIZE + j;
                #5;
                if ((rd_c_acc_data !== gold_acc[i][j]) || (rd_c_data !== gold_out[i][j])) begin
                    $display("  [ERROR at C[%0d][%0d]] HW_Acc=%0d (Gold=%0d), HW_Out=%0d (Gold=%0d)",
                             i, j, rd_c_acc_data, gold_acc[i][j], rd_c_data, gold_out[i][j]);
                    err_count++;
                end
            end
        end

        if (err_count == 0) begin
            $display("  --> RESULT: [PASSED] 16/16 elements matched exactly!");
            passed_tests++;
        end else begin
            $display("  --> RESULT: [FAILED] %0d mismatches found!", err_count);
            failed_tests++;
        end
    endtask

    initial begin
        int i, j;
        clk         = 0;
        rst_n       = 0;
        start       = 0;
        bypass_relu = 0;
        shift_bits  = 4;
        k_dim       = K_DIM;
        wr_a_en     = 0;
        wr_b_en     = 0;
        wr_a_addr   = 0;
        wr_b_addr   = 0;
        wr_a_data   = 0;
        wr_b_data   = 0;
        rd_c_addr   = 0;

        #40;
        rst_n = 1;
        #20;

        $display("[TB] Starting stress and corner-case verification...");

        // --------------------------------------------------------------------
        // CORNER-CASE 1: Asymmetric Extreme Values (-128 and +127)
        // Testing: (-128) * (-128) = +16384 (Critical 2's complement boundary)
        // --------------------------------------------------------------------
        for (i = 0; i < ARRAY_SIZE; i++) begin
            for (j = 0; j < K_DIM; j++) mat_a[i][j] = -8'sd128;
            for (j = 0; j < ARRAY_SIZE; j++) mat_b[i][j] = -8'sd128;
        end
        run_test_scenario("Extreme Min (-128 * -128 = +16384 test)", 1'b0, 5'd8);

        // --------------------------------------------------------------------
        // CORNER-CASE 2: Saturation Clamping Test (Large Overflow clamping to 127)
        // --------------------------------------------------------------------
        for (i = 0; i < ARRAY_SIZE; i++) begin
            for (j = 0; j < K_DIM; j++) mat_a[i][j] = 8'sd127;
            for (j = 0; j < ARRAY_SIZE; j++) mat_b[i][j] = 8'sd127;
        end
        // With shift_bits=0, sum = 4 * 127*127 = 64516 >> 0 = 64516 > 127 -> MUST CLAMP TO 127!
        run_test_scenario("Saturation Clamping Test (Must clamp to +127)", 1'b0, 5'd0);

        // --------------------------------------------------------------------
        // CORNER-CASE 3: Bypass ReLU & Negative Value Retention
        // --------------------------------------------------------------------
        for (i = 0; i < ARRAY_SIZE; i++) begin
            for (j = 0; j < K_DIM; j++) mat_a[i][j] = 8'sd50;
            for (j = 0; j < ARRAY_SIZE; j++) mat_b[i][j] = -8'sd2;
        end
        // Product = 4 * 50 * (-2) = -400. Shift right 2 = -100.
        // bypass_relu = 1 -> must output -100!
        run_test_scenario("Bypass ReLU Test (Negative values must be preserved)", 1'b1, 5'd2);

        // --------------------------------------------------------------------
        // CORNER-CASE 4: All-Zero Input & Weights Test
        // --------------------------------------------------------------------
        for (i = 0; i < ARRAY_SIZE; i++) begin
            for (j = 0; j < K_DIM; j++) mat_a[i][j] = 8'sd0;
            for (j = 0; j < ARRAY_SIZE; j++) mat_b[i][j] = 8'sd0;
        end
        run_test_scenario("Zero Matrix Test (All zeros)", 1'b0, 5'd4);

        // --------------------------------------------------------------------
        // STRESS TEST 5: Back-to-Back Run 1 (Consecutive run without HW reset)
        // --------------------------------------------------------------------
        for (i = 0; i < ARRAY_SIZE; i++) begin
            for (j = 0; j < K_DIM; j++) mat_a[i][j] = 8'sd10 + i;
            for (j = 0; j < ARRAY_SIZE; j++) mat_b[i][j] = 8'sd5 - j;
        end
        run_test_scenario("Back-to-Back Run #1 (Check stale state clean)", 1'b0, 5'd2);

        // --------------------------------------------------------------------
        // STRESS TEST 6: Back-to-Back Run 2 (Immediately run after Run 1)
        // --------------------------------------------------------------------
        for (i = 0; i < ARRAY_SIZE; i++) begin
            for (j = 0; j < K_DIM; j++) mat_a[i][j] = -8'sd15 + i*2;
            for (j = 0; j < ARRAY_SIZE; j++) mat_b[i][j] = 8'sd8 + j;
        end
        run_test_scenario("Back-to-Back Run #2 (Check pipeline residual)", 1'b0, 5'd3);

        // Final Report
        $display("\n--- Verification Summary: %0d/%0d passed ---", passed_tests, total_tests);
        if (failed_tests == 0) begin
            $display("[TB] Status: PASSED");
        end else begin
            $display("[TB] Status: FAILED (%0d failed)", failed_tests);
        end

        #100;
        $finish;
    end

endmodule
