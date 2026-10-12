# ============================================================================
# ModelSim Waveform Script: wave_de1_io.do
# Description: Launch full GUI simulation focusing exclusively on
#              Phase 4: Terasic DE1 Board Physical IO & Peripherals.
# Usage:
#   In ModelSim command prompt: do wave_de1_io.do
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

# 5. Build Waveform Window Focused on DE1 Board IO
view wave
delete wave *

# Divider: System Clock & Reset
add wave -divider "System Clock & Reset (50 MHz)"
add wave -color "Yellow" /tb_soc_top/clk
add wave -color "Red"    /tb_soc_top/rst_n

# Divider: DE1 Status LEDs
add wave -divider "DE1 Diagnostic LEDs"
add wave -color "Red"     {/tb_soc_top/ledr[0]}
add wave -color "Orange"  {/tb_soc_top/ledr[1]}
add wave -color "Green"   {/tb_soc_top/ledg[0]}
add wave -color "Cyan"    {/tb_soc_top/ledg[1]}
add wave -color "Red"     -radix hex /tb_soc_top/ledr
add wave -color "Green"   -radix hex /tb_soc_top/ledg

# Divider: DE1 7-Segment Displays
add wave -divider "DE1 7-Segment Displays (Active-Low)"
add wave -color "Magenta" -radix unsigned /tb_soc_top/dut/hex_digit_0
add wave -color "Magenta" -radix hex      /tb_soc_top/hex0
add wave -color "Violet"  -radix unsigned /tb_soc_top/dut/hex_digit_1
add wave -color "Violet"  -radix hex      /tb_soc_top/hex1

# Divider: RS-232 / UART Serial Communication
add wave -divider "RS-232 / UART Serial (115200 Baud)"
add wave -color "White"   /tb_soc_top/uart_rx
add wave -color "Green"   /tb_soc_top/uart_tx
add wave -color "Cyan"    -radix ascii /tb_soc_top/dut/u_uart/tx_byte_latch
add wave -color "Yellow"  /tb_soc_top/dut/u_uart/tx_busy

# Run simulation
run -all
wave zoomfull
