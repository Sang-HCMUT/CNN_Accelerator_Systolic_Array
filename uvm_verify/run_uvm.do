# ModelSim DO Script: Run UVM Verification for Systolic GEMM Accelerator

if [file exists work] {
    vdel -lib work -all
}
vlib work
vmap work work

# 1. Compile UVM Base Package
vlog -sv +incdir+C:/13.0sp1/modelsim_ase/verilog_src/uvm-1.1c/src \
     +define+UVM_NO_DPI \
     C:/13.0sp1/modelsim_ase/verilog_src/uvm-1.1c/src/uvm_pkg.sv

# 2. Compile RTL Design Modules
vlog -sv ../RTL/pe_gemm.sv
vlog -sv ../RTL/systolic_skew_unit.sv
vlog -sv ../RTL/systolic_array_core.sv
vlog -sv ../RTL/quantize_relu_unit.sv
vlog -sv ../RTL/matrix_buffer_a.sv
vlog -sv ../RTL/matrix_buffer_b.sv
vlog -sv ../RTL/matrix_buffer_c.sv
vlog -sv ../RTL/gemm_controller.sv
vlog -sv ../RTL/systolic_accelerator_top.sv

# 3. Compile UVM Testbench Environment
vlog -sv +incdir+C:/13.0sp1/modelsim_ase/verilog_src/uvm-1.1c/src \
     +incdir+. \
     +define+UVM_NO_DPI \
     gemm_if.sv \
     gemm_pkg.sv \
     tb_top.sv

# 4. Execute UVM Verification Test
if {![info exists UVM_TEST]} {
    set UVM_TEST "gemm_directed_test"
}
vsim tb_top +UVM_TESTNAME=$UVM_TEST +UVM_VERBOSITY=UVM_LOW
run -all
quit -f
