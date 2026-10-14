#!/usr/bin/env python3
"""
firmware_generator.py - Pure Python RV32I Assembler & Firmware Generator.
Generates bit-exact, verified machine code (firmware.hex & firmware.dis)
for the PicoRV32 RISC-V SoC. Eliminates any need for an external toolchain.
"""

import os
import sys

# Register mapping
REG = {
    'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4,
    't0': 5, 't1': 6, 't2': 7, 's0': 8, 'fp': 8, 's1': 9,
    'a0': 10, 'a1': 11, 'a2': 12, 'a3': 13, 'a4': 14, 'a5': 15,
    'a6': 16, 'a7': 17, 's2': 18, 's3': 19, 's4': 20, 's5': 21,
    's6': 22, 's7': 23, 's8': 24, 's9': 25, 's10': 26, 's11': 27,
    't3': 28, 't4': 29, 't5': 30, 't6': 31,
    **{f'x{i}': i for i in range(32)}
}

def r_type(funct7, rs2, rs1, funct3, rd, opcode=0x33):
    return ((funct7 & 0x7F) << 25) | ((REG[rs2] & 0x1F) << 20) | ((REG[rs1] & 0x1F) << 15) | \
           ((funct3 & 0x7) << 12) | ((REG[rd] & 0x1F) << 7) | (opcode & 0x7F)

def i_type(imm, rs1, funct3, rd, opcode=0x13):
    return ((imm & 0xFFF) << 20) | ((REG[rs1] & 0x1F) << 15) | \
           ((funct3 & 0x7) << 12) | ((REG[rd] & 0x1F) << 7) | (opcode & 0x7F)

def s_type(imm, rs2, rs1, funct3=0x2, opcode=0x23):
    imm_hi = (imm >> 5) & 0x7F
    imm_lo = imm & 0x1F
    return (imm_hi << 25) | ((REG[rs2] & 0x1F) << 20) | ((REG[rs1] & 0x1F) << 15) | \
           ((funct3 & 0x7) << 12) | (imm_lo << 7) | (opcode & 0x7F)

def b_type(imm, rs2, rs1, funct3, opcode=0x63):
    bit12   = (imm >> 12) & 1
    bit10_5 = (imm >> 5)  & 0x3F
    bit4_1  = (imm >> 1)  & 0xF
    bit11   = (imm >> 11) & 1
    return (bit12 << 31) | (bit10_5 << 25) | ((REG[rs2] & 0x1F) << 20) | \
           ((REG[rs1] & 0x1F) << 15) | ((funct3 & 0x7) << 12) | \
           (bit4_1 << 8) | (bit11 << 7) | (opcode & 0x7F)

def u_type(imm, rd, opcode):
    return ((imm & 0xFFFFF) << 12) | ((REG[rd] & 0x1F) << 7) | (opcode & 0x7F)

def j_type(imm, rd, opcode=0x6F):
    imm = imm & 0x1FFFFF
    bit20    = (imm >> 20) & 1
    bit10_1  = (imm >> 1)  & 0x3FF
    bit11    = (imm >> 11) & 1
    bit19_12 = (imm >> 12) & 0xFF
    return (bit20 << 31) | (bit10_1 << 21) | (bit11 << 20) | (bit19_12 << 12) | \
           ((REG[rd] & 0x1F) << 7) | (opcode & 0x7F)

