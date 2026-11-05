# -*- coding: utf-8 -*-
"""
Script: generate_visual_portal.py
Creates figures/visual_architecture_portal.html: An all-in-one interactive visual
engineering portal explaining ALL core complex concepts of the project:
1. im2col & CNN -> GEMM Mapping
2. Matrix Tiling Engine (Arbitrary Size -> 8x8 Hardware Tiles)
3. INT8 Quantization & Zero-Overflow 32-bit Math
4. Wavefront Skew Unit (0T..7T Delay Matching)
5. Micro-Architecture of a Single PE (Output-Stationary Datapath)
6. Gen-1 vs. Gen-2 Architectural Evolution (37 vs. 93 cycles)
7. AMBA AXI4-Lite 5-Channel Decoupled Handshake & Busy Interlock
8. Three-Tier Verification Pyramid & UVM 1.1c Coverage Closure (88 Bins)
"""

import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
FIGURES_DIR = os.path.join(PROJECT_ROOT, "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

portal_path = os.path.join(FIGURES_DIR, "visual_architecture_portal.html")

portal_html = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Interactive Visual Engineering Portal — CNN Systolic SoC Accelerator</title>
<!-- KaTeX for math formulas -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"
        onload="renderMathInElement(document.body, {delimiters: [{left: '$$', right: '$$', display: true}, {left: '$', right: '$', display: false}]});"></script>
<style>
  :root {
    --bg-dark: #0b1120;
    --card-bg: #1e293b;
    --card-header: #334155;
    --border: #475569;
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --cyan: #06b6d4;
    --cyan-light: #67e8f9;
    --emerald: #10b981;
    --amber: #f59e0b;
    --rose: #f43f5e;
    --purple: #a855f7;
    --blue: #3b82f6;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
  body { background: var(--bg-dark); color: var(--text-main); line-height: 1.6; }
  
  /* Layout */
  .app-container { display: flex; height: 100vh; overflow: hidden; }
  
  /* Sidebar */
  .sidebar { width: 320px; background: #0f172a; border-right: 1px solid var(--border); display: flex; flex-direction: column; }
  .sidebar-header { padding: 20px; border-bottom: 1px solid var(--border); }
  .sidebar-header h2 { font-size: 17px; color: var(--cyan); text-transform: uppercase; letter-spacing: 0.5px; }
  .sidebar-header p { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
  
  .nav-list { flex: 1; overflow-y: auto; padding: 12px 8px; }
  .nav-category { font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: bold; padding: 8px 12px 4px 12px; letter-spacing: 0.8px; }
  .nav-item { display: flex; align-items: center; gap: 10px; padding: 10px 14px; border-radius: 6px; cursor: pointer; color: #cbd5e1; font-size: 13.5px; transition: 0.2s; margin-bottom: 3px; }
  .nav-item:hover { background: #1e293b; color: #fff; }
  .nav-item.active { background: #0369a1; color: #fff; font-weight: 600; }
  .nav-icon { width: 20px; text-align: center; font-size: 14px; }
  
  /* Main Content Area */
  .main-content { flex: 1; display: flex; flex-direction: column; overflow-y: auto; background: var(--bg-dark); }
  .top-banner { background: #1e293b; border-bottom: 1px solid var(--border); padding: 16px 32px; display: flex; justify-content: space-between; align-items: center; }
  .top-banner h1 { font-size: 20px; color: #f8fafc; }
  .top-banner .meta { font-size: 13px; color: var(--cyan-light); }
  
  .content-body { padding: 32px; max-width: 1200px; width: 100%; margin: 0 auto; }
  
  /* Cards & Sections */
  .section-pane { display: none; }
  .section-pane.active { display: block; animation: fadeIn 0.3s ease-in-out; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
  
  .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 24px; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
  .card-title { font-size: 18px; color: var(--cyan); margin-bottom: 12px; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #334155; padding-bottom: 8px; }
  
  /* Interactive Interactive Canvas & Demos */
  .interactive-box { background: #090d16; border: 1px solid #334155; border-radius: 8px; padding: 20px; margin: 16px 0; text-align: center; }
  .control-row { display: flex; gap: 12px; justify-content: center; align-items: center; margin-top: 14px; flex-wrap: wrap; }
  button.btn { background: #0284c7; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 13.5px; font-weight: 500; transition: 0.2s; }
  button.btn:hover { background: #0369a1; }
  button.btn-green { background: #10b981; }
  button.btn-green:hover { background: #059669; }
  button.btn-red { background: #ef4444; }
  button.btn-red:hover { background: #dc2626; }
  
  /* Visual Grids */
  .grid-table { display: inline-grid; gap: 3px; background: #334155; padding: 4px; border-radius: 6px; }
  .grid-cell { width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-family: monospace; font-weight: bold; border-radius: 3px; }
  
  /* Code & Formula Displays */
  .code-block { background: #0f172a; border: 1px solid #334155; padding: 14px; border-radius: 6px; font-family: "Consolas", monospace; font-size: 13px; color: #38bdf8; overflow-x: auto; margin: 10px 0; }
  .math-callout { background: #1e1b4b; border-left: 4px solid #818cf8; padding: 12px 18px; border-radius: 0 6px 6px 0; margin: 12px 0; }
  
  /* Tables */
  table.data-table { width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 13.5px; }
  table.data-table th { background: #0f172a; color: var(--cyan); text-align: left; padding: 10px 14px; border: 1px solid #334155; }
  table.data-table td { padding: 10px 14px; border: 1px solid #334155; }
  table.data-table tr:nth-child(even) { background: #182234; }
</style>
</head>
<body>

<div class="app-container">
  <!-- SIDEBAR NAVIGATION -->
  <div class="sidebar">
    <div class="sidebar-header">
      <h2>Visual Architecture</h2>
      <p>Bản Đồ Trực Quan Toàn Bộ Dự Án</p>
    </div>
    <div class="nav-list">
      <div class="nav-category">1. Thuật Toán & Lý Thuyết</div>
      <div class="nav-item active" onclick="switchTab('tab_im2col')"><span class="nav-icon">🧩</span> 1. Thuật Toán im2col & GEMM</div>
      <div class="nav-item" onclick="switchTab('tab_tiling')"><span class="nav-icon">🧱</span> 2. Phân Mảnh Tiling Engine</div>
      <div class="nav-item" onclick="switchTab('tab_quant')"><span class="nav-icon">🔢</span> 3. Lượng Tử Hóa INT8 & Không Tràn Số</div>

      <div class="nav-category">2. Thiết Kế Vi Mạch RTL</div>
      <div class="nav-item" onclick="switchTab('tab_skew')"><span class="nav-icon">🌊</span> 4. Mạng Lệch Pha Wavefront Skew</div>
      <div class="nav-item" onclick="switchTab('tab_pe')"><span class="nav-icon">⚙️</span> 5. Cấu Trúc Vi Mô 1 PE Cơ Sở</div>
      <div class="nav-item" onclick="switchTab('tab_gen1_gen2')"><span class="nav-icon">⚡</span> 6. Cải Tiến Gen-1 vs. Gen-2 (37 cyc)</div>

      <div class="nav-category">3. Tích Hợp SoC & Bus</div>
      <div class="nav-item" onclick="switchTab('tab_axi')"><span class="nav-icon">🔄</span> 7. Bus AXI4-Lite & Decoupled AW/W</div>
      <div class="nav-item" onclick="switchTab('tab_soc')"><span class="nav-icon">💻</span> 8. SoC PicoRV32 & Firmware C</div>

      <div class="nav-category">4. Kiểm Chứng Đa Tầng</div>
      <div class="nav-item" onclick="switchTab('tab_uvm')"><span class="nav-icon">🎯</span> 9. Chuẩn UVM 1.1c & 88 Bins</div>
    </div>
  </div>

  <!-- MAIN VIEWPORT -->
  <div class="main-content">
    <div class="top-banner">
      <h1 id="topTitle">Thuật Toán im2col & Ánh Xạ Phép Tích Chập Sang GEMM</h1>
      <div class="meta">Đồ Án Tốt Nghiệp Kỹ Sư — Mảng Tâm Thu 8x8 FPGA SoC</div>
    </div>

    <div class="content-body">

      <!-- ============================================================ -->
      <!-- TAB 1: IM2COL -->
      <!-- ============================================================ -->
      <div id="tab_im2col" class="section-pane active">
        <div class="card">
          <div class="card-title"><span>🧩</span> Tại Sao Phải Cần Thuật Toán im2col?</div>
          <p>
            Mạng nơ-ron chập (CNN) vốn thực hiện phép tích chập không gian 2D với 6 vòng lặp lồng nhau (vô cùng chậm và phức tạp trên phần cứng). 
            Thuật toán <strong>im2col (Image to Column)</strong> giải quyết bài toán này bằng cách: <em>Biến đổi toàn bộ phép tích chập thành phép nhân 2 ma trận tiêu chuẩn:</em>
          </p>
          <div class="math-callout">
            $$\mathbf{C}_{[M \times N]} = \mathbf{A}_{[M \times K]} \times \mathbf{B}_{[K \times N]}$$
          </div>
        </div>

        <div class="card">
          <div class="card-title"><span>🔍</span> Trực Quan Hóa Quá Trình Trải Cột (Live im2col Demo)</div>
          <p>Di chuyển thanh trượt bên dưới để xem cửa sổ trượt $3 \times 3$ trên ảnh $5 \times 5$ được duỗi thẳng thành một <strong>cột dọc của Ma trận B</strong> như thế nào:</p>
          
          <div class="interactive-box">
            <div style="display:flex; justify-content:space-around; align-items:center; flex-wrap:wrap; gap:20px;">
              <div>
                <div style="color:var(--cyan); margin-bottom:8px; font-weight:bold;">Ảnh Đầu Vào (5x5 Single Channel)</div>
                <div id="im2col_img" class="grid-table" style="grid-template-columns: repeat(5, 34px);"></div>
              </div>
              <div style="font-size:24px; color:#94a3b8;">➔ im2col ➔</div>
              <div>
                <div style="color:var(--purple); margin-bottom:8px; font-weight:bold;">Ma Trận Đầu Vào B (9 Hàng x 9 Cột Patches)</div>
                <div id="im2col_mat" class="grid-table" style="grid-template-columns: repeat(9, 28px);"></div>
              </div>
            </div>

            <div class="control-row">
              <button class="btn" onclick="prevPatch()">◀ Patch Trước</button>
              <span id="patchLabel" style="font-family:monospace; color:var(--amber); font-weight:bold;">Patch 0 (Vị trí hàng 0, cột 0)</span>
              <button class="btn" onclick="nextPatch()">Patch Tiếp Theo ▶</button>
            </div>
          </div>

          <table class="data-table">
            <tr>
              <th>Toán Hạng</th>
              <th>Ý Nghĩa Trong Tích Chập (CNN)</th>
              <th>Kích Thước Conv1 (MNIST)</th>
            </tr>
            <tr>
              <td><strong>Ma trận A</strong> (Trọng số)</td>
              <td>Mỗi hàng là một bộ lọc $3 \times 3$ duỗi thẳng</td>
              <td>$[M \times K] = [16 \times 9]$ (16 bộ lọc, 9 trọng số/lọc)</td>
            </tr>
            <tr>
              <td><strong>Ma trận B</strong> (Đầu vào)</td>
              <td>Mỗi cột là một cửa sổ trượt $3 \times 3$ trên ảnh duỗi thẳng</td>
              <td>$[K \times N] = [9 \times 784]$ (9 pixels/patch, 784 patches)</td>
            </tr>
            <tr>
              <td><strong>Ma trận C</strong> (Kết quả)</td>
              <td>Điểm ảnh kích hoạt của 16 Feature Maps ngõ ra</td>
              <td>$[M \times N] = [16 \times 784]$ ($16 \times 28 \times 28$)</td>
            </tr>
          </table>
        </div>
      </div>

      <!-- ============================================================ -->
      <!-- TAB 2: TILING ENGINE -->
      <!-- ============================================================ -->
      <div id="tab_tiling" class="section-pane">
        <div class="card">
          <div class="card-title"><span>🧱</span> Chiến Lược Chia Khối Ma Trận Lớn (Tiling Engine)</div>
          <p>
            Phần cứng mảng tâm thu có kích thước vật lý cố định là <strong>$8 \times 8$ PE (64 bộ nhân)</strong> và hỗ trợ chiều sâu $K \le 16$.
            Ma trận tầng Conv1 có kích thước khổng lồ: $[16 \times 9] \times [9 \times 784]$. Làm sao để nhét vừa mảng $8 \times 8$?
          </p>
          <div class="math-callout">
            $$N_{\text{Tiles}} = \left\lceil \frac{M}{8} \right\rceil \times \left\lceil \frac{N}{8} \right\rceil = \frac{16}{8} \times \frac{784}{8} = 2 \times 98 = \mathbf{196\text{ Sub-tiles}}$$
          </div>
        </div>

        <div class="card">
          <div class="card-title"><span>📐</span> Mô Hình Chia Mảnh Khối Trên Phần Cứng</div>
          <div class="interactive-box">
            <svg width="650" height="280" style="background:#0b1120; border-radius:6px;">
              <!-- Matrix A -->
              <rect x="30" y="40" width="100" height="80" fill="#e11d48" opacity="0.3" stroke="#f43f5e" stroke-width="2"/>
              <rect x="30" y="130" width="100" height="80" fill="#e11d48" opacity="0.3" stroke="#f43f5e" stroke-width="2"/>
              <text x="80" y="85" fill="#fff" font-size="12" text-anchor="middle">Tile A0 [8x9]</text>
              <text x="80" y="175" fill="#fff" font-size="12" text-anchor="middle">Tile A1 [8x9]</text>
              <text x="80" y="25" fill="#f43f5e" font-size="13" font-weight="bold" text-anchor="middle">Ma Trận A [16x9]</text>

              <!-- Multiply Symbol -->
              <text x="160" y="130" fill="#94a3b8" font-size="24" font-weight="bold">×</text>

              <!-- Matrix B -->
              <rect x="200" y="40" width="70" height="100" fill="#9333ea" opacity="0.3" stroke="#a855f7" stroke-width="2"/>
              <rect x="280" y="40" width="70" height="100" fill="#9333ea" opacity="0.3" stroke="#a855f7" stroke-width="2"/>
              <text x="370" y="95" fill="#94a3b8" font-size="20">...</text>
              <rect x="400" y="40" width="70" height="100" fill="#9333ea" opacity="0.3" stroke="#a855f7" stroke-width="2"/>
              <text x="235" y="95" fill="#fff" font-size="11" text-anchor="middle">Tile B0</text>
              <text x="315" y="95" fill="#fff" font-size="11" text-anchor="middle">Tile B1</text>
              <text x="435" y="95" fill="#fff" font-size="11" text-anchor="middle">Tile B97</text>
              <text x="330" y="25" fill="#a855f7" font-size="13" font-weight="bold" text-anchor="middle">Ma Trận B [9x784] (98 Dải Cột)</text>

              <!-- Arrow down -->
              <path d="M 330 160 L 330 200" stroke="#06b6d4" stroke-width="3" marker-end="url(#arrow)"/>

              <!-- Target 8x8 Hardware -->
              <rect x="230" y="210" width="200" height="50" rx="6" fill="#0369a1" stroke="#38bdf8" stroke-width="2"/>
              <text x="330" y="240" fill="#fff" font-size="13" font-weight="bold" text-anchor="middle">Mảng Tâm Thu Vật Lý 8x8 (64 PEs)</text>
            </svg>
          </div>
          <p>
            <strong>Tái sử dụng trọng số (Weight Reuse)</strong>: Tile $A_0$ được nạp vào bộ đệm `matrix_buffer_a` <strong>đúng 1 lần</strong>, sau đó giữ cố định và lần lượt cho 98 tiles $B_0 \dots B_{97}$ đi qua. Tiết kiệm 98 lần đọc lại bộ nhớ ngoài!
          </p>
        </div>
      </div>

      <!-- ============================================================ -->
      <!-- TAB 3: QUANTIZATION -->
      <!-- ============================================================ -->
      <div id="tab_quant" class="section-pane">
        <div class="card">
          <div class="card-title"><span>🔢</span> Chuỗi Biến Đổi Số Học: INT8 In ➔ INT32 Acc ➔ INT8 Out</div>
          <p>
            Để tiết kiệm tài nguyên FPGA và loại bỏ hoàn toàn bộ nhân số thực (Float32), hệ thống áp dụng kỹ thuật lượng tử hóa số nguyên đối xứng có dấu.
          </p>
          <div class="interactive-box">
            <svg width="700" height="140" style="background:#0f172a; border-radius:6px;">
              <!-- Node 1 -->
              <rect x="20" y="35" width="100" height="70" rx="6" fill="#1e293b" stroke="#0284c7" stroke-width="2"/>
              <text x="70" y="62" fill="#fff" font-size="12" font-weight="bold" text-anchor="middle">Toán Hạng</text>
              <text x="70" y="82" fill="#38bdf8" font-size="11" text-anchor="middle">Signed INT8</text>

              <text x="135" y="75" fill="#94a3b8" font-size="20">→</text>

              <!-- Node 2 -->
              <rect x="150" y="35" width="110" height="70" rx="6" fill="#1e293b" stroke="#06b6d4" stroke-width="2"/>
              <text x="205" y="62" fill="#fff" font-size="12" font-weight="bold" text-anchor="middle">Bộ Nhân PE</text>
              <text x="205" y="82" fill="#67e8f9" font-size="11" text-anchor="middle">Signed INT16</text>

              <text x="275" y="75" fill="#94a3b8" font-size="20">→</text>

              <!-- Node 3 -->
              <rect x="290" y="35" width="120" height="70" rx="6" fill="#172554" stroke="#3b82f6" stroke-width="2"/>
              <text x="350" y="62" fill="#fff" font-size="12" font-weight="bold" text-anchor="middle">Bộ Tích Lũy</text>
              <text x="350" y="82" fill="#60a5fa" font-size="11" text-anchor="middle">Signed INT32</text>

              <text x="425" y="75" fill="#94a3b8" font-size="20">→</text>

              <!-- Node 4 -->
              <rect x="440" y="35" width="110" height="70" rx="6" fill="#064e3b" stroke="#10b981" stroke-width="2"/>
              <text x="495" y="62" fill="#fff" font-size="12" font-weight="bold" text-anchor="middle">>> Shift + ReLU</text>
              <text x="495" y="82" fill="#34d399" font-size="11" text-anchor="middle">Hậu Xử Lý</text>

              <text x="565" y="75" fill="#94a3b8" font-size="20">→</text>

              <!-- Node 5 -->
              <rect x="580" y="35" width="100" height="70" rx="6" fill="#1e293b" stroke="#22c55e" stroke-width="2"/>
              <text x="630" y="62" fill="#fff" font-size="12" font-weight="bold" text-anchor="middle">Ngõ Ra C</text>
              <text x="630" y="82" fill="#4ade80" font-size="11" text-anchor="middle">[0, 127] INT8</text>
            </svg>
          </div>
          
          <div class="math-callout">
            <strong>Bảo đảm không tràn số (Zero-Overflow Guarantee)</strong>:<br/>
            Tích lớn nhất: $(-128) \times (-128) = +16,384$.<br/>
            Cộng dồn qua tối đa $K=16$ bước: $16 \times 16,384 = \mathbf{262,144}$.<br/>
            Trong khi thanh ghi tích lũy 32-bit chứa được tới $\mathbf{2,147,483,647} \implies$ <em>Tuyệt đối không bao giờ bị tràn số!</em>
          </div>
        </div>
      </div>

      <!-- ============================================================ -->
      <!-- TAB 4: SKEW UNIT -->
      <!-- ============================================================ -->
      <div id="tab_skew" class="section-pane">
        <div class="card">
          <div class="card-title"><span>🌊</span> Mạng Lệch Pha Nhịp Sóng Bậc Thang (Wavefront Skew Unit)</div>
          <p>
            Do mảng tâm thu truyền dữ liệu giữa các PE kề cận mất đúng 1 chu kỳ xung nhịp, nên nếu bơm cả hàng $A$ và cột $B$ vào cùng lúc thì các số sẽ không gặp nhau đúng lúc.
            Module `systolic_skew_unit.sv` tạo ra các tầng trễ bậc thang:
          </p>
          <div class="interactive-box">
            <svg width="600" height="260" style="background:#0f172a; border-radius:6px;">
              <!-- Rows of A -->
              <text x="30" y="30" fill="#f43f5e" font-weight="bold">Hàng Ma Trận A</text>
              <text x="30" y="65" fill="#cbd5e1">Hàng 0:</text>
              <line x1="90" y1="60" x2="450" y2="60" stroke="#f43f5e" stroke-width="2"/>
              <text x="470" y="65" fill="#38bdf8">Trễ 0T</text>

              <text x="30" y="105" fill="#cbd5e1">Hàng 1:</text>
              <rect x="90" y="90" width="35" height="25" fill="#e11d48" rx="3"/><text x="107" y="107" fill="#fff" font-size="10" text-anchor="middle">FF</text>
              <line x1="125" y1="102" x2="450" y2="102" stroke="#f43f5e" stroke-width="2"/>
              <text x="470" y="105" fill="#38bdf8">Trễ 1T</text>

              <text x="30" y="145" fill="#cbd5e1">Hàng 2:</text>
              <rect x="90" y="130" width="35" height="25" fill="#e11d48" rx="3"/><text x="107" y="147" fill="#fff" font-size="10" text-anchor="middle">FF</text>
              <rect x="135" y="130" width="35" height="25" fill="#e11d48" rx="3"/><text x="152" y="147" fill="#fff" font-size="10" text-anchor="middle">FF</text>
              <line x1="170" y1="142" x2="450" y2="142" stroke="#f43f5e" stroke-width="2"/>
              <text x="470" y="145" fill="#38bdf8">Trễ 2T</text>

              <text x="30" y="185" fill="#cbd5e1">Hàng 7:</text>
              <text x="90" y="185" fill="#94a3b8">[ 7 Tầng Thanh Ghi Flip-Flop Nối Tiếp ]</text>
              <line x1="380" y1="182" x2="450" y2="182" stroke="#f43f5e" stroke-width="2"/>
              <text x="470" y="185" fill="#38bdf8">Trễ 7T</text>
            </svg>
          </div>
          <div class="math-callout">
            <strong>Định luật gặp nhau của phần tử</strong>:<br/>
            Phần tử $A[i, k]$ và $B[k, j]$ gặp nhau tại $PE(i, j)$ vào đúng chu kỳ:
            $$t_{\text{gặp}} = 1 + k + i + j$$
          </div>
        </div>
      </div>

      <!-- ============================================================ -->
      <!-- TAB 5: PE MICROARCHITECTURE -->
      <!-- ============================================================ -->
      <div id="tab_pe" class="section-pane">
        <div class="card">
          <div class="card-title"><span>⚙️</span> Cấu Trúc Vi Mô 1 Phần Tử Xử Lý (PE Datapath)</div>
          <p>
            Mỗi khối `pe_gemm.sv` là một đơn vị tính toán nhân-cộng dồn độc lập. Trong kiến trúc <strong>Output-Stationary</strong>, giá trị cộng dồn đứng yên trong PE:
          </p>
          <div class="interactive-box">
            <svg width="600" height="280" style="background:#0f172a; border-radius:6px;">
              <!-- Inputs -->
              <text x="40" y="80" fill="#f43f5e" font-weight="bold">a_in [7:0] (Tây) ➔</text>
              <text x="260" y="30" fill="#a855f7" font-weight="bold">b_in [7:0] (Bắc) ↓</text>

              <!-- PE Box -->
              <rect x="180" y="50" width="240" height="180" rx="8" fill="#1e293b" stroke="#06b6d4" stroke-width="2"/>
              <text x="300" y="75" fill="#38bdf8" font-size="14" font-weight="bold" text-anchor="middle">PE(i, j) Hardware</text>

              <!-- Multiplier -->
              <circle cx="250" cy="120" r="18" fill="#0284c7" stroke="#38bdf8"/>
              <text x="250" y="126" fill="#fff" font-size="16" font-weight="bold" text-anchor="middle">×</text>
              <text x="250" y="150" fill="#94a3b8" font-size="10" text-anchor="middle">INT8 x INT8</text>

              <!-- Adder -->
              <circle cx="340" cy="120" r="18" fill="#10b981" stroke="#34d399"/>
              <text x="340" y="126" fill="#fff" font-size="16" font-weight="bold" text-anchor="middle">+</text>
              <text x="340" y="150" fill="#94a3b8" font-size="10" text-anchor="middle">32-bit Adder</text>

              <!-- Accumulator Register -->
              <rect x="290" y="170" width="100" height="35" rx="4" fill="#172554" stroke="#3b82f6"/>
              <text x="340" y="192" fill="#facc15" font-size="11" font-weight="bold" text-anchor="middle">acc_reg [31:0]</text>

              <!-- Outputs -->
              <text x="440" y="125" fill="#f43f5e" font-weight="bold">➔ a_out (Đông)</text>
              <text x="260" y="260" fill="#a855f7" font-weight="bold">↓ b_out (Nam)</text>
            </svg>
          </div>
        </div>
      </div>

      <!-- ============================================================ -->
      <!-- TAB 6: GEN-1 VS GEN-2 -->
      <!-- ============================================================ -->
      <div id="tab_gen1_gen2" class="section-pane">
        <div class="card">
          <div class="card-title"><span>⚡</span> So Sánh Bước Nhảy Vọt Kiến Trúc: Gen-1 vs. Gen-2</div>
          <p>
            Tại sao phiên bản Gen-2 của bạn lại giảm được tới <strong>60.2% thời gian tính toán lõi</strong> (từ 93 chu kỳ xuống đúng 37 chu kỳ)?
          </p>
          <table class="data-table">
            <tr>
              <th>Đặc Tính Kiến Trúc</th>
              <th>Phiên Bản Gen-1 (Cũ)</th>
              <th>Phiên Bản Gen-2 (Hiện Tại)</th>
              <th>Hiệu Quả Cải Tiến</th>
            </tr>
            <tr>
              <td><strong>Cổng nạp dữ liệu A/B</strong></td>
              <td>Ghi từng byte đơn lẻ (Single Byte MMIO)</td>
              <td><strong>Gói 4 byte / 1 từ 32-bit (Packed 4-INT8)</strong></td>
              <td>Nạp nhanh gấp <strong>4 lần</strong> trên bus AXI</td>
            </tr>
            <tr>
              <td><strong>Cụm Lượng tử hóa</strong></td>
              <td>1 khối Quantizer duy nhất quét nối tiếp</td>
              <td><strong>8 khối Quantizer song song (Lockstep SIMD)</strong></td>
              <td>Tăng thông lượng hậu xử lý gấp <strong>8 lần</strong></td>
            </tr>
            <tr>
              <td><strong>Pha đọc kết quả (Readout)</strong></td>
              <td>Mất 64 chu kỳ quét từng phần tử</td>
              <td><strong>Mất đúng 8 chu kỳ (Quét song song 8 hàng)</strong></td>
              <td>Tiết kiệm <strong>56 chu kỳ xung nhịp</strong></td>
            </tr>
            <tr>
              <td><strong>Tổng chu kỳ tính toán lõi</strong></td>
              <td>$93\text{ chu kỳ}$ ($1.86\ \mu\text{s}$)</td>
              <td><strong>$37\text{ chu kỳ}$ ($0.74\ \mu\text{s}$)</strong></td>
              <td><strong>Giảm 60.2% độ trễ lõi</strong></td>
            </tr>
            <tr>
              <td><strong>Gia tốc toàn hệ thống SoC</strong></td>
              <td>$39.3\times$ so với CPU RISC-V</td>
              <td><strong>$173.7\times$ so với CPU RISC-V</strong></td>
              <td><strong>Nhanh hơn 4.4 lần so với Gen-1</strong></td>
            </tr>
          </table>
        </div>
      </div>

      <!-- ============================================================ -->
      <!-- TAB 7: AXI4-LITE -->
      <!-- ============================================================ -->
      <div id="tab_axi" class="section-pane">
        <div class="card">
          <div class="card-title"><span>🔄</span> Giao Thức Bus AMBA AXI4-Lite & Chống Deadlock (Decoupled AW/W)</div>
          <p>
            Chuẩn AXI4-Lite tách rời kênh địa chỉ ghi (`AW`) và dữ liệu ghi (`W`). Master có thể gửi địa chỉ trước, dữ liệu trước hoặc cùng lúc:
          </p>
          <div class="interactive-box">
            <svg width="600" height="200" style="background:#0f172a; border-radius:6px;">
              <!-- Master -->
              <rect x="30" y="40" width="120" height="120" rx="6" fill="#1e293b" stroke="#0284c7" stroke-width="2"/>
              <text x="90" y="105" fill="#38bdf8" font-size="13" font-weight="bold" text-anchor="middle">CPU Master</text>

              <!-- Slave -->
              <rect x="450" y="40" width="120" height="120" rx="6" fill="#1e293b" stroke="#10b981" stroke-width="2"/>
              <text x="510" y="105" fill="#34d399" font-size="13" font-weight="bold" text-anchor="middle">AXI Slave</text>

              <!-- Channels -->
              <line x1="150" y1="60" x2="450" y2="60" stroke="#06b6d4" stroke-width="2"/>
              <text x="300" y="55" fill="#67e8f9" font-size="11" text-anchor="middle">Write Address (AW): awaddr, awvalid, awready ➔</text>

              <line x1="150" y1="100" x2="450" y2="100" stroke="#f59e0b" stroke-width="2"/>
              <text x="300" y="95" fill="#fcd34d" font-size="11" text-anchor="middle">Write Data (W): wdata, wstrb, wvalid, wready ➔</text>

              <line x1="450" y1="140" x2="150" y2="140" stroke="#10b981" stroke-width="2"/>
              <text x="300" y="135" fill="#6ee7b7" font-size="11" text-anchor="middle">⬅ Write Response (B): bresp, bvalid, bready</text>
            </svg>
          </div>
          <div class="math-callout">
            <strong>Khóa liên động tự vệ (Hardware Interlock)</strong>:<br/>
            Khi mảng PE đang bận (`busy == 1`), nếu CPU vô tình ghi đè dữ liệu vào bộ đệm, phần cứng tự động khóa xung ghi nội bộ, bảo vệ ma trận cũ nguyên vẹn và phản hồi `bresp = OKAY` để CPU không bị treo!
          </div>
        </div>
      </div>

      <!-- ============================================================ -->
      <!-- TAB 8: SOC INTEGRATION -->
      <!-- ============================================================ -->
      <div id="tab_soc" class="section-pane">
        <div class="card">
          <div class="card-title"><span>💻</span> Hệ Thống Trên Chip (SoC) & Vai Trò Firmware C</div>
          <p>
            Đây là mô hình thiết kế đồng bộ Phần cứng - Phần mềm (Hardware-Software Co-Design):
          </p>
          <table class="data-table">
            <tr>
              <th>Khối Chức Năng</th>
              <th>Thực Thể</th>
              <th>Nhiệm Vụ Cụ Thể Trong Hệ Thống</th>
            </tr>
            <tr>
              <td><strong>Vi xử lý Host</strong></td>
              <td>PicoRV32 RISC-V CPU (Mã nguồn mở)</td>
              <td>Chạy Firmware C điều khiển Menu, giao tiếp UART, chia khối Tiling và xuất kết quả ra LED 7 đoạn.</td>
            </tr>
            <tr>
              <td><strong>Bộ Tăng Tốc</strong></td>
              <td>Mảng Tâm Thu 64 PE (Systolic Core)</td>
              <td>Thực hiện các phép nhân tích lũy ma trận nặng nề nhất với tốc độ gấp $173.7\times$.</td>
            </tr>
            <tr>
              <td><strong>Trục Kết Nối</strong></td>
              <td>AXI4-Lite Crossbar Interconnect</td>
              <td>Phân xử bus và ánh xạ địa chỉ MMIO giữa CPU, RAM 32KB, UART và Accelerator.</td>
            </tr>
          </table>
        </div>
      </div>

      <!-- ============================================================ -->
      <!-- TAB 9: UVM VERIFICATION -->
      <!-- ============================================================ -->
      <div id="tab_uvm" class="section-pane">
        <div class="card">
          <div class="card-title"><span>🎯</span> Kim Tự Tháp Kiểm Chứng & Chuẩn UVM 1.1c (88 Bins)</div>
          <p>
            Chiến lược kiểm chứng vi mạch đa tầng bảo đảm tiêu chuẩn nghiệm thu <strong>100% Bit-True</strong> so với mô hình toán học tham chiếu:
          </p>
          <div class="interactive-box">
            <svg width="600" height="240" style="background:#0f172a; border-radius:6px;">
              <!-- Tier 3 -->
              <polygon points="300,30 200,90 400,90" fill="#0369a1" stroke="#38bdf8" stroke-width="2"/>
              <text x="300" y="70" fill="#fff" font-size="11" font-weight="bold" text-anchor="middle">TẦNG 3: SoC Co-Sim (3.87M Cycles)</text>

              <!-- Tier 2 -->
              <polygon points="200,95 400,95 460,160 140,160" fill="#047857" stroke="#34d399" stroke-width="2"/>
              <text x="300" y="135" fill="#fff" font-size="11" font-weight="bold" text-anchor="middle">TẦNG 2: AXI Backpressure & UVM 1.1c (88 Bins 100%)</text>

              <!-- Tier 1 -->
              <polygon points="140,165 460,165 520,225 80,225" fill="#b45309" stroke="#fbbf24" stroke-width="2"/>
              <text x="300" y="200" fill="#fff" font-size="11" font-weight="bold" text-anchor="middle">TẦNG 1: Unit Tests Từng Module RTL (61/61 Checks PASS)</text>
            </svg>
          </div>
          <p>
            <strong>Độ bao phủ chức năng 100%</strong>: 39 Point Bins + 49 Cross Bins đo đạc toàn bộ các số cực trị ($-128, +127, 0$), toàn bộ kích thước $K \in [1..16]$, 9 mức dịch bit và các chế độ kích hoạt phi tuyến.
          </p>
        </div>
      </div>

    </div>
  </div>
</div>

<script>
const titles = {
  tab_im2col: "Thuật Toán im2col & Ánh Xạ Phép Tích Chập Sang GEMM",
  tab_tiling: "Chiến Lược Chia Khối Ma Trận Lớn (Tiling Engine)",
  tab_quant: "Lượng Tử Hóa INT8 & Bảo Đảm Toán Học Không Tràn Số",
  tab_skew: "Mạng Lệch Pha Nhịp Sóng Bậc Thang (0T..7T)",
  tab_pe: "Cấu Trúc Vi Mô 1 Phần Tử Xử Lý (PE Datapath)",
  tab_gen1_gen2: "Bước Nhảy Vọt Kiến Trúc: Gen-1 vs. Gen-2",
  tab_axi: "Giao Thức Bus AMBA AXI4-Lite & Cơ Chế Decoupled Handshake",
  tab_soc: "Hệ Thống Trên Chip (SoC) & Vai Trò Của Firmware C",
  tab_uvm: "Kim Tự Tháp Kiểm Chứng & Chuẩn UVM 1.1c (88 Bins)"
};

function switchTab(tabId) {
  // Update sidebar active
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  event.currentTarget.classList.add('active');

  // Update tabs
  document.querySelectorAll('.section-pane').forEach(el => el.classList.remove('active'));
  document.getElementById(tabId).classList.add('active');

  // Update header title
  document.getElementById('topTitle').innerText = titles[tabId];
}

// Interactive im2col logic
let currentPatch = 0;
const imgSize = 5;
const kernelSize = 3;
const outSize = imgSize - kernelSize + 1; // 3x3 = 9 patches
const totalPatches = outSize * outSize;

// Sample 5x5 image pixels
const imgPixels = [
  12, 18, 25, 30, 42,
  15, 22, 33, 40, 55,
  10, 14, 28, 35, 48,
  8,  12, 20, 26, 38,
  5,  9,  15, 21, 30
];

function renderIm2col() {
  const imgBox = document.getElementById('im2col_img');
  const matBox = document.getElementById('im2col_mat');
  imgBox.innerHTML = '';
  matBox.innerHTML = '';

  const patchRow = Math.floor(currentPatch / outSize);
  const patchCol = currentPatch % outSize;

  // Render 5x5 image
  for (let r = 0; r < 5; r++) {
    for (let c = 0; c < 5; c++) {
      const cell = document.createElement('div');
      cell.className = 'grid-cell';
      cell.innerText = imgPixels[r * 5 + c];

      const inKernel = (r >= patchRow && r < patchRow + 3 && c >= patchCol && c < patchCol + 3);
      if (inKernel) {
        cell.style.background = '#0284c7';
        cell.style.color = '#fff';
        cell.style.border = '1px solid #38bdf8';
      } else {
        cell.style.background = '#1e293b';
        cell.style.color = '#94a3b8';
      }
      imgBox.appendChild(cell);
    }
  }

  // Render 9x9 Matrix B (9 rows, 9 cols)
  for (let r = 0; r < 9; r++) {
    for (let c = 0; c < 9; c++) {
      const cell = document.createElement('div');
      cell.className = 'grid-cell';
      cell.style.width = '28px';
      cell.style.height = '24px';
      cell.style.fontSize = '9px';

      if (c === currentPatch) {
        cell.style.background = '#9333ea';
        cell.style.color = '#fff';
        cell.style.border = '1px solid #c084fc';
        // Compute pixel value
        const kr = Math.floor(r / 3);
        const kc = r % 3;
        cell.innerText = imgPixels[(patchRow + kr) * 5 + (patchCol + kc)];
      } else {
        cell.style.background = '#1e293b';
        cell.style.color = '#64748b';
        cell.innerText = '·';
      }
      matBox.appendChild(cell);
    }
  }

  document.getElementById('patchLabel').innerText = `Patch ${currentPatch} (Tọa độ hàng ${patchRow}, cột ${patchCol})`;
}

function nextPatch() {
  currentPatch = (currentPatch + 1) % totalPatches;
  renderIm2col();
}

function prevPatch() {
  currentPatch = (currentPatch - 1 + totalPatches) % totalPatches;
  renderIm2col();
}

renderIm2col();
</script>
</body>
</html>
"""

with open(portal_path, 'w', encoding='utf-8') as f:
    f.write(portal_html)

print(f"[SUCCESS] Generated Visual Architecture Portal: {portal_path} (Size: {os.path.getsize(portal_path):,} bytes)")

# Copy to artifacts
ARTIFACT_DIR = r"C:\Users\hoang\.gemini\antigravity\brain\9f77ab99-8f96-4134-8b24-d1c001f13ee8"
if os.path.exists(ARTIFACT_DIR):
    import shutil
    shutil.copy(portal_path, os.path.join(ARTIFACT_DIR, "visual_architecture_portal.html"))
    print(f"[SUCCESS] Copied portal to artifact directory.")
