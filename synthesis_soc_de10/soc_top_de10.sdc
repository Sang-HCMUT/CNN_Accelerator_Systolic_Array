# ============================================================================
# SDC Timing Constraints — DE10-Standard Cyclone V 5CSXFC6D6F31C6N
# Clock: 50 MHz from CLOCK_50[0] (Pin AF14)
#        Period = 20.000 ns  (same frequency as DE1)
# ============================================================================

# Primary 50 MHz system clock
create_clock -name clk -period 20.000 [get_ports clk]

# Derive clock uncertainty from PLL and I/O specs
derive_clock_uncertainty
