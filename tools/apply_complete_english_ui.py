# -*- coding: utf-8 -*-
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('tools/build_metis_unified_platform.py', 'r', encoding='utf-8') as f:
    code = f.read()

replacements = [
    # Top Nav
    ('<i class="bi bi-file-earmark-text"></i> Báo Cáo 50%', '<i class="bi bi-file-earmark-text"></i> 50% Report'),
    ('<i class="bi bi-collection-play"></i> 18 GIFs Động', '<i class="bi bi-collection-play"></i> 18 GIFs'),
    ('<i class="bi bi-speedometer2"></i> Đo Kiểm FPGA', '<i class="bi bi-speedometer2"></i> FPGA Telemetry'),
    ('title="Đổi giao diện Sáng / Tối"', 'title="Toggle Light / Dark Theme"'),
    ('title="Xem toàn màn hình"', 'title="Toggle Fullscreen"'),
    ('title="Mở tài liệu báo cáo"', 'title="Documentation"'),
    ('<i class="bi bi-play-fill me-1"></i>Chạy Suy Luận', '<i class="bi bi-play-fill me-1"></i>Live Studio'),

    # Sidebar Groups & Items
    ('<div class="sidebar-group-title">Ứng Dụng Nền Tảng</div>', '<div class="sidebar-group-title">Platform Apps</div>'),
    ('<span>Báo Cáo Nghiên Cứu 50%</span>', '<span>50% Research Report</span>'),
    ('<span>Thư Viện 18 Mô Phỏng Động</span>', '<span>18 Architectural GIFs</span>'),
    ('<span>Mô Phỏng 2D Skew Wavefront</span>', '<span>2D Wavefront Skew Sim</span>'),
    ('<span>Đo Kiểm & Tài Nguyên FPGA</span>', '<span>FPGA Telemetry & STA</span>'),
    ('<small class="fw-semibold text-emphasis">Kiến trúc phần cứng</small>', '<small class="fw-semibold text-emphasis">Hardware Architecture</small>'),

    # Tab 1 Header buttons & KPIs (Keep Title in Vietnamese as it's the Thesis Report)
    ('<i class="bi bi-printer me-1"></i>In Báo Cáo', '<i class="bi bi-printer me-1"></i>Print Report'),
    ('<i class="bi bi-play-circle me-1"></i>Chạy Thử Nghiệm CNN', '<i class="bi bi-play-circle me-1"></i>Launch CNN Studio'),
    ('<div class="kpi-label">Mảng Tâm Thu</div>', '<div class="kpi-label">Systolic Core</div>'),
    ('<div class="kpi-label">Chu Kỳ 1 Tile</div>', '<div class="kpi-label">Tile Latency</div>'),
    ('<div class="kpi-label">Tái Sử Dụng A</div>', '<div class="kpi-label">Weight Reuse</div>'),
    ('<small class="text-muted">Tiết Kiệm DRAM</small>', '<small class="text-muted">DRAM Traffic Saved</small>'),
    ('<div class="kpi-label">Tần Số FMAX</div>', '<div class="kpi-label">Maximum FMAX</div>'),
    ('<div class="kpi-label">Tăng Tốc Gen-2</div>', '<div class="kpi-label">Gen-2 Speedup</div>'),

    # Tab 2
    ('Độ Trễ @ 50MHz: 145.04 µs', 'Latency @ 50MHz: 145.04 µs'),
    ('<i class="bi bi-pencil me-1"></i>Vẽ Tay', '<i class="bi bi-pencil me-1"></i>Freehand Draw'),
    ('Bạn có thể tự do vẽ số bằng chuột hoặc click chọn 10 mẫu chuẩn (0..9) ở trên.',
     'Draw digits freely with mouse or touch, or select any of the 10 preset MNIST test samples (0..9) above.'),

    # Tab 3
    ('<span class="badge bg-warning-subtle text-warning border border-warning-subtle mb-1">Bộ Sưu Tập Đồ Họa Kỹ Thuật Vi Mạch</span>',
     '<span class="badge bg-warning-subtle text-warning border border-warning-subtle mb-1">Hardware Engineering Visuals</span>'),
    ('<h2 class="h5 fw-bold text-emphasis mb-0">Thư Viện Trực Quan Hóa Động 18 Mô Phỏng Vi Kiến Trúc</h2>',
     '<h2 class="h5 fw-bold text-emphasis mb-0">18-Module Interactive Architectural Simulation Library</h2>'),
    ('<p class="text-secondary small mb-0">Bộ ảnh GIF 16:9 sắc nét, mô phỏng từ tầng bóng bán dẫn PE đến toàn hệ thống SoC trên kit FPGA.</p>',
     '<p class="text-secondary small mb-0">Comprehensive 16:9 animations visualizing hardware dataflows from PE logic gates to full SoC on FPGA.</p>'),
    ('<button class="btn btn-sm btn-outline-secondary" onclick="filterGifs(\'deepdive\')">Chuyên Sâu (3)</button>',
     '<button class="btn btn-sm btn-outline-secondary" onclick="filterGifs(\'deepdive\')">Deep Dives (4)</button>'),

    # Tab 5 Table 2 Benchmark
    ('<th>Mức Cải Thiện</th>', '<th>Improvement / Speedup</th>'),
    ('<td class="fw-semibold">Chu kỳ rút kết quả C (Drain Phase)</td>', '<td class="fw-semibold">Result Drain Latency (Drain Phase)</td>'),
    ('<td>64 chu kỳ (1 phần tử/chu kỳ)</td>', '<td>64 cycles (1 element/cycle)</td>'),
    ('<td class="text-success fw-bold">8 chu kỳ (SIMD 8 hàng)</td>', '<td class="text-success fw-bold">8 cycles (8-row parallel SIMD)</td>'),
    ('<td><span class="badge bg-success">Tăng tốc 8.0×</span></td>', '<td><span class="badge bg-success">8.0× Speedup</span></td>'),
    ('<td class="fw-semibold">Đóng gói nạp dữ liệu AXI</td>', '<td class="fw-semibold">AXI Data Packing Efficiency</td>'),
    ('<td>1 Byte / Giao dịch AXI</td>', '<td>1 Byte / AXI Transfer</td>'),
    ('<td class="text-success fw-bold">4 Bytes / Giao dịch AXI</td>', '<td class="text-success fw-bold">4 Bytes / AXI Transfer</td>'),
    ('<td><span class="badge bg-success">Tăng tốc 4.0×</span></td>', '<td><span class="badge bg-success">4.0× Throughput</span></td>'),
    ('<td class="fw-semibold">Độ trễ toàn bộ mạng MNIST (14×14×16)</td>', '<td class="fw-semibold">Full MNIST CNN Latency (14×14×16)</td>'),
    ('<td><span class="badge bg-success">Tăng tốc 4.81×</span></td>', '<td><span class="badge bg-success">4.81× Speedup</span></td>'),
    ('<td class="fw-semibold">Tái sử dụng trọng số SRAM Buffer A</td>', '<td class="fw-semibold">SRAM Buffer A Weight Reuse</td>'),
    ('<td>0 (Đọc lại từng lần)</td>', '<td>None (Read every tile)</td>'),
    ('<td class="text-success fw-bold">98× Tái sử dụng</td>', '<td class="text-success fw-bold">98× In-Situ Reuse</td>'),
    ('<td><span class="badge bg-success">Giảm 98× DRAM</span></td>', '<td><span class="badge bg-success">98× DRAM Saved</span></td>'),

    # Lightbox Modal
    ('<h5 class="mb-0 fw-bold text-emphasis" id="lightboxTitle">Chi Tiết Vi Kiến Trúc</h5>',
     '<h5 class="mb-0 fw-bold text-emphasis" id="lightboxTitle">Microarchitectural Details</h5>'),
    ('<p class="text-secondary small mb-3" id="lightboxDesc">Mô tả chi tiết vi kiến trúc.</p>',
     '<p class="text-secondary small mb-3" id="lightboxDesc">Detailed microarchitectural description and timing analysis.</p>'),
    ("title || 'Chi Tiết Mô Phỏng'", "title || 'Simulation Details'")
]

count = 0
for old, new in replacements:
    if old in code:
        code = code.replace(old, new)
        count += 1
    else:
        print(f"Warning: pattern not matched: {old[:50]}")

print(f"Applied {count}/{len(replacements)} replacements.")

with open('tools/build_metis_unified_platform.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("Successfully updated tools/build_metis_unified_platform.py")
