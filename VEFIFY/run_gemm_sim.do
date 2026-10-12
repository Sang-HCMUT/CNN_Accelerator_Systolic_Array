# ============================================================================
# ModelSim Script: run_gemm_sim.do
# Description: Compiles and executes SystemVerilog Systolic Array GEMM verification.
# ============================================================================

# 1. Initialize work library
vlib work
vmap work work

# 2. Compile SystemVerilog RTL source files
vlog -sv -work work ../RTL/pe_gemm.sv
vlog -sv -work work ../RTL/systolic_skew_unit.sv
vlog -sv -work work ../RTL/systolic_array_core.sv
vlog -sv -work work ../RTL/systolic_array_gemm.sv
vlog -sv -work work ../RTL/matrix_buffer_a.sv
vlog -sv -work work ../RTL/matrix_buffer_b.sv
vlog -sv -work work ../RTL/matrix_buffer_c.sv
vlog -sv -work work ../RTL/quantize_relu_unit.sv
vlog -sv -work work ../RTL/gemm_controller.sv
vlog -sv -work work ../RTL/systolic_accelerator_top.sv

# 3. Compile automated Scoreboard testbench
vlog -sv -work work tb_systolic_gemm.sv
vlog -sv -work work tb_systolic_stress_test.sv

# 4. Launch simulation
vsim -voptargs=+acc work.tb_systolic_gemm

# 5. Configure Waveform window
view wave
delete wave *

# Global Control & Clock
add wave -divider "Control & Clock"
add wave -color "Yellow" /tb_systolic_gemm/clk
add wave -color "Red"    /tb_systolic_gemm/rst_n
add wave                 /tb_systolic_gemm/start
add wave                 /tb_systolic_gemm/busy
add wave -color "Green"  /tb_systolic_gemm/done

# Wavefront Skew feeder
add wave -divider "Systolic Array Feeder"
add wave -radix decimal  /tb_systolic_gemm/dut/u_skew_unit/a_row_skew
add wave -radix decimal  /tb_systolic_gemm/dut/u_skew_unit/b_col_skew

# Internal 2D Accumulators
add wave -divider "Internal 2D Accumulators"
add wave -radix decimal  /tb_systolic_gemm/dut/c_matrix_core

# Quantization & Output Readout
add wave -divider "Quantization & Output"
add wave -radix decimal  /tb_systolic_gemm/rd_c_acc_data
add wave -radix decimal  /tb_systolic_gemm/rd_c_data

# 6. Execute full simulation
run -all
wave zoomfull
