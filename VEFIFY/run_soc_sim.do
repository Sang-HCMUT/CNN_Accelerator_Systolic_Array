# ModelSim Simulation Script for Phase 3: RISC-V SoC Co-Simulation
vlib work
vmap work work

# Compile Core Systolic Array RTL
vlog -sv -work work ../RTL/pe_gemm.sv
vlog -sv -work work ../RTL/systolic_array_core.sv
vlog -sv -work work ../RTL/systolic_skew_unit.sv
vlog -sv -work work ../RTL/gemm_controller.sv
vlog -sv -work work ../RTL/matrix_buffer_a.sv
vlog -sv -work work ../RTL/matrix_buffer_b.sv
vlog -sv -work work ../RTL/matrix_buffer_c.sv
vlog -sv -work work ../RTL/quantize_relu_unit.sv
vlog -sv -work work ../RTL/systolic_accelerator_top.sv
vlog -sv -work work ../RTL/systolic_gemm_axi_lite.sv

# Compile SoC Bus, Memory, UART & CPU
vlog -sv -work work ../RTL/axi_ram.sv
vlog -sv -work work ../RTL/axi_uart.sv
vlog -sv -work work ../RTL/axi_interconnect.sv
vlog -work work ../RTL/picorv32.v
vlog -sv -work work ../RTL/soc_top.sv

# Compile Testbench
vlog -sv -work work tb_soc_top.sv

# Launch Simulation
vsim -c -voptargs="+acc" work.tb_soc_top
run -all
quit -f