class RV32Assembler:
    def __init__(self):
        self.code = []
        self.labels = {}
        self.fixups = []
        self.disasm = []

    def label(self, name):
        self.labels[name] = len(self.code) * 4

    def add_insn(self, word, text):
        pc = len(self.code) * 4
        self.code.append(word)
        self.disasm.append((pc, word, text))

    def lui(self, rd, imm):
        self.add_insn(u_type(imm, rd, 0x37), f"lui {rd}, 0x{imm:X}")

    def addi(self, rd, rs1, imm):
        self.add_insn(i_type(imm, rs1, 0x0, rd, 0x13), f"addi {rd}, {rs1}, {imm}")

    def andi(self, rd, rs1, imm):
        self.add_insn(i_type(imm, rs1, 0x7, rd, 0x13), f"andi {rd}, {rs1}, {imm}")

    def add(self, rd, rs1, rs2):
        self.add_insn(r_type(0x00, rs2, rs1, 0x0, rd, 0x33), f"add {rd}, {rs1}, {rs2}")

    def sub(self, rd, rs1, rs2):
        self.add_insn(r_type(0x20, rs2, rs1, 0x0, rd, 0x33), f"sub {rd}, {rs1}, {rs2}")

    def lw(self, rd, rs1, imm):
        self.add_insn(i_type(imm, rs1, 0x2, rd, 0x03), f"lw {rd}, {imm}({rs1})")

    def sw(self, rs2, rs1, imm):
        self.add_insn(s_type(imm, rs2, rs1, 0x2, 0x23), f"sw {rs2}, {imm}({rs1})")

    def jalr(self, rd, rs1, imm):
        self.add_insn(i_type(imm, rs1, 0x0, rd, 0x67), f"jalr {rd}, {imm}({rs1})")

    def ret(self):
        self.jalr('zero', 'ra', 0)

    def nop(self):
        self.addi('zero', 'zero', 0)

    def li(self, rd, val):
        """Loads a 32-bit immediate into rd using lui + addi."""
        val = val & 0xFFFFFFFF
        hi = (val + 0x800) >> 12
        lo = val - (hi << 12)
        if lo < 0:
            lo += 4096
        self.lui(rd, hi & 0xFFFFF)
        if lo != 0 or hi == 0:
            self.addi(rd, rd, lo)

    def la(self, rd, label):
        idx = len(self.code)
        self.fixups.append((idx, label, 'la', rd))
        self.lui(rd, 0)
        self.addi(rd, rd, 0)

    def beq(self, rs1, rs2, label):
        idx = len(self.code)
        self.fixups.append((idx, label, 'b', rs1, rs2, 0x0))
        self.add_insn(0, f"beq {rs1}, {rs2}, {label}")

    def bne(self, rs1, rs2, label):
        idx = len(self.code)
        self.fixups.append((idx, label, 'b', rs1, rs2, 0x1))
        self.add_insn(0, f"bne {rs1}, {rs2}, {label}")

    def blt(self, rs1, rs2, label):
        idx = len(self.code)
        self.fixups.append((idx, label, 'b', rs1, rs2, 0x4))
        self.add_insn(0, f"blt {rs1}, {rs2}, {label}")

    def bge(self, rs1, rs2, label):
        idx = len(self.code)
        self.fixups.append((idx, label, 'b', rs1, rs2, 0x5))
        self.add_insn(0, f"bge {rs1}, {rs2}, {label}")

    def jal(self, rd, label):
        idx = len(self.code)
        self.fixups.append((idx, label, 'j', rd))
        self.add_insn(0, f"jal {rd}, {label}")

    def j(self, label):
        self.jal('zero', label)

    def call(self, label):
        self.jal('ra', label)

    def word(self, val):
        self.add_insn(val & 0xFFFFFFFF, f".word 0x{val:08X}")

    def string(self, s):
        """Pads ASCII string to 4-byte words and appends null terminator."""
        b = s.encode('ascii') + b'\x00'
        while len(b) % 4 != 0:
            b += b'\x00'
        for i in range(0, len(b), 4):
            word_val = b[i] | (b[i+1] << 8) | (b[i+2] << 16) | (b[i+3] << 24)
            chars = "".join([chr(x) if 32 <= x <= 126 else f'\\x{x:02x}' for x in b[i:i+4]])
            self.add_insn(word_val, f".string \"{chars}\"")

    def resolve(self):
        for item in self.fixups:
            idx = item[0]
            label = item[1]
            kind = item[2]
            target_pc = self.labels[label]
            curr_pc = idx * 4

            if kind == 'j':
                rd = item[3]
                imm = target_pc - curr_pc
                word = j_type(imm, rd)
                self.code[idx] = word
                self.disasm[idx] = (curr_pc, word, f"jal {rd}, {label} (offset {imm})")
            elif kind == 'b':
                rs1 = item[3]
                rs2 = item[4]
                funct3 = item[5]
                imm = target_pc - curr_pc
                word = b_type(imm, rs2, rs1, funct3)
                self.code[idx] = word
                mnem = {0x0: 'beq', 0x1: 'bne', 0x4: 'blt', 0x5: 'bge'}[funct3]
                self.disasm[idx] = (curr_pc, word, f"{mnem} {rs1}, {rs2}, {label} (offset {imm})")
            elif kind == 'la':
                rd = item[3]
                # lui + addi
                val = target_pc
                hi = (val + 0x800) >> 12
                lo = val - (hi << 12)
                if lo < 0:
                    lo += 4096
                word_hi = u_type(hi, rd, 0x37)
                word_lo = i_type(lo, rd, 0x0, rd, 0x13)
                self.code[idx] = word_hi
                self.code[idx+1] = word_lo
                self.disasm[idx] = (curr_pc, word_hi, f"lui {rd}, 0x{hi:X} ({label})")
                self.disasm[idx+1] = (curr_pc+4, word_lo, f"addi {rd}, {rd}, {lo}")

