# ============================================================================
# ModelSim Waveform Script: wave_soc.do
# Description: Launch full GUI simulation and configure grouped waveforms for
#              Phase 3 & 4 RISC-V SoC + Systolic CNN Accelerator.
# Usage:
#   In ModelSim command prompt: do wave_soc.do
# ============================================================================

vlib work
vmap work work

# 1. Compile Core RTL
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

# 2. Compile SoC Infrastructure
vlog -sv -work work ../RTL/seven_seg_decoder.sv
vlog -sv -work work ../RTL/axi_ram.sv
vlog -sv -work work ../RTL/axi_uart.sv
vlog -sv -work work ../RTL/axi_interconnect.sv
vlog -work work ../RTL/picorv32.v
vlog -sv -work work ../RTL/soc_top.sv

# 3. Compile Testbench
vlog -sv -work work tb_soc_top.sv

# 4. Launch Simulation with full visibility
vsim -voptargs="+acc" work.tb_soc_top

# 5. Build Waveform Window
view wave
delete wave *

# Divider: System Clock & Reset
add wave -divider "System Clock & Reset"
add wave -color "Yellow" /tb_soc_top/clk
add wave -color "Red"    /tb_soc_top/rst_n

# Divider: PicoRV32 CPU Status
add wave -divider "PicoRV32 RISC-V CPU"
add wave -color "Orange" -radix hex /tb_soc_top/dut/cpu_axi_araddr
add wave -color "Orange" -radix hex /tb_soc_top/dut/cpu_axi_awaddr
add wave -color "Green"  -radix hex /tb_soc_top/dut/cpu_axi_wdata
add wave -color "Red"    /tb_soc_top/dut/trap

# Divider: AXI4-Lite Crossbar Bus
add wave -divider "AXI4-Lite Interconnect Routing"
add wave -color "Cyan"    /tb_soc_top/dut/s0_arvalid
add wave -color "Magenta" /tb_soc_top/dut/s1_awvalid
add wave -color "Yellow"  /tb_soc_top/dut/s2_awvalid

# Divider: Systolic Array Accelerator
add wave -divider "Systolic Accelerator HW"
add wave -color "Green"  /tb_soc_top/dut/u_accelerator/core_start
add wave -color "Orange" /tb_soc_top/dut/u_accelerator/core_busy
add wave -color "Cyan"   /tb_soc_top/dut/u_accelerator/core_done
add wave -radix decimal  /tb_soc_top/dut/u_accelerator/k_dim_reg
add wave -radix decimal  /tb_soc_top/dut/u_accelerator/core_inst/c_matrix_core

# Divider: DE1 Board Physical IO
add wave -divider "Terasic DE1 Board IO"
add wave -color "White"  /tb_soc_top/uart_rx
add wave -color "Green"  /tb_soc_top/uart_tx
add wave -color "Red"    /tb_soc_top/ledr
add wave -color "Green"  /tb_soc_top/ledg
add wave -radix hex      /tb_soc_top/hex0
add wave -radix hex      /tb_soc_top/hex1

# Run simulation
run -all
wave zoomfull
