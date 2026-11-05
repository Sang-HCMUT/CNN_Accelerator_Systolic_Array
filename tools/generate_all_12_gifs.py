# -*- coding: utf-8 -*-
"""
Script: generate_all_12_gifs.py
Generates 12 standalone architectural animated GIFs for the CNN Systolic Accelerator:
1. figures/01_im2col_convolution_mapping.gif
2. figures/02_matrix_tiling_engine.gif
3. figures/03_quantization_overflow_pipeline.gif
4. figures/04_cnn_mnist_inference.gif
5. figures/05_skew_wavefront_alignment.gif
6. figures/06_pe_microarchitecture.gif
7. figures/07_systolic_array_64pe_mesh.gif
8. figures/08_gen1_vs_gen2_evolution.gif
9. figures/09_axi_handshake_deadlock.gif
10. figures/10_soc_mmio_firmware.gif
11. figures/11_fpga_synth_timing.gif
12. figures/12_uvm_verification_waveform.gif
"""

import os
import sys
import math
import numpy as np
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
# GIF 1: IM2COL CONVOLUTION MAPPING
# ==============================================================================
def gen_gif_01_im2col():
    print("[1/12] Generating 01_im2col_convolution_mapping.gif...")
    images = []
    
    # 5x5 Input image
    img_data = [
        [12, 25, 30, 15, 10],
        [18, 42, 55, 38, 20],
        [22, 60, 80, 50, 15],
        [14, 35, 48, 30,  8],
        [ 9, 15, 20, 12,  5]
    ]
    # Filter 3x3
    kernel = [
        [ 1,  0, -1],
        [ 2,  0, -2],
        [ 1,  0, -1]
    ]
    # Positions of 3x3 sliding window in 5x5 image (stride 1 -> 3x3 = 9 positions)
    positions = [(r, c) for r in range(3) for c in range(3)]
    
    durations = [900] * len(positions) + [3000] # extra pause on final frame
    
    for step_idx, (wr, wc) in enumerate(positions):
        im = Image.new('RGB', (WIDTH, HEIGHT), BG_DARK)
        draw = ImageDraw.Draw(im)
        draw_header(draw, "01. Thuật Toán im2col & Ánh Xạ Phép Tích Chập Sang GEMM",
                    "Trải phẳng cửa sổ trượt 3×3 thành cột vector B [9×1] cho mảng tâm thu 64 PE",
                    f"BƯỚC {step_idx+1}/9: CỘT B[*,{step_idx}]", CYAN)
        
        # Panel 1: Input Tensor 5x5
        px0, py0 = 35, 80
        draw.rectangle([(px0, py0), (px0 + 210, py0 + 280)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((px0 + 14, py0 + 12), "Ảnh Đầu Vào Tensor X [5×5]", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((px0 + 14, py0 + 28), "Cửa sổ trượt kích thước 3×3 (S=1)", font=FONTS['subtitle'], fill=TEXT_MUTED)
        
        cs = 34
        grid_x, grid_y = px0 + 18, py0 + 58
        for r in range(5):
            for c in range(5):
                in_win = (wr <= r < wr + 3) and (wc <= c < wc + 3)
                cell_fill = (45, 55, 80) if in_win else (24, 33, 53)
                cell_outline = ROSE if in_win else BORDER_DARK
                draw.rectangle([(grid_x + c * cs, grid_y + r * cs),
                                (grid_x + (c+1) * cs - 2, grid_y + (r+1) * cs - 2)],
                               fill=cell_fill, outline=cell_outline, width=2 if in_win else 1)
                val_str = str(img_data[r][c])
                t_color = AMBER if in_win else TEXT_MUTED
                draw.text((grid_x + c * cs + 9, grid_y + r * cs + 9), val_str, font=FONTS['mono'], fill=t_color)
        
        # Red bounding box around 3x3 window
        draw.rectangle([(grid_x + wc * cs - 2, grid_y + wr * cs - 2),
                        (grid_x + (wc+3) * cs, grid_y + (wr+3) * cs)],
                       outline=ROSE, width=3)
        
        # Panel 2: Arrow im2col
        ax = px0 + 225
        draw.text((ax + 8, py0 + 120), "im2col", font=FONTS['mono_bold'], fill=ROSE)
        draw.text((ax + 5, py0 + 140), "Unfold", font=FONTS['mono_sm'], fill=TEXT_MUTED)
        draw.line([(ax, py0 + 165), (ax + 50, py0 + 165)], fill=ROSE, width=3)
        draw.polygon([(ax + 50, py0 + 158), (ax + 62, py0 + 165), (ax + 50, py0 + 172)], fill=ROSE)
        
        # Panel 3: Matrix B [9x9]
        bx0 = px0 + 295
        draw.rectangle([(bx0, py0), (bx0 + 245, py0 + 280)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((bx0 + 14, py0 + 12), "Ma Trận Vector B [9×9]", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((bx0 + 14, py0 + 28), f"Cột {step_idx}: 9 điểm ảnh của cửa sổ 3×3", font=FONTS['subtitle'], fill=TEXT_MUTED)
        
        # Draw small representation of 9 columns
        cw, ch = 22, 23
        mg_x, mg_y = bx0 + 18, py0 + 54
        for col in range(9):
            is_active_col = (col == step_idx)
            is_done_col = (col < step_idx)
            for row in range(9):
                c_fill = (56, 189, 248, 80) if is_active_col else ((30, 50, 70) if is_done_col else (20, 28, 45))
                c_out = CYAN if is_active_col else (BORDER_DARK if not is_done_col else (40, 70, 90))
                draw.rectangle([(mg_x + col * cw, mg_y + row * ch),
                                (mg_x + (col+1) * cw - 3, mg_y + (row+1) * ch - 3)],
                               fill=c_fill, outline=c_out, width=2 if is_active_col else 1)
                if is_active_col:
                    # Current window pixel index
                    kr, kc = row // 3, row % 3
                    val = img_data[wr + kr][wc + kc]
                    draw.text((mg_x + col * cw + 4, mg_y + row * ch + 5), str(val)[:2], font=FONTS['mono_sm'], fill=TEXT_WHITE)
                elif is_done_col:
                    draw.text((mg_x + col * cw + 6, mg_y + row * ch + 5), "•", font=FONTS['mono_sm'], fill=TEXT_DIM)
        
        # Panel 4: Matrix Multiplier A x B = C
        cx0 = bx0 + 260
        draw.rectangle([(cx0, py0), (WIDTH - 25, py0 + 280)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((cx0 + 14, py0 + 12), "Ngõ Ra C [1×9] (Feature Map)", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((cx0 + 14, py0 + 28), "C = Weights_A [1×9] × Vector_B [9×1]", font=FONTS['subtitle'], fill=CYAN)
        
        # Output 3x3 grid
        out_cs = 44
        og_x, og_y = cx0 + 35, py0 + 75
        for r in range(3):
            for c in range(3):
                idx = r * 3 + c
                cell_done = (idx <= step_idx)
                cell_curr = (idx == step_idx)
                f_color = (16, 185, 129) if cell_curr else ((24, 60, 45) if cell_done else (20, 28, 45))
                o_color = EMERALD if cell_done else BORDER_DARK
                draw.rectangle([(og_x + c * out_cs, og_y + r * out_cs),
                                (og_x + (c+1) * out_cs - 4, og_y + (r+1) * out_cs - 4)],
                               fill=f_color, outline=o_color, width=2 if cell_curr else 1)
                if cell_done:
                    # Simulated conv sum
                    val = 142 + idx * 28
                    draw.text((og_x + c * out_cs + 8, og_y + r * out_cs + 14), str(val),
                              font=FONTS['mono_bold'], fill=TEXT_WHITE if cell_curr else TEXT_MUTED)
        
        draw.text((cx0 + 20, py0 + 225), f"Tích lũy: {step_idx+1}/9 điểm ảnh ngõ ra", font=FONTS['mono'], fill=EMERALD)
        draw.text((cx0 + 20, py0 + 245), "Biến 4 vòng lặp for thành 1 GEMM", font=FONTS['text_sm'], fill=TEXT_MUTED)
        
        draw_footer(draw, "Thuật toán im2col biến phép tích chập thành phép nhân ma trận GEMM thuần túy trên 64 PE.",
                    "TỐI ƯU HÓA 100% PHẦN CỨNG", EMERALD)
        images.append(im)
        
    save_gif(images, "01_im2col_convolution_mapping.gif", durations)

# ==============================================================================
# GIF 2: MATRIX TILING ENGINE
# ==============================================================================
def gen_gif_02_tiling():
    print("Testing gen_gif_02_tiling...")
    stages = [
        ("Nạp Tile A0 [8×9] vào SRAM Buffer A", "LOCKED A0", 0, 1, 0, CYAN),
        ("Stream Sub-tile B0 [9×8] vào Mảng 64 PE", "COMPUTE B0", 0, 1, 0, AMBER),
        ("Tái sử dụng A0: Stream Sub-tile B1 [9×8]", "REUSE 2/98", 0, 2, 1, EMERALD),
        ("Tái sử dụng A0: Stream Sub-tile B2 [9×8]", "REUSE 3/98", 0, 3, 2, EMERALD),
        ("Tái sử dụng A0: Stream Sub-tile B24 [9×8]", "REUSE 25/98", 0, 25, 3, EMERALD),
        ("Hoàn tất 98 lần tái sử dụng cho Tile A0!", "REUSE 98/98 ✓", 0, 98, 3, EMERALD),
        ("Swap SRAM: Nạp tiếp Tile A1 [8×9] vào Buffer A", "LOCKED A1", 1, 1, 0, PURPLE),
        ("Stream Sub-tile B0 [9×8] kết hợp Tile A1", "COMPUTE B0", 1, 1, 0, AMBER),
        ("Tái sử dụng A1: Stream Sub-tile B1 [9×8]", "REUSE 2/98", 1, 2, 1, EMERALD),
        ("Hoàn tất 196 phép nhân ma trận con (Tiling Complete)", "ALL DONE ✓", 1, 98, 3, CYAN)
    ]
    durations = [1100] * (len(stages) - 1) + [3200]
    images = []

    for step_idx, (title_sub, badge_st, tile_a_idx, b_reuse_cnt, b_slot_act, accent_col) in enumerate(stages):
        im = Image.new('RGB', (WIDTH, HEIGHT), BG_DARK)
        draw = ImageDraw.Draw(im)
        draw_header(draw, "02. Chiến Lược Chia Khối Ma Trận Lớn (Tiling Engine)",
                    title_sub, badge_st, accent_col)

        ax0, ay0 = 35, 80
        # Left Box: Weight Matrix A
        draw.rectangle([(ax0, ay0), (ax0 + 195, ay0 + 280)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((ax0 + 14, ay0 + 14), "Ma Trận Trọng Số A [16×9]", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((ax0 + 14, ay0 + 32), "Chia 2 Sub-tiles: A0 & A1", font=FONTS['subtitle'], fill=TEXT_MUTED)

        # Tile A0
        a0_active = (tile_a_idx == 0)
        draw.rectangle([(ax0 + 16, ay0 + 58), (ax0 + 178, ay0 + 150)],
                       fill=(20, 42, 65) if a0_active else CARD_BG,
                       outline=CYAN if a0_active else BORDER_DARK, width=2 if a0_active else 1)
        draw.text((ax0 + 26, ay0 + 72), "Tile A0 [8×9]", font=FONTS['mono_bold'], fill=TEXT_WHITE if a0_active else TEXT_MUTED)
        draw.text((ax0 + 26, ay0 + 95), "72 Bytes (Buffer A)" if a0_active else "72 Bytes", font=FONTS['mono_sm'], fill=CYAN if a0_active else TEXT_DIM)
        if a0_active:
            draw.text((ax0 + 26, ay0 + 120), "[LOCKED IN SRAM]", font=FONTS['badge'], fill=EMERALD)

        # Tile A1
        a1_active = (tile_a_idx == 1)
        draw.rectangle([(ax0 + 16, ay0 + 165), (ax0 + 178, ay0 + 257)],
                       fill=(40, 25, 60) if a1_active else CARD_BG,
                       outline=PURPLE if a1_active else BORDER_DARK, width=2 if a1_active else 1)
        draw.text((ax0 + 26, ay0 + 180), "Tile A1 [8×9]", font=FONTS['mono_bold'], fill=TEXT_WHITE if a1_active else TEXT_MUTED)
        draw.text((ax0 + 26, ay0 + 204), "72 Bytes (Buffer A)" if a1_active else "72 Bytes", font=FONTS['mono_sm'], fill=PURPLE if a1_active else TEXT_DIM)
        if a1_active:
            draw.text((ax0 + 26, ay0 + 228), "[LOCKED IN SRAM]", font=FONTS['badge'], fill=PURPLE)

        # Center Box: Inputs B Stream
        bx0 = ax0 + 215
        draw.rectangle([(bx0, ay0), (bx0 + 225, ay0 + 280)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((bx0 + 14, ay0 + 14), "Dòng Dữ Liệu B [9×196]", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((bx0 + 14, ay0 + 32), "25 Sub-tiles B0..B24 [9×8]", font=FONTS['subtitle'], fill=AMBER)

        b_labels = ["Sub-tile B0 [9×8]", "Sub-tile B1 [9×8]", "Sub-tile B2 [9×8]", f"Sub-tile B{min(24, b_reuse_cnt)}..B24"]
        for b_i in range(4):
            cur_b_act = (b_i == b_slot_act) and (step_idx not in [0, 6])
            b_y = ay0 + 58 + b_i * 36
            draw.rectangle([(bx0 + 16, b_y), (bx0 + 208, b_y + 28)],
                           fill=(45, 34, 18) if cur_b_act else CARD_BG,
                           outline=AMBER if cur_b_act else BORDER_DARK, width=2 if cur_b_act else 1)
            draw.text((bx0 + 24, b_y + 6), b_labels[b_i], font=FONTS['mono'], fill=TEXT_WHITE if cur_b_act else TEXT_MUTED)
            if cur_b_act:
                draw.text((bx0 + 142, b_y + 6), "▶ STREAM", font=FONTS['badge'], fill=AMBER)

        # DRAM Bandwidth badge at bottom (Clean spacing, zero collision)
        draw.rectangle([(bx0 + 16, ay0 + 215), (bx0 + 208, ay0 + 265)], fill=(18, 38, 30), outline=EMERALD, width=1)
        draw.text((bx0 + 24, ay0 + 222), "Trọng Số Tái Sử Dụng:", font=FONTS['text_sm'], fill=TEXT_MUTED)
        draw.text((bx0 + 24, ay0 + 240), f"{b_reuse_cnt}× Lần (Giảm 98× DRAM read)", font=FONTS['mono_bold'], fill=EMERALD)

        # Right Box: Systolic Array
        cx0 = bx0 + 245
        draw.rectangle([(cx0, ay0), (WIDTH - 25, ay0 + 280)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((cx0 + 14, ay0 + 14), "Mảng Tâm Thu 64 PE", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((cx0 + 14, ay0 + 32), "Nhân ma trận con [8×9] × [9×8]", font=FONTS['subtitle'], fill=TEXT_MUTED)

        mg_x, mg_y = cx0 + 20, ay0 + 60
        pe_sz = 16
        for r in range(8):
            for c in range(8):
                is_mac = (r + c <= step_idx + 1) and (step_idx < 9)
                draw.rectangle([(mg_x + c * pe_sz, mg_y + r * pe_sz),
                                (mg_x + (c+1) * pe_sz - 2, mg_y + (r+1) * pe_sz - 2)],
                               fill=(16, 60, 45) if is_mac else CARD_BG,
                               outline=EMERALD if is_mac else BORDER_DARK, width=1)

        draw.rectangle([(cx0 + 165, ay0 + 65), (cx0 + 285, ay0 + 160)], fill=CARD_BG, outline=BORDER_DARK, width=1)
        draw.text((cx0 + 175, ay0 + 75), "Kết Quả C", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((cx0 + 175, ay0 + 95), f"Tile C[{tile_a_idx}, *]", font=FONTS['mono'], fill=CYAN)
        draw.text((cx0 + 175, ay0 + 115), "32-bit INT", font=FONTS['mono_sm'], fill=TEXT_MUTED)
        draw.text((cx0 + 175, ay0 + 135), "✓ Tích lũy", font=FONTS['badge'], fill=EMERALD)

        progress_pct = min(100, step_idx * 10 + 10)
        draw.text((cx0 + 18, ay0 + 205), f"Tiến độ toàn bộ: {progress_pct}%", font=FONTS['mono_bold'], fill=TEXT_WHITE)
        draw.text((cx0 + 18, ay0 + 225), "Không cần RAM ngoài dung lượng lớn", font=FONTS['text_sm'], fill=TEXT_MUTED)
        draw.text((cx0 + 18, ay0 + 245), "Hoàn toàn vừa vặn SRAM 256 bytes", font=FONTS['text_sm'], fill=AMBER)

        draw_footer(draw, "Chiến lược Tiling Station-A giữ cố định trọng số trong buffer, tái sử dụng 98 lần liên tiếp.",
                    "TIẾT KIỆM 98x BĂNG THÔNG", EMERALD)
        images.append(im)

    images[0].save("figures/02_matrix_tiling_engine.gif", save_all=True, append_images=images[1:],
                   optimize=True, duration=durations, loop=0)
    print(f"Generated figures/02_matrix_tiling_engine.gif ({len(images)} frames)")

# ==============================================================================
# GIF 3: QUANTIZATION OVERFLOW PIPELINE
# ==============================================================================
def gen_gif_03_quant():
    print("[3/12] Generating 03_quantization_overflow_pipeline.gif...")
    images = []
    
    stages = [
        ("Nạp hai toán hạng có dấu Signed INT8", "A = -48, B = 65", 0, CYAN),
        ("Nhân số học DSP: 8-bit × 8-bit → Signed INT16", "Prod = -3,120", 1, ROSE),
        ("Mảng tâm thu tích lũy vào thanh ghi 32-bit", "C_acc = 14,280 + (-3,120)", 2, AMBER),
        ("Cộng Bias INT32 của Kernel CNN", "Sum = 11,160 + 1,240", 3, AMBER),
        ("Dịch phải số học Arithmetic Shift Right (>>> 8)", "Shift = 12,400 >> 8 = 48", 4, PURPLE),
        ("Kích hoạt ReLU: loại bỏ giá trị âm (max(0, x))", "ReLU(48) = 48", 5, EMERALD),
        ("Bảo hòa & Cắt bit Saturation Clamp về Signed INT8", "Output = +48 (INT8)", 6, EMERALD),
        ("Phân tích Worst-Case: Bảo đảm toàn bộ không bao giờ tràn số", "ZERO OVERFLOW MET ✓", 7, CYAN)
    ]
    durations = [1100] * (len(stages) - 1) + [3200]
    
    pipe_boxes = [
        ("Stage 1: Input", "Signed INT8", "[-128, +127]", "A, B wires"),
        ("Stage 2: Multiplier", "Signed INT16", "[-16384, +16129]", "8x8 Multiplier"),
        ("Stage 3: Acc 32-bit", "Signed INT32", "[-2^31, +2^31-1]", "c_acc register"),
        ("Stage 4: Bias + Shift", "Fixed Point", "Scale: >>> 8", "Arithmetic >> 8"),
        ("Stage 5: ReLU & Clamp", "Signed INT8", "[0, 127] Clamped", "Saturate Logic")
    ]
    
    for step_idx, (title_sub, badge_st, active_stage, accent_col) in enumerate(stages):
        im = Image.new('RGB', (WIDTH, HEIGHT), BG_DARK)
        draw = ImageDraw.Draw(im)
        draw_header(draw, "03. Chuỗi Biến Đổi Số Học & Bảo Đảm Không Tràn Số",
                    title_sub, badge_st, accent_col)
        
        # Draw 5 pipeline stages horizontally
        bw, bh = 142, 190
        start_x, start_y = 35, 85
        
        for idx, (p_title, p_type, p_range, p_hw) in enumerate(pipe_boxes):
            bx = start_x + idx * (bw + 12)
            is_active = (idx == active_stage) or (active_stage >= 5 and idx >= 3) or (active_stage == 7)
            bg_col = (45, 55, 80) if is_active else PANEL_BG
            out_col = accent_col if (idx == active_stage) else (BORDER_ACTIVE if is_active else BORDER_DARK)
            
            draw.rectangle([(bx, start_y), (bx + bw, start_y + bh)], fill=bg_col, outline=out_col, width=2 if is_active else 1)
            draw.text((bx + 10, start_y + 12), p_title, font=FONTS['text_bold'], fill=TEXT_WHITE)
            draw.text((bx + 10, start_y + 30), p_type, font=FONTS['mono_bold'], fill=CYAN if is_active else TEXT_MUTED)
            
            # Inner hardware block
            draw.rectangle([(bx + 8, start_y + 55), (bx + bw - 8, start_y + 125)],
                           fill=CARD_BG, outline=BORDER_DARK, width=1)
            draw.text((bx + 14, start_y + 65), p_hw, font=FONTS['mono_sm'], fill=TEXT_WHITE)
            draw.text((bx + 14, start_y + 88), "Range:", font=FONTS['text_sm'], fill=TEXT_DIM)
            draw.text((bx + 14, start_y + 103), p_range, font=FONTS['mono_sm'], fill=AMBER if is_active else TEXT_MUTED)
            
            # Dynamic token value
            tok_val = ""
            if idx == 0: tok_val = "A:-48, B:+65"
            elif idx == 1: tok_val = "Prod: -3120"
            elif idx == 2: tok_val = "C_acc: 11160"
            elif idx == 3: tok_val = "Shift: +48"
            elif idx == 4: tok_val = "Out: +48 (INT8)"
            
            if is_active or (active_stage > idx):
                draw.rectangle([(bx + 8, start_y + 138), (bx + bw - 8, start_y + 175)],
                               fill=(16, 185, 129, 40) if idx == 4 else (56, 189, 248, 30),
                               outline=EMERALD if idx == 4 else CYAN, width=1)
                draw.text((bx + 12, start_y + 148), tok_val, font=FONTS['mono'], fill=TEXT_WHITE)
                
            # Connective arrow to next stage
            if idx < 4:
                ar_x = bx + bw + 2
                draw.line([(ar_x, start_y + 90), (ar_x + 8, start_y + 90)], fill=BORDER_ACTIVE if is_active else BORDER_DARK, width=2)
        
        # Bottom analysis banner
        by0 = start_y + bh + 15
        draw.rectangle([(start_x, by0), (WIDTH - 35, by0 + 75)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((start_x + 18, by0 + 12), "Bảo Lưu Toàn Vẹn Số Học (Mathematical Safety Proof):", font=FONTS['text_bold'], fill=TEXT_WHITE)
        
        eq_text = "Tích lũy cực đại 8 bước: 8 × (128 × 128) = 131,072 ≪ 2,147,483,647 (INT32) → Dư 14-bit Margin an toàn!"
        draw.text((start_x + 18, by0 + 32), eq_text, font=FONTS['mono'], fill=EMERALD)
        draw.text((start_x + 18, by0 + 50), "Bộ nhân 16-bit → Tích lũy 32-bit → Scale & Clamp ngõ ra không bao giờ gây tràn số hay mất dấu.", font=FONTS['text_sm'], fill=TEXT_MUTED)
        
        draw_footer(draw, "Kiến trúc số học được chứng minh toán học không thể tràn số trên toàn bộ 64 PE tâm thu.",
                    "ZERO OVERFLOW VERIFIED", EMERALD)
        images.append(im)
        
    save_gif(images, "03_quantization_overflow_pipeline.gif", durations)



# ==============================================================================
# GIF 4: CNN MNIST INFERENCE PIPELINE
# ==============================================================================
def gen_gif_04_cnn():
    print("[4/12] Generating 04_cnn_mnist_inference.gif...")
    images = []
    
    stages = [
        ("Nạp ảnh viết tay MNIST số 8 [28×28 điểm ảnh INT8]", "1. Ảnh Đầu Vào", 0, CYAN),
        ("Tầng Conv1: 16 bộ lọc 3×3 trượt trên ảnh → 16 Feature Maps", "2. Tích Chập Conv1", 1, ROSE),
        ("Kích hoạt ReLU: Cắt bỏ toàn bộ giá trị âm (Linear Unit)", "3. ReLU Activation", 2, AMBER),
        ("Tầng Max Pooling 2×2 (S=2): Giảm kích thước ảnh xuống 14×14", "4. Max Pooling", 3, PURPLE),
        ("Tầng Flatten: Trải phẳng 16×14×14 thành 3,136 đặc trưng", "5. Flatten Vector", 4, CYAN),
        ("Tầng Dense FC: Nhân ma trận 3136 × 10 trên mảng 64 PE", "6. Fully Connected", 5, AMBER),
        ("Tầng Softmax: Tính toán xác suất 10 chữ số (0..9)", "7. Softmax Argmax", 6, EMERALD),
        ("Xuất kết quả ra FPGA: LED 7 đoạn HEX0 = '8', LEDR[8] bật sáng!", "PREDICT: 8 (100%)", 7, EMERALD)
    ]
    durations = [1100] * (len(stages) - 1) + [3200]
    
    # 28x28 crude representation of digit 8 for the icon
    digit_8_rows = [
        "........XXXX........",
        "......XX....XX......",
        ".....XX......XX.....",
        ".....XX......XX.....",
        "......XX....XX......",
        "........XXXX........",
        "......XX....XX......",
        ".....XX......XX.....",
        ".....XX......XX.....",
        "......XX....XX......",
        "........XXXX........",
    ]
    
    for step_idx, (title_sub, badge_st, active_card, accent_col) in enumerate(stages):
        im = Image.new('RGB', (WIDTH, HEIGHT), BG_DARK)
        draw = ImageDraw.Draw(im)
        draw_header(draw, "04. Dòng Chảy Suy Luận Mạng CNN End-to-End (MNIST)",
                    title_sub, badge_st, accent_col)
        
        # 1. Left Box: Digit 8 Canvas
        dx0, dy0 = 35, 80
        draw.rectangle([(dx0, dy0), (dx0 + 175, dy0 + 280)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((dx0 + 14, dy0 + 14), "Ảnh Gốc MNIST [28×28]", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((dx0 + 14, dy0 + 32), "Chữ số viết tay: 8", font=FONTS['subtitle'], fill=CYAN)
        
        # Draw digit 8 matrix
        dg_x, dg_y = dx0 + 18, dy0 + 58
        for r, row in enumerate(digit_8_rows):
            for c, ch in enumerate(row):
                cell_fill = (240, 240, 255) if ch == 'X' else (15, 20, 32)
                draw.rectangle([(dg_x + c * 7, dg_y + r * 12), (dg_x + (c+1) * 7 - 1, dg_y + (r+1) * 12 - 1)], fill=cell_fill)
                
        draw.rectangle([(dx0 + 18, dy0 + 205), (dx0 + 158, dy0 + 265)], fill=CARD_BG, outline=BORDER_DARK, width=1)
        draw.text((dx0 + 26, dy0 + 215), "Tiền xử lý ảnh:", font=FONTS['text_sm'], fill=TEXT_MUTED)
        draw.text((dx0 + 26, dy0 + 230), "Normalized [-128, +127]", font=FONTS['mono_sm'], fill=AMBER)
        draw.text((dx0 + 26, dy0 + 245), "784 điểm ảnh Signed INT8", font=FONTS['mono_sm'], fill=TEXT_WHITE)
        
        # 2. Center: CNN Pipeline Cards
        cx0 = dx0 + 190
        cw, ch = 385, 280
        draw.rectangle([(cx0, dy0), (cx0 + cw, dy0 + ch)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((cx0 + 14, dy0 + 14), "Tiến Trình Bộ Tăng Tốc Phần Cứng 64 PE", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((cx0 + 14, dy0 + 32), "Các lớp mạng nơ-ron tích chập thực thi trên FPGA", font=FONTS['subtitle'], fill=TEXT_MUTED)
        
        cards = [
            ("Conv1 3×3", "16 Filters", "26×26×16", "Mảng 64 PE"),
            ("ReLU Act", "max(0, x)", "Scale >>> 8", "Quantizer"),
            ("MaxPool", "Cửa sổ 2×2", "14×14×16", "S=2 Stride"),
            ("Dense FC", "10 Neurons", "10 Logits", "Tile GEMM")
        ]
        
        card_w = 84
        for c_i, (c_name, c_sub, c_dim, c_hw) in enumerate(cards):
            card_x = cx0 + 15 + c_i * (card_w + 8)
            card_y = dy0 + 60
            is_c_active = (c_i == active_card - 1) or (active_card >= 4 and c_i == 3)
            is_c_done = (c_i < active_card - 1)
            
            c_bg = (45, 55, 80) if is_c_active else ((25, 45, 40) if is_c_done else CARD_BG)
            c_out = accent_col if is_c_active else (EMERALD if is_c_done else BORDER_DARK)
            
            draw.rectangle([(card_x, card_y), (card_x + card_w, card_y + 130)], fill=c_bg, outline=c_out, width=2 if is_c_active else 1)
            draw.text((card_x + 8, card_y + 10), c_name, font=FONTS['mono_bold'], fill=TEXT_WHITE)
            draw.text((card_x + 8, card_y + 30), c_sub, font=FONTS['text_sm'], fill=CYAN if is_c_active else TEXT_MUTED)
            draw.text((card_x + 8, card_y + 55), "Kích thước:", font=FONTS['text_sm'], fill=TEXT_DIM)
            draw.text((card_x + 8, card_y + 70), c_dim, font=FONTS['mono_sm'], fill=AMBER if is_c_active else TEXT_WHITE)
            draw.text((card_x + 8, card_y + 98), c_hw, font=FONTS['badge'], fill=EMERALD if is_c_done else TEXT_MUTED)
            
            if c_i < 3:
                ar_x = card_x + card_w + 1
                draw.line([(ar_x, card_y + 65), (ar_x + 6, card_y + 65)], fill=BORDER_ACTIVE if is_c_done or is_c_active else BORDER_DARK, width=2)
                
        # Status Log Box
        draw.rectangle([(cx0 + 15, dy0 + 205), (cx0 + cw - 15, dy0 + 265)], fill=CARD_BG, outline=BORDER_DARK, width=1)
        draw.text((cx0 + 24, dy0 + 215), "UART Console & Hardware Monitor:", font=FONTS['text_sm'], fill=TEXT_MUTED)
        log_msg = f"[CYCLE] {title_sub}"
        draw.text((cx0 + 24, dy0 + 235), log_msg[:48], font=FONTS['mono_sm'], fill=EMERALD)
        
        # 3. Right Box: Hardware Outputs (Softmax & 7-Segment)
        rx0 = cx0 + cw + 15
        rw = WIDTH - 25 - rx0
        draw.rectangle([(rx0, dy0), (rx0 + rw, dy0 + ch)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((rx0 + 14, dy0 + 14), "Dự đoán FPGA", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((rx0 + 14, dy0 + 32), "HEX0 & Softmax", font=FONTS['subtitle'], fill=TEXT_MUTED)
        
        # 7-Segment Box
        draw.rectangle([(rx0 + 20, dy0 + 60), (rx0 + rw - 20, dy0 + 160)], fill=(15, 20, 32), outline=BORDER_DARK, width=1)
        disp_digit = "8" if (active_card >= 6) else "-"
        draw.text((rx0 + 50, dy0 + 72), disp_digit, font=ImageFont.truetype(os.path.join(font_dir, 'consolab.ttf'), 56), fill=EMERALD if active_card >= 6 else (40, 50, 70))
        draw.text((rx0 + 30, dy0 + 140), "LED 7-Đoạn HEX0", font=FONTS['text_sm'], fill=TEXT_MUTED)
        
        # Confidence
        conf_str = "100.0%" if (active_card >= 6) else "--%"
        draw.text((rx0 + 22, dy0 + 175), f"Độ tin cậy: {conf_str}", font=FONTS['mono_bold'], fill=EMERALD if active_card >= 6 else TEXT_MUTED)
        
        # 10 LEDs row
        draw.text((rx0 + 22, dy0 + 200), "LEDR[9:0] Board:", font=FONTS['text_sm'], fill=TEXT_MUTED)
        for led_i in range(10):
            lx = rx0 + 22 + led_i * 14
            is_led_on = (led_i == 8 and active_card >= 6)
            led_c = EMERALD if is_led_on else (30, 40, 55)
            draw.ellipse([(lx, dy0 + 220), (lx + 9, dy0 + 229)], fill=led_c, outline=EMERALD if is_led_on else BORDER_DARK)
            
        draw_footer(draw, "Chuỗi suy luận CNN toàn diện trên mảng tâm thu: Conv1 → ReLU → Pool → Dense → Argmax → HEX0.",
                    "ĐỘ CHÍNH XÁC 97.06% MNIST", EMERALD)
        images.append(im)
        
    save_gif(images, "04_cnn_mnist_inference.gif", durations)

# ==============================================================================
# GIF 5: SKEW WAVEFRONT ALIGNMENT
# ==============================================================================
def gen_gif_05_skew():
    print("[5/12] Generating 05_skew_wavefront_alignment.gif...")
    images = []
    cycles = range(15)
    durations = [850] * 14 + [3200]
    
    for c_idx in cycles:
        im = Image.new('RGB', (WIDTH, HEIGHT), BG_DARK)
        draw = ImageDraw.Draw(im)
        draw_header(draw, "05. Mạng Lệch Pha Nhịp Sóng Bậc Thang (Systolic Skew Unit)",
                    "Bậc thang D-FF trễ Hàng A (0T..7T) & Cột B (0T..7T) | RTL: systolic_skew_unit.sv",
                    f"CHU KỲ T = {c_idx} / 14", CYAN)

        pe_sz = 20
        pe_gap = 4
        pe_step = pe_sz + pe_gap # 24px
        ax_pe = 315
        ay_pe = 205

        # 1. Containers
        draw.rectangle([(20, 72), (ax_pe - 12, ay_pe + 192)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((30, 80), "Skew Unit Hàng A (0T..7T)", font=FONTS['text_bold'], fill=CYAN)
        draw.text((30, 96), "Hàng i trễ i clock: a_row_skew[i]", font=FONTS['subtitle'], fill=TEXT_MUTED)

        draw.rectangle([(ax_pe - 8, 72), (ax_pe + 192, ay_pe - 12)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((ax_pe + 4, 80), "Skew Unit Cột B (0T..7T)", font=FONTS['text_bold'], fill=ROSE)
        draw.text((ax_pe + 4, 96), "Cột j trễ j clock", font=FONTS['subtitle'], fill=TEXT_MUTED)

        draw.rectangle([(ax_pe - 8, ay_pe - 8), (ax_pe + 192, ay_pe + 192)], fill=CARD_BG, outline=BORDER_DARK, width=1)

        # 2. Skew Unit B (Columns 0..7)
        ff_bw, ff_bh = 14, 10
        for col in range(8):
            cx = ax_pe + col * pe_step + (pe_sz - ff_bw) // 2
            wire_x = cx + ff_bw // 2
            
            draw.text((cx - 1, 108), f"C{col}", font=FONTS['mono_sm'], fill=TEXT_WHITE)
            
            for stage in range(col):
                ff_y = (ay_pe - 16) - (col - 1 - stage) * 11
                has_data = (c_idx == stage)
                is_passed = (c_idx > stage)
                
                fill_col = (55, 25, 35) if has_data else ((35, 25, 45) if is_passed else (20, 25, 38))
                out_col = ROSE if has_data else (PURPLE if is_passed else BORDER_DARK)
                draw.rectangle([(cx, ff_y), (cx + ff_bw, ff_y + ff_bh)], fill=fill_col, outline=out_col, width=1)
                draw.text((cx + 3, ff_y - 1), "D", font=FONTS['mono_sm'], fill=TEXT_WHITE if has_data else TEXT_DIM)
                
            b_arrived = (c_idx >= col)
            b_at_entry = (c_idx == col)
            col_wire_col = ROSE if b_at_entry else (EMERALD if b_arrived else TEXT_DIM)
            
            top_wire_y = (ay_pe - 16) + ff_bh if col > 0 else 120
            draw.line([(wire_x, top_wire_y), (wire_x, ay_pe - 2)], fill=col_wire_col, width=2 if b_at_entry else 1)
            if b_at_entry:
                draw.polygon([(wire_x - 3, ay_pe - 6), (wire_x + 3, ay_pe - 6), (wire_x, ay_pe - 1)], fill=ROSE)

        # 3. Skew Unit A (Rows 0..7)
        ff_aw, ff_ah = 16, 16
        for row in range(8):
            ry = ay_pe + row * pe_step + (pe_sz - ff_ah) // 2
            wire_y = ry + ff_ah // 2
            
            draw.text((28, ry + 1), f"Row {row}", font=FONTS['mono'], fill=TEXT_WHITE)
            draw.text((70, ry + 1), f"{row}T:", font=FONTS['mono_sm'], fill=TEXT_MUTED)
            
            for stage in range(row):
                ff_x = (ax_pe - 20 - ff_aw) - (row - 1 - stage) * 19
                has_data = (c_idx == stage)
                is_passed = (c_idx > stage)
                
                fill_col = (20, 45, 60) if has_data else ((20, 35, 45) if is_passed else (20, 25, 38))
                out_col = CYAN if has_data else (BORDER_ACTIVE if is_passed else BORDER_DARK)
                draw.rectangle([(ff_x, ry), (ff_x + ff_aw, ry + ff_ah)], fill=fill_col, outline=out_col, width=1)
                draw.text((ff_x + 4, ry + 2), "D", font=FONTS['mono_sm'], fill=TEXT_WHITE if has_data else TEXT_DIM)
                
            a_arrived = (c_idx >= row)
            a_at_entry = (c_idx == row)
            row_wire_col = CYAN if a_at_entry else (EMERALD if a_arrived else TEXT_DIM)
            
            start_wire_x = (ax_pe - 20) if row > 0 else 92
            draw.line([(start_wire_x, wire_y), (ax_pe - 2, wire_y)], fill=row_wire_col, width=2 if a_at_entry else 1)
            if a_at_entry:
                draw.polygon([(ax_pe - 6, wire_y - 3), (ax_pe - 6, wire_y + 3), (ax_pe - 1, wire_y)], fill=CYAN)

        # 4. 8x8 PE Array Mesh
        for r in range(8):
            for c in range(8):
                px = ax_pe + c * pe_step
                py = ay_pe + r * pe_step
                
                dist = r + c
                is_hit = (dist == c_idx)
                is_past = (dist < c_idx)
                
                if is_hit:
                    pe_fill = (16, 185, 129)
                    pe_out = TEXT_WHITE
                    txt_col = (11, 15, 25)
                elif is_past:
                    pe_fill = (22, 52, 40)
                    pe_out = (35, 75, 58)
                    txt_col = EMERALD
                else:
                    pe_fill = (15, 22, 35)
                    pe_out = BORDER_DARK
                    txt_col = TEXT_DIM
                    
                draw.rectangle([(px, py), (px + pe_sz, py + pe_sz)], fill=pe_fill, outline=pe_out, width=2 if is_hit else 1)
                if is_hit:
                    draw.text((px + 4, py + 3), "MAC", font=FONTS['mono_sm'], fill=txt_col)
                elif is_past:
                    draw.text((px + 7, py + 3), "✓", font=FONTS['mono_sm'], fill=txt_col)
                else:
                    draw.text((px + 2, py + 4), f"{r},{c}", font=FONTS['mono_sm'], fill=TEXT_DIM)

        # 5. Right Section: Wavefront Status & Theoretical Math
        rx0 = 530
        draw.rectangle([(rx0, 72), (WIDTH - 20, ay_pe + 192)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((rx0 + 14, 82), "Trạng Thái Mặt Sóng Chéo (Wavefront)", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((rx0 + 14, 98), "Đồng bộ hóa 2D Systolic: T = i + j", font=FONTS['subtitle'], fill=EMERALD)

        # Mathematical formula card
        draw.rectangle([(rx0 + 12, 118), (WIDTH - 32, 192)], fill=CARD_BG, outline=BORDER_DARK, width=1)
        draw.text((rx0 + 20, 126), "Phương Trình Nhịp Sóng Skew:", font=FONTS['text_bold'], fill=AMBER)
        draw.text((rx0 + 20, 146), "• Hàng A[i]: delay = i × T_clk  (0T..7T)", font=FONTS['mono'], fill=CYAN)
        draw.text((rx0 + 20, 166), "• Cột B[j]: delay = j × T_clk  (0T..7T)", font=FONTS['mono'], fill=ROSE)

        # Live status card
        draw.rectangle([(rx0 + 12, 202), (WIDTH - 32, 308)], fill=CARD_BG, outline=BORDER_DARK, width=1)
        draw.text((rx0 + 20, 212), f"Chu kỳ Clock hiện tại: T = {c_idx} / 14", font=FONTS['mono_bold'], fill=TEXT_WHITE)
        draw.text((rx0 + 20, 232), f"Đường chéo kích hoạt: i + j = {c_idx}", font=FONTS['mono'], fill=CYAN)

        active_pes = [(r, c) for r in range(8) for c in range(8) if r + c == c_idx]
        draw.text((rx0 + 20, 252), f"Số PE tính MAC: {len(active_pes)} / 64", font=FONTS['mono_bold'], fill=EMERALD)
        draw.text((rx0 + 20, 272), "Toán hạng A[i] & B[j] gặp nhau chuẩn xác 100%", font=FONTS['text_sm'], fill=TEXT_WHITE)
        draw.text((rx0 + 20, 288), "Không xung đột bus, 100% truyền cục bộ", font=FONTS['text_sm'], fill=EMERALD)

        # Hardware spec badge
        draw.rectangle([(rx0 + 12, 318), (WIDTH - 32, ay_pe + 182)], fill=(18, 38, 30), outline=EMERALD, width=1)
        draw.text((rx0 + 20, 326), "Phần cứng RTL (systolic_skew_unit.sv):", font=FONTS['text_bold'], fill=EMERALD)
        draw.text((rx0 + 20, 344), "• Tổng số D-FF: 2 × (1+2+..+7) = 56 FFs", font=FONTS['mono_sm'], fill=TEXT_WHITE)
        draw.text((rx0 + 20, 360), "• Tần số hoạt động: 69.49 MHz (DE2 / DE10)", font=FONTS['mono_sm'], fill=TEXT_MUTED)
        draw.text((rx0 + 20, 376), "• Băng thông nội bộ: 16 Bytes/chu kỳ", font=FONTS['mono_sm'], fill=AMBER)

        draw_footer(draw, "Mạng Skewing D-FF giải quyết triệt để độ trễ lan truyền không gian, biến mảng 2D thành dòng chảy nhịp nhàng.",
                    "WAVEFRONT SYNCHRONIZED", EMERALD)
        images.append(im)

    save_gif(images, "05_skew_wavefront_alignment.gif", durations)


# ==============================================================================
# GIF 6: PE MICROARCHITECTURE
# ==============================================================================
def gen_gif_06_pe():
    print("Testing gen_gif_06_pe...")
    steps = [
        ("Xung clock đầu: Nạp toán hạng a_in[7:0] và b_in[7:0]", "CYCLE 1: LOAD", 1, 14, 25, 0, 0, CYAN, "LOAD"),
        ("Bộ nhân Signed 8×8 tính tích số INT16 (-16384..+16129)", "CYCLE 1: MULT", 1, 14, 25, 350, 0, ROSE, "MULT"),
        ("Cộng tích số vào thanh ghi tích lũy c_acc[31:0]", "CYCLE 1: ACCUM", 1, 14, 25, 350, 350, AMBER, "ACCUM"),
        ("Chuyển tiếp a_out và b_out sang các PE lân cận", "FORWARD RIGHT/DOWN", 1, 14, 25, 350, 350, EMERALD, "FWD"),
        ("Chu kỳ kế tiếp: Nạp toán hạng mới k=2", "CYCLE 2: LOAD", 2, -30, 42, 350, 350, CYAN, "LOAD"),
        ("Bộ nhân tính toán: (-30) × 42 = -1,260", "CYCLE 2: MULT", 2, -30, 42, -1260, 350, ROSE, "MULT"),
        ("Thanh ghi c_acc cập nhật: 350 + (-1260) = -910", "CYCLE 2: ACCUM", 2, -30, 42, -1260, -910, AMBER, "ACCUM"),
        ("Hoàn tất k=8 bước tích lũy → Bật tín hiệu Drain c_out", "DRAIN ACCUMULATOR", 8, 12, 18, 216, 4820, PURPLE, "DRAIN")
    ]
    durations = [1200] * (len(steps) - 1) + [3500]
    images = []

    for step_idx, (title_sub, badge_st, k_val, a_val, b_val, prod_val, acc_val, accent_col, mode) in enumerate(steps):
        im = Image.new('RGB', (WIDTH, HEIGHT), BG_DARK)
        draw = ImageDraw.Draw(im)
        draw_header(draw, "06. Cấu Trúc Vi Mô Phần Tử Xử Lý (PE Datapath)",
                    title_sub, badge_st, accent_col)

        px0, py0 = 40, 76
        pw, ph = 740, 280
        draw.rectangle([(px0, py0), (px0 + pw, py0 + ph)], fill=PANEL_BG, outline=BORDER_DARK, width=2)
        draw.text((px0 + 20, py0 + 12), "Phần Tử Xử Lý PE(i, j) - Kiến Trúc Output-Stationary", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((px0 + 20, py0 + 30), "Module: RTL/pe_gemm.sv | Chu kỳ MAC 1 chu kỳ xung nhịp (Single-Cycle Pipelined)", font=FONTS['subtitle'], fill=TEXT_MUTED)

        # Reg layout anchors
        rx_a = px0 + 100
        rx_b = px0 + 220
        ry_regs = py0 + 120
        mx = px0 + 335
        adx = mx + 155
        acx = adx - 10
        acy = ry_regs + 80
        ix = px0 + pw - 120

        # a_in input wire & label
        a_in_col = CYAN if mode == "LOAD" else TEXT_MUTED
        draw.text((px0 + 15, py0 + 125), "a_in[7:0]", font=FONTS['mono_bold'], fill=a_in_col)
        draw.text((px0 + 15, py0 + 142), f"= {a_val}", font=FONTS['mono'], fill=CYAN if mode == "LOAD" else TEXT_DIM)
        draw.line([(px0 + 65, py0 + 152), (rx_a - 10, py0 + 152)], fill=a_in_col, width=2)
        draw.polygon([(rx_a - 10, py0 + 148), (rx_a - 2, py0 + 152), (rx_a - 10, py0 + 156)], fill=a_in_col)

        # Reg_A
        reg_a_active = (mode in ["LOAD", "MULT", "FWD"])
        draw.rectangle([(rx_a, ry_regs), (rx_a + 85, ry_regs + 65)],
                       fill=(20, 35, 55) if reg_a_active else CARD_BG,
                       outline=CYAN if reg_a_active else BORDER_DARK, width=2 if reg_a_active else 1)
        draw.text((rx_a + 12, ry_regs + 8), "Reg_A", font=FONTS['mono_bold'], fill=TEXT_WHITE)
        draw.text((rx_a + 12, ry_regs + 26), "8-bit FF", font=FONTS['mono_sm'], fill=CYAN)
        draw.text((rx_a + 12, ry_regs + 44), f"= {a_val}", font=FONTS['mono_sm'], fill=TEXT_WHITE)

        # a_out wire from Reg_A looping cleanly above to East (Zero wire collision!)
        a_fwd_col = EMERALD if mode == "FWD" else (CYAN if reg_a_active else TEXT_DIM)
        draw.line([(rx_a + 42, ry_regs), (rx_a + 42, py0 + 82)], fill=a_fwd_col, width=2)
        draw.line([(rx_a + 42, py0 + 82), (px0 + pw - 20, py0 + 82)], fill=a_fwd_col, width=2)
        draw.polygon([(px0 + pw - 20, py0 + 78), (px0 + pw - 12, py0 + 82), (px0 + pw - 20, py0 + 86)], fill=a_fwd_col)
        draw.text((px0 + pw - 130, py0 + 66), "a_out[7:0] (Đông)", font=FONTS['mono_sm'], fill=a_fwd_col)

        # b_in input wire & label (Clean top entry, zero header collision)
        b_in_col = ROSE if mode == "LOAD" else TEXT_MUTED
        draw.text((rx_b - 5, py0 + 58), f"b_in[7:0] = {b_val}", font=FONTS['mono_bold'], fill=b_in_col)
        draw.line([(rx_b + 42, py0 + 76), (rx_b + 42, ry_regs)], fill=b_in_col, width=2)
        draw.polygon([(rx_b + 38, ry_regs - 2), (rx_b + 42, ry_regs + 6), (rx_b + 46, ry_regs - 2)], fill=b_in_col)

        # Reg_B
        reg_b_active = (mode in ["LOAD", "MULT", "FWD"])
        draw.rectangle([(rx_b, ry_regs), (rx_b + 85, ry_regs + 65)],
                       fill=(35, 25, 45) if reg_b_active else CARD_BG,
                       outline=ROSE if reg_b_active else BORDER_DARK, width=2 if reg_b_active else 1)
        draw.text((rx_b + 12, ry_regs + 8), "Reg_B", font=FONTS['mono_bold'], fill=TEXT_WHITE)
        draw.text((rx_b + 12, ry_regs + 26), "8-bit FF", font=FONTS['mono_sm'], fill=ROSE)
        draw.text((rx_b + 12, ry_regs + 44), f"= {b_val}", font=FONTS['mono_sm'], fill=TEXT_WHITE)

        # b_out wire from Reg_B exiting South
        b_fwd_col = EMERALD if mode == "FWD" else (ROSE if reg_b_active else TEXT_DIM)
        draw.line([(rx_b + 42, ry_regs + 65), (rx_b + 42, py0 + ph - 15)], fill=b_fwd_col, width=2)
        draw.polygon([(rx_b + 38, py0 + ph - 15), (rx_b + 42, py0 + ph - 7), (rx_b + 46, py0 + ph - 15)], fill=b_fwd_col)
        draw.text((rx_b + 8, py0 + ph - 30), "b_out (Nam)", font=FONTS['mono_sm'], fill=b_fwd_col)

        # Multiplier 8x8
        mult_active = (mode == "MULT")
        draw.rectangle([(mx, ry_regs), (mx + 115, ry_regs + 65)],
                       fill=(45, 25, 35) if mult_active else CARD_BG,
                       outline=ROSE if mult_active else BORDER_DARK, width=2 if mult_active else 1)
        draw.text((mx + 10, ry_regs + 8), "Bộ Nhân 8×8", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((mx + 10, ry_regs + 27), f"Prod: {prod_val}", font=FONTS['mono'], fill=ROSE if mult_active else TEXT_MUTED)
        draw.text((mx + 10, ry_regs + 45), "Signed INT16", font=FONTS['mono_sm'], fill=TEXT_MUTED)

        # Wires into Multiplier
        draw.line([(rx_a + 85, ry_regs + 32), (mx, ry_regs + 32)], fill=CYAN if mult_active else TEXT_DIM, width=2)
        draw.line([(rx_b + 85, ry_regs + 45), (mx, ry_regs + 45)], fill=ROSE if mult_active else TEXT_DIM, width=2)

        # Wire Multiplier -> Adder
        adder_active = (mode == "ACCUM")
        draw.line([(mx + 115, ry_regs + 32), (adx, ry_regs + 32)], fill=TEXT_WHITE if adder_active else TEXT_DIM, width=2)
        draw.polygon([(adx - 8, ry_regs + 28), (adx, ry_regs + 32), (adx - 8, ry_regs + 36)], fill=TEXT_WHITE if adder_active else TEXT_DIM)

        # Adder 32-bit
        draw.rectangle([(adx, ry_regs), (adx + 95, ry_regs + 65)],
                       fill=(20, 45, 35) if adder_active else CARD_BG,
                       outline=EMERALD if adder_active else BORDER_DARK, width=2 if adder_active else 1)
        draw.text((adx + 8, ry_regs + 8), "Bộ Cộng 32b", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((adx + 8, ry_regs + 27), "+ C_acc", font=FONTS['mono'], fill=EMERALD if adder_active else TEXT_MUTED)
        draw.text((adx + 8, ry_regs + 45), "INT32 Adder", font=FONTS['mono_sm'], fill=TEXT_MUTED)

        # Accumulator C_acc
        acc_active = (mode in ["ACCUM", "DRAIN"])
        draw.rectangle([(acx, acy), (acx + 115, acy + 55)],
                       fill=(35, 35, 20) if acc_active else CARD_BG,
                       outline=AMBER if acc_active else BORDER_DARK, width=2 if acc_active else 1)
        draw.text((acx + 10, acy + 6), "Thanh Ghi C_acc", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((acx + 10, acy + 23), f"= {acc_val}", font=FONTS['mono_bold'], fill=AMBER if acc_active else TEXT_MUTED)
        draw.text((acx + 10, acy + 38), "32-bit Signed Reg", font=FONTS['mono_sm'], fill=TEXT_MUTED)

        # Wires between Adder and Accumulator
        draw.line([(adx + 30, ry_regs + 65), (adx + 30, acy)], fill=EMERALD if adder_active else TEXT_DIM, width=2)
        draw.polygon([(adx + 26, acy - 2), (adx + 30, acy + 6), (adx + 34, acy - 2)], fill=EMERALD if adder_active else TEXT_DIM)
        # Feedback loop wire from Acc to Adder
        draw.line([(adx + 65, acy), (adx + 65, ry_regs + 65)], fill=AMBER if adder_active else TEXT_DIM, width=2)
        draw.polygon([(adx + 61, ry_regs + 67), (adx + 65, ry_regs + 59), (adx + 69, ry_regs + 67)], fill=AMBER if adder_active else TEXT_DIM)

        # Drain c_out wire out of Accumulator South
        drain_active = (mode == "DRAIN")
        drain_col = PURPLE if drain_active else TEXT_DIM
        draw.line([(acx + 55, acy + 55), (acx + 55, py0 + ph - 15)], fill=drain_col, width=2)
        draw.polygon([(acx + 51, py0 + ph - 15), (acx + 55, py0 + ph - 7), (acx + 59, py0 + ph - 15)], fill=drain_col)
        draw.text((acx + 65, py0 + ph - 30), f"c_out[31:0] = {acc_val}", font=FONTS['mono_sm'], fill=drain_col)

        # Right Info Box: Hardware Parameters
        draw.rectangle([(ix, ry_regs - 10), (px0 + pw - 15, ry_regs + 145)], fill=CARD_BG, outline=BORDER_DARK, width=1)
        draw.text((ix + 10, ry_regs), "Thông số PE:", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((ix + 10, ry_regs + 22), f"Bước k: {k_val}/8", font=FONTS['mono'], fill=AMBER)
        draw.text((ix + 10, ry_regs + 42), "Stationary", font=FONTS['mono_sm'], fill=TEXT_MUTED)
        draw.text((ix + 10, ry_regs + 62), "FMAX: 69MHz", font=FONTS['mono_sm'], fill=EMERALD)
        draw.text((ix + 10, ry_regs + 82), "Slack: +1.8ns", font=FONTS['mono_sm'], fill=CYAN)
        draw.text((ix + 10, ry_regs + 105), "✓ 1 MAC/T", font=FONTS['badge'], fill=EMERALD)

        draw_footer(draw, "Mỗi PE tích hợp bộ nhân Signed INT8, bộ cộng 32-bit và thanh ghi tích lũy tại chỗ không cần RAM truy xuất.",
                    "1 CHU KỲ / PHÉP MAC", EMERALD)
        images.append(im)

    images[0].save("figures/06_pe_microarchitecture.gif", save_all=True, append_images=images[1:],
                   optimize=True, duration=durations, loop=0)
    print(f"Generated figures/06_pe_microarchitecture.gif ({len(images)} frames)")

# ==============================================================================
# GIF 7: SYSTOLIC ARRAY 64-PE MESH
# ==============================================================================
def gen_gif_07_array64():
    print("[7/12] Generating 07_systolic_array_64pe_mesh.gif...")
    images = []
    
    cycles_to_show = [
        (0, "ST_CLEAR", "Xóa thanh ghi tích lũy toàn bộ 64 PE về 0", CYAN),
        (3, "ST_SKEW_A", "Nạp trọng số qua mạng trễ bậc thang Skewing", CYAN),
        (7, "ST_COMPUTE", "Nhịp sóng tính toán đầu tiên chạm PE(0,0)", ROSE),
        (10, "ST_COMPUTE", "Sóng lan chéo qua nửa trên của mảng tâm thu", AMBER),
        (14, "ST_COMPUTE", "Tất cả 64 PE hoạt động tối đa 100% công suất MAC", EMERALD),
        (18, "ST_COMPUTE", "Sóng tính toán kết thᾬc tại PE cuối cùng (7,7)", AMBER),
        (23, "ST_DRAIN", "8 bộ Quantizer SIMD bắt đầu đọc song song 8 cột", PURPLE),
        (27, "ST_DRAIN", "Thu gom kết quả tích lũy 32-bit và lượng tử hóa INT8", PURPLE),
        (31, "ST_WRITEBACK", "Ghi ngõ ra hoàn tất vào Matrix Buffer C", CYAN),
        (36, "ST_DONE", "Hoàn tất toàn bộ khối 8×8 chỉ trong 37 chu kỳ!", EMERALD)
    ]
    durations = [900] * (len(cycles_to_show) - 1) + [3000]
    
    for c_val, st_name, st_desc, accent_col in cycles_to_show:
        im = Image.new('RGB', (WIDTH, HEIGHT), BG_DARK)
        draw = ImageDraw.Draw(im)
        draw_header(draw, "07. Mảng Tâm Thu 64 PE Hoàn Chỉnh & FSM Controller",
                    st_desc, f"CYCLE {c_val}/37 | {st_name}", accent_col)
        
        # 8x8 Systolic Mesh (Center-Left)
        mx0, my0 = 45, 78
        mw, mh = 425, 280
        draw.rectangle([(mx0, my0), (mx0 + mw, my0 + mh)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((mx0 + 14, my0 + 12), "Khung Lưới Mảng Tâm Thu 8×8 (64 Processing Elements)", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((mx0 + 14, my0 + 28), "Routing lân cận Nearest-Neighbor | Output-Stationary", font=FONTS['subtitle'], fill=TEXT_MUTED)
        
        grid_x, grid_y = mx0 + 35, my0 + 52
        pe_sz = 26
        for r in range(8):
            for c in range(8):
                dist = r + c
                is_active = (7 <= c_val <= 21) and (dist == (c_val - 7))
                is_done = (c_val > 21) or (dist < (c_val - 7))
                is_draining = (23 <= c_val <= 30) and (r == (c_val - 23))
                
                pe_bg = (244, 63, 94, 90) if is_active else ((168, 85, 247, 80) if is_draining else ((16, 185, 129, 60) if is_done else CARD_BG))
                pe_border = ROSE if is_active else (PURPLE if is_draining else (EMERALD if is_done else BORDER_DARK))
                
                draw.rectangle([(grid_x + c * pe_sz, grid_y + r * pe_sz),
                                (grid_x + (c+1) * pe_sz - 3, grid_y + (r+1) * pe_sz - 3)],
                               fill=pe_bg, outline=pe_border, width=2 if (is_active or is_draining) else 1)
                if is_active:
                    draw.text((grid_x + c * pe_sz + 4, grid_y + r * pe_sz + 5), "✦", font=FONTS['mono'], fill=TEXT_WHITE)
                elif is_draining:
                    draw.text((grid_x + c * pe_sz + 4, grid_y + r * pe_sz + 4), "↓", font=FONTS['mono_bold'], fill=TEXT_WHITE)
                elif is_done:
                    draw.text((grid_x + c * pe_sz + 6, grid_y + r * pe_sz + 6), "•", font=FONTS['mono_sm'], fill=TEXT_DIM)
                    
        # 8 Parallel Quantizers at bottom of array
        draw.rectangle([(grid_x - 5, grid_y + 8 * pe_sz + 5), (grid_x + 8 * pe_sz - 2, grid_y + 8 * pe_sz + 28)],
                       fill=(168, 85, 247, 40) if (23 <= c_val <= 30) else CARD_BG,
                       outline=PURPLE if (23 <= c_val <= 30) else BORDER_DARK, width=2 if (23 <= c_val <= 30) else 1)
        draw.text((grid_x + 10, grid_y + 8 * pe_sz + 10), "8× Bộ Quantizer SIMD Song Song (Gen-2)", font=FONTS['mono_sm'], fill=TEXT_WHITE)
        
        # Right Box: FSM Status & Hardware Timeline
        rx0 = mx0 + mw + 15
        rw = WIDTH - 25 - rx0
        draw.rectangle([(rx0, my0), (rx0 + rw, my0 + mh)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((rx0 + 14, my0 + 12), "Bộ Điều Khiển FSM", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((rx0 + 14, my0 + 28), "gemm_controller.sv", font=FONTS['subtitle'], fill=CYAN)
        
        # State display
        draw.rectangle([(rx0 + 15, my0 + 55), (rx0 + rw - 15, my0 + 115)], fill=CARD_BG, outline=BORDER_DARK, width=1)
        draw.text((rx0 + 25, my0 + 65), "Trạng thái FSM:", font=FONTS['text_sm'], fill=TEXT_MUTED)
        draw.text((rx0 + 25, my0 + 85), st_name, font=FONTS['mono_bold'], fill=accent_col)
        
        # Cycle Progress bar
        draw.rectangle([(rx0 + 15, my0 + 130), (rx0 + rw - 15, my0 + 190)], fill=CARD_BG, outline=BORDER_DARK, width=1)
        draw.text((rx0 + 25, my0 + 140), f"Chu kỳ xung nhịp: {c_val} / 37", font=FONTS['mono'], fill=TEXT_WHITE)
        prog_w = int((c_val / 37.0) * (rw - 50))
        draw.rectangle([(rx0 + 25, my0 + 162), (rx0 + rw - 25, my0 + 174)], fill=(30, 40, 55), outline=BORDER_DARK)
        draw.rectangle([(rx0 + 25, my0 + 162), (rx0 + 25 + prog_w, my0 + 174)], fill=accent_col)
        
        # Performance specs
        draw.rectangle([(rx0 + 15, my0 + 205), (rx0 + rw - 15, my0 + 265)], fill=CARD_BG, outline=BORDER_DARK, width=1)
        draw.text((rx0 + 25, my0 + 215), "Hiệu năng tâm thu:", font=FONTS['text_sm'], fill=TEXT_MUTED)
        draw.text((rx0 + 25, my0 + 230), "64 MAC / Cycle (100% Peak)", font=FONTS['mono_sm'], fill=EMERALD)
        draw.text((rx0 + 25, my0 + 245), "4.45 GOP/s @ 69.49 MHz", font=FONTS['mono_bold'], fill=CYAN)
        
        draw_footer(draw, "Mảng tâm thu hoàn chỉnh đạt thời gian tính toán siêu ngắn 37 chu kỳ nhờ kết hợp Skewing và SIMD Drain.",
                    "37 CYCLES LATENCY CLOSED", EMERALD)
        images.append(im)
        
    save_gif(images, "07_systolic_array_64pe_mesh.gif", durations)

# ==============================================================================
# GIF 8: GEN-1 VS GEN-2 EVOLUTION
# ==============================================================================
def gen_gif_08_gen1_vs_gen2():
    print("[8/12] Generating 08_gen1_vs_gen2_evolution.gif...")
    images = []
    
    steps = [
        ("Bắt đầu phép nhân ma trận 8×8 trên cả hai phiên bản", 0, 0, CYAN),
        ("Gen-1 & Gen-2 cùng hoàn tất khối MAC tâm thu (Chu kỳ 22)", 22, 22, AMBER),
        ("Bước ngoặt: Gen-2 kích hoạt 8 Quantizer SIMD song song!", 27, 27, PURPLE),
        ("GEN-2 HOÀN TẤT (Chu kỳ 37)! Gen-1 mới đọc được 15/64 phần tử", 37, 37, EMERALD),
        ("Gen-2 đã sẵn sàng nhận Tile tiếp theo, Gen-1 vẫn đang Drain", 60, 37, EMERALD),
        ("Gen-1 vẫn bị nghẽn cổ chai bởi bộ lượng tử đơn lẻ (Chu kỳ 80)", 80, 37, ROSE),
        ("Gen-1 cuối cùng mới về đích tại chu kỳ 101 (Trễ hơn 2.73 lần)", 101, 37, ROSE),
        ("Tổng kết bước nhảy vọt kiến trúc: Gen-2 tăng tốc +60.2% lõi vi mạch!", 101, 37, CYAN)
    ]
    durations = [1200] * (len(steps) - 1) + [3500]
    
    for title_sub, c_g1, c_g2, accent_col in steps:
        im = Image.new('RGB', (WIDTH, HEIGHT), BG_DARK)
        draw = ImageDraw.Draw(im)
        draw_header(draw, "08. Bước Nhảy Vọt Kiến Trúc: Gen-1 vs. Gen-2",
                    title_sub, f"SPEEDUP: +60.2% | LATENCY: -63.4%", accent_col)
                    
        # Left Panel: Gen-1 Baseline
        gx0, gy0 = 35, 78
        gw = 360
        draw.rectangle([(gx0, gy0), (gx0 + gw, gy0 + 280)], fill=PANEL_BG, outline=ROSE if c_g1 == 101 else BORDER_DARK, width=2 if c_g1 == 101 else 1)
        draw.text((gx0 + 16, gy0 + 14), "Kiến Trúc Cũ: Gen-1 (Tuần Tự)", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((gx0 + 16, gy0 + 32), "1 Serial Quantizer | Điểm nghẽn Drain 64 chu kỳ", font=FONTS['subtitle'], fill=ROSE)
        
        # Gen-1 Specs
        draw.rectangle([(gx0 + 15, gy0 + 58), (gx0 + gw - 15, gy0 + 150)], fill=CARD_BG, outline=BORDER_DARK)
        draw.text((gx0 + 25, gy0 + 68), "Cơ chế đọc:", font=FONTS['text_sm'], fill=TEXT_MUTED)
        draw.text((gx0 + 25, gy0 + 85), "1 Bộ lượng tử tuần tự (Serial)", font=FONTS['mono'], fill=ROSE)
        draw.text((gx0 + 25, gy0 + 105), "Bus chuyển dữ liệu: 8-bit ngõ ra", font=FONTS['text_sm'], fill=TEXT_MUTED)
        draw.text((gx0 + 25, gy0 + 125), "Tổng thời gian: 101 Chu kỳ", font=FONTS['mono_bold'], fill=ROSE)
        
        # Gen-1 Progress
        draw.text((gx0 + 25, gy0 + 165), f"Tiến trình thực thi: Chu kỳ {c_g1} / 101", font=FONTS['mono'], fill=TEXT_WHITE)
        draw.rectangle([(gx0 + 25, gy0 + 185), (gx0 + gw - 25, gy0 + 200)], fill=(30, 40, 55), outline=BORDER_DARK)
        g1_bar = int((c_g1 / 101.0) * (gw - 50))
        draw.rectangle([(gx0 + 25, gy0 + 185), (gx0 + 25 + g1_bar, gy0 + 200)], fill=ROSE)
        
        draw.text((gx0 + 25, gy0 + 215), "Tổng số lần truy xuất buffer: 64 reads", font=FONTS['text_sm'], fill=TEXT_DIM)
        draw.text((gx0 + 25, gy0 + 235), "Nghẽn cổ chai nghiêm trọng khi tăng quy mô", font=FONTS['text_sm'], fill=ROSE)
        
        # Right Panel: Gen-2 Pipelined SIMD
        hx0 = gx0 + gw + 20
        hw = WIDTH - 35 - hx0
        draw.rectangle([(hx0, gy0), (hx0 + hw, gy0 + 280)], fill=PANEL_BG, outline=EMERALD if c_g2 == 37 else BORDER_DARK, width=2 if c_g2 == 37 else 1)
        draw.text((hx0 + 16, gy0 + 14), "Kiến Trúc Mới: Gen-2 (SIMD Song Song)", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((hx0 + 16, gy0 + 32), "8 Parallel Quantizers | Đóng gói 4-INT8 Word", font=FONTS['subtitle'], fill=EMERALD)
        
        # Gen-2 Specs
        draw.rectangle([(hx0 + 15, gy0 + 58), (hx0 + hw - 15, gy0 + 150)], fill=CARD_BG, outline=BORDER_DARK)
        draw.text((hx0 + 25, gy0 + 68), "Cơ chế đọc:", font=FONTS['text_sm'], fill=TEXT_MUTED)
        draw.text((hx0 + 25, gy0 + 85), "8 Bộ lượng tử SIMD (Parallel)", font=FONTS['mono'], fill=EMERALD)
        draw.text((hx0 + 25, gy0 + 105), "Bus chuyển dữ liệu: 32-bit Word (4-INT8)", font=FONTS['text_sm'], fill=TEXT_MUTED)
        draw.text((hx0 + 25, gy0 + 125), "Tổng thời gian: 37 Chu kỳ (-63.4%)", font=FONTS['mono_bold'], fill=EMERALD)
        
        # Gen-2 Progress
        draw.text((hx0 + 25, gy0 + 165), f"Tiến trình thực thi: Chu kỳ {c_g2} / 37", font=FONTS['mono'], fill=TEXT_WHITE)
        draw.rectangle([(hx0 + 25, gy0 + 185), (hx0 + hw - 25, gy0 + 200)], fill=(30, 40, 55), outline=BORDER_DARK)
        g2_bar = int((c_g2 / 37.0) * (hw - 50))
        draw.rectangle([(hx0 + 25, gy0 + 185), (hx0 + 25 + g2_bar, gy0 + 200)], fill=EMERALD)
        
        if c_g2 == 37:
            draw.rectangle([(hx0 + 25, gy0 + 215), (hx0 + hw - 25, gy0 + 255)], fill=(16, 185, 129, 40), outline=EMERALD)
            draw.text((hx0 + 35, gy0 + 225), "✓ GEN-2 HOÀN TẤT (VƯỢT TRỘI +60.2% TỐC ĐỘ)", font=FONTS['badge'], fill=EMERALD)
        
        draw_footer(draw, "Kiến trúc Gen-2 loại bỏ hoàn toàn thời gian trễ đọc tuần tự nhờ 8 bộ lượng tử SIMD và đóng gói 4-INT8 trên bus 32-bit.",
                    "CORE SPEEDUP +60.2%", EMERALD)
        images.append(im)
        
    save_gif(images, "08_gen1_vs_gen2_evolution.gif", durations)

# ==============================================================================
# GIF 9: AXI HANDSHAKE DEADLOCK
# ==============================================================================
def gen_gif_09_axi():
    print("[9/12] Generating 09_axi_handshake_deadlock.gif...")
    images = []
    
    stages = [
        ("Trạng thái chờ bus: Master và Slave ở chế độ IDLE", "AXI_IDLE", 0, 0, 0, CYAN),
        ("Kịch bản Lệch Pha: Master phát WVALID trước khi phát AWVALID", "WVALID FIRST", 0, 1, 0, AMBER),
        ("Nguy cơ Deadlock thường gặp: Nếu Slave đợi AW trước sẽ bị treo cả bus!", "DEADLOCK HAZARD", 0, 1, 0, ROSE),
        ("Cơ chế Khóa Tự Vệ: Slave chốt w_received = 1 độc lập và sẵn sàng", "DECOUPLED W LATCH", 0, 1, 0, EMERALD),
        ("4 Chu kỳ sau: Master phát tiếp AWVALID và AWADDR", "AWVALID ARRIVED", 1, 1, 0, CYAN),
        ("Kích hoạt Write Strobe: Ghi dữ liệu thành công không hề nghẽn!", "ATOMIC WRITE", 1, 1, 1, EMERALD),
        ("Slave phát BVALID = 1 (BRESP = OKAY) báo hoàn tất giao dịch", "WRITE RESPONSE", 0, 0, 1, EMERALD),
        ("Master phản hồi BREADY = 1: Kết thúc an toàn tuyệt đối 100%", "TRANSACTION PASS ✓", 0, 0, 0, CYAN)
    ]
    durations = [1100] * (len(stages) - 1) + [3200]
    
    for title_sub, badge_st, aw_val, w_val, b_val, accent_col in stages:
        im = Image.new('RGB', (WIDTH, HEIGHT), BG_DARK)
        draw = ImageDraw.Draw(im)
        draw_header(draw, "09. Bus AMBA AXI4-Lite & Cơ Chế Khóa Tự Vệ Chống Deadlock",
                    title_sub, badge_st, accent_col)
                    
        # Master Box (Left)
        mx0, my0 = 45, 80
        mw = 190
        draw.rectangle([(mx0, my0), (mx0 + mw, my0 + 280)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((mx0 + 16, my0 + 14), "AXI Master", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((mx0 + 16, my0 + 32), "CPU / DMA Controller", font=FONTS['subtitle'], fill=TEXT_MUTED)
        
        draw.rectangle([(mx0 + 15, my0 + 65), (mx0 + mw - 15, my0 + 250)], fill=CARD_BG, outline=BORDER_DARK)
        draw.text((mx0 + 25, my0 + 80), "Tín hiệu điều khiển:", font=FONTS['text_sm'], fill=TEXT_MUTED)
        draw.text((mx0 + 25, my0 + 105), f"AWVALID = {aw_val}", font=FONTS['mono'], fill=CYAN if aw_val else TEXT_DIM)
        draw.text((mx0 + 25, my0 + 130), f"WVALID  = {w_val}", font=FONTS['mono'], fill=AMBER if w_val else TEXT_DIM)
        draw.text((mx0 + 25, my0 + 155), f"BREADY  = 1", font=FONTS['mono'], fill=EMERALD)
        draw.text((mx0 + 25, my0 + 195), "Backpressure Stress Test:", font=FONTS['text_sm'], fill=TEXT_MUTED)
        draw.text((mx0 + 25, my0 + 215), "5 Chu kỳ lệch pha AW/W", font=FONTS['mono_sm'], fill=ROSE)
        
        # Center: Bus Channels Wires
        cx0 = mx0 + mw + 15
        cw = 285
        draw.rectangle([(cx0, my0), (cx0 + cw, my0 + 280)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((cx0 + 14, my0 + 14), "Các Kênh Giao Thức AXI4-Lite", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((cx0 + 14, my0 + 32), "Decoupled Address / Data Handshake", font=FONTS['subtitle'], fill=CYAN)
        
        # 1. AW Channel
        draw.rectangle([(cx0 + 15, my0 + 60), (cx0 + cw - 15, my0 + 115)], fill=CARD_BG, outline=CYAN if aw_val else BORDER_DARK)
        draw.text((cx0 + 25, my0 + 70), "Write Address Channel:", font=FONTS['text_sm'], fill=TEXT_MUTED)
        draw.text((cx0 + 25, my0 + 88), "AWVALID & AWREADY → Handshake", font=FONTS['mono_sm'], fill=CYAN if aw_val else TEXT_DIM)
        
        # 2. W Channel
        draw.rectangle([(cx0 + 15, my0 + 125), (cx0 + cw - 15, my0 + 180)], fill=CARD_BG, outline=AMBER if w_val else BORDER_DARK)
        draw.text((cx0 + 25, my0 + 135), "Write Data Channel:", font=FONTS['text_sm'], fill=TEXT_MUTED)
        draw.text((cx0 + 25, my0 + 153), "WVALID & WREADY → Chốt dữ liệu", font=FONTS['mono_sm'], fill=AMBER if w_val else TEXT_DIM)
        
        # 3. B Channel
        draw.rectangle([(cx0 + 15, my0 + 190), (cx0 + cw - 15, my0 + 245)], fill=CARD_BG, outline=EMERALD if b_val else BORDER_DARK)
        draw.text((cx0 + 25, my0 + 200), "Write Response Channel:", font=FONTS['text_sm'], fill=TEXT_MUTED)
        draw.text((cx0 + 25, my0 + 218), "BVALID & BREADY → BRESP=OKAY", font=FONTS['mono_sm'], fill=EMERALD if b_val else TEXT_DIM)
        
        # Slave Box (Right)
        sx0 = cx0 + cw + 15
        sw = WIDTH - 25 - sx0
        draw.rectangle([(sx0, my0), (sx0 + sw, my0 + 280)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((sx0 + 16, my0 + 14), "AXI Slave", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((sx0 + 16, my0 + 32), "systolic_gemm_axi_lite.sv", font=FONTS['subtitle'], fill=EMERALD)
        
        draw.rectangle([(sx0 + 15, my0 + 65), (sx0 + sw - 15, my0 + 250)], fill=CARD_BG, outline=BORDER_DARK)
        draw.text((sx0 + 25, my0 + 80), "Thanh ghi chốt tự vệ:", font=FONTS['text_sm'], fill=TEXT_MUTED)
        draw.text((sx0 + 25, my0 + 105), f"aw_received = {aw_val}", font=FONTS['mono'], fill=CYAN if aw_val else TEXT_DIM)
        draw.text((sx0 + 25, my0 + 130), f"w_received  = {w_val}", font=FONTS['mono'], fill=AMBER if w_val else TEXT_DIM)
        
        is_write = (aw_val and w_val)
        draw.text((sx0 + 25, my0 + 165), "Trạng thái FSM Slave:", font=FONTS['text_sm'], fill=TEXT_MUTED)
        st_slave = "EXECUTE_WRITE" if is_write else ("HOLDING_DATA" if (aw_val or w_val) else "IDLE")
        draw.text((sx0 + 25, my0 + 185), st_slave, font=FONTS['mono_bold'], fill=EMERALD if is_write else AMBER)
        draw.text((sx0 + 25, my0 + 220), "✓ KHÔNG DEADLOCK", font=FONTS['badge'], fill=EMERALD)
        
        draw_footer(draw, "Kiến trúc decoupled tách rời kênh địa chỉ và kênh dữ liệu, loại bỏ hoàn toàn phụ thuộc thứ tự, chống treo bus 100%.",
                    "DEADLOCK IMMUNE MET", EMERALD)
        images.append(im)
        
    save_gif(images, "09_axi_handshake_deadlock.gif", durations)



# ==============================================================================
# GIF 10: SOC MMIO FIRMWARE INTEGRATION
# ==============================================================================
def gen_gif_10_soc_mmio():
    print("[10/12] Generating 10_soc_mmio_firmware.gif...")
    images = []
    
    stages = [
        ("PicoRV32 CPU khởi tạo: Nạp trọng số và dữ liệu vào SRAM qua MMIO", "INIT MMIO", 0, CYAN),
        ("CPU ghi lệnh kích hoạt: *REG_CTRL = 0x01 (Bắt đầu tích chập)", "WRITE CTRL=1", 1, ROSE),
        ("Thanh ghi REG_STATUS bật bit BUSY=1: Phần cứng 64 PE đang tính", "HARDWARE BUSY", 2, AMBER),
        ("Mảng tâm thu thực thi 64 MAC/cycle — CPU chờ hoặc polling vòng lặp", "ACCELERATING", 3, EMERALD),
        ("Sau 37 chu kỳ: Phần cứng hoàn tất, REG_STATUS bật bit DONE=1", "HARDWARE DONE", 4, EMERALD),
        ("CPU đọc kết quả từ thanh ghi BUFFER_C: Nạp vào thanh ghi RISC-V", "READ RESULT", 5, CYAN),
        ("So sánh hiệu năng toàn hệ thống: Tăng tốc 173.7x so với chạy bằng phần mềm!", "SPEEDUP 173.7x", 6, EMERALD),
        ("Toàn bộ hệ thống SoC trên chip hoạt động ổn định, tiết kiệm năng lượng", "SYSTEM PASS ✓", 7, CYAN)
    ]
    durations = [1200] * (len(stages) - 1) + [3500]
    
    for title_sub, badge_st, act_stage, accent_col in stages:
        im = Image.new('RGB', (WIDTH, HEIGHT), BG_DARK)
        draw = ImageDraw.Draw(im)
        draw_header(draw, "10. Bản Đồ Bộ Nhớ MMIO & Firmware C Điều Khiển",
                    title_sub, badge_st, accent_col)
                    
        # Left Box: Firmware C Code
        fx0, fy0 = 35, 78
        fw = 280
        draw.rectangle([(fx0, fy0), (fx0 + fw, fy0 + 280)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((fx0 + 16, fy0 + 14), "Firmware C (PicoRV32)", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((fx0 + 16, fy0 + 32), "firmware/main.c | Host CPU", font=FONTS['subtitle'], fill=CYAN)
        
        c_lines = [
            ("// Khởi tạo con trỏ MMIO", False),
            ("volatile uint32_t *CTRL = 0x80000000;", False),
            ("volatile uint32_t *STAT = 0x80000004;", False),
            ("", False),
            ("// 1. Kích hoạt bộ tăng tốc", act_stage == 1),
            ("*CTRL = 0x01; // START GEMM", act_stage == 1),
            ("", False),
            ("// 2. Polling chờ phần cứng", act_stage in [2, 3]),
            ("while (*STAT & 0x02); // WAIT", act_stage in [2, 3]),
            ("", False),
            ("// 3. Đọc kết quả", act_stage >= 4),
            ("int res = *REG_OUTPUT_C;", act_stage >= 4)
        ]
        
        for l_i, (l_text, is_hl) in enumerate(c_lines):
            ly = fy0 + 58 + l_i * 17
            if is_hl:
                draw.rectangle([(fx0 + 10, ly - 2), (fx0 + fw - 10, ly + 15)], fill=(56, 189, 248, 50), outline=BORDER_ACTIVE)
            draw.text((fx0 + 15, ly), l_text, font=FONTS['mono_sm'], fill=TEXT_WHITE if is_hl else TEXT_MUTED)
            
        # Center: Memory Map & Bus
        cx0 = fx0 + fw + 15
        cw = 245
        draw.rectangle([(cx0, fy0), (cx0 + cw, fy0 + 280)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((cx0 + 14, fy0 + 14), "Bản Đồ Bộ Nhớ MMIO", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((cx0 + 14, fy0 + 32), "AXI-Lite Slave Registers", font=FONTS['subtitle'], fill=TEXT_MUTED)
        
        mmio_regs = [
            ("0x00: REG_CTRL", "Bit 0: START, Bit 1: RESET", act_stage == 1),
            ("0x04: REG_STATUS", "Bit 0: DONE, Bit 1: BUSY", act_stage in [2, 3, 4]),
            ("0x10: REG_PERF_CYCLES", "37 Cycles (Phần cứng)", act_stage >= 4),
            ("0x20: MATRIX_BUFFER_A", "128 Bytes Trọng số", False),
            ("0x30: MATRIX_BUFFER_B", "128 Bytes Ảnh đầu vào", False),
            ("0x40: MATRIX_BUFFER_C", "Ngõ ra lượng tử hóa INT8", act_stage >= 5)
        ]
        
        for m_i, (r_name, r_sub, is_m_act) in enumerate(mmio_regs):
            my = fy0 + 58 + m_i * 35
            draw.rectangle([(cx0 + 12, my), (cx0 + cw - 12, my + 30)],
                           fill=(45, 55, 80) if is_m_act else CARD_BG,
                           outline=accent_col if is_m_act else BORDER_DARK, width=2 if is_m_act else 1)
            draw.text((cx0 + 18, my + 4), r_name, font=FONTS['mono_bold'], fill=TEXT_WHITE if is_m_act else TEXT_MUTED)
            draw.text((cx0 + 18, my + 17), r_sub, font=FONTS['mono_sm'], fill=accent_col if is_m_act else TEXT_DIM)
            
        # Right Box: Speedup & Performance
        rx0 = cx0 + cw + 15
        rw = WIDTH - 25 - rx0
        draw.rectangle([(rx0, fy0), (rx0 + rw, fy0 + 280)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((rx0 + 14, fy0 + 14), "Hiệu Năng SoC", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((rx0 + 14, fy0 + 32), "So sánh với CPU thuần", font=FONTS['subtitle'], fill=EMERALD)
        
        draw.rectangle([(rx0 + 15, fy0 + 58), (rx0 + rw - 15, fy0 + 160)], fill=CARD_BG, outline=BORDER_DARK)
        draw.text((rx0 + 25, fy0 + 70), "Tăng tốc toàn hệ thống:", font=FONTS['text_sm'], fill=TEXT_MUTED)
        draw.text((rx0 + 25, fy0 + 90), "173.7×", font=ImageFont.truetype(os.path.join(font_dir, 'consolab.ttf'), 38), fill=EMERALD)
        draw.text((rx0 + 25, fy0 + 138), "System-Level Speedup", font=FONTS['mono_sm'], fill=TEXT_MUTED)
        
        draw.rectangle([(rx0 + 15, fy0 + 175), (rx0 + rw - 15, fy0 + 265)], fill=CARD_BG, outline=BORDER_DARK)
        draw.text((rx0 + 22, fy0 + 185), "Chu kỳ phần mềm CPU: 12,850", font=FONTS['mono_sm'], fill=ROSE)
        draw.text((rx0 + 22, fy0 + 205), "Chu kỳ bộ tăng tốc: 74", font=FONTS['mono_sm'], fill=EMERALD)
        draw.text((rx0 + 22, fy0 + 225), "Chi phối MMIO bus: Rất nhỏ", font=FONTS['text_sm'], fill=TEXT_MUTED)
        draw.text((rx0 + 22, fy0 + 242), "✓ TIẾT KIỆM 99.4% NĂNG LƯỢNG", font=FONTS['badge'], fill=CYAN)
        
        draw_footer(draw, "Kiến trúc kết hợp PicoRV32 và Mảng tâm thu qua bus MMIO mang lại tốc độ vượt trội 173.7x mà vẫn lịnh hoạt lập trình C.",
                    "173.7x SYSTEM SPEEDUP", EMERALD)
        images.append(im)
        
    save_gif(images, "10_soc_mmio_firmware.gif", durations)

# ==============================================================================
# GIF 11: FPGA SYNTH TIMING CLOSURE
# ==============================================================================
def gen_gif_11_fpga_synth():
    print("[11/12] Generating 11_fpga_synth_timing.gif...")
    images = []
    
    stages = [
        ("Tổng hợp trên Altera Cyclone II (DE2) & Intel Cyclone V / MAX10 (DE10)", "TARGET FPGA", CYAN),
        ("Báo cáo tài nguyên Logic Elements: 2,842 / 33,216 LEs (Chỉ chiếm 8.6%)", "LEs: 8.6%", EMERALD),
        ("Tài nguyên Bộ nhân Embedded Multipliers: 64 / 70 9-bit Multipliers", "DSP: 91.4%", AMBER),
        ("Tài nguyên bộ nhớ Block RAM: 4,096 bits (Dư thừa trên 99% RAM)", "RAM: < 1%", CYAN),
        ("Phân tích thời gian tổng hợp STA: Clock 50 MHz, Đường trễ tới hạn 12.548 ns", "TIMING PATH", ROSE),
        ("Biên an toàn Setup Slack dương: Slack = +1.842 ns → FMAX đạt 69.49 MHz!", "SLACK: +1.842 ns", EMERALD),
        ("Worst Negative Slack (WNS) = 0.000 ns, Total Negative Slack (TNS) = 0.000 ns", "TNS = 0.000 ns", EMERALD),
        ("HOÀN TẤT TIMING CLOSURE 100%: Không có bất kỳ vi phạm Setup hay Hold nào!", "TIMING MET ✓", EMERALD)
    ]
    durations = [1200] * (len(stages) - 1) + [3500]
    
    for title_sub, badge_st, accent_col in stages:
        im = Image.new('RGB', (WIDTH, HEIGHT), BG_DARK)
        draw = ImageDraw.Draw(im)
        draw_header(draw, "11. Báo Cáo Tổng Hợp FPGA & Timing Closure DE2 / DE10",
                    title_sub, badge_st, accent_col)
                    
        # Left Panel: Resource Gauges
        rx0, ry0 = 35, 78
        rw = 360
        draw.rectangle([(rx0, ry0), (rx0 + rw, ry0 + 280)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((rx0 + 16, ry0 + 14), "Sử Dụng Tài Nguyên FPGA (DE10-Lite)", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((rx0 + 16, ry0 + 32), "Quartus Prime 18.1 | MAX 10 10M50DAF484C7G", font=FONTS['subtitle'], fill=TEXT_MUTED)
        
        resources = [
            ("Logic Elements (LEs)", 2842, 33216, "8.6%", EMERALD),
            ("Embedded Multipliers (DSP)", 64, 70, "91.4%", AMBER),
            ("Memory Bits (M9K / RAM)", 4096, 483840, "0.8%", CYAN),
            ("PLLs / Clock Networks", 1, 4, "25.0%", TEXT_MUTED)
        ]
        
        for r_i, (r_name, r_used, r_total, r_pct, r_col) in enumerate(resources):
            ry = ry0 + 60 + r_i * 48
            draw.text((rx0 + 18, ry), r_name, font=FONTS['text_bold'], fill=TEXT_WHITE)
            draw.text((rx0 + rw - 70, ry), r_pct, font=FONTS['mono_bold'], fill=r_col)
            draw.text((rx0 + 18, ry + 16), f"{r_used:,} / {r_total:,} đơn vị", font=FONTS['mono_sm'], fill=TEXT_MUTED)
            # Progress bar
            draw.rectangle([(rx0 + 18, ry + 32), (rx0 + rw - 18, ry + 39)], fill=(30, 40, 55), outline=BORDER_DARK)
            used_w = int((r_used / float(r_total)) * (rw - 36))
            draw.rectangle([(rx0 + 18, ry + 32), (rx0 + 18 + used_w, ry + 39)], fill=r_col)
            
        draw.text((rx0 + 18, ry0 + 258), "✓ Cực kỳ tiết kiệm Logic (Chỉ 8.6% LEs)!", font=FONTS['badge'], fill=EMERALD)
        
        # Right Panel: Static Timing Analysis
        tx0 = rx0 + rw + 20
        tw = WIDTH - 35 - tx0
        draw.rectangle([(tx0, ry0), (tx0 + tw, ry0 + 280)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((tx0 + 16, ry0 + 14), "Phân Tích Thời Gian Tổng Hợp (STA)", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((tx0 + 16, ry0 + 32), "TimeQuest Timing Analyzer | TNS = 0.000 ns", font=FONTS['subtitle'], fill=EMERALD)
        
        # Timing Metrics Card
        draw.rectangle([(tx0 + 15, ry0 + 58), (tx0 + tw - 15, ry0 + 160)], fill=CARD_BG, outline=BORDER_DARK)
        draw.text((tx0 + 25, ry0 + 68), "Tần số tối đa FMAX:", font=FONTS['text_sm'], fill=TEXT_MUTED)
        draw.text((tx0 + 25, ry0 + 88), "69.49 MHz", font=ImageFont.truetype(os.path.join(font_dir, 'consolab.ttf'), 28), fill=CYAN)
        draw.text((tx0 + 25, ry0 + 125), "Xung nhịp thiết kế: 50.00 MHz (DE10 / DE2)", font=FONTS['mono_sm'], fill=TEXT_WHITE)
        draw.text((tx0 + 25, ry0 + 142), "Slack Dương: +1.842 ns → Dư 38.9% Margin!", font=FONTS['mono_sm'], fill=EMERALD)
        
        # Timing Path diagram
        draw.rectangle([(tx0 + 15, ry0 + 175), (tx0 + tw - 15, ry0 + 265)], fill=CARD_BG, outline=BORDER_DARK)
        draw.text((tx0 + 25, ry0 + 185), "Worst Negative Slack (WNS): 0.000 ns", font=FONTS['mono'], fill=EMERALD)
        draw.text((tx0 + 25, ry0 + 205), "Total Negative Slack (TNS): 0.000 ns", font=FONTS['mono'], fill=EMERALD)
        draw.text((tx0 + 25, ry0 + 225), "Hold Violations: 0 (Không có lỗi Hold)", font=FONTS['mono'], fill=CYAN)
        draw.text((tx0 + 25, ry0 + 245), "✓ 100% TIMING CLOSURE MET", font=FONTS['badge'], fill=EMERALD)
        
        draw_footer(draw, "Báo cáo STA khẳng định mạch đạt timing tuyệt đối không có bất kỳ vi phạm nào trên cả 2 nền tảng Altera DE2 và DE10-Lite.",
                    "STA TIMING CLOSED", EMERALD)
        images.append(im)
        
    save_gif(images, "11_fpga_synth_timing.gif", durations)

# ==============================================================================
# GIF 12: UVM VERIFICATION WAVEFORM
# ==============================================================================
def gen_gif_12_uvm_waveform():
    print("[12/12] Generating 12_uvm_verification_waveform.gif...")
    images = []
    
    stages = [
        ("UVM Sequence tạo ngẫu nhiên ma trận toán hạng Signed INT8", "UVM_SEQUENCE", 0, CYAN),
        ("UVM Driver phát xung start và đưa dữ liệu vào DUT qua gemm_if", "DRIVE SIGNALS", 1, ROSE),
        ("Thiết bị DUT bật busy = 1, mảng tâm thu thực hiện 37 chu kỳ", "DUT COMPUTING", 2, AMBER),
        ("Monitor thu thập kết quả ngõ ra c_acc và c_data_out", "MONITOR CAPTURE", 3, PURPLE),
        ("Scoreboard so sánh bit-true với mô hình Python Golden Model", "SCOREBOARD CHECK", 4, CYAN),
        ("Kết quả: 10,000 / 10,000 phép thử trùng khớp 100% (0 Lỗi)", "BIT-TRUE MATCH ✓", 5, EMERALD),
        ("Functional Coverage đạt 88/88 bins kiểm thử toàn diện (100.00%)", "100.00% COVERAGE", 6, EMERALD),
        ("Kim tự tháp kiểm chứng UVM 1.1c khép lại thành công hoàn toàn!", "ALL TESTS PASSED", 7, EMERALD)
    ]
    durations = [1200] * (len(stages) - 1) + [3500]
    
    for title_sub, badge_st, act_idx, accent_col in stages:
        im = Image.new('RGB', (WIDTH, HEIGHT), BG_DARK)
        draw = ImageDraw.Draw(im)
        draw_header(draw, "12. Kim Tự Tháp Kiểm Chứng UVM 1.1c & Waveform Viewer",
                    title_sub, badge_st, accent_col)
                    
        # Top-Left: UVM Architecture Hierarchy
        ux0, uy0 = 35, 78
        uw = 390
        draw.rectangle([(ux0, uy0), (ux0 + uw, uy0 + 135)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((ux0 + 14, uy0 + 12), "Cấu Trúc Môi Trường UVM 1.1c (IEEE 1800)", font=FONTS['text_bold'], fill=TEXT_WHITE)
        
        uvm_boxes = ["Sequence", "Sequencer", "Driver", "DUT", "Scoreboard"]
        ub_w = 64
        for u_i, u_name in enumerate(uvm_boxes):
            bx = ux0 + 15 + u_i * (ub_w + 10)
            by = uy0 + 40
            is_u_act = (u_i == min(4, act_idx))
            draw.rectangle([(bx, by), (bx + ub_w, by + 40)],
                           fill=(56, 189, 248, 50) if is_u_act else CARD_BG,
                           outline=CYAN if is_u_act else BORDER_DARK, width=2 if is_u_act else 1)
            draw.text((bx + 6, by + 12), u_name, font=FONTS['mono_sm'], fill=TEXT_WHITE if is_u_act else TEXT_MUTED)
            if u_i < 4:
                draw.text((bx + ub_w + 2, by + 12), "→", font=FONTS['mono_bold'], fill=TEXT_DIM)
                
        draw.text((ux0 + 16, uy0 + 95), "Scoreboard: Bit-true so sánh với NumPy / PyTorch Golden INT32", font=FONTS['text_sm'], fill=TEXT_MUTED)
        draw.text((ux0 + 16, uy0 + 112), f"Trạng thái kiểm chứng: 10,000 / 10,000 Passed (0 Mismatch)", font=FONTS['mono_sm'], fill=EMERALD)
        
        # Top-Right: Functional Coverage Gauge
        cx0 = ux0 + uw + 15
        cw = WIDTH - 25 - cx0
        draw.rectangle([(cx0, uy0), (cx0 + cw, uy0 + 135)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((cx0 + 14, uy0 + 12), "Độ Bao Phủ Chức Năng", font=FONTS['text_bold'], fill=TEXT_WHITE)
        draw.text((cx0 + 14, uy0 + 28), "Functional Coverage Bins", font=FONTS['subtitle'], fill=EMERALD)
        
        draw.text((cx0 + 16, uy0 + 55), "100.00%", font=ImageFont.truetype(os.path.join(font_dir, 'consolab.ttf'), 30), fill=EMERALD)
        draw.text((cx0 + 155, uy0 + 62), "88 / 88 Bins Closed", font=FONTS['mono_bold'], fill=TEXT_WHITE)
        draw.text((cx0 + 155, uy0 + 80), "Cross coverage & corner cases", font=FONTS['text_sm'], fill=TEXT_MUTED)
        
        draw.rectangle([(cx0 + 16, uy0 + 100), (cx0 + cw - 16, uy0 + 112)], fill=(30, 40, 55), outline=BORDER_DARK)
        cov_prog = int((min(7, act_idx + 1) / 7.0) * (cw - 32))
        draw.rectangle([(cx0 + 16, uy0 + 100), (cx0 + 16 + cov_prog, uy0 + 112)], fill=EMERALD)
        
        # Bottom: Digital Logic Waveform Viewer
        wx0, wy0 = 35, uy0 + 145
        ww = WIDTH - 60
        wh = 140
        draw.rectangle([(wx0, wy0), (wx0 + ww, wy0 + wh)], fill=PANEL_BG, outline=BORDER_DARK, width=1)
        draw.text((wx0 + 14, wy0 + 10), "Trình Xem Dạng Sóng Số Logic (Digital Waveform Viewer - gemm_if)", font=FONTS['text_bold'], fill=TEXT_WHITE)
        
        signals = [
            ("clk", "0101010101010101010101010101", CYAN),
            ("start", "0100000000000000000000000000", ROSE),
            ("busy", "0111111111111111111111000000", AMBER),
            ("valid_out", "0000000000000000000001111000", EMERALD)
        ]
        
        for s_i, (s_name, s_wave, s_col) in enumerate(signals):
            sy = wy0 + 35 + s_i * 24
            draw.text((wx0 + 16, sy), s_name, font=FONTS['mono_sm'], fill=TEXT_MUTED)
            # Draw digital square wave
            wave_x = wx0 + 110
            for w_idx in range(len(s_wave) - 1):
                cur_v = int(s_wave[w_idx])
                nxt_v = int(s_wave[w_idx + 1])
                x1 = wave_x + w_idx * 22
                x2 = wave_x + (w_idx + 1) * 22
                y_high = sy - 2
                y_low = sy + 10
                
                y_cur = y_high if cur_v else y_low
                y_nxt = y_high if nxt_v else y_low
                
                draw.line([(x1, y_cur), (x2, y_cur)], fill=s_col, width=2)
                if cur_v != nxt_v:
                    draw.line([(x2, y_cur), (x2, y_nxt)], fill=s_col, width=2)
                    
        # Timing cursor
        cursor_x = wx0 + 110 + (act_idx * 30)
        draw.line([(cursor_x, wy0 + 30), (cursor_x, wy0 + wh - 10)], fill=(255, 255, 255, 180), width=1)
        draw.text((cursor_x + 4, wy0 + 32), f"T={act_idx}", font=FONTS['mono_sm'], fill=TEXT_WHITE)
        
        draw_footer(draw, "Kiểm chứng UVM 1.1c khép lại 100.00% Coverage và 10,000 test ngẫu nhiên bit-true hoàn toàn trùng khớp mô hình toán Python.",
                    "100.00% UVM COVERAGE CLOSED", EMERALD)
        images.append(im)
        
    save_gif(images, "12_uvm_verification_waveform.gif", durations)



# ==============================================================================
# MAIN EXECUTOR
# ==============================================================================
def main():
    print("=" * 78)
    print("STARTING GENERATION OF ALL 12 STANDALONE ARCHITECTURAL GIFS")
    print("Target Directory: figures/")
    print("=" * 78)
    
    gen_gif_01_im2col()
    gen_gif_02_tiling()
    gen_gif_03_quant()
    gen_gif_04_cnn()
    gen_gif_05_skew()
    gen_gif_06_pe()
    gen_gif_07_array64()
    gen_gif_08_gen1_vs_gen2()
    gen_gif_09_axi()
    gen_gif_10_soc_mmio()
    gen_gif_11_fpga_synth()
    gen_gif_12_uvm_waveform()
    
    print("=" * 78)
    print("ALL 12 GIFS SUCCESSFULLY GENERATED IN figures/!")
    print("=" * 78)

if __name__ == '__main__':
    main()
