# -*- coding: utf-8 -*-
"""
Script: tools/build_metis_unified_platform.py
Builds the Flagship Single-Page Metis Application: index.html
Unifying:
1. Full 50% Research Report (All 6 chapters, equations, tables, figures)
2. Live MNIST CNN Inference Studio (Drawing canvas, Im2Col, 64-PE Systolic Core, 7-seg hex display, argmax)
3. Architectural Gallery of all 18 Standalone GIFs with Lightbox Modal
4. Interactive 2D Systolic Wavefront & Skew Unit Simulator
5. FPGA Telemetry & Benchmark Dashboard (FMAX 69.49 MHz, Slack, ALUTs, UVM 100% coverage)
All under the refined neutral Zinc Metis Design System!
"""

import os
import re
import json

def build():
    print("==============================================================================")
    print("BUILDING UNIFIED METIS ARCHITECTURE PLATFORM -> index.html")
    print("==============================================================================")

    # 1. Read Report Markdown and convert to Metis HTML
    with open('BaoCao_TienDo_50_CNN_Systolic_SoC.md', 'r', encoding='utf-8') as f:
        md_text = f.read()

    # 2. Read CNN Model Data
    with open('scratch/mnist_model_and_samples.json', 'r', encoding='utf-8') as f:
        mnist_data_str = f.read()

    # 3. Read CNN Studio JS
    with open('scratch/cnn_studio_js_extracted.js', 'r', encoding='utf-8') as f:
        cnn_js_str = f.read()

    # Convert Markdown to HTML with Metis styling
    lines = md_text.splitlines()
    report_html_lines = []
    
    in_code = False
    code_lang = ""
    code_buf = []
    
    in_table = False
    table_header = []
    table_rows = []
    
    def flush_table():
        nonlocal in_table, table_header, table_rows
        if not in_table:
            return ""
        t_html = ['<div class="table-responsive my-3"><table class="table table-hover table-striped-columns align-middle border mb-0">']
        if table_header:
            t_html.append('<thead class="table-dark"><tr>')
            for th in table_header:
                t_html.append(f'<th class="fw-semibold py-2 px-3">{th}</th>')
            t_html.append('</tr></thead>')
        if table_rows:
            t_html.append('<tbody>')
            for r in table_rows:
                t_html.append('<tr>')
                for td in r:
                    t_html.append(f'<td class="py-2 px-3 text-secondary">{td}</td>')
                t_html.append('</tr>')
            t_html.append('</tbody>')
        t_html.append('</table></div>')
        in_table = False
        table_header = []
        table_rows = []
        return '\n'.join(t_html)

    def format_inline(txt):
        def img_repl(m):
            alt = m.group(1)
            url = m.group(2).strip()
            if not url.startswith('figures/') and not url.startswith('data:') and not url.startswith('http'):
                url = 'figures/' + url.replace('\\', '/').split('/')[-1]
            return f'''<div class="card my-4 overflow-hidden border shadow-sm">
  <div class="card-body p-2 text-center bg-black bg-opacity-25">
    <img src="{url}" alt="{alt}" class="img-fluid rounded report-fig" style="max-height: 480px; object-fit: contain; cursor: zoom-in;" onclick="openLightbox('{url}', '{alt}')" title="Click to view full size">
  </div>
  <div class="card-footer bg-transparent py-2 px-3 border-top text-center text-muted small">
    <i class="bi bi-image me-1"></i> {alt}
  </div>
</div>'''
        txt = re.sub(r'!\[(.*?)\]\((.*?)\)', img_repl, txt)
        txt = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong class="fw-bold text-emphasis"><em>\1</em></strong>', txt)
        txt = re.sub(r'\*\*(.*?)\*\*', r'<strong class="fw-semibold text-emphasis">\1</strong>', txt)
        txt = re.sub(r'\*(.*?)\*', r'<em>\1</em>', txt)
        txt = re.sub(r'`([^`]+)`', r'<code class="px-1.5 py-0.5 rounded bg-body-tertiary text-primary font-monospace small">\1</code>', txt)
        return txt

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Code fence
        if stripped.startswith('```'):
            if in_code:
                in_code = False
                code_content = '\n'.join(code_buf)
                report_html_lines.append(f'''<div class="card my-3 border shadow-sm overflow-hidden">
  <div class="card-header bg-body-tertiary py-1.5 px-3 d-flex justify-content-between align-items-center border-bottom">
    <span class="badge bg-primary-subtle text-primary font-monospace small">{code_lang or "code"}</span>
    <button class="btn btn-sm btn-link text-muted p-0 text-decoration-none" onclick="navigator.clipboard.writeText(this.closest('.card').querySelector('pre').innerText); alert('Copied to clipboard!')"><i class="bi bi-clipboard me-1"></i>Copy</button>
  </div>
  <div class="card-body p-0">
    <pre class="m-0 p-3 bg-dark text-light font-monospace small" style="overflow-x: auto;"><code>{code_content}</code></pre>
  </div>
</div>''')
                code_buf = []
                code_lang = ""
            else:
                report_html_lines.append(flush_table())
                in_code = True
                code_lang = stripped[3:].strip()
                code_buf = []
            i += 1
            continue
            
        if in_code:
            code_buf.append(line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
            i += 1
            continue
            
        # Table row
        if stripped.startswith('|') and stripped.endswith('|'):
            cells = [format_inline(c.strip()) for c in stripped.split('|')[1:-1]]
            if all(set(c).issubset({'-', ':', ' '}) for c in cells):
                i += 1
                continue
            if not in_table:
                in_table = True
                table_header = cells
            else:
                table_rows.append(cells)
            i += 1
            continue
        else:
            if in_table:
                report_html_lines.append(flush_table())
                
        # Headings
        if stripped.startswith('# '):
            title = stripped[2:].strip()
            anchor = re.sub(r'[^a-zA-Z0-9]+', '-', title).strip('-').lower()
            report_html_lines.append(f'<div class="pt-4 pb-2 mb-4 border-bottom" id="{anchor}"><h1 class="h2 fw-bold text-primary mb-1">{title}</h1></div>')
            i += 1
            continue
            
        if stripped.startswith('## '):
            title = stripped[3:].strip()
            anchor = re.sub(r'[^a-zA-Z0-9]+', '-', title).strip('-').lower()
            report_html_lines.append(f'<div class="pt-4 pb-2 mb-3 mt-4 border-bottom" id="{anchor}"><h2 class="h4 fw-bold text-emphasis mb-1"><i class="bi bi-bookmark-check text-primary me-2"></i>{title}</h2></div>')
            i += 1
            continue
            
        if stripped.startswith('### '):
            title = stripped[4:].strip()
            anchor = re.sub(r'[^a-zA-Z0-9]+', '-', title).strip('-').lower()
            report_html_lines.append(f'<div class="pt-3 pb-1 mb-2 mt-3" id="{anchor}"><h3 class="h5 fw-semibold text-emphasis mb-1"><i class="bi bi-chevron-right text-muted small me-1"></i>{title}</h3></div>')
            i += 1
            continue
            
        if stripped.startswith('#### '):
            title = stripped[5:].strip()
            report_html_lines.append(f'<h4 class="h6 fw-semibold text-secondary mt-3 mb-2">{title}</h4>')
            i += 1
            continue
            
        if stripped.startswith('##### '):
            title = stripped[6:].strip()
            report_html_lines.append(f'<h5 class="h6 fw-medium text-muted mt-2 mb-1">{title}</h5>')
            i += 1
            continue
            
        if stripped.startswith('> '):
            quote_text = format_inline(stripped[2:])
            report_html_lines.append(f'<div class="alert alert-primary bg-primary-subtle border-primary-subtle py-2 px-3 mb-3 small d-flex align-items-center gap-2"><i class="bi bi-info-circle-fill text-primary"></i><div>{quote_text}</div></div>')
            i += 1
            continue
            
        if stripped.startswith('- ') or stripped.startswith('* '):
            li_text = format_inline(stripped[2:])
            report_html_lines.append(f'<li class="mb-1 text-secondary">{li_text}</li>')
            i += 1
            continue
            
        if stripped == '':
            i += 1
            continue
            
        report_html_lines.append(f'<p class="mb-3 text-secondary lh-base">{format_inline(line)}</p>')
        i += 1
        
    report_html_lines.append(flush_table())
    report_body_html = '\n'.join(report_html_lines)
    print(f"Report Body HTML ready ({len(report_body_html):,} chars).")

    # 4. Define 18 GIFs metadata
    gifs_metadata = [
        {
            "id": "GIF-01",
            "file": "01_im2col_convolution_mapping.gif",
            "title": "01. Ánh Xạ Tích Chập Im2Col Sang Mảng 64 PE",
            "category": "wavefront",
            "category_name": "Dòng Dữ Liệu & Wavefront",
            "desc": "Chuyển đổi cửa sổ trượt 3×3 trên ảnh 28×28 thành ma trận 2D [9×196], nạp song song vào 64 PE để tính chập không gian.",
            "latency": "1 chu kỳ / pixel",
            "throughput": "64 MAC / chu kỳ",
            "module": "RTL/pe_gemm.sv"
        },
        {
            "id": "GIF-02",
            "file": "02_matrix_tiling_engine.gif",
            "title": "02. Chiến Lược Chia Khối Ma Trận Lớn (Tiling Engine)",
            "category": "wavefront",
            "category_name": "Dòng Dữ Liệu & Wavefront",
            "desc": "Cố định Tile A0 [8×9] trong SRAM Buffer A, tái sử dụng 98 lần liên tiếp với các Sub-tile B0..B24, giảm 98× số lần đọc DRAM ngoài.",
            "latency": "37 Cycles / Sub-tile",
            "throughput": "Tiết kiệm 98× DRAM",
            "module": "RTL/gemm_controller.sv"
        },
        {
            "id": "GIF-03",
            "file": "03_quantization_overflow_pipeline.gif",
            "title": "03. Đường Ống Lượng Hóa INT8 & Chống Tràn INT32",
            "category": "pe",
            "category_name": "Vi Kiến Trúc PE",
            "desc": "Tích lũy INT32 không bao giờ tràn số (-2.14B..+2.14B), sau đó dịch bit và kẹp ngưỡng ReLU [0, 127] bảo toàn độ chính xác 100%.",
            "latency": "1 chu kỳ Pipelined",
            "throughput": "8 Ngõ Ra Song Song",
            "module": "RTL/quantize_relu_unit.sv"
        },
        {
            "id": "GIF-04",
            "file": "04_cnn_mnist_inference.gif",
            "title": "04. Dòng Dữ Liệu Suy Luận Mạng CNN MNIST Đầu Cuối",
            "category": "soc",
            "category_name": "Hệ Thống SoC & AXI",
            "desc": "Chuỗi tính toán đầy đủ: Ảnh [28×28] → Conv1 [14×14×16] → ReLU → MaxPool [7×7×16] → Fully Connected [10] → Dự đoán Argmax.",
            "latency": "145.04 µs @ 50MHz",
            "throughput": "6,895 Khung Hình/s",
            "module": "RTL/soc_top.sv"
        },
        {
            "id": "GIF-05",
            "file": "05_skew_wavefront_alignment.gif",
            "title": "05. Mạng Lệch Pha Nhịp Sóng Bậc Thang (Skew Unit)",
            "category": "wavefront",
            "category_name": "Dòng Dữ Liệu & Wavefront",
            "desc": "Chuỗi D-FF trễ Hàng A (0T..7T) và Cột B (0T..7T) đồng bộ toán hạng gặp nhau chính xác tại chu kỳ T = i + j, tạo sóng chéo 45 độ.",
            "latency": "56 D-FFs Trễ",
            "throughput": "16 Bytes / Chu kỳ",
            "module": "RTL/systolic_skew_unit.sv"
        },
        {
            "id": "GIF-06",
            "file": "06_pe_microarchitecture.gif",
            "title": "06. Cấu Trúc Vi Mô Phần Tử Xử Lý (PE Datapath)",
            "category": "pe",
            "category_name": "Vi Kiến Trúc PE",
            "desc": "Mỗi PE tích hợp thanh ghi Reg_A, Reg_B, bộ nhân Signed 8×8, bộ cộng 32-bit và thanh ghi C_acc Output-Stationary đạt FMAX 69.49 MHz.",
            "latency": "1 MAC / Chu kỳ",
            "throughput": "Slack +1.815 ns (MET)",
            "module": "RTL/pe_gemm.sv"
        },
        {
            "id": "GIF-07",
            "file": "07_systolic_array_64pe_mesh.gif",
            "title": "07. Mạng Lưới Mảng Tâm Thu 64 PE Không Gian 2D (8×8 Mesh)",
            "category": "pe",
            "category_name": "Vi Kiến Trúc PE",
            "desc": "Mạng lưới 64 PE kết nối cục bộ 100%, không xung đột bus toàn cục, truyền sóng nhịp nhàng 64 phép tính nhân-cộng đồng thời.",
            "latency": "14 chu kỳ Wavefront",
            "throughput": "64 Phép MAC / Cycle",
            "module": "RTL/systolic_array_core.sv"
        },
        {
            "id": "GIF-08",
            "file": "08_gen1_vs_gen2_evolution.gif",
            "title": "08. Tiến Hóa Vi Kiến Trúc Gen-1 Sang Gen-2",
            "category": "deepdive",
            "category_name": "Nghiên Cứu Chuyên Sâu",
            "desc": "Đột phá Gen-2: Đóng gói 4-byte nạp 1 chu kỳ, xuất dữ liệu SIMD 8 hàng đồng thời (8 cycles vs 64 cycles Gen-1), tăng tốc tổng thể 4.81×.",
            "latency": "8 Cycles Drain (vs 64)",
            "throughput": "Tăng tốc 4.81×",
            "module": "RTL/systolic_accelerator_top.sv"
        },
        {
            "id": "GIF-09",
            "file": "09_axi_handshake_deadlock.gif",
            "title": "09. Cơ Chế Bắt Tay AXI4-Lite & Chống Deadlock",
            "category": "soc",
            "category_name": "Hệ Thống SoC & AXI",
            "desc": "Giao thức bắt tay kép VALID/READY hai chiều, cơ chế Busy-Gating tự động phản hồi chèn chu kỳ chờ, ngăn chặn 100% tình trạng deadlock.",
            "latency": "Zero Deadlock",
            "throughput": "Chuẩn AXI4-Lite AMBA",
            "module": "RTL/axi_interconnect.sv"
        },
        {
            "id": "GIF-10",
            "file": "10_soc_mmio_firmware.gif",
            "title": "10. Giao Thức Thanh Ghi MMIO & Firmware PicoRV32",
            "category": "soc",
            "category_name": "Hệ Thống SoC & AXI",
            "desc": "CPU PicoRV32 điều khiển bộ tăng tốc qua vùng địa chỉ MMIO 0x1000_0000 bằng driver C thuần túy (systolic.h), tương thích SoC chuẩn mở.",
            "latency": "1 Chu kỳ Read/Write",
            "throughput": "Độc lập Phần Mềm/Cứng",
            "module": "RTL/soc_top.sv"
        },
        {
            "id": "GIF-11",
            "file": "11_fpga_synth_timing.gif",
            "title": "11. Hiện Thực Hóa FPGA Cyclone IV/V & Khép Thời Gian (STA)",
            "category": "uvm",
            "category_name": "Kiểm Thử UVM & FPGA",
            "desc": "Tổng hợp và phân tích thời gian tĩnh trên Quartus Prime: FMAX đạt 65.04 MHz (DE2-115) và 69.49 MHz (DE10-Standard), Slack dương +1.815 ns.",
            "latency": "FMAX 69.49 MHz",
            "throughput": "Timing Met 100%",
            "module": "Quartus Prime STA"
        },
        {
            "id": "GIF-12",
            "file": "12_uvm_verification_waveform.gif",
            "title": "12. Môi Trường Kiểm Thử UVM 1.2 & Dạng Sóng Waveform",
            "category": "uvm",
            "category_name": "Kiểm Thử UVM & FPGA",
            "desc": "Khung kiểm thử chuẩn công nghiệp UVM: Sequence, Driver, Monitor, Scoreboard đối soát Bit-True với Golden Model Python, đóng 100% Coverage.",
            "latency": "3.87M Chu kỳ Co-Sim",
            "throughput": "100% Coverage Đóng",
            "module": "TB/tb_soc_uvm.sv"
        },
        {
            "id": "DEEP-01",
            "file": "memory_wall_von_neumann.gif",
            "title": "13. Nút Thắt Cổ Chai Bộ Nhớ (Memory Wall) Von Neumann vs Mảng Tâm Thu",
            "category": "deepdive",
            "category_name": "Nghiên Cứu Chuyên Sâu",
            "desc": "So sánh trực quan: CPU truyền thống bị nghẽn bus DRAM 90% thời gian, trong khi mảng tâm thu tái sử dụng không gian giúp giảm 98× băng thông.",
            "latency": "Giảm 98× Truy Xuất RAM",
            "throughput": "Vượt Nút Thắt Memory Wall",
            "module": "Kiến Trúc Máy Tính"
        },
        {
            "id": "DEEP-02",
            "file": "neural_network_general_architecture.gif",
            "title": "14. Sơ Đồ Khối Kiến Trúc Mạng CNN Tổng Quát",
            "category": "deepdive",
            "category_name": "Nghiên Cứu Chuyên Sâu",
            "desc": "Mô hình toán học đa tầng: Input Tensor → Convolution → Batch Normalization → Activation ReLU → Pooling → Fully Connected → Softmax.",
            "latency": "Đa Tầng Khả Mở",
            "throughput": "Tương Thích Mọi Mạng CNN",
            "module": "Mô Hình AI"
        },
        {
            "id": "DEEP-03",
            "file": "soc_general_architecture.gif",
            "title": "15. Kiến Trúc Hệ Thống Trên Chip (SoC) Tổng Quát với Bus AXI",
            "category": "soc",
            "category_name": "Hệ Thống SoC & AXI",
            "desc": "Sơ đồ kiến trúc toàn diện: CPU PicoRV32, AXI Crossbar phân xử trung tâm, AXI RAM 64KB, AXI UART, và CNN Systolic Core 64 PE.",
            "latency": "AMBA AXI4-Lite Crossbar",
            "throughput": "Bus 32-bit Chuẩn Công Nghiệp",
            "module": "RTL/soc_top.sv"
        },
        {
            "id": "DEEP-04",
            "file": "uvm_internal_communication.gif",
            "title": "16. Giao Tiếp Nội Bộ Môi Trường UVM (TLM FIFO & Analysis Ports)",
            "category": "uvm",
            "category_name": "Kiểm Thử UVM & FPGA",
            "desc": "Luồng dữ liệu chuẩn IEEE 1800.2: Sequence tạo transaction → TLM FIFO → Driver phát xung AXI → Monitor thu thập → Scoreboard đối soát.",
            "latency": "Chuẩn UVM 1.2 IEEE",
            "throughput": "Bit-True 100% 64/64 PE",
            "module": "TB/uvm_env.sv"
        },
        {
            "id": "DEEP-05",
            "file": "gen1_vs_gen2_deep_dive.gif",
            "title": "17. Phân Tích Chuyên Sâu Hiệu Năng Vi Kiến Trúc Gen-1 vs Gen-2",
            "category": "deepdive",
            "category_name": "Nghiên Cứu Chuyên Sâu",
            "desc": "So sánh chi tiết chu trình Drain: Gen-1 rút tuần tự 64 chu kỳ, Gen-2 rút SIMD song song 8 hàng chỉ trong 8 chu kỳ, tăng tốc 4.81×.",
            "latency": "8 Cycles Drain (vs 64)",
            "throughput": "Tăng Tốc 4.81× Đo Đạc Thật",
            "module": "Kiến Trúc So Sánh"
        },
        {
            "id": "DEEP-06",
            "file": "systolic_dataflow_8x8.gif",
            "title": "18. Mô Phỏng Đồng Bộ Lan Truyền Sóng Dữ Liệu 64 PE 2D Wavefront",
            "category": "wavefront",
            "category_name": "Dòng Dữ Liệu & Wavefront",
            "desc": "37 chu kỳ xung nhịp hoàn chỉnh của một tile tính toán: nạp dữ liệu, truyền sóng chéo 45 độ, tích lũy cục bộ và rút kết quả ra đệm.",
            "latency": "37 Cycles / Tile",
            "throughput": "Hoạt Họa 64 PE Động",
            "module": "Mô Phỏng 2D Systolic"
        }
    ]

    # Build GIF cards HTML
    gif_cards_html = []
    for g in gifs_metadata:
        card = f'''<div class="col-xl-4 col-md-6 gif-card-item" data-category="{g['category']}">
  <div class="card h-100 border shadow-sm metis-card">
    <div class="card-header bg-transparent py-2.5 px-3 d-flex justify-content-between align-items-center border-bottom">
      <div class="d-flex align-items-center gap-2">
        <span class="badge bg-primary-subtle text-primary border border-primary-subtle font-monospace">{g['id']}</span>
        <h6 class="mb-0 fw-semibold text-truncate" style="max-width: 220px;" title="{g['title']}">{g['title']}</h6>
      </div>
      <span class="badge bg-secondary-subtle text-secondary small">{g['category_name'].split('&')[0].strip()}</span>
    </div>
    <div class="card-body p-2 text-center bg-black bg-opacity-25 position-relative">
      <img src="figures/{g['file']}" class="w-100 img-fluid rounded" style="max-height: 220px; object-fit: contain; cursor: zoom-in;" alt="{g['title']}" onclick="openLightbox('figures/{g['file']}', '{g['title']}', '{g['desc']}', '{g['module']}')">
    </div>
    <div class="card-body p-3 pt-2">
      <p class="text-secondary small mb-2 lh-sm" style="min-height: 48px;">{g['desc']}</p>
      <div class="d-flex justify-content-between align-items-center small text-muted pt-2 border-top">
        <span><i class="bi bi-clock-history me-1 text-primary"></i>{g['latency']}</span>
        <span><i class="bi bi-cpu me-1 text-success"></i>{g['throughput']}</span>
      </div>
    </div>
    <div class="card-footer bg-transparent border-top-0 d-flex justify-content-between align-items-center pt-0 pb-3 px-3">
      <small class="text-muted font-monospace"><i class="bi bi-code-slash me-1"></i>{g['module']}</small>
      <button class="btn btn-sm btn-outline-primary" onclick="openLightbox('figures/{g['file']}', '{g['title']}', '{g['desc']}', '{g['module']}')">
        <i class="bi bi-zoom-in me-1"></i>Phóng To
      </button>
    </div>
  </div>
</div>'''
        gif_cards_html.append(card)
    gif_grid_str = '\n'.join(gif_cards_html)

    # 5. Assemble Master index.html
    full_html = f'''<!DOCTYPE html>
<html lang="vi" data-bs-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CNN Systolic SoC Platform — Metis Architecture Suite (Báo Cáo 50% & Interactive Studio)</title>
  
  <!-- Google Fonts: Inter & Fira Code -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500;600;700&display=swap" rel="stylesheet">
  
  <!-- Bootstrap 5.3 & Bootstrap Icons -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
  
  <!-- KaTeX Support for Mathematical Formulas -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"
          onload="renderMathInElement(document.body, {{delimiters: [{{left: '$$', right: '$$', display: true}}, {{left: '$', right: '$', display: false}}]}});"></script>

  <style>
    /* ==========================================================================
       METIS DESIGN SYSTEM — REFINED ZINC PALETTE & TOKENS
       ========================================================================== */
    :root, [data-bs-theme="dark"] {{
      --surface-app: #09090b;
      --surface-panel: #121215;
      --surface-card: #18181b;
      --surface-sunken: #0c0c0e;
      --surface-hover: #222226;
      --border-subtle: #27272a;
      --border-strong: #3f3f46;
      --ink-primary: #f4f4f5;
      --ink-secondary: #a1a1aa;
      --ink-muted: #71717a;
      --accent-blue: #2563eb;
      --accent-emerald: #10b981;
      --accent-amber: #f59e0b;
      --accent-rose: #f43f5e;
      --accent-purple: #8b5cf6;
      --accent-cyan: #06b6d4;
      --bs-body-bg: var(--surface-app);
      --bs-body-color: var(--ink-primary);
      --bs-border-color: var(--border-subtle);
    }}

    [data-bs-theme="light"] {{
      --surface-app: #fafafa;
      --surface-panel: #ffffff;
      --surface-card: #ffffff;
      --surface-sunken: #f4f4f5;
      --surface-hover: #e4e4e7;
      --border-subtle: #e4e4e7;
      --border-strong: #d4d4d8;
      --ink-primary: #09090b;
      --ink-secondary: #52525b;
      --ink-muted: #71717a;
      --bs-body-bg: var(--surface-app);
      --bs-body-color: var(--ink-primary);
      --bs-border-color: var(--border-subtle);
    }}

    body {{
      font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background-color: var(--surface-app);
      color: var(--ink-primary);
      overflow-x: hidden;
      font-size: 0.9rem;
      line-height: 1.6;
    }}

    /* Layout */
    .app-wrapper {{
      display: flex;
      min-height: 100vh;
      flex-direction: column;
    }}

    .app-header {{
      height: 62px;
      position: sticky;
      top: 0;
      z-index: 1030;
      background: var(--surface-panel);
      border-bottom: 1px solid var(--border-subtle);
      backdrop-filter: blur(8px);
    }}

    .app-main-layout {{
      display: flex;
      flex: 1;
    }}

    .app-sidebar {{
      width: 280px;
      background: var(--surface-panel);
      border-right: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      position: sticky;
      top: 62px;
      height: calc(100vh - 62px);
      overflow-y: auto;
      flex-shrink: 0;
      transition: width 0.25s ease;
    }}

    .app-content {{
      flex: 1;
      padding: 24px 32px;
      min-width: 0;
      background: var(--surface-app);
    }}

    @media (max-width: 992px) {{
      .app-sidebar {{
        display: none;
      }}
      .app-content {{
        padding: 16px;
      }}
    }}

    /* Sidebar Navigation Links */
    .sidebar-group-title {{
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 0.8px;
      text-transform: uppercase;
      color: var(--ink-muted);
      padding: 16px 20px 6px;
    }}

    .sidebar-nav-link {{
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 16px;
      margin: 2px 10px;
      border-radius: 8px;
      color: var(--ink-secondary);
      text-decoration: none;
      font-size: 0.85rem;
      font-weight: 500;
      transition: all 0.15s ease;
      cursor: pointer;
      border: 1px solid transparent;
    }}

    .sidebar-nav-link:hover {{
      background: var(--surface-hover);
      color: var(--ink-primary);
    }}

    .sidebar-nav-link.active {{
      background: rgba(37, 99, 235, 0.12);
      color: var(--accent-blue);
      font-weight: 600;
      border-color: rgba(37, 99, 235, 0.3);
    }}

    /* Nav Pills Header */
    .nav-tab-btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 0.825rem;
      font-weight: 600;
      color: var(--ink-secondary);
      border: 1px solid transparent;
      background: transparent;
      transition: all 0.15s ease;
      cursor: pointer;
    }}

    .nav-tab-btn:hover {{
      background: var(--surface-hover);
      color: var(--ink-primary);
    }}

    .nav-tab-btn.active {{
      background: var(--accent-blue);
      color: #fff;
    }}

    /* Card System */
    .card {{
      background-color: var(--surface-card);
      border-color: var(--border-subtle);
      border-radius: 12px;
    }}

    .card-header {{
      background-color: var(--surface-panel);
      border-bottom-color: var(--border-subtle);
    }}

    /* KPI Cards */
    .kpi-card {{
      padding: 16px 20px;
      border-radius: 12px;
      background: var(--surface-card);
      border: 1px solid var(--border-subtle);
      transition: transform 0.15s ease, border-color 0.15s ease;
    }}
    .kpi-card:hover {{
      transform: translateY(-2px);
      border-color: var(--border-strong);
    }}
    .kpi-label {{
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--ink-muted);
    }}
    .kpi-value {{
      font-size: 1.5rem;
      font-weight: 700;
      line-height: 1.2;
      margin-top: 4px;
      color: var(--ink-primary);
    }}

    /* Tab Panes */
    .tab-content-pane {{
      display: none;
    }}
    .tab-content-pane.active {{
      display: block;
      animation: tabFade 0.2s ease-in-out;
    }}
    @keyframes tabFade {{
      from {{ opacity: 0; transform: translateY(4px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Lightbox Modal */
    .lightbox-modal {{
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0, 0, 0, 0.85);
      z-index: 1090;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 24px;
      backdrop-filter: blur(8px);
    }}
    .lightbox-modal.active {{
      display: flex;
    }}
    .lightbox-container {{
      max-width: 1000px;
      width: 100%;
      background: var(--surface-card);
      border: 1px solid var(--border-strong);
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
    }}

    /* CNN Studio Controls & Styling */
    .digit-pill-btn {{
      width: 32px;
      height: 32px;
      border-radius: 6px;
      border: 1px solid var(--border-subtle);
      background: var(--surface-panel);
      color: var(--ink-secondary);
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .digit-pill-btn:hover {{
      background: var(--surface-hover);
      color: var(--ink-primary);
    }}
    .digit-pill-btn.active {{
      background: var(--accent-blue);
      color: #fff;
      border-color: var(--accent-blue);
    }}

    #inputCanvas, #filterCanvas, #outputCanvas {{
      background: #000;
      border-radius: 8px;
      border: 1px solid var(--border-subtle);
    }}

    /* 7-Segment SVG Lit */
    #hexSvg polygon {{
      fill: #1f2937;
      transition: fill 0.15s ease, filter 0.15s ease;
    }}
    #hexSvg polygon.lit {{
      fill: #10b981 !important;
      filter: drop-shadow(0 0 6px #10b981) drop-shadow(0 0 2px #fff);
    }}

    /* Hardware LEDs */
    .hw-led {{
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2px;
      font-size: 9px;
      font-family: 'Fira Code', monospace;
      color: var(--ink-muted);
    }}
    .led-dot {{
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: #374151;
      border: 1px solid #4b5563;
      transition: all 0.15s ease;
    }}
    .led-dot.lit {{
      background: #10b981 !important;
      box-shadow: 0 0 8px #10b981, 0 0 2px #fff !important;
      border-color: #6ee7b7 !important;
    }}
  </style>
</head>

<body>
<div class="app-wrapper">

  <!-- =========================================================================
       METIS HEADER BAR
       ========================================================================= -->
  <header class="app-header d-flex align-items-center justify-content-between px-3 px-lg-4">
    <div class="d-flex align-items-center gap-3">
      <!-- Brand Logo -->
      <a href="./index.html" class="d-flex align-items-center text-decoration-none gap-2">
        <div class="rounded-3 p-1 d-flex align-items-center justify-content-center" style="background: linear-gradient(135deg, #2563eb, #10b981); width: 34px; height: 34px;">
          <i class="bi bi-cpu-fill text-white fs-5"></i>
        </div>
        <div>
          <span class="h6 mb-0 fw-bold text-emphasis">CNN Systolic SoC</span>
          <span class="badge bg-primary-subtle text-primary border border-primary-subtle ms-2 d-none d-sm-inline-block">Metis v2.4</span>
        </div>
      </a>

      <!-- Quick Nav Switcher (Top Pills) -->
      <nav class="d-none d-xl-flex align-items-center gap-1 ms-4">
        <button class="nav-tab-btn active" onclick="switchMainTab('report')" id="nav-btn-report">
          <i class="bi bi-file-earmark-text"></i> Báo Cáo 50%
        </button>
        <button class="nav-tab-btn" onclick="switchMainTab('cnn-studio')" id="nav-btn-cnn-studio">
          <i class="bi bi-play-circle"></i> MNIST Studio
        </button>
        <button class="nav-tab-btn" onclick="switchMainTab('gif-library')" id="nav-btn-gif-library">
          <i class="bi bi-collection-play"></i> 18 GIFs Động
        </button>
        <button class="nav-tab-btn" onclick="switchMainTab('skew-sim')" id="nav-btn-skew-sim">
          <i class="bi bi-water"></i> Skew & Wavefront
        </button>
        <button class="nav-tab-btn" onclick="switchMainTab('fpga-metrics')" id="nav-btn-fpga-metrics">
          <i class="bi bi-speedometer2"></i> Đo Kiểm FPGA
        </button>
      </nav>
    </div>

    <!-- Header Right Action Tools -->
    <div class="d-flex align-items-center gap-2">
      <span class="badge bg-success-subtle text-success border border-success-subtle px-2.5 py-1.5 d-none d-md-inline-flex align-items-center gap-1 font-monospace">
        <span class="spinner-grow spinner-grow-sm text-success" style="width: 8px; height: 8px;"></span>
        FMAX: 69.49 MHz (Met)
      </span>

      <!-- Theme Switcher -->
      <button class="btn btn-sm btn-outline-secondary rounded-3 px-2.5 py-1.5" onclick="toggleTheme()" title="Chuyển chế độ Sáng / Tối" id="btn-theme-toggle">
        <i class="bi bi-moon-fill" id="theme-icon"></i>
      </button>

      <!-- Print Report Button -->
      <button class="btn btn-sm btn-outline-secondary rounded-3 px-2.5 py-1.5 d-none d-sm-inline-block" onclick="window.print()" title="In hoặc Xuất PDF">
        <i class="bi bi-printer"></i>
      </button>

      <!-- Fullscreen Button -->
      <button class="btn btn-sm btn-outline-secondary rounded-3 px-2.5 py-1.5 d-none d-lg-inline-block" onclick="toggleFullscreen()" title="Toàn màn hình">
        <i class="bi bi-arrows-fullscreen"></i>
      </button>

      <!-- Run Demo Button -->
      <button class="btn btn-sm btn-primary rounded-3 px-3 py-1.5 fw-semibold" onclick="switchMainTab('cnn-studio')">
        <i class="bi bi-play-fill me-1"></i>Chạy Suy Luận
      </button>
    </div>
  </header>

  <!-- =========================================================================
       APP MAIN LAYOUT (SIDEBAR + CONTENT)
       ========================================================================= -->
  <div class="app-main-layout">

    <!-- METIS SIDEBAR -->
    <aside class="app-sidebar">
      <div class="sidebar-group-title">Ứng Dụng Nền Tảng</div>
      <a class="sidebar-nav-link active" onclick="switchMainTab('report')" id="side-link-report">
        <i class="bi bi-file-earmark-text text-primary"></i>
        <span>Báo Cáo Nghiên Cứu 50%</span>
        <span class="badge bg-secondary-subtle text-secondary ms-auto small">6 Chương</span>
      </a>
      <a class="sidebar-nav-link" onclick="switchMainTab('cnn-studio')" id="side-link-cnn-studio">
        <i class="bi bi-camera-video text-success"></i>
        <span>Studio MNIST Live (64 PE)</span>
        <span class="badge bg-success-subtle text-success ms-auto small">Live</span>
      </a>
      <a class="sidebar-nav-link" onclick="switchMainTab('gif-library')" id="side-link-gif-library">
        <i class="bi bi-film text-warning"></i>
        <span>Thư Viện 18 Mô Phỏng Động</span>
        <span class="badge bg-warning-subtle text-warning ms-auto small">18 GIFs</span>
      </a>
      <a class="sidebar-nav-link" onclick="switchMainTab('skew-sim')" id="side-link-skew-sim">
        <i class="bi bi-water text-info"></i>
        <span>Mô Phỏng 2D Skew Wavefront</span>
        <span class="badge bg-info-subtle text-info ms-auto small">RTL</span>
      </a>
      <a class="sidebar-nav-link" onclick="switchMainTab('fpga-metrics')" id="side-link-fpga-metrics">
        <i class="bi bi-speedometer2 text-danger"></i>
        <span>Đo Kiểm & Tài Nguyên FPGA</span>
        <span class="badge bg-danger-subtle text-danger ms-auto small">100% Cov</span>
      </a>

      <div class="sidebar-group-title">Mục Lục Báo Cáo 50%</div>
      <a class="sidebar-nav-link py-1 text-muted small" href="#phan-i-tai-lieu-thuyet-minh-tien-do-50" onclick="switchMainTab('report')">
        <i class="bi bi-hash"></i> Phần I: Thuyết Minh 50%
      </a>
      <a class="sidebar-nav-link py-1 text-muted small" href="#1-thong-tin-chung-dong-luc-de-tai" onclick="switchMainTab('report')">
        <i class="bi bi-1-circle"></i> 1. Động Lực & GEMM
      </a>
      <a class="sidebar-nav-link py-1 text-muted small" href="#2-thiet-ke-vi-mach-phan-cung-rtl-kien-truc-gen-2" onclick="switchMainTab('report')">
        <i class="bi bi-2-circle"></i> 2. Vi Mạch RTL Gen-2
      </a>
      <a class="sidebar-nav-link py-1 text-muted small" href="#3-tich-hop-he-thong-tren-chip-soc-va-giao-tiep-bus" onclick="switchMainTab('report')">
        <i class="bi bi-3-circle"></i> 3. Tích Hợp SoC & AXI
      </a>
      <a class="sidebar-nav-link py-1 text-muted small" href="#4-phuong-phap-luan-va-ket-qua-kiem-chung-vi-mach-phan-tang" onclick="switchMainTab('report')">
        <i class="bi bi-4-circle"></i> 4. Kiểm Chứng UVM 1.2
      </a>
      <a class="sidebar-nav-link py-1 text-muted small" href="#5-ket-qua-tong-hop-mach-va-phan-tich-thoi-gian-tinh-sta" onclick="switchMainTab('report')">
        <i class="bi bi-5-circle"></i> 5. Tổng Hợp & STA FPGA
      </a>
      <a class="sidebar-nav-link py-1 text-muted small" href="#6-danh-gia-khoi-luong-da-dat-ke-hoach-50-tiep-theo" onclick="switchMainTab('report')">
        <i class="bi bi-6-circle"></i> 6. Đánh Giá & Kế Hoạch
      </a>
      <a class="sidebar-nav-link py-1 text-muted small" href="#phan-ii-huong-dan-chi-tiet-tung-buoc-chay-demo-truoc-hoi-dong" onclick="switchMainTab('report')">
        <i class="bi bi-terminal"></i> Phần II: Chạy 7 Demo
      </a>
      <a class="sidebar-nav-link py-1 text-muted small" href="#phan-iii-de-cuong-noi-dung-slide-thuyet-trinh-19-slides-kem-speaker-notes" onclick="switchMainTab('report')">
        <i class="bi bi-easel"></i> Phần III: 19 Slide Bảo Vệ
      </a>

      <!-- Mini Hardware Telemetry Widget at Bottom -->
      <div class="mt-auto p-3 border-top bg-body-tertiary">
        <div class="d-flex justify-content-between align-items-center mb-1">
          <small class="fw-semibold text-emphasis">Kiến trúc phần cứng</small>
          <span class="badge bg-success-subtle text-success">Gen-2 Active</span>
        </div>
        <div class="small text-muted font-monospace mb-1">• 64 PE Mesh (INT8 MAC)</div>
        <div class="small text-muted font-monospace mb-1">• 98× DRAM Bandwidth Saved</div>
        <div class="small text-muted font-monospace">• 8 Cycles Drain SIMD Output</div>
      </div>
    </aside>

    <!-- METIS CONTENT REGION -->
    <main class="app-content">

      <!-- =====================================================================
           TAB 1: BÁO CÁO TIẾN ĐỘ 50% TOÀN DIỆN
           ===================================================================== -->
      <div class="tab-content-pane active" id="pane-report">
        
        <!-- Report Executive Summary Header -->
        <div class="card mb-4 border shadow-sm">
          <div class="card-body p-4">
            <div class="d-flex flex-wrap justify-content-between align-items-start gap-3">
              <div>
                <span class="badge bg-primary-subtle text-primary border border-primary-subtle mb-2">Đồ Án Tốt Nghiệp Kỹ Sư Vi Mạch</span>
                <h1 class="h3 fw-bold text-emphasis mb-2">THIẾT KẾ VÀ HIỆN THỰC BỘ TĂNG TỐC MẠNG NƠ-RON CHẬP (CNN ACCELERATOR) DỰA TRÊN KIẾN TRÚC MẢNG TÂM THU (SYSTOLIC ARRAY) TRÊN FPGA</h1>
                <p class="text-secondary mb-0">Hệ Thống SoC Tích Hợp RISC-V PicoRV32, AMBA AXI4-Lite, Mảng 64 PE INT8, Khung Kiểm Thử UVM 1.2 và Hiện Thực Kit FPGA DE10-Standard.</p>
              </div>
              <div class="d-flex gap-2">
                <button class="btn btn-outline-secondary" onclick="window.print()"><i class="bi bi-printer me-1"></i>Xuất PDF</button>
                <button class="btn btn-primary" onclick="switchMainTab('cnn-studio')"><i class="bi bi-play-circle me-1"></i>Chạy MNIST Studio</button>
              </div>
            </div>

            <!-- Top 6 KPI Metric Cards -->
            <div class="row g-3 mt-3">
              <div class="col-6 col-md-4 col-xl-2">
                <div class="kpi-card text-center">
                  <div class="kpi-label">Mảng Tâm Thu</div>
                  <div class="kpi-value text-primary">64 PE</div>
                  <small class="text-muted">8×8 2D Mesh</small>
                </div>
              </div>
              <div class="col-6 col-md-4 col-xl-2">
                <div class="kpi-card text-center">
                  <div class="kpi-label">Chu Kỳ 1 Tile</div>
                  <div class="kpi-value text-success">37 T</div>
                  <small class="text-muted">Single-Cycle MAC</small>
                </div>
              </div>
              <div class="col-6 col-md-4 col-xl-2">
                <div class="kpi-card text-center">
                  <div class="kpi-label">Tái Sử Dụng A</div>
                  <div class="kpi-value text-warning">98×</div>
                  <small class="text-muted">Tiết Kiệm DRAM</small>
                </div>
              </div>
              <div class="col-6 col-md-4 col-xl-2">
                <div class="kpi-card text-center">
                  <div class="kpi-label">Tần Số FMAX</div>
                  <div class="kpi-value text-info">69.49 MHz</div>
                  <small class="text-muted">DE10-Standard</small>
                </div>
              </div>
              <div class="col-6 col-md-4 col-xl-2">
                <div class="kpi-card text-center">
                  <div class="kpi-label">Tăng Tốc Gen-2</div>
                  <div class="kpi-value text-danger">4.81×</div>
                  <small class="text-muted">vs Gen-1 Baseline</small>
                </div>
              </div>
              <div class="col-6 col-md-4 col-xl-2">
                <div class="kpi-card text-center">
                  <div class="kpi-label">UVM Coverage</div>
                  <div class="kpi-value text-purple" style="color: #8b5cf6;">100%</div>
                  <small class="text-muted">4/4 Test Plans Met</small>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Converted Report Content -->
        <div class="card border shadow-sm">
          <div class="card-body p-4 p-lg-5" style="max-width: 1100px; margin: 0 auto;">
            {report_body_html}
          </div>
        </div>

      </div>

      <!-- =====================================================================
           TAB 2: MNIST CNN HARDWARE INFERENCE STUDIO (LIVE ENGINE)
           ===================================================================== -->
      <div class="tab-content-pane" id="pane-cnn-studio">
        
        <!-- Header Banner -->
        <div class="card mb-3 border shadow-sm">
          <div class="card-body p-3 d-flex flex-wrap justify-content-between align-items-center gap-2">
            <div>
              <span class="badge bg-success-subtle text-success border border-success-subtle mb-1">Interactive Studio</span>
              <h2 class="h5 fw-bold text-emphasis mb-0">Phòng Trực Quan Hóa Động Thuật Toán CNN & Bộ Tăng Tốc Tâm Thu 64 PE</h2>
            </div>
            <div class="d-flex align-items-center gap-2">
              <span class="badge bg-secondary-subtle text-secondary font-monospace">DE10: 69.49 MHz</span>
              <span class="badge bg-primary-subtle text-primary font-monospace">Độ Trễ @ 50MHz: 145.04 µs</span>
            </div>
          </div>
        </div>

        <!-- Controls Toolbar -->
        <div class="card mb-3 border shadow-sm">
          <div class="card-body p-2.5 d-flex flex-wrap justify-content-between align-items-center gap-2">
            
            <!-- Sample Digit Selectors -->
            <div class="d-flex align-items-center gap-1.5 flex-wrap">
              <span class="small fw-semibold text-secondary me-2">Mẫu MNIST:</span>
              <div class="d-flex gap-1" id="digitPresetContainer">
                <button class="digit-pill-btn active" onclick="selectPresetDigit(0)">0</button>
                <button class="digit-pill-btn" onclick="selectPresetDigit(1)">1</button>
                <button class="digit-pill-btn" onclick="selectPresetDigit(2)">2</button>
                <button class="digit-pill-btn" onclick="selectPresetDigit(3)">3</button>
                <button class="digit-pill-btn" onclick="selectPresetDigit(4)">4</button>
                <button class="digit-pill-btn" onclick="selectPresetDigit(5)">5</button>
                <button class="digit-pill-btn" onclick="selectPresetDigit(6)">6</button>
                <button class="digit-pill-btn" onclick="selectPresetDigit(7)">7</button>
                <button class="digit-pill-btn" onclick="selectPresetDigit(8)">8</button>
                <button class="digit-pill-btn" onclick="selectPresetDigit(9)">9</button>
              </div>
              <!-- Hidden select for compatibility with legacy JS -->
              <select id="digitSelect" class="d-none" onchange="handleDigitSelectChange()"></select>
            </div>

            <!-- Actions & Speed -->
            <div class="d-flex align-items-center gap-2">
              <button class="btn btn-sm btn-success px-3 fw-semibold" id="btnStart" onclick="startConvolution()">
                <i class="bi bi-play-fill me-1"></i>Bắt Đầu Tích Chập
              </button>
              <button class="btn btn-sm btn-outline-secondary" id="btnPause" onclick="togglePause()">
                <i class="bi bi-pause-fill me-1"></i>Tạm Dừng
              </button>
              <button class="btn btn-sm btn-outline-secondary" id="btnStep" onclick="stepNext()" disabled>
                <i class="bi bi-skip-forward-fill me-1"></i>Bước Kế (+1)
              </button>
              <button class="btn btn-sm btn-outline-secondary d-none" id="btnDrawMode" onclick="toggleDrawMode()">
                <i class="bi bi-pencil me-1"></i>Vẽ Tay
              </button>
              <select class="form-select form-select-sm w-auto font-monospace" id="speedSelect" onchange="handleSpeedChange()">
                <option value="slow">Chậm (1.2s)</option>
                <option value="normal" selected>Chuẩn (0.6s)</option>
                <option value="fast">Nhanh (0.25s)</option>
              </select>
            </div>
          </div>
        </div>

        <!-- 3-Column Studio Grid -->
        <div class="row g-3">
          
          <!-- Column 1: Input Drawing Canvas -->
          <div class="col-xl-3 col-md-4">
            <div class="card h-100 border shadow-sm">
              <div class="card-header py-2.5 px-3 d-flex justify-content-between align-items-center bg-transparent">
                <span class="fw-semibold small"><i class="bi bi-pencil-square me-1 text-primary"></i>1. Tầng Đầu Vào (Input)</span>
                <span class="badge bg-secondary-subtle text-secondary font-monospace">28×28 INT8</span>
              </div>
              <div class="card-body p-3 text-center">
                <canvas id="inputCanvas" width="196" height="196" class="shadow-sm mx-auto d-block" style="cursor: crosshair;"></canvas>
                
                <div class="d-flex justify-content-center gap-1 mt-2">
                  <button class="btn btn-sm btn-outline-secondary py-1 px-2 small" onclick="clearCanvas()">Xóa Bảng</button>
                  <button class="btn btn-sm btn-outline-secondary py-1 px-2 small" onclick="invertCanvas()">Đảo Màu</button>
                  <button class="btn btn-sm btn-outline-secondary py-1 px-2 small" onclick="centerDrawing()">Căn Giữa</button>
                </div>

                <div class="mt-3 p-2 rounded bg-body-tertiary text-start small">
                  <div class="d-flex justify-content-between font-monospace text-muted mb-1">
                    <span>Tọa độ con trỏ:</span> <span id="mouseCoord" class="text-primary">(0, 0)</span>
                  </div>
                  <div class="d-flex justify-content-between font-monospace text-muted">
                    <span>Giá trị INT8:</span> <span id="mouseVal" class="text-success">-128 (Đen)</span>
                  </div>
                </div>
                <small class="text-muted d-block mt-2">Bạn có thể tự do vẽ số bằng chuột hoặc click chọn 10 mẫu chuẩn ở thanh trên.</small>
              </div>
            </div>
          </div>

          <!-- Column 2: Center Computing Monitor -->
          <div class="col-xl-6 col-md-8">
            <div class="card h-100 border shadow-sm">
              <div class="card-header py-2.5 px-3 d-flex justify-content-between align-items-center bg-transparent">
                <span class="fw-semibold small"><i class="bi bi-cpu me-1 text-success"></i>2. Tiến Trình Tính Toán Phần Cứng (Systolic Engine)</span>
                <span class="badge bg-primary-subtle text-primary font-monospace" id="lblEngineTag">Chờ Khởi Động</span>
              </div>
              <div class="card-body p-3">
                <canvas id="filterCanvas" width="560" height="260" class="w-100 mb-2"></canvas>
                
                <!-- Progress Track -->
                <div class="progress mb-2" style="height: 6px;">
                  <div class="progress-bar bg-success progress-bar-striped progress-bar-animated" id="progressFill" style="width: 0%;"></div>
                </div>

                <!-- Layer Description -->
                <div class="p-2.5 rounded bg-body-tertiary small">
                  <div class="d-flex justify-content-between align-items-center mb-1">
                    <span class="fw-semibold text-emphasis" id="currentLayer">Sẵn sàng thực thi...</span>
                    <span class="badge bg-secondary-subtle text-secondary font-monospace" id="layerSize">Output: Chờ lệnh</span>
                  </div>
                  <div class="text-secondary" id="layerDescription">Nhấn nút 'Bắt Đầu Tích Chập' để kích hoạt chuỗi trực quan hóa động qua lõi tăng tốc 64 PE.</div>
                </div>

                <!-- Hidden layers 0..7 for compatibility -->
                <div class="d-none">
                  <span id="layer0"></span><span id="layer1"></span><span id="layer2"></span>
                  <span id="layer3"></span><span id="layer4"></span><span id="layer5"></span>
                  <span id="layer6"></span><span id="layer7"></span>
                </div>

                <!-- Feature Maps Mini Canvas -->
                <canvas id="outputCanvas" width="560" height="100" class="w-100 mt-2"></canvas>
              </div>
            </div>
          </div>

          <!-- Column 3: FPGA Hardware Display & Argmax -->
          <div class="col-xl-3 col-md-12">
            <div class="card h-100 border shadow-sm">
              <div class="card-header py-2.5 px-3 d-flex justify-content-between align-items-center bg-transparent">
                <span class="fw-semibold small"><i class="bi bi-display me-1 text-warning"></i>3. Dự Đoán & Phần Cứng FPGA</span>
                <span class="badge bg-secondary-subtle text-secondary font-monospace">HEX & Softmax</span>
              </div>
              <div class="card-body p-3 d-flex flex-column justify-content-between">
                
                <!-- Prediction & 7-Segment -->
                <div class="p-3 rounded bg-black text-center border">
                  <div class="small text-muted font-monospace mb-1">DỰ ĐOÁN (ARGMAX)</div>
                  <div class="display-3 fw-bold text-success font-monospace my-1" id="predictedDigit">--</div>
                  <div class="small text-primary font-monospace" id="confidence">Độ tin cậy: --%</div>
                </div>

                <!-- 7-Segment Visualizer (OLED) -->
                <div class="my-3 text-center">
                  <small class="text-muted font-monospace d-block mb-1">HEX0 (FPGA 7-SEGMENT)</small>
                  <svg id="hexSvg" class="mx-auto" width="50" height="80" viewBox="0 0 100 160">
                    <polygon id="seg_a" points="20,10 80,10 70,20 30,20"/>
                    <polygon id="seg_b" points="80,12 90,22 80,78 72,70"/>
                    <polygon id="seg_c" points="80,82 90,90 80,148 72,138"/>
                    <polygon id="seg_d" points="20,150 80,150 70,140 30,140"/>
                    <polygon id="seg_e" points="20,82 28,90 20,148 10,138"/>
                    <polygon id="seg_f" points="20,12 28,22 20,78 10,70"/>
                    <polygon id="seg_g" points="22,78 78,78 72,82 28,82"/>
                  </svg>
                </div>

                <!-- LEDs -->
                <div>
                  <small class="text-muted font-monospace d-block mb-1">ĐÈN LEDR[9:0] (KIT DE10):</small>
                  <div class="d-flex justify-content-between p-2 rounded bg-black border" id="ledStrip"></div>
                </div>

                <!-- UART Console -->
                <div class="mt-3 p-2 rounded bg-black border text-start font-monospace small" style="max-height: 90px; overflow-y: auto;" id="uartLine">
                  <span class="text-success">[UART Core]:</span> Sẵn sàng nhận dữ liệu ma trận.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- =====================================================================
           TAB 3: THƯ VIỆN 18 MÔ PHỎNG ĐỘNG KIẾN TRÚC
           ===================================================================== -->
      <div class="tab-content-pane" id="pane-gif-library">
        
        <!-- Header -->
        <div class="card mb-3 border shadow-sm">
          <div class="card-body p-3 d-flex flex-wrap justify-content-between align-items-center gap-3">
            <div>
              <span class="badge bg-warning-subtle text-warning border border-warning-subtle mb-1">Bộ Sưu Tập Đồ Họa</span>
              <h2 class="h5 fw-bold text-emphasis mb-0">Thư Viện Trực Quan Hóa Động 18 Mô Phỏng Vi Kiến Trúc</h2>
              <p class="text-secondary small mb-0">Bộ ảnh GIF 16:9 sắc nét, mô phỏng từ tầng bóng bán dẫn PE đến toàn bộ mạng SoC & bus AXI.</p>
            </div>

            <!-- Filter Buttons -->
            <div class="d-flex flex-wrap gap-1" id="gifFilterContainer">
              <button class="btn btn-sm btn-primary" onclick="filterGifs('all')">Tất Cả (18)</button>
              <button class="btn btn-sm btn-outline-secondary" onclick="filterGifs('pe')">Vi Kiến Trúc PE (3)</button>
              <button class="btn btn-sm btn-outline-secondary" onclick="filterGifs('wavefront')">Wavefront (4)</button>
              <button class="btn btn-sm btn-outline-secondary" onclick="filterGifs('soc')">SoC & AXI (4)</button>
              <button class="btn btn-sm btn-outline-secondary" onclick="filterGifs('uvm')">UVM & FPGA (4)</button>
              <button class="btn btn-sm btn-outline-secondary" onclick="filterGifs('deepdive')">Chuyên Sâu (3)</button>
            </div>
          </div>
        </div>

        <!-- GIF Cards Grid -->
        <div class="row g-3" id="gifGridContainer">
          {gif_grid_str}
        </div>
      </div>

      <!-- =====================================================================
           TAB 4: MÔ PHỎNG 2D SKEW UNIT & WAVEFRONT TƯƠNG TÁC
           ===================================================================== -->
      <div class="tab-content-pane" id="pane-skew-sim">
        <div class="card border shadow-sm mb-4">
          <div class="card-header bg-transparent py-3 px-4 d-flex justify-content-between align-items-center border-bottom">
            <div>
              <span class="badge bg-info-subtle text-info border border-info-subtle mb-1">RTL Hardware Wavefront</span>
              <h3 class="h5 fw-bold text-emphasis mb-0">Mô Phỏng Lan Truyền Sóng Dữ Liệu 2D Systolic Array (64 PE)</h3>
            </div>
            <span class="badge bg-success-subtle text-success font-monospace">RTL: systolic_skew_unit.sv</span>
          </div>
          <div class="card-body p-4 text-center">
            <p class="text-secondary small mb-3">Toán hạng Hàng A trễ $i \times T_{{clk}}$, Cột B trễ $j \times T_{{clk}}$. Dữ liệu gặp nhau chính xác tại chu kỳ $T = i + j$.</p>
            
            <div class="d-flex justify-content-center align-items-center gap-3 mb-3">
              <button class="btn btn-primary btn-sm px-3" onclick="toggleWavePlay()" id="btnWavePlay"><i class="bi bi-play-fill me-1"></i>Tự Động Chạy</button>
              <button class="btn btn-outline-secondary btn-sm" onclick="stepWaveCycle(-1)"><i class="bi bi-skip-backward-fill"></i></button>
              <span class="fw-bold font-monospace px-3 py-1 rounded bg-body-tertiary border" id="waveCycleLabel">Chu kỳ T = 6 / 14</span>
              <button class="btn btn-outline-secondary btn-sm" onclick="stepWaveCycle(1)"><i class="bi bi-skip-forward-fill"></i></button>
              <input type="range" class="form-range w-auto" min="0" max="14" value="6" id="waveRangeSlider" oninput="setWaveCycle(this.value)">
            </div>

            <div class="d-flex justify-content-center my-3">
              <img src="figures/05_skew_wavefront_alignment.gif" id="skewSimGif" class="img-fluid rounded border shadow-sm" style="max-height: 480px;">
            </div>

            <div class="row g-3 text-start mt-3" style="max-width: 900px; margin: 0 auto;">
              <div class="col-md-4">
                <div class="p-3 rounded bg-body-tertiary border">
                  <div class="small text-muted fw-semibold mb-1">ĐỘ TRỄ HÀNG A</div>
                  <div class="font-monospace text-primary fw-bold">delay_A[i] = i × T_clk</div>
                  <small class="text-secondary">Trễ từ 0T đến 7T qua 28 D-FF</small>
                </div>
              </div>
              <div class="col-md-4">
                <div class="p-3 rounded bg-body-tertiary border">
                  <div class="small text-muted fw-semibold mb-1">ĐỘ TRỄ CỘT B</div>
                  <div class="font-monospace text-danger fw-bold">delay_B[j] = j × T_clk</div>
                  <small class="text-secondary">Trễ từ 0T đến 7T qua 28 D-FF</small>
                </div>
              </div>
              <div class="col-md-4">
                <div class="p-3 rounded bg-body-tertiary border">
                  <div class="small text-muted fw-semibold mb-1">ĐẶC TÍNH SÓNG CHÉO</div>
                  <div class="font-monospace text-success fw-bold">T = i + j (Wavefront)</div>
                  <small class="text-secondary">100% truyền cục bộ, 0% xung đột bus</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- =====================================================================
           TAB 5: ĐO KIỂM & TÀI NGUYÊN FPGA
           ===================================================================== -->
      <div class="tab-content-pane" id="pane-fpga-metrics">
        <div class="card border shadow-sm mb-4">
          <div class="card-header bg-transparent py-3 px-4 d-flex justify-content-between align-items-center border-bottom">
            <div>
              <span class="badge bg-danger-subtle text-danger border border-danger-subtle mb-1">Hardware Telemetry</span>
              <h3 class="h5 fw-bold text-emphasis mb-0">Báo Cáo Tổng Hợp Mạch & Phân Tích Thời Gian Tĩnh (STA)</h3>
            </div>
            <span class="badge bg-primary-subtle text-primary font-monospace">Quartus Prime 22.1 Lite</span>
          </div>
          <div class="card-body p-4">
            
            <!-- Summary Stats -->
            <div class="row g-3 mb-4">
              <div class="col-md-3">
                <div class="kpi-card text-center">
                  <div class="kpi-label">FMAX DE10-Standard</div>
                  <div class="kpi-value text-success">69.49 MHz</div>
                  <small class="text-muted">Cyclone V (5CSEMA5F31C6)</small>
                </div>
              </div>
              <div class="col-md-3">
                <div class="kpi-card text-center">
                  <div class="kpi-label">FMAX DE2-115</div>
                  <div class="kpi-value text-info">65.04 MHz</div>
                  <small class="text-muted">Cyclone IV E (EP4CE115F29C7)</small>
                </div>
              </div>
              <div class="col-md-3">
                <div class="kpi-card text-center">
                  <div class="kpi-label">Worst Case Slack</div>
                  <div class="kpi-value text-primary">+1.815 ns</div>
                  <small class="text-muted">Met Timing @ 50 MHz Nominal</small>
                </div>
              </div>
              <div class="col-md-3">
                <div class="kpi-card text-center">
                  <div class="kpi-label">UVM Functional Cov</div>
                  <div class="kpi-value text-purple" style="color: #8b5cf6;">100.0%</div>
                  <small class="text-muted">4/4 Test Plans Completed</small>
                </div>
              </div>
            </div>

            <!-- Detailed Tables -->
            <h5 class="fw-bold text-emphasis mb-3"><i class="bi bi-table me-2 text-primary"></i>1. Bảng Tiêu Hao Tài Nguyên Phần Cứng Trên Kit FPGA</h5>
            <div class="table-responsive mb-4">
              <table class="table table-hover border">
                <thead class="table-dark">
                  <tr>
                    <th>Khối Chức Năng</th>
                    <th>Tài Nguyên Logic (ALMs / LEs)</th>
                    <th>Thanh Ghi D-FF</th>
                    <th>Bộ Nhân DSP 9×9</th>
                    <th>Bộ Nhớ M10K</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td class="fw-semibold">Mảng Tâm Thu 64 PE (`systolic_array_core.sv`)</td>
                    <td>4,120 ALMs (12.8%)</td>
                    <td>2,304 FFs</td>
                    <td>64 DSP Blocks</td>
                    <td>0 Kbits (Local FFs)</td>
                  </tr>
                  <tr>
                    <td class="fw-semibold">Mạng Lệch Pha (`systolic_skew_unit.sv`)</td>
                    <td>112 ALMs (0.3%)</td>
                    <td>448 FFs</td>
                    <td>0</td>
                    <td>0</td>
                  </tr>
                  <tr>
                    <td class="fw-semibold">Bộ Lượng Tử Hóa SIMD 8 Hàng (`quantize_relu_unit.sv`)</td>
                    <td>384 ALMs (1.2%)</td>
                    <td>256 FFs</td>
                    <td>0</td>
                    <td>0</td>
                  </tr>
                  <tr>
                    <td class="fw-semibold">Bộ Đệm Ma Trận A, B, C (32KB SRAM Buffer)</td>
                    <td>210 ALMs (0.6%)</td>
                    <td>128 FFs</td>
                    <td>0</td>
                    <td>256 Kbits (25 M10K)</td>
                  </tr>
                  <tr>
                    <td class="fw-semibold">CPU PicoRV32 + Bus AXI4-Lite Crossbar</td>
                    <td>1,420 ALMs (4.4%)</td>
                    <td>1,120 FFs</td>
                    <td>0</td>
                    <td>16 M10K (Instruction RAM)</td>
                  </tr>
                  <tr class="table-success fw-bold">
                    <td>TỔNG TOÀN HỆ THỐNG SOC (GEN-2)</td>
                    <td>8,421 ALMs (26.3%)</td>
                    <td>5,124 FFs</td>
                    <td>64 DSP (73%)</td>
                    <td>41 M10K Blocks (10%)</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <h5 class="fw-bold text-emphasis mb-3 mt-4"><i class="bi bi-graph-up-arrow me-2 text-success"></i>2. So Sánh Hiệu Năng & Tăng Tốc Gen-1 vs. Gen-2</h5>
            <div class="table-responsive">
              <table class="table table-hover border">
                <thead class="table-dark">
                  <tr>
                    <th>Tiêu Chí Kỹ Thuật</th>
                    <th>Gen-1 Baseline</th>
                    <th>Gen-2 Active</th>
                    <th>Mức Cải Thiện</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td class="fw-semibold">Chu kỳ rút kết quả C (Drain Phase)</td>
                    <td>64 chu kỳ (1 phần tử/chu kỳ)</td>
                    <td class="text-success fw-bold">8 chu kỳ (SIMD 8 hàng)</td>
                    <td><span class="badge bg-success">Tăng tốc 8.0×</span></td>
                  </tr>
                  <tr>
                    <td class="fw-semibold">Đóng gói nạp dữ liệu AXI</td>
                    <td>1 Byte / Giao dịch AXI</td>
                    <td class="text-success fw-bold">4 Bytes / Giao dịch AXI</td>
                    <td><span class="badge bg-success">Tăng tốc 4.0×</span></td>
                  </tr>
                  <tr>
                    <td class="fw-semibold">Độ trễ toàn bộ mạng MNIST (14×14×16)</td>
                    <td>697.6 µs @ 50MHz</td>
                    <td class="text-success fw-bold">145.04 µs @ 50MHz</td>
                    <td><span class="badge bg-success">Tăng tốc 4.81×</span></td>
                  </tr>
                  <tr>
                    <td class="fw-semibold">Tái sử dụng trọng số SRAM Buffer A</td>
                    <td>0 (Đọc lại từng lần)</td>
                    <td class="text-success fw-bold">98× Tái sử dụng</td>
                    <td><span class="badge bg-success">Giảm 98× DRAM</span></td>
                  </tr>
                </tbody>
              </table>
            </div>

          </div>
        </div>
      </div>

    </main>
  </div>
</div>

<!-- =========================================================================
     METIS UNIVERSAL LIGHTBOX MODAL
     ========================================================================= -->
<div class="lightbox-modal" id="lightboxModal" onclick="closeLightbox(event)">
  <div class="lightbox-container" onclick="event.stopPropagation()">
    <div class="card-header bg-transparent py-3 px-4 d-flex justify-content-between align-items-center border-bottom">
      <div class="d-flex align-items-center gap-2">
        <span class="badge bg-primary-subtle text-primary border" id="lightboxId">GIF-01</span>
        <h5 class="mb-0 fw-bold text-emphasis" id="lightboxTitle">Chi Tiết Vi Kiến Trúc</h5>
      </div>
      <button class="btn btn-sm btn-outline-secondary rounded-circle" onclick="closeLightbox()"><i class="bi bi-x-lg"></i></button>
    </div>
    <div class="p-3 text-center bg-black bg-opacity-50">
      <img src="" id="lightboxImg" class="img-fluid rounded shadow" style="max-height: 520px; object-fit: contain;">
    </div>
    <div class="p-4 border-top">
      <p class="text-secondary small mb-3" id="lightboxDesc">Mô tả chi tiết vi kiến trúc.</p>
      <div class="d-flex justify-content-between align-items-center">
        <span class="small font-monospace text-muted" id="lightboxModule"><i class="bi bi-code-slash me-1"></i>RTL/pe_gemm.sv</span>
        <a href="" id="lightboxDownloadBtn" download class="btn btn-sm btn-outline-primary"><i class="bi bi-download me-1"></i>Tải GIF Gốc</a>
      </div>
    </div>
  </div>
</div>

<!-- MODEL DATA & SCRIPTS -->
<script>
  // 1. EMBEDDED MODEL DATA (W1, W2, Biases, 10 MNIST Digits)
  const MODEL_DATA = {mnist_data_str};

  // 2. MAIN NAVIGATION CONTROLLER
  function switchMainTab(tabId) {{
    // Hide all panes
    document.querySelectorAll('.tab-content-pane').forEach(p => p.classList.remove('active'));
    // Deactivate top nav buttons
    document.querySelectorAll('.nav-tab-btn').forEach(b => b.classList.remove('active'));
    // Deactivate sidebar links
    document.querySelectorAll('.sidebar-nav-link').forEach(l => l.classList.remove('active'));

    // Activate selected
    const targetPane = document.getElementById('pane-' + tabId);
    if (targetPane) targetPane.classList.add('active');

    const topBtn = document.getElementById('nav-btn-' + tabId);
    if (topBtn) topBtn.classList.add('active');

    const sideLink = document.getElementById('side-link-' + tabId);
    if (sideLink) sideLink.classList.add('active');

    window.location.hash = tabId;
    window.scrollTo({{ top: 0, behavior: 'smooth' }});

    if (tabId === 'cnn-studio') {{
      setTimeout(() => {{
        if (typeof renderInputCanvas === 'function') renderInputCanvas();
        if (typeof resetVisualization === 'function' && (typeof isRunningAnimation === 'undefined' || !isRunningAnimation)) {{
          resetVisualization(false);
        }}
      }}, 60);
    }}
  }}

  // 3. THEME TOGGLE
  function toggleTheme() {{
    const html = document.documentElement;
    const current = html.getAttribute('data-bs-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-bs-theme', next);
    const icon = document.getElementById('theme-icon');
    icon.className = next === 'dark' ? 'bi bi-moon-fill' : 'bi bi-sun-fill';
  }}

  // 4. FULLSCREEN TOGGLE
  function toggleFullscreen() {{
    if (!document.fullscreenElement) {{
      document.documentElement.requestFullscreen();
    }} else if (document.exitFullscreen) {{
      document.exitFullscreen();
    }}
  }}

  // 5. LIGHTBOX MODAL
  function openLightbox(url, title, desc, module) {{
    document.getElementById('lightboxImg').src = url;
    document.getElementById('lightboxTitle').textContent = title || 'Chi Tiết Mô Phỏng';
    document.getElementById('lightboxDesc').textContent = desc || '';
    document.getElementById('lightboxModule').innerHTML = '<i class="bi bi-code-slash me-1"></i>' + (module || 'RTL Source');
    document.getElementById('lightboxDownloadBtn').href = url;
    document.getElementById('lightboxModal').classList.add('active');
  }}

  function closeLightbox(e) {{
    document.getElementById('lightboxModal').classList.remove('active');
  }}

  // 6. GIF FILTER CONTROLLER
  function filterGifs(cat) {{
    document.querySelectorAll('#gifFilterContainer button').forEach(b => {{
      b.classList.remove('btn-primary');
      b.classList.add('btn-outline-secondary');
    }});
    if (event && event.target) {{
      event.target.classList.remove('btn-outline-secondary');
      event.target.classList.add('btn-primary');
    }}

    document.querySelectorAll('.gif-card-item').forEach(card => {{
      if (cat === 'all' || card.getAttribute('data-category') === cat) {{
        card.style.display = 'block';
      }} else {{
        card.style.display = 'none';
      }}
    }});
  }}

  // 7. WAVEFRONT SIMULATOR
  let waveCycle = 6;
  let waveTimer = null;
  function setWaveCycle(c) {{
    waveCycle = parseInt(c);
    document.getElementById('waveCycleLabel').textContent = `Chu kỳ T = ${{waveCycle}} / 14`;
    document.getElementById('waveRangeSlider').value = waveCycle;
  }}
  function stepWaveCycle(delta) {{
    let next = waveCycle + delta;
    if (next < 0) next = 14;
    if (next > 14) next = 0;
    setWaveCycle(next);
  }}
  function toggleWavePlay() {{
    const btn = document.getElementById('btnWavePlay');
    if (waveTimer) {{
      clearInterval(waveTimer);
      waveTimer = null;
      btn.innerHTML = '<i class="bi bi-play-fill me-1"></i>Tự Động Chạy';
    }} else {{
      waveTimer = setInterval(() => stepWaveCycle(1), 850);
      btn.innerHTML = '<i class="bi bi-pause-fill me-1"></i>Tạm Dừng';
    }}
  }}

  // 8. CNN STUDIO EXTENSIONS & HELPERS
  function selectPresetDigit(d) {{
    document.querySelectorAll('#digitPresetContainer button').forEach((b, idx) => {{
      if (idx === d) b.classList.add('active');
      else b.classList.remove('active');
    }});
    const sel = document.getElementById('digitSelect');
    if (sel) sel.value = d;
    if (typeof loadPresetDigit === 'function') {{
      loadPresetDigit(d);
      if (typeof resetVisualization === 'function') resetVisualization(false);
    }}
  }}

  function clearCanvas() {{
    if (typeof inputPixels !== 'undefined') {{
      for (let r = 0; r < 28; r++) inputPixels[r].fill(0);
      if (typeof renderInputCanvas === 'function') renderInputCanvas();
      if (typeof resetVisualization === 'function') resetVisualization(false);
      if (typeof logUART === 'function') logUART("Đã xóa trắng bảng vẽ.");
    }}
  }}

  function invertCanvas() {{
    if (typeof inputPixels !== 'undefined') {{
      for (let r = 0; r < 28; r++) {{
        for (let c = 0; c < 28; c++) {{
          inputPixels[r][c] = 255 - inputPixels[r][c];
        }}
      }}
      if (typeof renderInputCanvas === 'function') renderInputCanvas();
      if (typeof logUART === 'function') logUART("Đã đảo màu bảng vẽ.");
    }}
  }}

  function centerDrawing() {{
    if (typeof inputPixels === 'undefined') return;
    let totalMass = 0, sumR = 0, sumC = 0;
    for (let r = 0; r < 28; r++) {{
      for (let c = 0; c < 28; c++) {{
        const v = inputPixels[r][c];
        if (v > 20) {{
          totalMass += v;
          sumR += r * v;
          sumC += c * v;
        }}
      }}
    }}
    if (totalMass === 0) return;
    const meanR = Math.round(sumR / totalMass);
    const meanC = Math.round(sumC / totalMass);
    const shiftR = 14 - meanR;
    const shiftC = 14 - meanC;

    const temp = [];
    for (let r = 0; r < 28; r++) temp[r] = new Uint8Array(28);

    for (let r = 0; r < 28; r++) {{
      for (let c = 0; c < 28; c++) {{
        const nr = r + shiftR;
        const nc = c + shiftC;
        if (nr >= 0 && nr < 28 && nc >= 0 && nc < 28) {{
          temp[nr][nc] = inputPixels[r][c];
        }}
      }}
    }}
    for (let r = 0; r < 28; r++) {{
      for (let c = 0; c < 28; c++) {{
        inputPixels[r][c] = temp[r][c];
      }}
    }}
    if (typeof renderInputCanvas === 'function') renderInputCanvas();
    if (typeof logUART === 'function') logUART(`Đã căn giữa nét vẽ (Dịch: hàng ${{shiftR}}, cột ${{shiftC}}).`);
  }}

  // 9. ON LOAD HASH ROUTING
  window.addEventListener('DOMContentLoaded', () => {{
    const canvas = document.getElementById('inputCanvas');
    if (canvas) {{
      canvas.addEventListener('mousemove', (e) => {{
        if (typeof inputPixels === 'undefined') return;
        const rect = canvas.getBoundingClientRect();
        const c = Math.min(27, Math.max(0, Math.floor(((e.clientX - rect.left) / rect.width) * 28)));
        const r = Math.min(27, Math.max(0, Math.floor(((e.clientY - rect.top) / rect.height) * 28)));
        const val = inputPixels[r][c];
        const qVal = Math.round((val / 255) * 255 - 128);
        const mouseCoord = document.getElementById('mouseCoord');
        const mouseVal = document.getElementById('mouseVal');
        if (mouseCoord) mouseCoord.textContent = `(${{r}}, ${{c}})`;
        if (mouseVal) mouseVal.textContent = `${{qVal}} (INT8)`;
      }});
    }}

    const hash = window.location.hash.replace('#', '');
    if (['report', 'cnn-studio', 'gif-library', 'skew-sim', 'fpga-metrics'].includes(hash)) {{
      switchMainTab(hash);
    }}
  }});
</script>

<!-- CNN STUDIO JAVASCRIPT ENGINE -->
<script>
{cnn_js_str}
</script>

</body>
</html>'''

    out_file = 'index.html'
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"[SUCCESS] Built Flagship Platform: {out_file} (Size: {os.path.getsize(out_file):,} bytes)!")

    # Also sync into figures/visual_architecture_portal.html
    with open('figures/visual_architecture_portal.html', 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"[SUCCESS] Synchronized figures/visual_architecture_portal.html!")

if __name__ == '__main__':
    build()
