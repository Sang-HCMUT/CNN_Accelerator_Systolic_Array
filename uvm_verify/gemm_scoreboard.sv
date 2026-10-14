`timescale 1ns / 1ps

// ============================================================================
// Scoreboard: gemm_scoreboard.sv
// Description: UVM Scoreboard comparing DUT outputs against Bit-True Golden Model.
// ============================================================================

import uvm_pkg::*;
`include "uvm_macros.svh"

`uvm_analysis_imp_decl(_exp)
`uvm_analysis_imp_decl(_act)

class gemm_scoreboard extends uvm_scoreboard;

    `uvm_component_utils(gemm_scoreboard)

    uvm_analysis_imp_exp #(gemm_seq_item, gemm_scoreboard) exp_export;
    uvm_analysis_imp_act #(gemm_seq_item, gemm_scoreboard) act_export;

    gemm_seq_item exp_queue[$];
    gemm_seq_item act_queue[$];

    int match_count     = 0;
    int mismatch_count  = 0;
    int total_evaluated = 0;

    function new(string name = "gemm_scoreboard", uvm_component parent = null);
        super.new(name, parent);
        exp_export = new("exp_export", this);
        act_export = new("act_export", this);
    endfunction

    function void write_exp(gemm_seq_item item);
        exp_queue.push_back(item);
        check_transactions();
    endfunction

    function void write_act(gemm_seq_item item);
        act_queue.push_back(item);
        check_transactions();
    endfunction

    function void check_transactions();
        while (exp_queue.size() > 0 && act_queue.size() > 0) begin
            gemm_seq_item exp = exp_queue.pop_front();
            gemm_seq_item act = act_queue.pop_front();
            bit is_match = 1;

            total_evaluated++;

            // Ensure golden result is computed
            exp.compute_golden();

            // Compare all 16 elements (INT32 accumulator and INT8 output)
            for (int r = 0; r < exp.ARRAY_SIZE; r++) begin
                for (int c = 0; c < exp.ARRAY_SIZE; c++) begin
                    bit signed [7:0]  act_out = act.matrix_c_out[r][c];
                    bit signed [7:0]  exp_out = exp.golden_out[r][c];
                    bit signed [31:0] act_acc = act.matrix_c_acc[r][c];
                    bit signed [31:0] exp_acc = exp.golden_acc[r][c];

                    if (act_out !== exp_out || act_acc !== exp_acc) begin
                        is_match = 0;
                        `uvm_error("SCOREBOARD_MISMATCH",
                            $sformatf("Mismatch at [%0d][%0d] in Tx #%0d (%s):\n  ACC: DUT=%0d vs GOLD=%0d\n  OUT: DUT=%0d vs GOLD=%0d",
                                      r, c, exp.trans_id, exp.scenario_name, act_acc, exp_acc, act_out, exp_out))
                    end
                end
            end

            if (is_match) begin
                match_count++;
                `uvm_info("SCB",
                    $sformatf("Tx #%0d matched (%s)",
                              exp.trans_id, exp.scenario_name), UVM_LOW)
            end else begin
                mismatch_count++;
            end
        end
    endfunction

    function void report_phase(uvm_phase phase);
        super.report_phase(phase);
        `uvm_info("SCB", "--- Scoreboard Summary ---", UVM_LOW)
        `uvm_info("SCB", $sformatf("Total: %0d | Passed: %0d | Failed: %0d",
                                  total_evaluated, match_count, mismatch_count), UVM_LOW)
        if (mismatch_count == 0 && total_evaluated > 0) begin
            `uvm_info("SCB", "Status: PASSED", UVM_LOW)
        end else begin
            `uvm_error("SCB", "Status: FAILED")
        end
    endfunction

endclass : gemm_scoreboard
