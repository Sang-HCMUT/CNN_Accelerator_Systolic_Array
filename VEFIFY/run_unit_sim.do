# ModelSim Simulation & Waveform Script for Unit Modules
# File: run_unit_sim.do

vlib work
vmap work work

# Compile RTL components
vlog -sv -work work ../RTL/pe_gemm.sv
vlog -sv -work work ../RTL/systolic_skew_unit.sv
vlog -sv -work work ../RTL/quantize_relu_unit.sv
vlog -sv -work work ../RTL/matrix_buffer_a.sv
vlog -sv -work work ../RTL/matrix_buffer_b.sv
vlog -sv -work work ../RTL/matrix_buffer_c.sv
vlog -sv -work work ../RTL/gemm_controller.sv
vlog -sv -work work ../RTL/systolic_array_core.sv
vlog -sv -work work ../RTL/seven_seg_decoder.sv

# Compile Unit Testbench
vlog -sv -work work tb_unit_modules.sv

# Launch simulation
vsim -voptargs="+acc" work.tb_unit_modules

# Configure Waveform Window
view wave
delete wave *

# Divider 1: Clock & Control
add wave -divider "Global Clock & Reset"
add wave -color "Yellow" /tb_unit_modules/clk
add wave -color "Red"    /tb_unit_modules/rst_n

# Divider 2: UNIT 1 - PE GEMM
add wave -divider "UNIT 1: PE GEMM (INT8 MAC)"
add wave -color "Cyan"                 /tb_unit_modules/pe_en
add wave -color "Red"                  /tb_unit_modules/pe_clear_acc
add wave -color "Green"  -radix dec    /tb_unit_modules/pe_a_in
add wave -color "Green"  -radix dec    /tb_unit_modules/pe_b_in
add wave -color "Orange" -radix dec    /tb_unit_modules/pe_a_out
add wave -color "Orange" -radix dec    /tb_unit_modules/pe_b_out
add wave -color "Yellow" -radix dec    /tb_unit_modules/pe_c_acc

# Divider 3: UNIT 2 - Systolic Skew Unit
add wave -divider "UNIT 2: Systolic Skew Unit (8x8 Wavefront)"
add wave -color "Cyan"                 /tb_unit_modules/skew_en
add wave -color "Magenta" -radix dec   /tb_unit_modules/skew_a_in
add wave -color "Yellow"  -radix dec   /tb_unit_modules/skew_a_out

# Divider 4: UNIT 3 - Hardware Quantization & ReLU
add wave -divider "UNIT 3: Quantization & ReLU"
add wave -color "Cyan"                 /tb_unit_modules/q_en
add wave -color "Orange"               /tb_unit_modules/q_bypass_relu
add wave -color "White"  -radix dec    /tb_unit_modules/q_shift_bits
add wave -color "Yellow" -radix dec    /tb_unit_modules/q_din
add wave -color "Green"  -radix dec    /tb_unit_modules/q_dout
add wave -color "Green"                /tb_unit_modules/q_valid_out

# Divider 5: UNIT 4 - Matrix Buffers
add wave -divider "UNIT 4: Matrix Buffers (A & C)"
add wave -color "Cyan"                 /tb_unit_modules/buf_a_wr_en
add wave -color "White"  -radix dec    /tb_unit_modules/buf_a_wr_addr
add wave -color "Green"  -radix dec    /tb_unit_modules/buf_a_wr_data
add wave -color "Yellow" -radix dec    /tb_unit_modules/buf_a_row_out
add wave -color "Cyan"                 /tb_unit_modules/buf_c_wr_acc_en
add wave -color "Yellow" -radix dec    /tb_unit_modules/buf_c_wr_acc_data
add wave -color "Cyan"                 /tb_unit_modules/buf_c_wr_int8_en
add wave -color "Green"  -radix dec    /tb_unit_modules/buf_c_wr_int8_data
add wave -color "Green"  -radix dec    /tb_unit_modules/buf_c_rd_data_int8
add wave -color "Yellow" -radix dec    /tb_unit_modules/buf_c_rd_data_acc32

# Divider 6: UNIT 6 - Central GEMM FSM Controller
add wave -divider "UNIT 6: GEMM FSM Controller"
add wave -color "Green"                 /tb_unit_modules/ctrl_start
add wave -color "White"  -radix dec     /tb_unit_modules/ctrl_k_dim
add wave -color "Orange"                /tb_unit_modules/ctrl_busy
add wave -color "Cyan"                  /tb_unit_modules/ctrl_done
add wave -color "Red"                   /tb_unit_modules/ctrl_error
add wave -color "Yellow"                /tb_unit_modules/ctrl_stream_en
add wave -color "White"  -radix dec     /tb_unit_modules/ctrl_k_step
add wave -color "Magenta" -radix dec    /tb_unit_modules/ctrl_readout_idx

# Divider 7: UNIT 7 - 2D Systolic Processing Mesh Core
add wave -divider "UNIT 7: 2D Systolic Core (64 PEs)"
add wave -color "Cyan"                  /tb_unit_modules/core_en
add wave -color "Red"                   /tb_unit_modules/core_clear_acc
add wave -color "Green"  -radix dec     /tb_unit_modules/core_a_row_skew
add wave -color "Green"  -radix dec     /tb_unit_modules/core_b_col_skew
add wave -color "Yellow" -radix dec     /tb_unit_modules/core_c_matrix_out

# Divider 8: UNIT 5 - 7-Segment Decoder
add wave -divider "UNIT 5: 7-Segment Display Decoder"
add wave -color "White"  -radix hex    /tb_unit_modules/dec_digit
add wave -color "Red"                  /tb_unit_modules/dec_blank
add wave -color "Green"  -radix bin    /tb_unit_modules/dec_seg

run -all
wave zoomfull
