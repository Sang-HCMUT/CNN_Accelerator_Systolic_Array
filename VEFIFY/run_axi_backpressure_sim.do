# ModelSim Simulation Script for AMBA AXI4-Lite Backpressure Verification
vlib work
vmap work work

vlog -sv -work work ../RTL/pe_gemm.sv
vlog -sv -work work ../RTL/systolic_skew_unit.sv
vlog -sv -work work ../RTL/systolic_array_core.sv
vlog -sv -work work ../RTL/quantize_relu_unit.sv
vlog -sv -work work ../RTL/matrix_buffer_a.sv
vlog -sv -work work ../RTL/matrix_buffer_b.sv
vlog -sv -work work ../RTL/matrix_buffer_c.sv
vlog -sv -work work ../RTL/gemm_controller.sv
vlog -sv -work work ../RTL/systolic_accelerator_top.sv
vlog -sv -work work ../RTL/systolic_gemm_axi_lite.sv
vlog -sv -work work ../RTL/axi_ram.sv
vlog -sv -work work ../RTL/axi_uart.sv
vlog -sv -work work ../RTL/axi_interconnect.sv
vlog -sv -work work tb_axi_backpressure.sv

vsim -c -t 1ps work.tb_axi_backpressure
run -all
quit -f
