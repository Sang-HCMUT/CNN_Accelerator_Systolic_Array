# RISC-V PicoRV32 Startup Code
.section .text.start
.globl _start

_start:
    # Initialize stack pointer
    li sp, 0x00007FF0

    # Initialize frame pointer and global pointer
    li fp, 0
    li gp, 0

    # Zero-out BSS section
    la t0, __bss_start
    la t1, __bss_end
bss_clear_loop:
    bge t0, t1, bss_clear_done
    sw zero, 0(t0)
    addi t0, t0, 4
    j bss_clear_loop
bss_clear_done:

    # Jump to C main()
    call main

    # Infinite loop upon exit
halt_loop:
    j halt_loop
