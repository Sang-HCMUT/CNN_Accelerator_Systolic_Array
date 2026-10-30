# ModelSim DO Script: Comprehensive Code Coverage Verification
# Enables Branch, Condition, Expression, Statement, and FSM coverage on Systolic RTL

if [file exists work] {
    vdel -lib work -all
}
vlib work
vmap work work

# 1. Compile Core RTL with full coverage instrumentation (+cover=bcesf)
vlog -sv +cover=bcesf -work work ../RTL/pe_gemm.sv
vlog -sv +cover=bcesf -work work ../RTL/systolic_skew_unit.sv
vlog -sv +cover=bcesf -work work ../RTL/systolic_array_core.sv
vlog -sv +cover=bcesf -work work ../RTL/matrix_buffer_a.sv
vlog -sv +cover=bcesf -work work ../RTL/matrix_buffer_b.sv
vlog -sv +cover=bcesf -work work ../RTL/matrix_buffer_c.sv
vlog -sv +cover=bcesf -work work ../RTL/quantize_relu_unit.sv
vlog -sv +cover=bcesf -work work ../RTL/gemm_controller.sv
vlog -sv +cover=bcesf -work work ../RTL/systolic_accelerator_top.sv

# 2. Compile Testbench
vlog -sv -work work tb_systolic_stress_test.sv

# 3. Simulate (Set ENABLE_CODE_COV 1 if running on QuestaSim / ModelSim SE with msimcoverage license)
if {![info exists ENABLE_CODE_COV]} {
    set ENABLE_CODE_COV 0
}

if {$ENABLE_CODE_COV} {
    vsim -coverage -c work.tb_systolic_stress_test
    run -all
    # Generate detailed coverage report (QuestaSim / ModelSim SE)
    coverage report -summary
    coverage report -detail -file code_coverage_report.txt
} else {
    vsim -c work.tb_systolic_stress_test
    run -all
}
quit -f
