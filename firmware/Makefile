# Makefile for RISC-V PicoRV32 Firmware Compilation

CROSS_COMPILE ?= riscv32-unknown-elf-
CC      = $(CROSS_COMPILE)gcc
OBJCOPY = $(CROSS_COMPILE)objcopy
OBJDUMP = $(CROSS_COMPILE)objdump

CFLAGS  = -march=rv32i -mabi=ilp32 -O2 -ffreestanding -nostdlib -Wall -Wextra
LDFLAGS = -T link.ld -nostdlib

SRCS    = start.s main.c
OBJS    = start.o main.o

all: firmware.hex firmware.dis

start.o: start.s
	$(CC) $(CFLAGS) -c $< -o $@

main.o: main.c systolic.h
	$(CC) $(CFLAGS) -c $< -o $@

firmware.elf: $(OBJS) link.ld
	$(CC) $(CFLAGS) $(LDFLAGS) $(OBJS) -o $@

firmware.bin: firmware.elf
	$(OBJCOPY) -O binary $< $@

firmware.dis: firmware.elf
	$(OBJDUMP) -d $< > $@

firmware.hex: firmware.bin
	python bin2hex.py $< $@

clean:
	rm -f *.o *.elf *.bin *.hex *.dis

.PHONY: all clean
