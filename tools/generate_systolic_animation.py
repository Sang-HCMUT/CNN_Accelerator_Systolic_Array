# -*- coding: utf-8 -*-
"""
Script: generate_systolic_animation.py
Generates:
1. figures/systolic_dataflow_8x8.gif: Standalone animated GIF showing the 2D Systolic Wavefront dataflow
   across 64 PEs over 37 hardware clock cycles.
2. figures/systolic_dataflow_animation.html: Interactive HTML5/JS simulator with Play/Pause, Step,
   and visual inspection of every PE, skew register, accumulator, and quantizer.
"""

import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
FIGURES_DIR = os.path.join(PROJECT_ROOT, "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

# Fonts
font_dir = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
font_title = ImageFont.truetype(os.path.join(font_dir, 'segoeui.ttf'), 20)
font_subtitle = ImageFont.truetype(os.path.join(font_dir, 'segoeui.ttf'), 14)
font_pe_title = ImageFont.truetype(os.path.join(font_dir, 'consola.ttf'), 11)
font_pe_val = ImageFont.truetype(os.path.join(font_dir, 'consola.ttf'), 13)
font_pe_sub = ImageFont.truetype(os.path.join(font_dir, 'consola.ttf'), 10)
font_legend = ImageFont.truetype(os.path.join(font_dir, 'segoeui.ttf'), 12)
font_skew = ImageFont.truetype(os.path.join(font_dir, 'consola.ttf'), 10)

ARRAY_SIZE = 8
K_DIM = 8

# Exact hardware simulation cycle-by-cycle
# Let A[i, k] = 2, B[k, j] = 3. Each MAC adds 6. Final acc = 48.
A_mat = np.full((8, 8), 2, dtype=np.int8)
B_mat = np.full((8, 8), 3, dtype=np.int8)

# Hardware state
acc_matrix = np.zeros((8, 8), dtype=np.int32)
a_skew_pipes = [[] for _ in range(8)]
b_skew_pipes = [[] for _ in range(8)]
for i in range(8):
    a_skew_pipes[i] = [0] * i
for j in range(8):
    b_skew_pipes[j] = [0] * j

a_pe_wires = np.zeros((8, 8), dtype=np.int8)
b_pe_wires = np.zeros((8, 8), dtype=np.int8)

history_frames = []

# Precompute cycle data for all 37 cycles (Cycle 0 to Cycle 36)
for cycle in range(37):
    # FSM State
    if cycle == 0:
        fsm_state = "ST_CLEAR"
        state_desc = "Clear all 64 PE accumulators to 0. Reset skew pipelines."
        acc_matrix.fill(0)
        a_pe_wires.fill(0)
        b_pe_wires.fill(0)
        for i in range(8): a_skew_pipes[i] = [0] * i
        for j in range(8): b_skew_pipes[j] = [0] * j
        active_pes = set()
        readout_row = -1
    elif 1 <= cycle <= 8:
        fsm_state = "ST_STREAM"
        k_step = cycle - 1
        state_desc = f"Streaming step k={k_step}/7 from Buffers into Wavefront Skew Units."
        readout_row = -1
    elif 9 <= cycle <= 24:
        fsm_state = "ST_DRAIN"
        drain_step = cycle - 8
        state_desc = f"Drain pipeline step {drain_step}/16. Wavefront propagates to bottom-right."
        readout_row = -1
    elif 25 <= cycle <= 32:
        fsm_state = "ST_READOUT"
        readout_row = cycle - 25
        state_desc = f"Parallel Row Readout: Row {readout_row} read through 8 parallel quantizers."
    elif cycle == 33:
        fsm_state = "ST_FLUSH"
        readout_row = -1
        state_desc = "Quantizer 1-cycle pipeline flush."
    else:
        fsm_state = "ST_DONE"
        readout_row = -1
        state_desc = "Computation complete! DONE asserted. All 64 values stored in Buffer C."

    # Compute array state at this cycle
    active_pes = set()
    pe_inputs_a = np.zeros((8, 8), dtype=np.int8)
    pe_inputs_b = np.zeros((8, 8), dtype=np.int8)

    if 1 <= cycle <= 24:
        # Check which k was at which PE
        for i in range(8):
            for j in range(8):
                # An element (k) arrives at PE(i, j) at cycle = 1 + k + i + j
                # Thus k = cycle - 1 - i - j
                k = cycle - 1 - i - j
                if 0 <= k < K_DIM:
                    active_pes.add((i, j))
                    pe_inputs_a[i, j] = A_mat[i, k]
                    pe_inputs_b[i, j] = B_mat[k, j]
                    # Update accumulator
                    acc_matrix[i, j] += int(A_mat[i, k]) * int(B_mat[k, j])

    # Store frame data
    history_frames.append({
        'cycle': cycle,
        'fsm_state': fsm_state,
        'state_desc': state_desc,
        'active_pes': set(active_pes),
        'acc_matrix': acc_matrix.copy(),
        'pe_inputs_a': pe_inputs_a.copy(),
        'pe_inputs_b': pe_inputs_b.copy(),
        'readout_row': readout_row
    })

print(f"Precomputed {len(history_frames)} cycles.")

# -------------------------------------------------------------------------
# GENERATE ANIMATED GIF (1200 x 920 pixels)
# -------------------------------------------------------------------------
WIDTH, HEIGHT = 1200, 920
images = []

# Layout constants
GRID_X = 280
GRID_Y = 170
PE_W = 82
PE_H = 68
PE_GAP_X = 14
PE_GAP_Y = 14

COLOR_BG = (15, 23, 42)          # Slate 900
COLOR_CARD = (30, 41, 59)        # Slate 800
COLOR_BORDER = (51, 65, 85)      # Slate 700
COLOR_TEXT_MAIN = (248, 250, 252)# Slate 50
COLOR_TEXT_MUTED = (148, 163, 184)# Slate 400
COLOR_ACTIVE_BG = (14, 116, 144) # Cyan 700
COLOR_ACTIVE_BORDER = (6, 182, 212) # Cyan 400
COLOR_ACC_BG = (23, 37, 84)      # Dark Blue
COLOR_READOUT_BG = (16, 185, 129)# Emerald 500
COLOR_SKEW_A = (244, 63, 94)     # Rose 500
COLOR_SKEW_B = (168, 85, 247)    # Purple 500
COLOR_DONE = (34, 197, 94)       # Green 500

for frame_idx, frame in enumerate(history_frames):
    img = Image.new('RGB', (WIDTH, HEIGHT), color=COLOR_BG)
    draw = ImageDraw.Draw(img)

    cycle = frame['cycle']
    fsm = frame['fsm_state']
    desc = frame['state_desc']
    active_pes = frame['active_pes']
    acc = frame['acc_matrix']
    in_a = frame['pe_inputs_a']
    in_b = frame['pe_inputs_b']
    readout_row = frame['readout_row']

    # 1. Header Box
    draw.rectangle([20, 15, WIDTH - 20, 85], fill=COLOR_CARD, outline=COLOR_BORDER, width=1)
    draw.text((40, 24), "2D SYSTOLIC ARRAY 8x8 (64 PEs) — OUTPUT-STATIONARY DATAFLOW", fill=(56, 189, 248), font=font_title)
    sub_text = f"Cycle {cycle:02d} / 36 | State: [{fsm}] | Dataflow: A (West -> East), B (North -> South), Acc (Stationary)"
    draw.text((40, 52), sub_text, fill=COLOR_TEXT_MAIN, font=font_subtitle)

    # State badge
    state_color = COLOR_DONE if fsm == "ST_DONE" else (COLOR_ACTIVE_BORDER if "STREAM" in fsm or "DRAIN" in fsm else (251, 146, 60))
    draw.rounded_rectangle([WIDTH - 210, 28, WIDTH - 40, 68], radius=6, fill=state_color)
    draw.text((WIDTH - 195, 38), fsm, fill=(0, 0, 0) if state_color == COLOR_DONE else (255, 255, 255), font=font_title)

    # 2. Timeline Progress Bar
    bar_x = 20
    bar_y = 95
    bar_w = WIDTH - 40
    draw.rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + 10], fill=(51, 65, 85))
    progress_w = int((cycle / 36) * bar_w)
    draw.rectangle([bar_x, bar_y, bar_x + progress_w, bar_y + 10], fill=(6, 182, 212))

    # 3. North: Column Skew Unit (Matrix B inputs from top)
    draw.text((GRID_X - 10, 115), "Matrix B (Inputs via Col Skew 0T..7T)", fill=COLOR_SKEW_B, font=font_legend)
    for c in range(8):
        px = GRID_X + c * (PE_W + PE_GAP_X)
        py = 135
        # Skew register indicator
        delays = c
        is_col_active = any((r, c) in active_pes for r in range(8))
        box_col = (147, 51, 234) if is_col_active else (55, 48, 63)
        draw.rounded_rectangle([px, py, px + PE_W, py + 22], radius=3, fill=box_col, outline=COLOR_BORDER)
        draw.text((px + 12, py + 4), f"Col {c} ({delays}T)", fill=(255, 255, 255), font=font_skew)
        # Arrow down
        arrow_y = py + 24
        draw.line([(px + PE_W // 2, arrow_y), (px + PE_W // 2, GRID_Y - 4)], fill=(168, 85, 247), width=2)

    # 4. West: Row Skew Unit (Matrix A weights from left)
    draw.text((25, GRID_Y - 25), "Matrix A (Weights via Row Skew 0T..7T)", fill=COLOR_SKEW_A, font=font_legend)
    for r in range(8):
        px = 120
        py = GRID_Y + r * (PE_H + PE_GAP_Y)
        delays = r
        is_row_active = any((r, c) in active_pes for c in range(8))
        box_col = (225, 29, 72) if is_row_active else (60, 40, 50)
        draw.rounded_rectangle([px, py + 14, px + 120, py + 54], radius=4, fill=box_col, outline=COLOR_BORDER)
        draw.text((px + 10, py + 18), f"Row {r}: Filter {r}", fill=(255, 255, 255), font=font_skew)
        draw.text((px + 10, py + 34), f"Delay: {delays}T (Pipe)", fill=COLOR_TEXT_MUTED, font=font_skew)
        # Arrow right
        arrow_x = px + 122
        draw.line([(arrow_x, py + PE_H // 2), (GRID_X - 6, py + PE_H // 2)], fill=(244, 63, 94), width=2)

    # 5. Center: The 64 PEs Grid
    for r in range(8):
        for c in range(8):
            px = GRID_X + c * (PE_W + PE_GAP_X)
            py = GRID_Y + r * (PE_H + PE_GAP_Y)

            is_active = (r, c) in active_pes
            is_readout = (r == readout_row)
            acc_val = acc[r, c]

            if is_readout:
                fill_color = COLOR_READOUT_BG
                border_color = (52, 211, 153)
                border_w = 2
            elif is_active:
                fill_color = COLOR_ACTIVE_BG
                border_color = COLOR_ACTIVE_BORDER
                border_w = 3
            elif acc_val > 0:
                fill_color = COLOR_ACC_BG
                border_color = (30, 58, 138)
                border_w = 1
            else:
                fill_color = COLOR_CARD
                border_color = COLOR_BORDER
                border_w = 1

            draw.rounded_rectangle([px, py, px + PE_W, py + PE_H], radius=6, fill=fill_color, outline=border_color, width=border_w)

            # PE Label
            draw.text((px + 6, py + 4), f"PE({r},{c})", fill=(255, 255, 255) if is_active or is_readout else COLOR_TEXT_MUTED, font=font_pe_title)

            # Accumulator value
            val_str = f"Acc:{acc_val:2d}"
            draw.text((px + 6, py + 22), val_str, fill=(254, 240, 138) if is_active else ((255, 255, 255) if acc_val > 0 else (100, 116, 139)), font=font_pe_val)

            # Status line
            if is_active:
                draw.text((px + 6, py + 46), f"MAC +6", fill=(34, 197, 94), font=font_pe_sub)
            elif is_readout:
                draw.text((px + 6, py + 46), f"READ OUT", fill=(255, 255, 255), font=font_pe_sub)
            elif acc_val == 48:
                draw.text((px + 6, py + 46), f"DONE (48)", fill=(56, 189, 248), font=font_pe_sub)
            else:
                draw.text((px + 6, py + 46), "IDLE", fill=(71, 85, 105), font=font_pe_sub)

    # 6. East: 8 Parallel Quantizers & Buffer C Readout
    quant_x = GRID_X + 8 * (PE_W + PE_GAP_X) + 15
    draw.text((quant_x, GRID_Y - 25), "Gen-2 Parallel Quantizers (x8)", fill=(52, 211, 153), font=font_legend)
    for r in range(8):
        py = GRID_Y + r * (PE_H + PE_GAP_Y)
        is_active_q = (r == readout_row)
        q_fill = (16, 185, 129) if is_active_q else (30, 41, 59)
        draw.rounded_rectangle([quant_x, py + 10, quant_x + 95, py + 58], radius=5, fill=q_fill, outline=(52, 211, 153) if is_active_q else COLOR_BORDER, width=2 if is_active_q else 1)
        draw.text((quant_x + 8, py + 14), f"Quant {r}", fill=(255, 255, 255), font=font_pe_title)
        draw.text((quant_x + 8, py + 30), ">>7 + ReLU" if is_active_q else "INT32->INT8", fill=(255, 255, 255) if is_active_q else COLOR_TEXT_MUTED, font=font_pe_sub)
        if is_active_q:
            draw.text((quant_x + 8, py + 44), "OUT: 48 (INT8)", fill=(254, 240, 138), font=font_pe_sub)

    # 7. Bottom: Explanation Box & Wavefront Stats
    desc_y = HEIGHT - 85
    draw.rectangle([20, desc_y, WIDTH - 20, HEIGHT - 15], fill=COLOR_CARD, outline=COLOR_BORDER, width=1)
    draw.text((35, desc_y + 10), f"CYC {cycle:02d} EVENT:", fill=(56, 189, 248), font=font_subtitle)
    draw.text((150, desc_y + 10), desc, fill=COLOR_TEXT_MAIN, font=font_subtitle)

    # Active PE counter
    active_cnt = len(active_pes)
    stat_str = f"Active PEs: {active_cnt:02d} / 64 | Instant Throughput: {active_cnt * 2:02d} OPs/cyc | Total Latency: 37 Cycles (0.74 us @ 50MHz)"
    draw.text((35, desc_y + 38), stat_str, fill=(250, 204, 21), font=font_pe_val)

    images.append(img)

# Save GIF
gif_path = os.path.join(FIGURES_DIR, "systolic_dataflow_8x8.gif")
# 500ms for regular frames, 1500ms for final frame
durations = [850] * (len(images) - 1) + [3000]
images[0].save(gif_path, save_all=True, append_images=images[1:], duration=durations, loop=0)
print(f"[SUCCESS] Generated Animated GIF: {gif_path} (Size: {os.path.getsize(gif_path):,} bytes)")

# -------------------------------------------------------------------------
# GENERATE STANDALONE INTERACTIVE HTML5 ANIMATION VIEWER
# -------------------------------------------------------------------------
html_path = os.path.join(FIGURES_DIR, "systolic_dataflow_animation.html")

html_content = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mô Phỏng Động Dataflow Mảng Tâm Thu 8x8 (64 PEs) — Output-Stationary</title>
<style>
  :root {
    --bg: #0f172a;
    --card: #1e293b;
    --border: #334155;
    --cyan: #06b6d4;
    --green: #22c55e;
    --yellow: #facc15;
    --rose: #f43f5e;
    --purple: #a855f7;
    --blue: #3b82f6;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; }
  body { background: var(--bg); color: #f8fafc; padding: 20px; display: flex; flex-direction: column; align-items: center; }
  .container { max-width: 1200px; width: 100%; }
  header { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 16px 24px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }
  h1 { font-size: 20px; color: var(--cyan); letter-spacing: 0.5px; }
  .subtitle { font-size: 13px; color: #94a3b8; margin-top: 4px; }
  .badge { background: #0284c7; color: #fff; padding: 6px 14px; border-radius: 6px; font-weight: bold; font-size: 14px; }
  
  .controls { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 12px 20px; margin-bottom: 16px; display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }
  button { background: #0284c7; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 500; transition: 0.2s; }
  button:hover { background: #0369a1; }
  button.reset { background: #dc2626; }
  button.reset:hover { background: #b91c1c; }
  .slider-box { display: flex; align-items: center; gap: 10px; font-size: 13px; color: #cbd5e1; }
  input[type=range] { cursor: pointer; }
  
  .canvas-wrap { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 20px; display: flex; justify-content: center; position: relative; }
  canvas { background: #090d16; border-radius: 6px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
  
  .info-bar { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 14px 20px; margin-top: 16px; display: flex; justify-content: space-between; align-items: center; font-size: 14px; }
  .info-desc { color: #f8fafc; font-weight: 500; }
  .info-stat { color: var(--yellow); font-family: monospace; font-size: 13px; }
  
  .legend { display: flex; gap: 20px; margin-top: 12px; font-size: 12px; color: #94a3b8; }
  .legend-item { display: flex; align-items: center; gap: 6px; }
  .legend-dot { width: 12px; height: 12px; border-radius: 3px; }
</style>
</head>
<body>
<div class="container">
  <header>
    <div>
      <h1>MÔ PHỎNG ĐỘNG DATAFLOW MẢNG TÂM THU 8x8 (64 PEs)</h1>
      <div class="subtitle">Kiến trúc Output-Stationary | Bậc thang Wavefront Skewing 0T..7T | Đọc song song 8 hàng Gen-2</div>
    </div>
    <div class="badge" id="stateBadge">ST_CLEAR</div>
  </header>

  <div class="controls">
    <button id="btnPlay">▶ Play</button>
    <button id="btnStep">⏭ Step (+1)</button>
    <button id="btnPrev">⏮ Back (-1)</button>
    <button class="reset" id="btnReset">↺ Reset</button>
    
    <div class="slider-box">
      <span>Tốc độ:</span>
      <input type="range" id="speedSlider" min="100" max="1500" value="500" step="50">
      <span id="speedVal">500 ms/cycle</span>
    </div>

    <div class="slider-box" style="margin-left: auto;">
      <span>Nhảy đến chu kỳ:</span>
      <input type="range" id="cycleSlider" min="0" max="36" value="0">
      <span id="cycleVal" style="font-weight: bold; color: var(--cyan);">00 / 36</span>
    </div>
  </div>

  <div class="canvas-wrap">
    <canvas id="canvas" width="1140" height="780"></canvas>
  </div>

  <div class="info-bar">
    <div class="info-desc" id="cycleDesc">Chu kỳ 0: Xóa toàn bộ 64 PE về 0. Reset thanh ghi Skew Unit.</div>
    <div class="info-stat" id="cycleStat">Active PEs: 00/64 | Thông lượng: 0 OPs/cyc</div>
  </div>

  <div class="legend">
    <div class="legend-item"><div class="legend-dot" style="background:#0e7490; border: 1px solid #06b6d4;"></div> PE Đang Tính MAC (Sóng tới)</div>
    <div class="legend-item"><div class="legend-dot" style="background:#172554;"></div> PE Đã Tích Lũy Kết Quả</div>
    <div class="legend-item"><div class="legend-dot" style="background:#10b981;"></div> Đọc Song Song Row Readout</div>
    <div class="legend-item"><div class="legend-dot" style="background:#f43f5e;"></div> Trọng Số A (West)</div>
    <div class="legend-item"><div class="legend-dot" style="background:#a855f7;"></div> Điểm Ảnh B (North)</div>
  </div>
</div>

<script>
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

let cycle = 0;
let isPlaying = false;
let timer = null;
let delay = 500;

const ARRAY_SIZE = 8;
const K_DIM = 8;
const GRID_X = 220;
const GRID_Y = 110;
const PE_W = 76;
const PE_H = 62;
const GAP_X = 12;
const GAP_Y = 12;

function getCycleData(cyc) {
  let fsm = "ST_CLEAR";
  let desc = "";
  let readoutRow = -1;
  let activePEs = [];

  if (cyc === 0) {
    fsm = "ST_CLEAR";
    desc = "Chu kỳ 0: Xóa toàn bộ thanh ghi tích lũy 64 PE về 0. Reset bộ Skew Unit.";
  } else if (cyc >= 1 && cyc <= 8) {
    fsm = "ST_STREAM";
    let k = cyc - 1;
    desc = `Chu kỳ ${cyc}: Bơm dữ liệu bước k=${k}/7 từ SRAM vào bộ tạo trễ đường chéo Skew Unit.`;
  } else if (cyc >= 9 && cyc <= 24) {
    fsm = "ST_DRAIN";
    desc = `Chu kỳ ${cyc}: Xả đường ống (Drain step ${cyc - 8}/16). Nhịp sóng tính toán lan dần xuống góc dưới phải PE(7,7).`;
  } else if (cyc >= 25 && cyc <= 32) {
    fsm = "ST_READOUT";
    readoutRow = cyc - 25;
    desc = `Chu kỳ ${cyc}: Đọc song song Gen-2! Hàng ${readoutRow} (8 phần tử) đi thẳng vào 8 bộ lượng tử hóa Quantizer.`;
  } else if (cyc === 33) {
    fsm = "ST_FLUSH";
    desc = "Chu kỳ 33: Hoàn tất chốt tầng pipeline cuối cùng của bộ lượng tử hóa ngõ ra.";
  } else {
    fsm = "ST_DONE";
    desc = "Chu kỳ 34-36: Hoàn tất 100%! Bật cờ DONE. 64 phần tử INT8 lưu sẵn sàng trong Buffer C.";
  }

  // Calculate active PEs & accumulators up to this cycle
  let acc = Array.from({length: 8}, () => Array(8).fill(0));
  for (let c = 1; c <= Math.min(cyc, 24); c++) {
    for (let i = 0; i < 8; i++) {
      for (let j = 0; j < 8; j++) {
        let k = c - 1 - i - j;
        if (k >= 0 && k < K_DIM) {
          acc[i][j] += 6; // 2 * 3 = 6
          if (c === cyc) activePEs.push({r: i, c: j});
        }
      }
    }
  }

  return { cyc, fsm, desc, readoutRow, activePEs, acc };
}

function draw() {
  const data = getCycleData(cycle);
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Update UI Elements
  document.getElementById('stateBadge').innerText = data.fsm;
  document.getElementById('stateBadge').style.background = (data.fsm === 'ST_DONE') ? '#22c55e' : (data.fsm.includes('STREAM') || data.fsm.includes('DRAIN')) ? '#0284c7' : '#f59e0b';
  document.getElementById('cycleVal').innerText = (cycle < 10 ? '0' : '') + cycle + ' / 36';
  document.getElementById('cycleSlider').value = cycle;
  document.getElementById('cycleDesc').innerText = data.desc;
  
  let actCount = data.activePEs.length;
  document.getElementById('cycleStat').innerText = `Active PEs: ${(actCount < 10 ? '0' : '') + actCount}/64 | Thông lượng: ${actCount * 2} OPs/nhịp | Độ trễ: 37 Cycles (0.74 us @ 50MHz)`;

  // Draw Matrix B Column Skew Header (Top)
  ctx.fillStyle = '#a855f7';
  ctx.font = 'bold 11px monospace';
  ctx.fillText("B_col (Inputs) ↓ [0T .. 7T Skew]", GRID_X, 35);
  for (let c = 0; c < 8; c++) {
    let px = GRID_X + c * (PE_W + GAP_X);
    let isColActive = data.activePEs.some(p => p.c === c);
    ctx.fillStyle = isColActive ? '#9333ea' : '#3b244d';
    ctx.strokeStyle = isColActive ? '#c084fc' : '#581c87';
    ctx.lineWidth = 1;
    ctx.fillRect(px, 48, PE_W, 20);
    ctx.strokeRect(px, 48, PE_W, 20);
    
    ctx.fillStyle = '#ffffff';
    ctx.font = '10px monospace';
    ctx.fillText(`Col ${c} (${c}T)`, px + 10, 62);
    
    // Draw arrow
    ctx.strokeStyle = '#a855f7';
    ctx.beginPath();
    ctx.moveTo(px + PE_W / 2, 68);
    ctx.lineTo(px + PE_W / 2, GRID_Y - 6);
    ctx.stroke();
  }

  // Draw Matrix A Row Skew Header (Left)
  ctx.fillStyle = '#f43f5e';
  ctx.font = 'bold 11px monospace';
  ctx.fillText("A_row (Weights) → [0T .. 7T Skew]", 15, GRID_Y - 15);
  for (let r = 0; r < 8; r++) {
    let py = GRID_Y + r * (PE_H + GAP_Y);
    let isRowActive = data.activePEs.some(p => p.r === r);
    ctx.fillStyle = isRowActive ? '#e11d48' : '#4c1d28';
    ctx.strokeStyle = isRowActive ? '#fb7185' : '#881337';
    ctx.lineWidth = 1;
    ctx.fillRect(20, py + 12, 105, 36);
    ctx.strokeRect(20, py + 12, 105, 36);
    
    ctx.fillStyle = '#ffffff';
    ctx.font = '10px monospace';
    ctx.fillText(`Row ${r} (${r}T)`, 26, py + 26);
    ctx.fillStyle = '#cbd5e1';
    ctx.fillText(`W[${r}, :]`, 26, py + 40);
    
    // Draw arrow
    ctx.strokeStyle = '#f43f5e';
    ctx.beginPath();
    ctx.moveTo(125, py + PE_H / 2);
    ctx.lineTo(GRID_X - 6, py + PE_H / 2);
    ctx.stroke();
  }

  // Draw 64 PEs
  for (let r = 0; r < 8; r++) {
    for (let c = 0; c < 8; c++) {
      let px = GRID_X + c * (PE_W + GAP_X);
      let py = GRID_Y + r * (PE_H + GAP_Y);
      let isActive = data.activePEs.some(p => p.r === r && p.c === c);
      let isReadout = (r === data.readoutRow);
      let accVal = data.acc[r][c];

      // Box color
      if (isReadout) {
        ctx.fillStyle = '#059669';
        ctx.strokeStyle = '#34d399';
        ctx.lineWidth = 2;
      } else if (isActive) {
        ctx.fillStyle = '#0e7490';
        ctx.strokeStyle = '#06b6d4';
        ctx.lineWidth = 2.5;
      } else if (accVal > 0) {
        ctx.fillStyle = '#172554';
        ctx.strokeStyle = '#1e3a8a';
        ctx.lineWidth = 1;
      } else {
        ctx.fillStyle = '#1e293b';
        ctx.strokeStyle = '#334155';
        ctx.lineWidth = 1;
      }

      ctx.fillRect(px, py, PE_W, PE_H);
      ctx.strokeRect(px, py, PE_W, PE_H);

      // PE Label
      ctx.fillStyle = (isActive || isReadout) ? '#ffffff' : '#94a3b8';
      ctx.font = '9px monospace';
      ctx.fillText(`PE(${r},${c})`, px + 5, py + 12);

      // Acc Value
      ctx.fillStyle = isActive ? '#fef08a' : (accVal > 0 ? '#ffffff' : '#475569');
      ctx.font = 'bold 12px monospace';
      ctx.fillText(`Acc:${accVal}`, px + 5, py + 30);

      // Bottom tag
      ctx.font = '9px monospace';
      if (isActive) {
        ctx.fillStyle = '#4ade80';
        ctx.fillText("MAC +6", px + 5, py + 48);
      } else if (isReadout) {
        ctx.fillStyle = '#ffffff';
        ctx.fillText("READOUT", px + 5, py + 48);
      } else if (accVal === 48) {
        ctx.fillStyle = '#38bdf8';
        ctx.fillText("DONE", px + 5, py + 48);
      } else {
        ctx.fillStyle = '#334155';
        ctx.fillText("IDLE", px + 5, py + 48);
      }
    }
  }

  // Draw 8 Parallel Quantizers (Right side)
  let qX = GRID_X + 8 * (PE_W + GAP_X) + 15;
  ctx.fillStyle = '#10b981';
  ctx.font = 'bold 11px monospace';
  ctx.fillText("Quantizers (x8) → C", qX, GRID_Y - 15);
  for (let r = 0; r < 8; r++) {
    let py = GRID_Y + r * (PE_H + GAP_Y);
    let isQActive = (r === data.readoutRow);
    ctx.fillStyle = isQActive ? '#059669' : '#1e293b';
    ctx.strokeStyle = isQActive ? '#34d399' : '#334155';
    ctx.lineWidth = isQActive ? 2 : 1;
    ctx.fillRect(qX, py + 6, 85, 48);
    ctx.strokeRect(qX, py + 6, 85, 48);

    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 10px monospace';
    ctx.fillText(`Q[${r}]`, qX + 8, py + 22);
    ctx.fillStyle = isQActive ? '#fef08a' : '#94a3b8';
    ctx.font = '9px monospace';
    ctx.fillText(isQActive ? "OUT: 48" : "ReLU+INT8", qX + 8, py + 38);
  }
}

// Controller handlers
function nextCycle() {
  cycle = (cycle + 1) % 37;
  draw();
}

function prevCycle() {
  cycle = (cycle - 1 + 37) % 37;
  draw();
}

function togglePlay() {
  isPlaying = !isPlaying;
  document.getElementById('btnPlay').innerText = isPlaying ? "⏸ Pause" : "▶ Play";
  if (isPlaying) {
    timer = setInterval(nextCycle, delay);
  } else {
    clearInterval(timer);
  }
}

function resetAnim() {
  cycle = 0;
  if (isPlaying) togglePlay();
  draw();
}

document.getElementById('btnPlay').onclick = togglePlay;
document.getElementById('btnStep').onclick = nextCycle;
document.getElementById('btnPrev').onclick = prevCycle;
document.getElementById('btnReset').onclick = resetAnim;

document.getElementById('speedSlider').oninput = function() {
  delay = parseInt(this.value);
  document.getElementById('speedVal').innerText = delay + " ms/cycle";
  if (isPlaying) {
    clearInterval(timer);
    timer = setInterval(nextCycle, delay);
  }
};

document.getElementById('cycleSlider').oninput = function() {
  cycle = parseInt(this.value);
  draw();
};

// Initial draw
draw();
</script>
</body>
</html>
"""

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"[SUCCESS] Generated Interactive HTML5 Animation: {html_path} (Size: {os.path.getsize(html_path):,} bytes)")

# Copy to artifacts directory
ARTIFACT_DIR = r"C:\Users\hoang\.gemini\antigravity\brain\5df3e537-4347-4cef-b9f4-2393c487f3e3"
if os.path.exists(ARTIFACT_DIR):
    import shutil
    shutil.copy(gif_path, os.path.join(ARTIFACT_DIR, "systolic_dataflow_8x8.gif"))
    shutil.copy(html_path, os.path.join(ARTIFACT_DIR, "systolic_dataflow_animation.html"))
    print(f"[SUCCESS] Copied GIF and HTML animation to artifact directory.")
