# ModelSim Waveform Script: run_stress_sim.do
# Compiles and runs Stress & Corner-Case testbench with Waveform GUI


vlib work
vmap work work

# 1. Compile RTL
vlog -sv -work work ../RTL/pe_gemm.sv
vlog -sv -work work ../RTL/systolic_skew_unit.sv
vlog -sv -work work ../RTL/systolic_array_core.sv
vlog -sv -work work ../RTL/matrix_buffer_a.sv
vlog -sv -work work ../RTL/matrix_buffer_b.sv
vlog -sv -work work ../RTL/matrix_buffer_c.sv
vlog -sv -work work ../RTL/quantize_relu_unit.sv
vlog -sv -work work ../RTL/gemm_controller.sv
vlog -sv -work work ../RTL/systolic_accelerator_top.sv

# 2. Compile Stress Test Testbench
vlog -sv -work work tb_systolic_stress_test.sv

# 3. Launch simulation with full accessibility
vsim -voptargs="+acc" work.tb_systolic_stress_test

# 4. Open & configure wave window
view wave
delete wave *

# Divider: Clock & Reset
add wave -divider "Control & Clock"
add wave -color "Yellow" /tb_systolic_stress_test/clk
add wave -color "Red"    /tb_systolic_stress_test/rst_n
add wave -color "Green"  /tb_systolic_stress_test/start
add wave -color "Orange" /tb_systolic_stress_test/busy
add wave -color "Cyan"   /tb_systolic_stress_test/done

# Divider: Configuration Registers
add wave -divider "Hyperparameter Config"
add wave -radix decimal  /tb_systolic_stress_test/k_dim
add wave                 /tb_systolic_stress_test/bypass_relu
add wave -radix decimal  /tb_systolic_stress_test/shift_bits

# Divider: Systolic Core Accumulators
add wave -divider "Internal 2D Accumulators"
add wave -radix decimal  /tb_systolic_stress_test/dut/c_matrix_core

# Divider: Output & Clamping Readout
add wave -divider "Quantization & Output"
add wave -radix decimal  /tb_systolic_stress_test/rd_c_acc_data
add wave -radix decimal  /tb_systolic_stress_test/rd_c_data

# 5. Execute simulation & Zoom
run -all
wave zoomfull
