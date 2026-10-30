# Makefile for RISC-V PicoRV32 Firmware Compilation

CROSS_COMPILE ?= riscv-none-elf-
CC      = $(CROSS_COMPILE)gcc
OBJCOPY = $(CROSS_COMPILE)objcopy
OBJDUMP = $(CROSS_COMPILE)objdump

CFLAGS  = -march=rv32i -mabi=ilp32 -Os -ffreestanding -nostdlib -Wall -Wextra
LDFLAGS = -T link.ld -nostdlib -lgcc -Wl,--no-warn-rwx-segments

SRCS    = start.s main.c
OBJS    = start.o main.o

all: firmware.hex firmware.dis

start.o: start.s
	$(CC) $(CFLAGS) -c $< -o $@

main.o: main.c systolic.h mnist_conv1_weights.h mnist_weights.h
	$(CC) $(CFLAGS) -c $< -o $@

firmware.elf: $(OBJS) link.ld
	$(CC) $(CFLAGS) $(OBJS) $(LDFLAGS) -o $@

firmware.bin: firmware.elf
	$(OBJCOPY) -O binary $< $@

firmware.dis: firmware.elf
	$(OBJDUMP) -d $< > $@

firmware.hex: firmware.elf
	$(OBJCOPY) -O verilog --verilog-data-width=4 $< $@

ifeq ($(OS),Windows_NT)
RM = del /Q /F
else
RM = rm -f
endif

clean:
	-$(RM) *.o *.elf *.bin *.hex *.dis 2>nul || exit 0

.PHONY: all clean

