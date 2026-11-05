# -*- coding: utf-8 -*-
"""
Script: generate_5_deep_dive_gifs.py
Generates 5 deep-dive architectural animated GIFs requested for the graduation thesis:
1. figures/memory_wall_von_neumann.gif
2. figures/neural_network_general_architecture.gif
3. figures/soc_general_architecture.gif
4. figures/uvm_internal_communication.gif
5. figures/gen1_vs_gen2_deep_dive.gif
"""

import os
import sys
import math
from PIL import Image, ImageDraw, ImageFont

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR) if os.path.basename(CURRENT_DIR) == 'tools' else CURRENT_DIR
FIGURES_DIR = os.path.join(PROJECT_ROOT, "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

WIDTH, HEIGHT = 820, 460

# Palette
BG_DARK = (11, 15, 25)
PANEL_BG = (17, 24, 39)
CARD_BG = (24, 33, 53)
BORDER_DARK = (30, 41, 59)
BORDER_ACTIVE = (56, 189, 248)
CYAN = (56, 189, 248)
EMERALD = (16, 185, 129)
AMBER = (245, 158, 11)
ROSE = (244, 63, 94)
PURPLE = (168, 85, 247)
TEXT_WHITE = (248, 250, 252)
TEXT_MUTED = (148, 163, 184)
TEXT_DIM = (100, 116, 139)

font_dir = os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts')
FONTS = {
    'title': ImageFont.truetype(os.path.join(font_dir, 'segoeuib.ttf'), 16),
    'subtitle': ImageFont.truetype(os.path.join(font_dir, 'segoeui.ttf'), 11),
    'badge': ImageFont.truetype(os.path.join(font_dir, 'segoeuib.ttf'), 10),
    'mono_bold': ImageFont.truetype(os.path.join(font_dir, 'consolab.ttf'), 12),
    'mono': ImageFont.truetype(os.path.join(font_dir, 'consola.ttf'), 11),
    'mono_sm': ImageFont.truetype(os.path.join(font_dir, 'consola.ttf'), 9.5),
    'text': ImageFont.truetype(os.path.join(font_dir, 'segoeui.ttf'), 12),
    'text_bold': ImageFont.truetype(os.path.join(font_dir, 'segoeuib.ttf'), 12),
    'text_sm': ImageFont.truetype(os.path.join(font_dir, 'segoeui.ttf'), 10)
}

def draw_header(draw, title, subtitle, badge_text, badge_color):
    draw.rectangle([(15, 12), (WIDTH - 15, 60)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
    draw.text((28, 20), title, font=FONTS['title'], fill=TEXT_WHITE)
    draw.text((28, 41), subtitle, font=FONTS['subtitle'], fill=TEXT_MUTED)
    
    bbox = FONTS['badge'].getbbox(badge_text)
    bw = bbox[2] - bbox[0] + 16
    bx = WIDTH - 28 - bw
    by = 24
    draw.rectangle([(bx, by), (bx + bw, by + 22)], fill=(badge_color[0]//4, badge_color[1]//4, badge_color[2]//4), outline=badge_color, width=1)
    draw.text((bx + 8, by + 3), badge_text, font=FONTS['badge'], fill=badge_color)

def draw_footer(draw, text_left, text_right, accent_color=CYAN):
    draw.rectangle([(15, HEIGHT - 42), (WIDTH - 15, HEIGHT - 14)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
    draw.text((28, HEIGHT - 33), text_left, font=FONTS['text_sm'], fill=TEXT_MUTED)
    bbox = FONTS['badge'].getbbox(text_right)
    draw.text((WIDTH - 28 - (bbox[2] - bbox[0]), HEIGHT - 33), text_right, font=FONTS['badge'], fill=accent_color)

def save_gif(images, filename, durations):
    path = os.path.join(FIGURES_DIR, filename)
    quantized_images = [img.quantize(colors=128, method=Image.Quantize.MEDIANCUT) for img in images]
    quantized_images[0].save(
        path,
        save_all=True,
        append_images=quantized_images[1:],
        duration=durations,
        loop=0,
        optimize=True
    )
    size_kb = os.path.getsize(path) / 1024
    print(f"  [CREATED] {filename} ({len(images)} frames, {size_kb:.1f} KB)")
    return path


# ==============================================================================
# 1. MEMORY WALL TRONG VON NEUMANN VS SYSTOLIC ACCELERATOR
# ==============================================================================
def gen_gif_memory_wall():
    print("[1/5] Generating memory_wall_von_neumann.gif...")
    images = []
    
    stages = [
        ("Ki\u1ebfn tr\xfac Von Neumann truy\u1ec1n th\u1ed1ng: CPU v\xe0 DRAM k\u1ebft n\u1ed1i qua Bus he\u0323p", "1. BUS NGH\u1ebcN C\u1ed4 CHAI", 0, 1, 0, ROSE),
        ("CPU ph\u1ea3i \u0111\u1ecdc t\u1eebng to\xe1n h\u1ea1ng tr\u1ecdng s\u1ed1 A v\xe0 \u1ea3nh B qua DRAM: 90% th\u1eddi gian b\u1ecb STALL!", "2. CPU B\u1eca TREO (STALL)", 0, 2, 0, ROSE),
        ("Chi ph\xed n\u0103ng l\u01b0\u1ee3ng: \u0110\u1ecdc 1 byte t\u1eeb DRAM t\u1ed1n g\u1ea5p 200\xd7 l\u1ea7n so v\u1edbi th\u1ef1c hi\u1ec7n ph\xe9p t\xednh MAC!", "3. L\xc3NG PH\xcd N\u0102NG L\u01af\u1ee2NG", 0, 3, 0, AMBER),
        ("Gi\u1ea3i ph\xe1p M\u1ea3ng T\xe2m Thu (Systolic Array): T\xe1i s\u1eed d\u1ee5ng d\u1eef li\u1ec7u kh\xf4ng gian (Spatial Reuse)", "4. N\u1ea0P 1 L\u1ea6N V\xc0O SRAM", 1, 1, 1, CYAN),
        ("To\xe1n h\u1ea1ng n\u1ea1p 1 l\u1ea7n v\xe0o SRAM on-chip, tr\xf4i li\xean t\u1ee5c qua 64 PE kh\xf4ng c\u1ea7n truy xu\u1ea5t DRAM", "5. 64 PE T\xcdNH LI\xcaN T\u1ee4C", 1, 2, 2, EMERALD),
        ("Hi\u1ec7u su\u1ea5t v\u01b0\u1ee3t tr\u1ed9i: 64 MAC/cycle li\xean t\u1ee5c, kh\xf4ng c\xf3 b\u1ea5t k\u1ef3 chu k\u1ef3 treo n\xe0o do b\u1ed9 nh\u1edb!", "6. PH\xc1 B\u1ece MEMORY WALL", 1, 3, 3, EMERALD),
        ("T\u1ed5ng k\u1ebft: Gi\u1ea3m 98\xd7 s\u1ed1 l\u1ea7n truy xu\u1ea5t DRAM v\xe0 ti\u1ebft ki\u1ec7m 95% n\u0103ng l\u01b0\u1ee3ng to\xe0n h\u1ec7 th\u1ed1ng!", "7. T\u1ed0I \u01afU H\xd3A 100%", 1, 3, 3, CYAN)
    ]
    durations = [1200] * (len(stages) - 1) + [3500]
    
    for title_sub, badge_st, is_systolic, step_phase, bus_traffic, accent_col in stages:
        im = Image.new('RGB', (WIDTH, HEIGHT), BG_DARK)
        draw = ImageDraw.Draw(im)
        draw_header(draw, "N\xfat Th\u1eaft C\u1ed5 Chai B\u1ed9 Nh\u1edb (Memory Wall) Trong Von Neumann vs M\u1ea3ng T\xe2m Thu",
                    title_sub, badge_st, accent_col)
                    
        # Left Panel: Von Neumann CPU
        vx0, vy0 = 35, 78
        vw = 360
        draw.rectangle([(vx0, vy0), (vx0 + vw, vy0 + 280)], fill=PANEL_BG, outline=ROSE if not is_systolic else BORDER_DARK, width=2 if not is_systolic else 1)
        draw.text((vx0 + 16, vy0 + 14), "1. Ki\u1ebfn Tr\xfac Von Neumann (CPU/GPU Thu\u1ea7n)", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((vx0 + 16, vy0 + 32), "B\u1ecb gi\u1edbi h\u1ea1n b\u1edfi b\u0103ng th\xf4ng bus v\xe0 \u0111\u1ed9 tr\u1ec5 DRAM", font=FONTS['subtitle'], fill=ROSE)
        
        # CPU Box
        draw.rectangle([(vx0 + 20, vy0 + 58), (vx0 + 150, vy0 + 150)], fill=(45, 25, 35) if not is_systolic else CARD_BG, outline=ROSE if not is_systolic else BORDER_DARK)
        draw.text((vx0 + 30, vy0 + 70), "CPU Core", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((vx0 + 30, vy0 + 90), "ALU (1-MAC)", font=FONTS['mono_sm'], fill=TEXT_MUTED)
        alu_st = "STALLED (90%)" if not is_systolic else "IDLE"
        draw.text((vx0 + 30, vy0 + 115), alu_st, font=FONTS['badge'], fill=ROSE if not is_systolic else TEXT_DIM)
        
        # DRAM Box
        draw.rectangle([(vx0 + 230, vy0 + 58), (vx0 + vw - 20, vy0 + 150)], fill=CARD_BG, outline=BORDER_DARK)
        draw.text((vx0 + 242, vy0 + 70), "DRAM Ngo\xe0i", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((vx0 + 242, vy0 + 90), "Tr\u1ecdng s\u1ed1 W & \u1ea2nh", font=FONTS['text_sm'], fill=TEXT_MUTED)
        draw.text((vx0 + 242, vy0 + 115), "Tr\u1ec5: 50-100 chu k\u1ef3", font=FONTS['mono_sm'], fill=AMBER)
        
        # Narrow Bus line with traffic bottleneck
        draw.line([(vx0 + 150, vy0 + 104), (vx0 + 230, vy0 + 104)], fill=ROSE if not is_systolic else BORDER_DARK, width=3)
        draw.text((vx0 + 160, vy0 + 82), "Bus 32b", font=FONTS['mono_sm'], fill=ROSE if not is_systolic else TEXT_DIM)
        if not is_systolic:
            draw.text((vx0 + 158, vy0 + 112), "\u26a0 NGH\u1ebcN", font=FONTS['badge'], fill=ROSE)
            
        # Von Neumann Metrics
        draw.rectangle([(vx0 + 20, vy0 + 170), (vx0 + vw - 20, vy0 + 265)], fill=CARD_BG, outline=BORDER_DARK)
        draw.text((vx0 + 30, vy0 + 180), "\u0110\u1ecdc/Ghi DRAM: 2 \xd7 N^3 l\u1ea7n (Kh\xf4ng t\xe1i s\u1eed d\u1ee5ng)", font=FONTS['mono_sm'], fill=ROSE)
        draw.text((vx0 + 30, vy0 + 202), "Hi\u1ec7u su\u1ea5t ALU th\u1ef1c t\u1ebf: Ch\u1ec9 \u0111\u1ea1t 5% - 10%", font=FONTS['mono_sm'], fill=AMBER)
        draw.text((vx0 + 30, vy0 + 224), "Ti\xeau hao n\u0103ng l\u01b0\u1ee3ng: 90% n\u0103ng l\u01b0\u1ee3ng nu\u1ed1t v\xe0o Bus", font=FONTS['mono_sm'], fill=TEXT_MUTED)
        draw.text((vx0 + 30, vy0 + 244), "\u2717 Memory Wall l\xe0m t\u1ee5t d\u1ed1c to\xe0n b\u1ed9 h\u1ec7 th\u1ed1ng!", font=FONTS['badge'], fill=ROSE)
        
        # Right Panel: Systolic Array (Spatial Architecture)
        sx0 = vx0 + vw + 20
        sw = WIDTH - 35 - sx0
        draw.rectangle([(sx0, vy0), (sx0 + sw, vy0 + 280)], fill=PANEL_BG, outline=EMERALD if is_systolic else BORDER_DARK, width=2 if is_systolic else 1)
        draw.text((sx0 + 16, vy0 + 14), "2. M\u1ea3ng T\xe2m Thu 64 PE (Ki\u1ebfn Tr\xfac \u0110\u1ec1 T\xe0i)", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((sx0 + 16, vy0 + 32), "Ph\xe1 b\u1ecf Memory Wall nh\u1edd t\xe1i s\u1eed d\u1ee5ng d\u1eef li\u1ec7u kh\xf4ng gian", font=FONTS['subtitle'], fill=EMERALD)
        
        # On-chip SRAM Box
        draw.rectangle([(sx0 + 20, vy0 + 58), (sx0 + 130, vy0 + 150)], fill=CARD_BG, outline=BORDER_ACTIVE if is_systolic else BORDER_DARK)
        draw.text((sx0 + 28, vy0 + 70), "SRAM On-chip", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((sx0 + 28, vy0 + 90), "Buffer A & B", font=FONTS['mono_sm'], fill=CYAN)
        draw.text((sx0 + 28, vy0 + 115), "N\u1ea1p 1 l\u1ea7n (Lock)", font=FONTS['badge'], fill=EMERALD if is_systolic else TEXT_DIM)
        
        # 64 PE Array Box
        draw.rectangle([(sx0 + 165, vy0 + 58), (sx0 + sw - 20, vy0 + 150)],
                       fill=(25, 55, 45) if is_systolic else CARD_BG,
                       outline=EMERALD if is_systolic else BORDER_DARK)
        draw.text((sx0 + 178, vy0 + 70), "M\u1ea3ng 64 PE (8\xd78)", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((sx0 + 178, vy0 + 90), "Data tr\xf4i PE \u2194 PE", font=FONTS['mono_sm'], fill=EMERALD)
        draw.text((sx0 + 178, vy0 + 115), "100% C\xf4ng su\u1ea5t (64 MAC)", font=FONTS['badge'], fill=EMERALD if is_systolic else TEXT_DIM)
        
        # Dataflow Arrow from SRAM to Array
        draw.line([(sx0 + 130, vy0 + 104), (sx0 + 165, vy0 + 104)], fill=EMERALD if is_systolic else BORDER_DARK, width=3)
        draw.polygon([(sx0 + 165, vy0 + 99), (sx0 + 173, vy0 + 104), (sx0 + 165, vy0 + 109)], fill=EMERALD if is_systolic else BORDER_DARK)
        
        # Systolic Metrics
        draw.rectangle([(sx0 + 20, vy0 + 170), (sx0 + sw - 20, vy0 + 265)], fill=CARD_BG, outline=BORDER_DARK)
        draw.text((sx0 + 30, vy0 + 180), "\u0110\u1ecdc DRAM: Ch\u1ec9 2 \xd7 N^2 l\u1ea7n (Gi\u1ea3m 98\xd7 DRAM read)", font=FONTS['mono_sm'], fill=EMERALD)
        draw.text((sx0 + 30, vy0 + 202), "Hi\u1ec7u su\u1ea5t PE: \u0110\u1ea1t 100% tuy\u1ec7t \u0111\u1ed1i kh\xf4ng b\u1ecb stall", font=FONTS['mono_sm'], fill=CYAN)
        draw.text((sx0 + 30, vy0 + 224), "Ti\u1ebft ki\u1ec7m n\u0103ng l\u01b0\u1ee3ng: 95% n\u0103ng l\u01b0\u1ee3ng bus \u0111\u01b0\u1ee3c c\u1eaft gi\u1ea3m", font=FONTS['mono_sm'], fill=TEXT_MUTED)
        draw.text((sx0 + 30, vy0 + 244), "\u2713 PH\xc1 B\u1ece HO\xc0N TO\xc0N MEMORY WALL!", font=FONTS['badge'], fill=EMERALD)
        
        draw_footer(draw, "M\u1ea3ng t\xe2m thu gi\u1ea3i quy\u1ebft g\u1ed1c r\u1ec5 b\xe0i to\xe1n Memory Wall nh\u1edd t\xe1i s\u1eed d\u1ee5ng tr\u1ecdng s\u1ed1 t\u1ea1i ch\u1ed7 v\xe0 chuy\u1ec3n d\u1eef li\u1ec7u tr\u1ef1c ti\u1ebfp gi\u1eefa c\xe1c PE l\xe2n c\u1eadn.",
                    "MEMORY WALL BROKEN", EMERALD)
        images.append(im)
        
    save_gif(images, "memory_wall_von_neumann.gif", durations)


# ==============================================================================
# 2. SƠ ĐỒ KIẾN TRÚC MẠNG NEURAL TỔNG QUÁT (GENERIC CNN PIPELINE)
# ==============================================================================
def gen_gif_generic_cnn():
    print("[2/5] Generating neural_network_general_architecture.gif...")
    images = []
    
    stages = [
        ("\u1ea2nh \u0111\u1ea7u v\xe0o Input Tensor X [H\xd7W\xd7C_in]: Khung nh\xecn kh\xf4ng gian 2D/3D", "1. INPUT TENSOR", 0, CYAN),
        ("T\u1ea7ng Convolution (Conv2D): C\xe1c b\u1ed9 l\u1ecdc Kernel tr\u01b0\u1ee3t tr\xedch xu\u1ea5t c\xe1c \u0111\u1eb7c tr\u01b0ng c\u1ee5c b\u1ed9", "2. CONVOLUTION 2D", 1, ROSE),
        ("H\xe0m k\xedch ho\u1ea1t phi tuy\u1ebfn ReLU (max(0, x)): C\u1eaft b\u1ecf gi\xe1 tr\u1ecb \xe2m, t\u1ea1o t\xednh phi tuy\u1ebfn", "3. ACTIVATION RELU", 2, AMBER),
        ("T\u1ea7ng Gom C\u1ef1c \u0110\u1ea1i Max-Pooling: Gi\u1ea3m chi\u1ec1u kh\xf4ng gian 2\xd72, gi\u1eef l\u1ea1i n\xe9t n\u1ed5i b\u1eadt nh\u1ea5t", "4. MAX POOLING", 3, PURPLE),
        ("X\xe2u chu\u1ed7i \u0111a t\u1ea7ng (Deep Layers): Conv2 \u2192 ReLU \u2192 Pool tr\xedch xu\u1ea5t \u0111\u1eb7c tr\u01b0ng c\u1ea5p cao", "5. DEEP HIERARCHY", 4, CYAN),
        ("T\u1ea7ng Tr\u1ea3i Ph\u1eb3ng (Flatten): Bi\u1ebfn tensor 3D th\xe0nh vector \u0111\u1eb7c tr\u01b0ng 1D duy nh\u1ea5t", "6. FLATTEN 1D", 5, AMBER),
        ("T\u1ea7ng K\u1ebft N\u1ed1i \u0110\u1ea7y \u0110\u1ee7 (Fully Connected / Dense): Ph\xe9p nh\xe2n ma tr\u1eadn GEMM t\xednh Logits", "7. DENSE FC GEMM", 6, EMERALD),
        ("T\u1ea7ng Softmax & Ph\xe2n Lo\u1ea1i (Argmax): Xu\u1ea5t ph\xe2n b\u1ed1 x\xe1c su\u1ea5t v\xe0 nh\xe3n ch\u1eef s\u1ed1 d\u1ef1 \u0111o\xe1n", "8. SOFTMAX ARGMAX", 7, EMERALD)
    ]
    durations = [1200] * (len(stages) - 1) + [3500]
    
    layer_boxes = [
        ("Input", "X [H\xd7W]", "Grayscale / RGB", CYAN),
        ("Conv2D", "W [K\xd7K]", "T\xedch ch\u1eadp kh\xf4ng gian", ROSE),
        ("ReLU", "max(0, x)", "Phi tuy\u1ebfn h\xf3a", AMBER),
        ("MaxPool", "Pool 2\xd72", "Gi\u1ea3m chi\u1ec1u (S=2)", PURPLE),
        ("Deep Conv", "L\u1edbp s\xe2u", "Hierarchical rep", CYAN),
        ("Flatten", "Vector 1D", "Tr\u1ea3i ph\u1eb3ng vector", AMBER),
        ("Dense FC", "GEMM", "Ma tr\u1eadn \xd7 Vector", EMERALD),
        ("Softmax", "Argmax", "X\xe1c su\u1ea5t l\u1edbp", EMERALD)
    ]
    
    for title_sub, badge_st, act_idx, accent_col in stages:
        im = Image.new('RGB', (WIDTH, HEIGHT), BG_DARK)
        draw = ImageDraw.Draw(im)
        draw_header(draw, "S\u01a1 \u0110\u1ed3 Ki\u1ebfn Tr\xfac M\u1ea1ng N\u01a1-ron Ch\u1eadp T\u1ed5ng Qu\xe1t (Generic Deep CNN Pipeline)",
                    title_sub, badge_st, accent_col)
                    
        # Pipeline Strip
        sx0, sy0 = 25, 80
        box_w = 88
        box_h = 175
        gap = 10
        
        for b_i, (b_title, b_math, b_desc, b_col) in enumerate(layer_boxes):
            bx = sx0 + b_i * (box_w + gap)
            is_active = (b_i == act_idx)
            is_past = (b_i < act_idx)
            
            fill_c = (45, 55, 80) if is_active else ((25, 45, 40) if is_past else CARD_BG)
            out_c = accent_col if is_active else (EMERALD if is_past else BORDER_DARK)
            
            draw.rectangle([(bx, sy0), (bx + box_w, sy0 + box_h)], fill=fill_c, outline=out_c, width=2 if is_active else 1)
            draw.text((bx + 8, sy0 + 10), b_title, font=FONTS['mono_bold'], fill=TEXT_WHITE)
            draw.text((bx + 8, sy0 + 32), b_math, font=FONTS['mono_sm'], fill=b_col if is_active else CYAN)
            
            # Mini Visual Icon
            draw.rectangle([(bx + 8, sy0 + 55), (bx + box_w - 8, sy0 + 115)], fill=(15, 20, 32), outline=BORDER_DARK)
            if b_i == 0:
                # 2D Grid
                for r in range(3):
                    for c in range(3):
                        draw.rectangle([(bx + 16 + c * 18, sy0 + 64 + r * 15), (bx + 30 + c * 18, sy0 + 75 + r * 15)], fill=(50, 70, 95))
            elif b_i == 1:
                # 3x3 filter
                draw.rectangle([(bx + 20, sy0 + 65), (bx + 68, sy0 + 105)], outline=ROSE, width=2)
                draw.text((bx + 28, sy0 + 78), "3\xd73", font=FONTS['mono'], fill=ROSE)
            elif b_i == 2:
                # ReLU ramp
                draw.line([(bx + 18, sy0 + 100), (bx + 44, sy0 + 100)], fill=AMBER, width=2)
                draw.line([(bx + 44, sy0 + 100), (bx + 70, sy0 + 70)], fill=AMBER, width=2)
            elif b_i == 3:
                # 2x2 Pool
                draw.rectangle([(bx + 25, sy0 + 68), (bx + 63, sy0 + 102)], outline=PURPLE, width=1)
                draw.text((bx + 30, sy0 + 78), "2\xd72", font=FONTS['mono'], fill=PURPLE)
            elif b_i == 4:
                # Stack of maps
                draw.rectangle([(bx + 18, sy0 + 70), (bx + 55, sy0 + 105)], outline=CYAN, width=1)
                draw.rectangle([(bx + 28, sy0 + 65), (bx + 65, sy0 + 100)], outline=CYAN, width=1)
            elif b_i == 5:
                # 1D column
                for ci in range(5):
                    draw.rectangle([(bx + 34, sy0 + 62 + ci * 10), (bx + 54, sy0 + 70 + ci * 10)], fill=AMBER)
            elif b_i == 6:
                # Synaptic network
                for si in range(3):
                    draw.line([(bx + 20, sy0 + 70 + si * 16), (bx + 68, sy0 + 80)], fill=EMERALD, width=1)
                    draw.line([(bx + 20, sy0 + 70 + si * 16), (bx + 68, sy0 + 96)], fill=EMERALD, width=1)
            elif b_i == 7:
                # Softmax bars
                draw.rectangle([(bx + 20, sy0 + 95), (bx + 30, sy0 + 105)], fill=CYAN)
                draw.rectangle([(bx + 35, sy0 + 65), (bx + 45, sy0 + 105)], fill=EMERALD)
                draw.rectangle([(bx + 50, sy0 + 85), (bx + 60, sy0 + 105)], fill=CYAN)
                
            draw.text((bx + 8, sy0 + 125), b_desc, font=FONTS['mono_sm'], fill=TEXT_MUTED)
            draw.text((bx + 8, sy0 + 150), f"T\u1ea7ng #{b_i+1}", font=FONTS['badge'], fill=b_col if is_past or is_active else TEXT_DIM)
            
            # Connector arrow
            if b_i < 7:
                ar_x = bx + box_w + 1
                draw.line([(ar_x, sy0 + 88), (ar_x + 6, sy0 + 88)], fill=BORDER_ACTIVE if is_past or is_active else BORDER_DARK, width=2)
                
        # Lower Detail Box: Mathematical Mapping to Systolic Array
        ly0 = sy0 + box_h + 16
        lw = WIDTH - 50
        lh = 95
        draw.rectangle([(sx0, ly0), (sx0 + lw, ly0 + lh)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((sx0 + 16, ly0 + 12), "\xc1nh X\u1ea1 Ph\u1ea7n C\u1ee9ng L\xean M\u1ea3ng T\xe2m Thu 64 PE:", font=FONTS['text_bold'], fill=TEXT_WHITE)
        
        map_text = "T\u1ea5t c\u1ea3 c\xe1c t\u1ea7ng Conv2D v\xe0 Dense FC \u0111\u1ec1u \u0111\u01b0\u1ee3c quy v\u1ec1 ph\xe9p to\xe1n GEMM: C = A \xd7 B + Bias"
        draw.text((sx0 + 16, ly0 + 34), map_text, font=FONTS['mono_bold'], fill=CYAN)
        draw.text((sx0 + 16, ly0 + 54), "\u2022 Conv2D \u2192 Thu\u1eadt to\xe1n im2col tr\u1ea3i ph\u1eb3ng c\u1eeda s\u1ed5 tr\u01b0\u1ee3t th\xe0nh vector B [9\xd71] n\u1ea1p v\xe0o m\u1ea3ng 64 PE.", font=FONTS['text_sm'], fill=TEXT_MUTED)
        draw.text((sx0 + 16, ly0 + 72), "\u2022 Dense FC \u2192 Ph\xe9p nh\xe2n ma tr\u1eadn tr\u1ecdng s\u1ed1 [10\xd73136] v\u1edbi vector ng\xf5 v\xe0o [3136\xd71] qua c\u01a1 ch\u1ebf Tiling 8\xd78.", font=FONTS['text_sm'], fill=EMERALD)
        
        draw_footer(draw, "Ki\u1ebfn tr\xfac m\u1ea1ng CNN to\xe0n di\u1ec7n \u0111\u01b0\u1ee3c \u00e1nh x\u1ea1 100% v\xe0o l\xf5i t\xe2m thu 64 PE v\xe0 b\u1ed9 l\u01b0\u1ee3ng t\u1eed h\xf3a ph\u1ea7n c\u1ee9ng.",
                    "GENERIC CNN MAPPED", EMERALD)
        images.append(im)
        
    save_gif(images, "neural_network_general_architecture.gif", durations)


# ==============================================================================
# 3. KIẾN TRÚC SOC TỔNG QUÁT (FULL SYSTEM-ON-CHIP TOPOLOGY)
# ==============================================================================
def gen_gif_soc_architecture():
    print("[3/5] Generating soc_general_architecture.gif...")
    images = []
    
    stages = [
        ("Kh\u1edfi \u0111\u1ed9ng h\u1ec7 th\u1ed1ng SoC tr\xean chip: Clock 50 MHz, Reset \u0111\u1ed3ng b\u1ed9", "1. SOC RESET", 0, CYAN),
        ("Vi x\u1eed l\xfd Host PicoRV32 (RISC-V 32-bit): N\u1ea1p ch\u01b0\u01a1ng tr\xecnh Firmware C t\u1eeb ROM", "2. PICORV32 CPU", 1, ROSE),
        ("Tr\u1ee5c giao ti\u1ebfp Bus AMBA AXI4-Lite: Ph\xe2n ph\u1ed1i l\u1ec7nh v\xe0 \u0111\u1ecba ch\u1ec9 MMIO", "3. AXI4-LITE BUS", 2, AMBER),
        ("B\u1ed9 nh\u1edb \u0111\u1ec7m SRAM On-chip: matrix_buffer_a (Tr\u1ecdng s\u1ed1) & matrix_buffer_b (\u1ea2nh)", "4. ON-CHIP SRAM", 3, PURPLE),
        ("L\xf5i B\u1ed9 T\u0103ng T\u1ed1c: 64 PE Output-Stationary th\u1ef1c hi\u1ec7n nh\xe2n ma tr\u1eadn 64 MAC/cycle", "5. SYSTOLIC ARRAY", 4, EMERALD),
        ("Kh\u1ed1i L\u01b0\u1ee3ng T\u1eed H\xf3a SIMD 8 k\xeanh: X\u1ea3 ng\xf5 ra song song v\xe0o matrix_buffer_c", "6. SIMD QUANTIZERS", 5, EMERALD),
        ("Ngo\u1ea1i vi SoC: UART Console k\u1ebft n\u1ed1i PC, LEDR[9:0], LED 7 \u0111o\u1ea1n HEX0 tr\xecnh di\u1ec5n", "7. PERIPHERALS", 6, CYAN),
        ("H\u1ec7 th\u1ed1ng SoC kh\xe9p k\xedn ho\xe0n to\xe0n: T\u0103ng t\u1ed1c 173.7x so v\u1edbi ch\u1ea1y ph\u1ea7n m\u1ec1m CPU thu\u1ea7n", "8. 173.7x SPEEDUP", 7, EMERALD)
    ]
    durations = [1200] * (len(stages) - 1) + [3500]
    
    for title_sub, badge_st, act_idx, accent_col in stages:
        im = Image.new('RGB', (WIDTH, HEIGHT), BG_DARK)
        draw = ImageDraw.Draw(im)
        draw_header(draw, "Ki\u1ebfn Tr\xfac H\u1ec7 Th\u1ed1ng Tr\xean Chip T\u1ed5ng Qu\xe1t (SoC Top-Level Architecture)",
                    title_sub, badge_st, accent_col)
                    
        # Chip Boundary Box
        cx0, cy0 = 35, 76
        cw = WIDTH - 70
        ch = 285
        draw.rectangle([(cx0, cy0), (cx0 + cw, cy0 + ch)], fill=PANEL_BG, outline=BORDER_DARK, width=2)
        draw.text((cx0 + 16, cy0 + 12), "Cyclone II / Cyclone V FPGA SoC Boundary (soc_top_de2 / de10)", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((cx0 + 16, cy0 + 28), "Clock: 50.00 MHz | FMAX: 69.49 MHz | AXI4-Lite Interconnect", font=FONTS['subtitle'], fill=TEXT_MUTED)
        
        # 1. CPU Box (Top-Left)
        cpu_act = (act_idx in [1, 7])
        draw.rectangle([(cx0 + 16, cy0 + 55), (cx0 + 200, cy0 + 145)], fill=(45, 55, 80) if cpu_act else CARD_BG, outline=CYAN if cpu_act else BORDER_DARK, width=2 if cpu_act else 1)
        draw.text((cx0 + 26, cy0 + 65), "Host CPU Core", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((cx0 + 26, cy0 + 85), "PicoRV32 (RV32I)", font=FONTS['mono_bold'], fill=CYAN if cpu_act else TEXT_MUTED)
        draw.text((cx0 + 26, cy0 + 105), "Firmware Bare-metal C", font=FONTS['mono_sm'], fill=TEXT_DIM)
        draw.text((cx0 + 26, cy0 + 122), "[AXI Master]", font=FONTS['badge'], fill=EMERALD if cpu_act else TEXT_DIM)
        
        # 2. Main AXI Bus Backbone (Center Vertical Stripe)
        bus_act = (act_idx in [2, 7])
        draw.rectangle([(cx0 + 225, cy0 + 55), (cx0 + 315, cy0 + 265)], fill=(56, 189, 248, 40) if bus_act else CARD_BG, outline=CYAN if bus_act else BORDER_DARK, width=2 if bus_act else 1)
        draw.text((cx0 + 235, cy0 + 75), "AMBA", font=FONTS['mono_bold'], fill=CYAN)
        draw.text((cx0 + 235, cy0 + 95), "AXI4-Lite", font=FONTS['mono_bold'], fill=CYAN)
        draw.text((cx0 + 235, cy0 + 115), "Crossbar", font=FONTS['mono_sm'], fill=TEXT_MUTED)
        draw.text((cx0 + 235, cy0 + 155), "32-bit", font=FONTS['mono_sm'], fill=AMBER)
        draw.text((cx0 + 235, cy0 + 175), "Decoupled", font=FONTS['mono_sm'], fill=AMBER)
        draw.text((cx0 + 235, cy0 + 215), "No Deadlock", font=FONTS['badge'], fill=EMERALD)
        
        # 3. Accelerator Core IP (Right Panel)
        acc_act = (act_idx in [3, 4, 5, 7])
        draw.rectangle([(cx0 + 340, cy0 + 55), (cx0 + cw - 16, cy0 + 265)], fill=(30, 45, 60) if acc_act else CARD_BG, outline=EMERALD if acc_act else BORDER_DARK, width=2 if acc_act else 1)
        draw.text((cx0 + 355, cy0 + 68), "CNN Accelerator Custom IP Core (systolic_gemm_axi_lite.sv)", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((cx0 + 355, cy0 + 86), "MMIO Base: 0x1000_0000 | 64 PE Systolic Core | 8 SIMD Quantizers", font=FONTS['subtitle'], fill=EMERALD if acc_act else TEXT_MUTED)
        
        # Sub-blocks inside Accelerator Core:
        # A. SRAM Buffers
        sram_act = (act_idx == 3)
        draw.rectangle([(cx0 + 355, cy0 + 110), (cx0 + 490, cy0 + 185)], fill=(45, 55, 80) if sram_act else (15, 20, 32), outline=PURPLE if sram_act else BORDER_DARK)
        draw.text((cx0 + 365, cy0 + 118), "SRAM Buffers", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((cx0 + 365, cy0 + 138), "Buf A: 128B (W)", font=FONTS['mono_sm'], fill=PURPLE)
        draw.text((cx0 + 365, cy0 + 155), "Buf B: 128B (X)", font=FONTS['mono_sm'], fill=CYAN)
        draw.text((cx0 + 365, cy0 + 168), "Buf C: 64B (Out)", font=FONTS['mono_sm'], fill=EMERALD)
        
        # B. 64-PE Array
        mesh_act = (act_idx == 4)
        draw.rectangle([(cx0 + 505, cy0 + 110), (cx0 + cw - 30, cy0 + 185)], fill=(25, 55, 45) if mesh_act else (15, 20, 32), outline=EMERALD if mesh_act else BORDER_DARK)
        draw.text((cx0 + 518, cy0 + 118), "M\u1ea3ng T\xe2m Thu 64 PE", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((cx0 + 518, cy0 + 138), "8\xd78 Mesh (Output-Stationary)", font=FONTS['mono_sm'], fill=EMERALD)
        draw.text((cx0 + 518, cy0 + 155), "64 INT8 MACs / Chu k\u1ef3", font=FONTS['mono_bold'], fill=TEXT_WHITE)
        draw.text((cx0 + 518, cy0 + 168), "Peak: 4.45 GOP/s @ 69 MHz", font=FONTS['mono_sm'], fill=AMBER)
        
        # C. 8 SIMD Quantizers
        simd_act = (act_idx == 5)
        draw.rectangle([(cx0 + 355, cy0 + 200), (cx0 + cw - 30, cy0 + 252)], fill=(45, 35, 60) if simd_act else (15, 20, 32), outline=AMBER if simd_act else BORDER_DARK)
        draw.text((cx0 + 365, cy0 + 208), "8\xd7 Quantizer SIMD Song Song & Saturation Clamp (Gen-2 Pipelined)", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((cx0 + 365, cy0 + 228), "X\u1ea3 8 c\u1ed9t \u0111\u1ed3ng th\u1eddi trong 8 chu k\u1ef3 \u2192 \u0110\xf3ng g\xf3i 4-INT8 v\xe0o Word 32-bit", font=FONTS['mono_sm'], fill=AMBER if simd_act else TEXT_MUTED)
        
        # 4. Peripherals Box (Bottom-Left)
        peri_act = (act_idx == 6)
        draw.rectangle([(cx0 + 16, cy0 + 165), (cx0 + 200, cy0 + 265)], fill=(45, 55, 80) if peri_act else CARD_BG, outline=CYAN if peri_act else BORDER_DARK, width=2 if peri_act else 1)
        draw.text((cx0 + 26, cy0 + 175), "Ngo\u1ea1i Vi FPGA", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((cx0 + 26, cy0 + 195), "UART (115200 Baud)", font=FONTS['mono_sm'], fill=CYAN)
        draw.text((cx0 + 26, cy0 + 215), "LED 7-\u0110o\u1ea1n HEX0..5", font=FONTS['mono_sm'], fill=EMERALD)
        draw.text((cx0 + 26, cy0 + 235), "10\xd7 LEDR, 4\xd7 KEY, SW", font=FONTS['mono_sm'], fill=AMBER)
        
        # Connective arrows
        draw.line([(cx0 + 200, cy0 + 100), (cx0 + 225, cy0 + 100)], fill=CYAN, width=2)
        draw.line([(cx0 + 200, cy0 + 215), (cx0 + 225, cy0 + 215)], fill=CYAN, width=2)
        draw.line([(cx0 + 315, cy0 + 160), (cx0 + 340, cy0 + 160)], fill=EMERALD, width=2)
        
        draw_footer(draw, "Ki\u1ebfn tr\xfac SoC to\xe0n di\u1ec7n k\u1ebft h\u1ee3p vi x\u1eed l\xfd RISC-V, bus chu\u1ea9n AMBA AXI4-Lite v\xe0 b\u1ed9 t\u0103ng t\u1ed1c t\xe2m thu 64 PE gi\xfap gia t\u1ed1c 173.7x to\xe0n h\u1ec7 th\u1ed1ng.",
                    "COMPLETE SOC TOPOLOGY", EMERALD)
        images.append(im)
        
    save_gif(images, "soc_general_architecture.gif", durations)


# ==============================================================================
# 4. KIẾN TRÚC UVM GIAO TIẾP VỚI NHAU BÊN TRONG (TLM INTERNAL DATAFLOW)
# ==============================================================================
def gen_gif_uvm_internal():
    print("[4/5] Generating uvm_internal_communication.gif...")
    images = []
    
    stages = [
        ("UVM Sequence: Sinh ng\u1eabu nhi\xean c\xf3 r\xe0ng bu\u1ed9c gemm_sequence_item (INT8, Backpressure)", "1. SEQUENCE GEN", 0, CYAN),
        ("TLM Export: Sequencer ph\xe2n ph\u1ed1i item xu\u1ed1ng Driver qua seq_item_port.get_next_item()", "2. TLM SEQUENCER", 1, ROSE),
        ("UVM Driver: Chuy\u1ec3n \u0111\u1ed5i transaction th\xe0nh d\u1ea1ng s\xf3ng logic tr\xean virtual interface gemm_if", "3. DRIVER \u2192 PINS", 2, AMBER),
        ("Thi\u1ebft b\u1ecb DUT: systolic_gemm_axi_lite th\u1ef1c thi ph\xe9p nh\xe2n ma tr\u1eadn trong 37 chu k\u1ef3", "4. DUT EXECUTE", 3, PURPLE),
        ("UVM Monitor: L\u1eafng nghe th\u1ee5 \u0111\u1ed9ng c\xe1c ch\xe2n bus vif.cb, \u0111\xf3ng g\xf3i l\u1ea1i transaction ng\xf5 ra", "5. MONITOR SNOOP", 4, CYAN),
        ("TLM Analysis Port: Broadcast song song g\xf3i tin sang Scoreboard v\xe0 Coverage Collector", "6. TLM BROADCAST", 5, AMBER),
        ("Scoreboard: So s\xe1nh Bit-true t\u1eebng byte ng\xf5 ra DUT v\u1edbi m\xf4 h\xecnh to\xe1n Python Golden Model", "7. BIT-TRUE MATCH", 6, EMERALD),
        ("Coverage Collector: \u0110\xf3ng k\xedn 88/88 functional coverage bins \u2192 100.00% COVERAGE CLOSED!", "8. 100% COVERAGE", 7, EMERALD)
    ]
    durations = [1200] * (len(stages) - 1) + [3500]
    
    for title_sub, badge_st, act_idx, accent_col in stages:
        im = Image.new('RGB', (WIDTH, HEIGHT), BG_DARK)
        draw = ImageDraw.Draw(im)
        draw_header(draw, "Ki\u1ebfn Tr\xfac UVM Giao Ti\u1ebfp B\xean Trong Qua TLM (IEEE 1800 UVM 1.1c)",
                    title_sub, badge_st, accent_col)
                    
        # Left: Stimulus Generation (Sequence & Sequencer)
        sx0, sy0 = 35, 78
        sw = 185
        draw.rectangle([(sx0, sy0), (sx0 + sw, sy0 + 280)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((sx0 + 14, sy0 + 14), "1. Ph\xe1t K\xedch Th\xedch (Stimulus)", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((sx0 + 14, sy0 + 32), "Constrained-Random", font=FONTS['subtitle'], fill=CYAN)
        
        # Sequence Box
        seq_act = (act_idx == 0)
        draw.rectangle([(sx0 + 15, sy0 + 58), (sx0 + sw - 15, sy0 + 140)], fill=(45, 55, 80) if seq_act else CARD_BG, outline=CYAN if seq_act else BORDER_DARK, width=2 if seq_act else 1)
        draw.text((sx0 + 24, sy0 + 68), "uvm_sequence", font=FONTS['mono_bold'], fill=TEXT_WHITE)
        draw.text((sx0 + 24, sy0 + 88), "gemm_item", font=FONTS['mono'], fill=CYAN)
        draw.text((sx0 + 24, sy0 + 108), "Corner / Stress", font=FONTS['mono_sm'], fill=AMBER)
        
        # Sequencer Box
        sqr_act = (act_idx == 1)
        draw.rectangle([(sx0 + 15, sy0 + 160), (sx0 + sw - 15, sy0 + 245)], fill=(45, 55, 80) if sqr_act else CARD_BG, outline=ROSE if sqr_act else BORDER_DARK, width=2 if sqr_act else 1)
        draw.text((sx0 + 24, sy0 + 170), "uvm_sequencer", font=FONTS['mono_bold'], fill=TEXT_WHITE)
        draw.text((sx0 + 24, sy0 + 190), "Arbitration FIFO", font=FONTS['mono_sm'], fill=TEXT_MUTED)
        draw.text((sx0 + 24, sy0 + 215), "seq_item_export", font=FONTS['badge'], fill=ROSE)
        
        # Center: Driver, Interface & DUT
        cx0 = sx0 + sw + 15
        cw = 295
        draw.rectangle([(cx0, sy0), (cx0 + cw, sy0 + 280)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((cx0 + 14, sy0 + 14), "2. M\xf4i Tr\u01b0\u1eddng Driver / Interface / DUT", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((cx0 + 14, sy0 + 32), "Chuy\u1ec3n \u0111\u1ed5i Transaction \u2194 D\u1ea1ng s\xf3ng Pin", font=FONTS['subtitle'], fill=TEXT_MUTED)
        
        # Driver Box
        drv_act = (act_idx == 2)
        draw.rectangle([(cx0 + 15, sy0 + 58), (cx0 + cw - 15, sy0 + 115)], fill=(45, 55, 80) if drv_act else CARD_BG, outline=AMBER if drv_act else BORDER_DARK, width=2 if drv_act else 1)
        draw.text((cx0 + 24, sy0 + 68), "uvm_driver", font=FONTS['mono_bold'], fill=TEXT_WHITE)
        draw.text((cx0 + 24, sy0 + 88), "seq_item_port.get_next_item() \u2192 Wiggle Pins", font=FONTS['mono_sm'], fill=AMBER)
        
        # Virtual Interface
        vif_act = (act_idx in [2, 3, 4])
        draw.rectangle([(cx0 + 15, sy0 + 128), (cx0 + cw - 15, sy0 + 185)], fill=(30, 45, 60) if vif_act else CARD_BG, outline=BORDER_ACTIVE if vif_act else BORDER_DARK)
        draw.text((cx0 + 24, sy0 + 138), "virtual gemm_if.cb (Clocking Block)", font=FONTS['mono_bold'], fill=CYAN)
        draw.text((cx0 + 24, sy0 + 158), "clk, rst_n, start, busy, a_data, b_data, valid_out", font=FONTS['mono_sm'], fill=TEXT_MUTED)
        
        # DUT Box
        dut_act = (act_idx == 3)
        draw.rectangle([(cx0 + 15, sy0 + 198), (cx0 + cw - 15, sy0 + 265)], fill=(25, 55, 45) if dut_act else CARD_BG, outline=EMERALD if dut_act else BORDER_DARK, width=2 if dut_act else 1)
        draw.text((cx0 + 24, sy0 + 208), "DUT: systolic_gemm_axi_lite.sv", font=FONTS['mono_bold'], fill=TEXT_WHITE)
        draw.text((cx0 + 24, sy0 + 228), "64 PE Systolic Core | 37 Cycles Exec", font=FONTS['mono_sm'], fill=EMERALD)
        draw.text((cx0 + 24, sy0 + 245), "[HARDWARE UNDER TEST]", font=FONTS['badge'], fill=EMERALD)
        
        # Right: Monitor, Scoreboard & Coverage
        rx0 = cx0 + cw + 15
        rw = WIDTH - 25 - rx0
        draw.rectangle([(rx0, sy0), (rx0 + rw, sy0 + 280)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((rx0 + 14, sy0 + 14), "3. Ph\xe2n T\xedch & \u0110\u1ed1i So\xe1t", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((rx0 + 14, sy0 + 32), "TLM Analysis Broadcast", font=FONTS['subtitle'], fill=EMERALD)
        
        # Monitor
        mon_act = (act_idx == 4)
        draw.rectangle([(rx0 + 15, sy0 + 58), (rx0 + rw - 15, sy0 + 115)], fill=(45, 55, 80) if mon_act else CARD_BG, outline=CYAN if mon_act else BORDER_DARK, width=2 if mon_act else 1)
        draw.text((rx0 + 24, sy0 + 68), "uvm_monitor", font=FONTS['mono_bold'], fill=TEXT_WHITE)
        draw.text((rx0 + 24, sy0 + 88), "analysis_port.write(item)", font=FONTS['mono_sm'], fill=CYAN)
        
        # Scoreboard
        scb_act = (act_idx in [5, 6])
        draw.rectangle([(rx0 + 15, sy0 + 128), (rx0 + rw - 15, sy0 + 195)], fill=(25, 55, 45) if scb_act else CARD_BG, outline=EMERALD if scb_act else BORDER_DARK, width=2 if scb_act else 1)
        draw.text((rx0 + 24, sy0 + 138), "uvm_scoreboard", font=FONTS['mono_bold'], fill=TEXT_WHITE)
        draw.text((rx0 + 24, sy0 + 156), "Python Golden Model Ref", font=FONTS['mono_sm'], fill=TEXT_MUTED)
        draw.text((rx0 + 24, sy0 + 174), "10,000/10,000 Passed (0 L\u1ed7i)", font=FONTS['mono_bold'], fill=EMERALD)
        
        # Coverage Collector
        cov_act = (act_idx == 7)
        draw.rectangle([(rx0 + 15, sy0 + 208), (rx0 + rw - 15, sy0 + 265)], fill=(25, 55, 45) if cov_act else CARD_BG, outline=EMERALD if cov_act else BORDER_DARK, width=2 if cov_act else 1)
        draw.text((rx0 + 24, sy0 + 216), "gemm_coverage", font=FONTS['mono_bold'], fill=TEXT_WHITE)
        draw.text((rx0 + 24, sy0 + 234), "88 / 88 Bins Closed", font=FONTS['mono_sm'], fill=EMERALD)
        draw.text((rx0 + 24, sy0 + 248), "100.00% COVERAGE \u2713", font=FONTS['badge'], fill=EMERALD)
        
        # Inter-block connective TLM lines
        draw.line([(sx0 + sw - 15, sy0 + 200), (cx0 + 15, sy0 + 85)], fill=ROSE, width=2)
        draw.line([(cx0 + cw - 15, sy0 + 155), (rx0 + 15, sy0 + 85)], fill=CYAN, width=2)
        draw.line([(rx0 + 90, sy0 + 115), (rx0 + 90, sy0 + 128)], fill=EMERALD, width=2)
        draw.line([(rx0 + 90, sy0 + 195), (rx0 + 90, sy0 + 208)], fill=EMERALD, width=2)
        
        draw_footer(draw, "Ki\u1ebfn tr\xfac UVM 1.1c v\u1edbi c\u01a1 ch\u1ebf TLM decoupling gi\xfap t\xe1ch r\u1eddi ho\xe0n to\xe0n kh\u1ed1i sinh d\u1eef li\u1ec7u, kh\u1ed1i l\xe1i bus, v\xe0 kh\u1ed1i ch\u1ea5m \u0111i\u1ec3m bit-true.",
                    "100.00% UVM VERIFIED", EMERALD)
        images.append(im)
        
    save_gif(images, "uvm_internal_communication.gif", durations)


# ==============================================================================
# 5. KIẾN TRÚC GEN-1 VS GEN-2 DEEP DIVE (TẠI SAO GEN-2 CHẠY NHANH HƠN?)
# ==============================================================================
def gen_gif_gen1_vs_gen2_deep_dive():
    print("[5/5] Generating gen1_vs_gen2_deep_dive.gif...")
    images = []
    
    stages = [
        ("So s\xe1nh chuy\xean s\xe2u ki\u1ebfn tr\xfac: Kh\u1ed1i t\xe2m thu 8\xd78 (64 PE) gi\u1eef nguy\xean gi\u1eefa 2 th\u1ebf h\u1ec7", 0, 0, CYAN),
        ("C\u1ea3 Gen-1 v\xe0 Gen-2 \u0111\u1ec1u ho\xe0n t\u1ea5t qu\xe1 tr\xecnh t\xednh to\xe1n nh\xe2n ma tr\u1eadn trong 22 chu k\u1ef3", 22, 22, AMBER),
        ("\u0110i\u1ec3m ngh\u1ebdn c\u1ed1t l\xf5i: Giai \u0111o\u1ea1n DRAIN thu gom k\u1ebft qu\u1ea3 t\xedch l\u0169y 32-bit v\xe0 l\u01b0\u1ee3ng t\u1eed h\xf3a INT8", 23, 23, ROSE),
        ("Gen-1 d\xf9ng 1 QUANTIZER \u0110\u01a0N L\u1eba: Ph\u1ea3i \u0111\u1ecdc l\u1ea7n l\u01b0\u1ee3t 64 ph\u1ea7n t\u1eed \u2192 M\u1ea4T 64 CHU K\u1ef2 DRAIN!", 30, 26, ROSE),
        ("Gen-2 b\u1ed1 tr\xed 8 QUANTIZER SIMD SONG SONG: X\u1ea3 8 c\u1ed9t c\xf9ng l\xfac \u2192 CH\u1ec8 M\u1ea4T 8 CHU K\u1ef2 DRAIN!", 37, 30, EMERALD),
        ("K\u1ebft h\u1ee3p \u0111\xf3ng g\xf3i 4-INT8 v\xe0o Word 32-bit: Gen-2 ho\xe0n t\u1ea5t to\xe0n b\u1ed9 \u1edf CHU K\u1ef2 37!", 50, 37, EMERALD),
        ("Gen-1 v\u1eabn \u0111ang ch\u1eadm ch\u1ea1p x\u1ea3 t\u1eebng ph\u1ea7n t\u1eed tr\xean bus 8-bit h\u1eb9p (Chu k\u1ef3 70...)", 70, 37, ROSE),
        ("Gen-1 m\u1ea5t t\u1ed5ng c\u1ed9ng 101 chu k\u1ef3 m\u1edbi xong \u2192 Gen-2 gi\u1ea3m 63.4% th\u1eddi gian, t\u0103ng t\u1ed1c +60.2% l\xf5i!", 101, 37, EMERALD)
    ]
    durations = [1300] * (len(stages) - 1) + [3800]
    
    for title_sub, c_g1, c_g2, accent_col in stages:
        im = Image.new('RGB', (WIDTH, HEIGHT), BG_DARK)
        draw = ImageDraw.Draw(im)
        draw_header(draw, "Ki\u1ebfn Tr\xfac Gen-1 vs Gen-2 Deep Dive: T\u1ea1i Sao Gen-2 Ch\u1ea1y Nhanh H\u01a1n?",
                    title_sub, f"DRAIN: 8 CYCLES vs 64 CYCLES (-87.5%)", accent_col)
                    
        # Left Panel: Gen-1 Architecture
        gx0, gy0 = 35, 78
        gw = 360
        draw.rectangle([(gx0, gy0), (gx0 + gw, gy0 + 280)], fill=PANEL_BG, outline=ROSE if c_g1 == 101 else BORDER_DARK, width=2 if c_g1 == 101 else 1)
        draw.text((gx0 + 16, gy0 + 14), "Gen-1 (Tu\u1ea7n T\u1ef1 - 1 Quantizer)", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((gx0 + 16, gy0 + 32), "\u0110i\u1ec3m ngh\u1ebdn Drain: 64 chu k\u1ef3 tu\u1ea7n t\u1ef1 | Bus 8-bit", font=FONTS['subtitle'], fill=ROSE)
        
        # Micro diagram Gen-1
        draw.rectangle([(gx0 + 16, gy0 + 58), (gx0 + 180, gy0 + 145)], fill=CARD_BG, outline=BORDER_DARK)
        draw.text((gx0 + 24, gy0 + 68), "8\xd78 Mesh", font=FONTS['mono_bold'], fill=TEXT_WHITE)
        draw.text((gx0 + 24, gy0 + 88), "64 PEs", font=FONTS['mono'], fill=CYAN)
        draw.text((gx0 + 24, gy0 + 108), "22 Cycles MAC", font=FONTS['mono_sm'], fill=TEXT_MUTED)
        
        # 1 Single Quantizer Box
        draw.rectangle([(gx0 + 205, gy0 + 58), (gx0 + gw - 16, gy0 + 145)], fill=(45, 25, 35), outline=ROSE, width=2)
        draw.text((gx0 + 215, gy0 + 68), "1\xd7 Quantizer", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((gx0 + 215, gy0 + 90), "\u0110\u01a1n l\u1ebb (Serial)", font=FONTS['mono_sm'], fill=ROSE)
        draw.text((gx0 + 215, gy0 + 110), "64 Cycles Drain", font=FONTS['mono_bold'], fill=ROSE)
        
        # Single arrow PE -> 1 Quantizer
        draw.line([(gx0 + 180, gy0 + 101), (gx0 + 205, gy0 + 101)], fill=ROSE, width=2)
        
        # Gen-1 Latency Breakdown
        draw.rectangle([(gx0 + 16, gy0 + 160), (gx0 + gw - 16, gy0 + 265)], fill=CARD_BG, outline=BORDER_DARK)
        draw.text((gx0 + 24, gy0 + 170), "Ph\xe2n r\xe3 chu k\u1ef3 Gen-1:", font=FONTS['text_sm'], fill=TEXT_MUTED)
        draw.text((gx0 + 24, gy0 + 188), "Load & Skew:  15 chu k\u1ef3", font=FONTS['mono_sm'], fill=TEXT_MUTED)
        draw.text((gx0 + 24, gy0 + 205), "MAC Compute:  22 chu k\u1ef3", font=FONTS['mono_sm'], fill=TEXT_MUTED)
        draw.text((gx0 + 24, gy0 + 222), "Drain x\u1ea3 ng\xf5 ra: 64 chu k\u1ef3 (Ngh\u1ebdn 63.4% th\u1eddi gian!)", font=FONTS['mono_sm'], fill=ROSE)
        draw.text((gx0 + 24, gy0 + 242), f"T\u1ed5ng th\u1ef1c thi: 101 Chu k\u1ef3 | Ti\u1ebfn \u0111\u1ed9: {c_g1}/101", font=FONTS['mono_bold'], fill=ROSE)
        
        # Right Panel: Gen-2 Architecture
        hx0 = gx0 + gw + 20
        hw = WIDTH - 35 - hx0
        draw.rectangle([(hx0, gy0), (hx0 + hw, gy0 + 280)], fill=PANEL_BG, outline=EMERALD if c_g2 == 37 else BORDER_DARK, width=2 if c_g2 == 37 else 1)
        draw.text((hx0 + 16, gy0 + 14), "Gen-2 (Pipelined SIMD - 8 Quantizers)", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((hx0 + 16, gy0 + 32), "8 Quantizer SIMD song song | \u0110\xf3ng g\xf3i 4-INT8 Word", font=FONTS['subtitle'], fill=EMERALD)
        
        # Micro diagram Gen-2
        draw.rectangle([(hx0 + 16, gy0 + 58), (hx0 + 175, gy0 + 145)], fill=CARD_BG, outline=BORDER_DARK)
        draw.text((hx0 + 24, gy0 + 68), "8\xd78 Mesh", font=FONTS['mono_bold'], fill=TEXT_WHITE)
        draw.text((hx0 + 24, gy0 + 88), "64 PEs", font=FONTS['mono'], fill=CYAN)
        draw.text((hx0 + 24, gy0 + 108), "22 Cycles MAC", font=FONTS['mono_sm'], fill=TEXT_MUTED)
        
        # 8 Parallel Quantizers Box
        draw.rectangle([(hx0 + 200, gy0 + 58), (hx0 + hw - 16, gy0 + 145)], fill=(25, 55, 45), outline=EMERALD, width=2)
        draw.text((hx0 + 210, gy0 + 68), "8\xd7 Quantizers", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((hx0 + 210, gy0 + 90), "Song song (SIMD)", font=FONTS['mono_sm'], fill=EMERALD)
        draw.text((hx0 + 210, gy0 + 110), "8 Cycles Drain!", font=FONTS['mono_bold'], fill=EMERALD)
        
        # Multi-arrows PE -> 8 Quantizers
        for ai in range(3):
            draw.line([(hx0 + 175, gy0 + 85 + ai * 16), (hx0 + 200, gy0 + 85 + ai * 16)], fill=EMERALD, width=2)
            
        # Gen-2 Latency Breakdown
        draw.rectangle([(hx0 + 16, gy0 + 160), (hx0 + hw - 16, gy0 + 265)], fill=CARD_BG, outline=BORDER_DARK)
        draw.text((hx0 + 24, gy0 + 170), "Ph\xe2n r\xe3 chu k\u1ef3 Gen-2:", font=FONTS['text_sm'], fill=TEXT_MUTED)
        draw.text((hx0 + 24, gy0 + 188), "Load & Skew:   7 chu k\u1ef3 (Pipelined)", font=FONTS['mono_sm'], fill=TEXT_MUTED)
        draw.text((hx0 + 24, gy0 + 205), "MAC Compute:  22 chu k\u1ef3", font=FONTS['mono_sm'], fill=TEXT_MUTED)
        draw.text((hx0 + 24, gy0 + 222), "Drain x\u1ea3 ng\xf5 ra:  8 chu k\u1ef3 (Gi\u1ea3m 8\xd7 th\u1eddi gian drain!)", font=FONTS['mono_sm'], fill=EMERALD)
        draw.text((hx0 + 24, gy0 + 242), f"T\u1ed5ng th\u1ef1c thi:  37 Chu k\u1ef3 (-63.4%) | Ti\u1ebfn \u0111\u1ed9: {c_g2}/37", font=FONTS['mono_bold'], fill=EMERALD)
        
        draw_footer(draw, "Nguy\xean nh\xe2n Gen-2 nhanh h\u01a1n Gen-1: Thay th\u1ebf b\u1ed9 l\u01b0\u1ee3ng t\u1eed \u0111\u01a1n b\u1eb1ng 8 quantizer SIMD gi\u1ea3m chu k\u1ef3 drain t\u1eeb 64 xu\u1ed1ng 8, k\u1ebft h\u1ee3p bus 32-bit.",
                    "CORE SPEEDUP +60.2%", EMERALD)
        images.append(im)
        
    save_gif(images, "gen1_vs_gen2_deep_dive.gif", durations)


def main():
    print("=" * 78)
    print("STARTING GENERATION OF 5 DEEP-DIVE ARCHITECTURAL GIFS")
    print("=" * 78)
    
    gen_gif_memory_wall()
    gen_gif_generic_cnn()
    gen_gif_soc_architecture()
    gen_gif_uvm_internal()
    gen_gif_gen1_vs_gen2_deep_dive()
    
    print("=" * 78)
    print("ALL 5 DEEP-DIVE GIFS GENERATED SUCCESSFULLY IN figures/!")
    print("=" * 78)

if __name__ == '__main__':
    main()