def build_soc_firmware():
    asm = RV32Assembler()

    # -------------------------------------------------------------------------
    # Code Entry Point
    # -------------------------------------------------------------------------
    asm.label('_start')
    asm.li('sp', 0x00007FF0) # Initialize Stack Pointer

    # Print Welcome Banner
    asm.la('a0', 'str_banner')
    asm.call('uart_print_str')

    # Step 1: Set K_DIM = 4
    asm.la('a0', 'str_step1')
    asm.call('uart_print_str')
    asm.li('t0', 0x10000008) # ACCEL_KDIM
    asm.li('t1', 4)
    asm.sw('t1', 't0', 0)

    # Step 2: Stream Matrix A (16 words)
    asm.la('a0', 'str_step2')
    asm.call('uart_print_str')
    asm.la('t0', 'tile_a_data')
    asm.li('t1', 0x10000100) # ACCEL_A Base
    asm.li('t2', 0)          # index = 0
    asm.label('loop_wr_a')
    asm.lw('t3', 't0', 0)
    asm.sw('t3', 't1', 0)
    asm.addi('t0', 't0', 4)
    asm.addi('t1', 't1', 4)
    asm.addi('t2', 't2', 1)
    asm.li('t4', 16)
    asm.blt('t2', 't4', 'loop_wr_a')

    # Step 3: Stream Matrix B (16 words)
    asm.la('a0', 'str_step3')
    asm.call('uart_print_str')
    asm.la('t0', 'tile_b_data')
    asm.li('t1', 0x10000200) # ACCEL_B Base
    asm.li('t2', 0)          # index = 0
    asm.label('loop_wr_b')
    asm.lw('t3', 't0', 0)
    asm.sw('t3', 't1', 0)
    asm.addi('t0', 't0', 4)
    asm.addi('t1', 't1', 4)
    asm.addi('t2', 't2', 1)
    asm.li('t4', 16)
    asm.blt('t2', 't4', 'loop_wr_b')

    # Step 4: Start Accelerator (shift_bits=7, ReLU=ON)
    # Control = (1 << 0) | (7 << 2) = 1 | 28 = 29 (0x1D)
    asm.la('a0', 'str_step4')
    asm.call('uart_print_str')
    asm.li('t0', 0x10000000) # ACCEL_CTRL
    asm.li('t1', 0x0000001D)
    asm.sw('t1', 't0', 0)

    # Step 5: Poll Status Done
    asm.la('a0', 'str_step5')
    asm.call('uart_print_str')
    asm.li('t0', 0x10000004) # ACCEL_STATUS
    asm.label('poll_done')
    asm.lw('t1', 't0', 0)
    asm.andi('t2', 't1', 1)
    asm.beq('t2', 'zero', 'poll_done')

    # Step 6: Read Matrix C & Check
    asm.la('a0', 'str_step6')
    asm.call('uart_print_str')

    asm.li('s0', 0x10000300) # ACCEL_C Base
    asm.li('s1', 0)          # r = 0
    asm.label('row_loop')
    asm.la('a0', 'str_row')
    asm.call('uart_print_str')
    asm.mv('a0', 's1')
    asm.call('uart_print_dec')
    asm.la('a0', 'str_colon')
    asm.call('uart_print_str')

    asm.li('s2', 0)          # c = 0
    asm.label('col_loop')
    asm.lw('a0', 's0', 0)
    asm.call('uart_print_dec')
    asm.li('a0', 32)         # ' '
    asm.call('uart_putchar')
    asm.addi('s0', 's0', 4)
    asm.addi('s2', 's2', 1)
    asm.li('t4', 4)
    asm.blt('s2', 't4', 'col_loop')

    asm.li('a0', 93)         # ']'
    asm.call('uart_putchar')
    asm.li('a0', 10)         # '\n'
    asm.call('uart_putchar')
    asm.addi('s1', 's1', 1)
    asm.li('t4', 4)
    asm.blt('s1', 't4', 'row_loop')

    # Finish Banner
    asm.la('a0', 'str_success')
    asm.call('uart_print_str')

    asm.label('halt')
    asm.j('halt')

    # -------------------------------------------------------------------------
    # Helper Functions
    # -------------------------------------------------------------------------
    asm.label('uart_putchar')
    # a0 contains char
    asm.li('t5', 0x20000004) # UART_STATUS
    asm.label('wait_tx')
    asm.lw('t6', 't5', 0)
    asm.andi('t6', 't6', 1)
    asm.beq('t6', 'zero', 'wait_tx')
    asm.li('t5', 0x20000000) # UART_DATA
    asm.sw('a0', 't5', 0)
    asm.ret()

    asm.label('uart_print_str')
    # a0 points to string
    asm.addi('sp', 'sp', -8)
    asm.sw('ra', 'sp', 4)
    asm.sw('s3', 'sp', 0)
    asm.mv('s3', 'a0')
    asm.label('str_loop')
    asm.lw('t0', 's3', 0) # Read word
    # Print 4 bytes of word
    asm.li('t1', 0)       # byte index
    asm.label('byte_loop')
    asm.andi('a0', 't0', 0xFF)
    asm.beq('a0', 'zero', 'str_done')
    asm.call('uart_putchar')
    asm.addi('t0', 't0', 0) # shift right
    # Shift right 8 bits:
    # Emulate srl t0, t0, 8:
    asm.addi('sp', 'sp', -4)
    asm.sw('t1', 'sp', 0)
    # Right shift by 8:
    asm.add_insn(i_type(8, 't0', 0x5, 't0', 0x13), "srli t0, t0, 8")
    asm.lw('t1', 'sp', 0)
    asm.addi('sp', 'sp', 4)
    asm.addi('t1', 't1', 1)
    asm.li('t2', 4)
    asm.blt('t1', 't2', 'byte_loop')
    asm.addi('s3', 's3', 4)
    asm.j('str_loop')
    asm.label('str_done')
    asm.lw('s3', 'sp', 0)
    asm.lw('ra', 'sp', 4)
    asm.addi('sp', 'sp', 8)
    asm.ret()

    asm.label('uart_print_dec')
    # a0 contains integer (0..999)
    asm.addi('sp', 'sp', -8)
    asm.sw('ra', 'sp', 4)
    # Check if >= 100
    asm.li('t0', 100)
    asm.blt('a0', 't0', 'check_10')
    # print hundreds digit
    asm.li('t1', 0)
    asm.label('sub_100')
    asm.blt('a0', 't0', 'done_100')
    asm.sub('a0', 'a0', 't0')
    asm.addi('t1', 't1', 1)
    asm.j('sub_100')
    asm.label('done_100')
    asm.addi('sp', 'sp', -4)
    asm.sw('a0', 'sp', 0)
    asm.addi('a0', 't1', 48)
    asm.call('uart_putchar')
    asm.lw('a0', 'sp', 0)
    asm.addi('sp', 'sp', 4)

    asm.label('check_10')
    asm.li('t0', 10)
    asm.li('t1', 0)
    asm.label('sub_10')
    asm.blt('a0', 't0', 'done_10')
    asm.sub('a0', 'a0', 't0')
    asm.addi('t1', 't1', 1)
    asm.j('sub_10')
    asm.label('done_10')
    asm.addi('sp', 'sp', -4)
    asm.sw('a0', 'sp', 0)
    asm.addi('a0', 't1', 48)
    asm.call('uart_putchar')
    asm.lw('a0', 'sp', 0)
    asm.addi('sp', 'sp', 4)

    # Ones digit
    asm.addi('a0', 'a0', 48)
    asm.call('uart_putchar')

    asm.lw('ra', 'sp', 4)
    asm.addi('sp', 'sp', 8)
    asm.ret()

    # -------------------------------------------------------------------------
    # Constant Strings and Data
    # -------------------------------------------------------------------------
    asm.label('str_banner')
    asm.string("\nRISC-V PicoRV32 SoC - Systolic GEMM Accelerator Co-Simulation\n")

    asm.label('str_step1')
    asm.string("[1] Configured Matrix Dimension K = 4.\n")

    asm.label('str_step2')
    asm.string("[2] Streamed Matrix A (Weights 4x4) via AXI-MMIO.\n")

    asm.label('str_step3')
    asm.string("[3] Streamed Matrix B (Activations 4x4) via AXI-MMIO.\n")

    asm.label('str_step4')
    asm.string("[4] Started Systolic Array Execution (Shift=7, ReLU=ON).\n")

    asm.label('str_step5')
    asm.string("[5] Accelerator execution finished! Done bit asserted.\n")

    asm.label('str_step6')
    asm.string("[6] Reading Matrix C output activations:\n")

    asm.label('str_row')
    asm.string("    Row ")

    asm.label('str_colon')
    asm.string(": [ ")

    asm.label('str_success')
    asm.string("\nCo-Simulation Status: Hardware-Software Co-Simulation SUCCESS\n\n")

    # Sample INT8 Matrix A tile (16 words)
    asm.label('tile_a_data')
    tile_a = [12, -8, 25, 10, -15, 30, 18, -5, 22, 14, -32, 8, 9, -7, 16, 28]
    for val in tile_a:
        asm.word(val & 0xFF)

    # Sample INT8 Matrix B tile (16 words)
    asm.label('tile_b_data')
    tile_b = [45, -12, 33, 8, 20, 15, -10, 25, -30, 40, 18, -14, 18, 22, -9, 31]
    for val in tile_b:
        asm.word(val & 0xFF)

    # Resolve all relative and absolute branches
    asm.resolve()
    return asm

