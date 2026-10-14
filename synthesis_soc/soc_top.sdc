create_clock -name clk -period 20.000 [get_ports clk]
derive_clock_uncertainty

# Asynchronous input ports (Pushbutton Reset & UART RX)
set_false_path -from [get_ports {rst_n uart_rx}]

# Static / Asynchronous output ports (UART TX, 7-Segment Displays, LEDs)
set_false_path -to [get_ports {uart_tx hex0[*] hex1[*] ledr[*] ledg[*]}]
