# ============================================================================
# SDC Timing Constraints — DE2 Cyclone II EP2C35F672C6
# System Clock: 50 MHz from CLOCK_50 (Pin N2), Period = 20.000 ns
# ============================================================================

# Primary 50 MHz system clock
create_clock -name clk -period 20.000 [get_ports clk]

# Derive clock uncertainty from PLL and I/O specs
derive_clock_uncertainty

# Asynchronous input ports (Pushbutton Reset & UART RX)
set_false_path -from [get_ports {rst_n uart_rx}]

# Static / Asynchronous output ports (UART TX, 7-Segment Displays, LEDs)
set_false_path -to [get_ports {uart_tx hex0[*] hex1[*] hex2[*] hex3[*] hex4[*] hex5[*] hex6[*] hex7[*] ledr[*] ledg[*]}]