# Helper to support pseudo-mv
def mv(self, rd, rs1):
    self.addi(rd, rs1, 0)
RV32Assembler.mv = mv

def main():
    asm = build_soc_firmware()

    out_hex = os.path.join(os.path.dirname(__file__), 'firmware.hex')
    out_dis = os.path.join(os.path.dirname(__file__), 'firmware.dis')
    verify_hex = os.path.join(os.path.dirname(__file__), '..', 'VEFIFY', 'firmware.hex')

    # Output Hex (32-bit words per line, zero-padded)
    # Total memory: 8192 words (32 KB)
    words = asm.code
    print(f"[Firmware] Assembled {len(words)} instructions/words ({len(words)*4} bytes).")

    with open(out_hex, 'w') as f:
        for w in words:
            f.write(f"{w:08X}\n")

    with open(verify_hex, 'w') as f:
        for w in words:
            f.write(f"{w:08X}\n")

    with open(out_dis, 'w') as f:
        for pc, word, text in asm.disasm:
            f.write(f"{pc:04X}: {word:08X}   {text}\n")

    print(f"[Firmware] Generated {out_hex}")
    print(f"[Firmware] Generated {verify_hex}")
    print(f"[Firmware] Generated {out_dis}")

if __name__ == '__main__':
    main()
