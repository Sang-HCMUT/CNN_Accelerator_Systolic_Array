# -*- coding: utf-8 -*-
"""
Script: tools/integrate_3d_workflow_tab.py
Integrates the 3D Hardware Architecture Workflow into index.html as a first-class feature tab.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('tools/build_metis_unified_platform.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add Top Nav Button
old_top_nav = """        <button class="nav-tab-btn" onclick="switchMainTab('fpga-metrics')" id="nav-btn-fpga-metrics">
          <i class="bi bi-speedometer2"></i> FPGA Telemetry
        </button>"""

new_top_nav = """        <button class="nav-tab-btn" onclick="switchMainTab('3d-workflow')" id="nav-btn-3d-workflow">
          <i class="bi bi-box"></i> 3D Hardware Model
        </button>
        <button class="nav-tab-btn" onclick="switchMainTab('fpga-metrics')" id="nav-btn-fpga-metrics">
          <i class="bi bi-speedometer2"></i> FPGA Telemetry
        </button>"""

if old_top_nav in code:
    code = code.replace(old_top_nav, new_top_nav)
    print("[1/4] Added 3D Hardware Model button to top navbar.")
else:
    print("Warning: old_top_nav not matched.")

# 2. Add Sidebar Navigation Link
old_sidebar_link = """      <a class="sidebar-nav-link" onclick="switchMainTab('skew-sim')" id="side-link-skew-sim">
        <i class="bi bi-water text-info"></i>
        <span>2D Wavefront Skew Sim</span>
        <span class="badge bg-info-subtle text-info ms-auto small">RTL</span>
      </a>"""

new_sidebar_link = """      <a class="sidebar-nav-link" onclick="switchMainTab('3d-workflow')" id="side-link-3d-workflow">
        <i class="bi bi-box text-primary"></i>
        <span>3D Architecture Model</span>
        <span class="badge bg-primary-subtle text-primary ms-auto small">WebGL 3D</span>
      </a>
      <a class="sidebar-nav-link" onclick="switchMainTab('skew-sim')" id="side-link-skew-sim">
        <i class="bi bi-water text-info"></i>
        <span>2D Wavefront Skew Sim</span>
        <span class="badge bg-info-subtle text-info ms-auto small">RTL</span>
      </a>"""

if old_sidebar_link in code:
    code = code.replace(old_sidebar_link, new_sidebar_link)
    print("[2/4] Added 3D Architecture Model link to sidebar.")
else:
    print("Warning: old_sidebar_link not matched.")

# 3. Add Tab 6: 3D Hardware Workflow Pane
old_pane_insertion = """          </div>
        </div>
      </div>

    </main>"""

tab_3d_html = """          </div>
        </div>
      </div>

      <!-- =====================================================================
           TAB 6: MÔ HÌNH RENDER 3D WORKFLOW KIẾN TRÚC PHẦN CỨNG TOÀN DIỆN
           ===================================================================== -->
      <div class="tab-content-pane" id="pane-3d-workflow">
        
        <!-- Header Card -->
        <div class="card border shadow-sm mb-3">
          <div class="card-body p-4 d-flex flex-wrap justify-content-between align-items-center gap-3">
            <div>
              <div class="d-flex align-items-center gap-2 mb-1">
                <span class="badge bg-primary-subtle text-primary border border-primary-subtle">WebGL 3D Engine • Three.js</span>
                <span class="badge bg-success-subtle text-success border border-success-subtle font-monospace">Interactive Co-Simulation</span>
              </div>
              <h2 class="h5 fw-bold text-emphasis mb-1">Mô Hình Không Gian 3D Trực Quan Hóa Toàn Diện Kiến Trúc Phần Cứng (3D Hardware Architecture)</h2>
              <p class="text-secondary small mb-0" style="max-width: 820px;">
                Mô hình 3D tương tác mô tả trực quan toàn bộ chu trình luồng dữ liệu (Dataflow Workflow): từ lúc ảnh đầu vào đi vào, tách thành ma trận A & B qua Im2Col, nạp đệm SRAM, trễ sóng qua Skew Unit, lan truyền sóng chéo 45° trên mảng 64 PE, rút nhanh SIMD 8 hàng, lượng hóa ReLU, MaxPool cho đến khi xuất ra các ngoại vi SoC.
              </p>
            </div>
            <div class="d-flex gap-2">
              <a href="figures/hardware_3d_workflow.html" target="_blank" class="btn btn-sm btn-primary px-3 fw-semibold">
                <i class="bi bi-arrows-fullscreen me-1"></i>Mở Fullscreen 3D
              </a>
              <button class="btn btn-sm btn-outline-secondary" onclick="document.getElementById('iframe3d').src = document.getElementById('iframe3d').src" title="Khởi động lại mô hình 3D">
                <i class="bi bi-arrow-clockwise me-1"></i>Reset Góc Nhìn
              </button>
            </div>
          </div>
        </div>

        <!-- Embedded 3D Viewport Frame -->
        <div class="card border shadow-sm overflow-hidden mb-4" style="height: 720px; border-radius: 12px; background: #09090b;">
          <iframe id="iframe3d" src="figures/hardware_3d_workflow.html" class="w-100 h-100 border-0" allow="fullscreen" loading="lazy"></iframe>
        </div>

        <!-- 7-Stage Architectural Workflow Technical Breakdown Cards -->
        <h4 class="h6 fw-bold text-emphasis mb-3 text-uppercase font-monospace text-muted">
          <i class="bi bi-diagram-3 me-2 text-primary"></i>7 Công Đoạn Chi Tiết Trong Luồng Xử Lý Phần Cứng (End-to-End Workflow)
        </h4>

        <div class="row g-3 mb-4">
          
          <!-- Stage 1 -->
          <div class="col-md-6 col-xl-3">
            <div class="card h-100 border shadow-sm">
              <div class="card-header bg-transparent py-2.5 px-3 border-bottom d-flex justify-content-between align-items-center">
                <span class="fw-bold small text-primary"><i class="bi bi-1-circle me-1"></i>1. Input & Im2Col</span>
                <span class="badge bg-secondary-subtle text-secondary font-monospace" style="font-size: 0.65rem;">Tensor → GEMM</span>
              </div>
              <div class="card-body p-3 small text-secondary">
                <p class="mb-2"><strong>Ảnh đầu vào [28×28] INT8</strong> được quét bằng cửa sổ trượt 3×3. Thuật toán Im2Col trải phẳng mỗi cửa sổ 3×3 thành cột vector [9×1], ghép thành <strong>Ma trận B [9×196]</strong>.</p>
                <p class="mb-0 text-muted">16 bộ lọc trọng số tạo thành <strong>Ma trận A [16×9]</strong>. Biến phép tích chập 4 vòng lặp for thành 1 phép nhân ma trận GEMM thuần túy.</p>
              </div>
            </div>
          </div>

          <!-- Stage 2 -->
          <div class="col-md-6 col-xl-3">
            <div class="card h-100 border shadow-sm">
              <div class="card-header bg-transparent py-2.5 px-3 border-bottom d-flex justify-content-between align-items-center">
                <span class="fw-bold small text-warning"><i class="bi bi-2-circle me-1"></i>2. On-Chip SRAM Buffers</span>
                <span class="badge bg-warning-subtle text-warning font-monospace" style="font-size: 0.65rem;">98× DRAM Saved</span>
              </div>
              <div class="card-body p-3 small text-secondary">
                <p class="mb-2"><strong>Chia khối (Tiling Engine)</strong> ma trận lớn thành các sub-tile vừa vặn mảng 8×8. <strong>Sub-tile A0 [8×9] (72 Bytes)</strong> được nạp vào Buffer A và <strong>khóa cố định (Stationary)</strong>.</p>
                <p class="mb-0 text-muted">Buffer B sử dụng cơ chế Ping-Pong luân phiên stream các Sub-tile B0..B24 [9×8], tái sử dụng A0 đến <strong>98 lần liên tiếp</strong>, giảm 98× số lần đọc DRAM.</p>
              </div>
            </div>
          </div>

          <!-- Stage 3 -->
          <div class="col-md-6 col-xl-3">
            <div class="card h-100 border shadow-sm">
              <div class="card-header bg-transparent py-2.5 px-3 border-bottom d-flex justify-content-between align-items-center">
                <span class="fw-bold small text-purple" style="color: #8b5cf6;"><i class="bi bi-3-circle me-1"></i>3. Wavefront Skew Unit</span>
                <span class="badge bg-purple-subtle font-monospace" style="color: #8b5cf6; background: rgba(139, 92, 246, 0.15); font-size: 0.65rem;">56 D-FFs</span>
              </div>
              <div class="card-body p-3 small text-secondary">
                <p class="mb-2">Do mỗi PE tốn 1 chu kỳ clock để truyền dữ liệu cho PE kế bên, dữ liệu phải được <strong>lệch pha không gian</strong> bằng 56 D-Flip-Flop bậc thang.</p>
                <p class="mb-0 text-muted">Hàng A trễ $i \times T_{clk}$ (0T..7T), Cột B trễ $j \times T_{clk}$ (0T..7T). Dữ liệu gặp nhau chính xác tại chu kỳ <strong>$T = i + j$</strong>, tạo sóng chéo 45°.</p>
              </div>
            </div>
          </div>

          <!-- Stage 4 -->
          <div class="col-md-6 col-xl-3">
            <div class="card h-100 border shadow-sm">
              <div class="card-header bg-transparent py-2.5 px-3 border-bottom d-flex justify-content-between align-items-center">
                <span class="fw-bold small text-success"><i class="bi bi-4-circle me-1"></i>4. 64-PE Systolic Array</span>
                <span class="badge bg-success-subtle text-success font-monospace" style="font-size: 0.65rem;">Output-Stationary</span>
              </div>
              <div class="card-body p-3 small text-secondary">
                <p class="mb-2">Lưới 64 phần tử xử lý (8×8 Mesh). Mỗi PE chứa bộ nhân Signed 8×8, bộ cộng 32-bit và thanh ghi tích lũy $C_{acc}$ 32-bit.</p>
                <p class="mb-0 text-muted">A trượt sang Đông, B trượt xuống Nam. $C_{acc}$ đứng yên tại chỗ tích lũy 64 phép MAC đồng thời mỗi chu kỳ với FMAX đạt <strong>69.49 MHz</strong>.</p>
              </div>
            </div>
          </div>

          <!-- Stage 5 -->
          <div class="col-md-6 col-xl-4">
            <div class="card h-100 border shadow-sm">
              <div class="card-header bg-transparent py-2.5 px-3 border-bottom d-flex justify-content-between align-items-center">
                <span class="fw-bold small text-pink" style="color: #ec4899;"><i class="bi bi-5-circle me-1"></i>5. Gen-2 SIMD 8-Row Drain Bus</span>
                <span class="badge bg-pink-subtle font-monospace" style="color: #ec4899; background: rgba(236, 72, 153, 0.15); font-size: 0.65rem;">8.0× Speedup</span>
              </div>
              <div class="card-body p-3 small text-secondary">
                <p class="mb-2">Sau khi hoàn tất $K=9$ chu kỳ tích lũy, các kết quả 32-bit trong 64 PE sẵn sàng được rút ra đệm.</p>
                <p class="mb-0 text-muted"><strong>Đột phá Gen-2</strong>: Thay vì rút tuần tự 64 chu kỳ như Gen-1, mạch bus SIMD rút đồng thời 8 hàng chỉ trong <strong>8 chu kỳ xung nhịp</strong>, tăng tốc 8.0× giai đoạn drain kết quả.</p>
              </div>
            </div>
          </div>

          <!-- Stage 6 -->
          <div class="col-md-6 col-xl-4">
            <div class="card h-100 border shadow-sm">
              <div class="card-header bg-transparent py-2.5 px-3 border-bottom d-flex justify-content-between align-items-center">
                <span class="fw-bold small text-emerald" style="color: #10b981;"><i class="bi bi-6-circle me-1"></i>6. Quantized ReLU & Max-Pooling</span>
                <span class="badge bg-success-subtle text-success font-monospace" style="font-size: 0.65rem;">Zero Overflow</span>
              </div>
              <div class="card-body p-3 small text-secondary">
                <p class="mb-2"><strong>Đơn vị Lượng Hóa & ReLU 8 kênh song song</strong>: Dịch bit phải ($>> 8$) và kẹp ngưỡng saturation $[0, 127]$, triệt tiêu 100% lỗi tràn số.</p>
                <p class="mb-0 text-muted"><strong>Khối Max-Pooling 2×2 (Stride 2)</strong>: Giảm kích thước không gian bản đồ đặc trưng từ 28×28 xuống 14×14, giảm 4× lượng dữ liệu cho tầng phân lớp kế tiếp.</p>
              </div>
            </div>
          </div>

          <!-- Stage 7 -->
          <div class="col-md-12 col-xl-4">
            <div class="card h-100 border shadow-sm">
              <div class="card-header bg-transparent py-2.5 px-3 border-bottom d-flex justify-content-between align-items-center">
                <span class="fw-bold small text-info"><i class="bi bi-7-circle me-1"></i>7. Dense FC & Physical SoC Output</span>
                <span class="badge bg-info-subtle text-info font-monospace" style="font-size: 0.65rem;">AXI MMIO & HEX0</span>
              </div>
              <div class="card-body p-3 small text-secondary">
                <p class="mb-2">Các đặc trưng được trải phẳng và đưa qua tầng Dense FC trên mảng 64 PE để tính toán 10 giá trị logit tương ứng 10 chữ số (0..9).</p>
                <p class="mb-0 text-muted">Khối Argmax xác định nhãn có xác suất cao nhất, ghi qua bus AXI4-Lite lên vùng nhớ MMIO <code>0x1000_0000</code>, kích hoạt <strong>đèn LED 7 đoạn HEX0</strong> và thanh LEDR[9:0] hiển thị kết quả phân loại.</p>
              </div>
            </div>
          </div>

        </div>

      </div>

    </main>"""

if old_pane_insertion in code:
    code = code.replace(old_pane_insertion, tab_3d_html)
    print("[3/4] Added Tab 6 3D Workflow pane.")
else:
    print("Warning: old_pane_insertion not matched.")

# 4. Update tab switching hash recognition in JavaScript
old_hash_check = "if (['report', 'cnn-studio', 'gif-library', 'skew-sim', 'fpga-metrics'].includes(hash)) {"
new_hash_check = "if (['report', 'cnn-studio', 'gif-library', 'skew-sim', 'fpga-metrics', '3d-workflow'].includes(hash)) {"

if old_hash_check in code:
    code = code.replace(old_hash_check, new_hash_check)
    print("[4/4] Updated URL hash check to support 3d-workflow.")
else:
    print("Warning: old_hash_check not matched.")

with open('tools/build_metis_unified_platform.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Successfully updated tools/build_metis_unified_platform.py with 3D Hardware Model tab.")
