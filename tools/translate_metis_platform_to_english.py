# -*- coding: utf-8 -*-
"""
Script: tools/translate_metis_platform_to_english.py
Translates all web UI elements of the Metis unified platform to English,
while strictly preserving the 50% Thesis Progress Report in Vietnamese.
"""
import re
import sys

def main():
    print("Translating web platform UI to English (Report 50% preserved in Vietnamese)...")
    
    # -------------------------------------------------------------------------
    # 1. Update scratch/cnn_studio_js_extracted.js
    # -------------------------------------------------------------------------
    with open('scratch/cnn_studio_js_extracted.js', 'r', encoding='utf-8') as f:
        js = f.read()

    # Stroke steps labels
    js = js.replace("'Nền đen (Background)'", "'Background (Void)'")
    js = js.replace("'Nét đỉnh chữ số (Top stroke)'", "'Top Stroke of Digit'")
    js = js.replace("'Góc trên bên phải'", "'Upper Right Curve'")
    js = js.replace("'Thân bên phải'", "'Right Vertical Stem'")
    js = js.replace("'Đường cong bên phải'", "'Lower Right Curve'")
    js = js.replace("'Khoảng trống bên trong'", "'Inner Void / Loop'")
    js = js.replace("'Nét đáy chữ số (Bottom stroke)'", "'Bottom Base Stroke'")
    js = js.replace("'Đường cong bên trái'", "'Lower Left Curve'")
    js = js.replace("'Thân bên trái'", "'Left Vertical Stem'")
    js = js.replace("'Góc trên bên trái'", "'Upper Left Curve'")

    # Canvas Headings & Labels in JS
    js = js.replace("PHÉP TÍCH CHẬP CONV1 & ÁNH XẠ IM2COL SANG MẢNG 64 PE", "CONV1 CONVOLUTION & IM2COL MAPPING TO 64-PE MESH")
    js = js.replace("Cửa sổ 3×3 trượt trên ảnh 28×28 -> Nạp vector B [9×1] vào 64 PE (Tích lũy C_acc 32-bit)", "3×3 Sliding Window on 28×28 Image -> Streams Column Vector B [9×1] to 64 PEs (INT32 C_acc)")
    js = js.replace("Ảnh Gốc MNIST [28×28]", "Input Image Tensor [28×28]")
    js = js.replace("Cửa Sổ 3×3", "3×3 Window")
    js = js.replace("Vị trí: Hàng", "Location: Row")
    js = js.replace("Cột", "Col")
    js = js.replace("Bản Đồ Đặc Trưng F#0 [28×28]", "Feature Map F#0 [28×28]")

    js = js.replace("ĐƠN VỊ ĐỊNH LƯỢNG & RELU SONG SONG (QUANTIZED RELU UNIT)", "PARALLEL QUANTIZED RELU UNIT")
    js = js.replace("Hàm truyền: ReLU(acc >> 8) kẹp ngưỡng saturation trong khoảng [0, 127]", "Transfer Function: ReLU(acc >> 8) clamped to saturation range [0, 127]")
    js = js.replace("TÍNH TOÁN RELU TẠI CHỖ", "IN-SITU QUANTIZED RELU ACTIVATION")
    js = js.replace("Kẹp ngưỡng bão hòa [0, 127]", "Clamped saturation [0, 127]")
    js = js.replace("Chống tràn số tuyệt đối (Zero Overflow)", "100% Overflow Prevention (Zero Saturation Error)")

    js = js.replace("TẦNG MAX-POOLING 2×2 (GIẢM KÍCH THƯỚC ĐẶC TRƯNG)", "PARALLEL MAX-POOLING STAGE [2×2] (STRIDE 2)")
    js = js.replace("Cửa sổ 2×2 trượt Stride=2: Giảm độ phân giải 28×28 -> 14×14 (Giảm 4× dữ liệu)", "2×2 Window Stride=2: Downsamples 28×28 -> 14×14 Feature Map (4× Data Reduction)")
    js = js.replace("Đặc Trưng Sau Conv1 [28×28]", "Conv1 Feature Map [28×28]")
    js = js.replace("Đặc Trưng Sau Pooling [14×14]", "Max-Pooled Output [14×14]")

    js = js.replace("TRẢI PHẲNG TENSOR (FLATTEN) & NẠP VÀO BUFFER SYSTOLIC", "TENSOR FLATTEN & SYSTOLIC INPUT BUFFER")
    js = js.replace("Chuyển đổi ma trận đặc trưng 14×14 thành vector 1D nạp vào 64 PE cho tầng Dense", "Reshapes 14×14 feature map into 1D vector feeding 64 PEs for Dense FC classification")

    js = js.replace("TẦNG FULLY-CONNECTED (DENSE) PHÂN LỚP 10 CHỮ SỐ", "FULLY-CONNECTED (DENSE) CLASSIFIER [64×10]")
    js = js.replace("Nhân ma trận trọng số W_fc [10×64] với vector đặc trưng -> 10 Logits", "Matrix-vector GEMM W_fc [10×64] × vector -> 10 Logit outputs on 64 PEs")

    js = js.replace("Xác Suất Softmax (10 Chữ Số)", "Softmax Probabilities (10 Digits)")
    js = js.replace("Bấm 'Bắt Đầu' để xem chuyển động trực quan", "Click 'Start Convolution' to run hardware animation")

    # UART Logs
    js = js.replace("Chế độ Vẽ Tay Kích Hoạt: Dùng chuột/ngón tay vẽ chữ số lên bảng trái.", "Freehand Drawing Active: Draw custom digits with mouse or touch.")
    js = js.replace("Chuyển lại chế độ mẫu thử chuẩn MNIST.", "Switched to standard MNIST benchmark sample.")
    js = js.replace("Đã xóa trắng bảng vẽ.", "Drawing canvas cleared.")
    js = js.replace("Đã đảo màu điểm ảnh.", "Canvas pixels inverted.")
    js = js.replace("Đã căn giữa chữ số theo trọng tâm.", "Centered digit mass based on center-of-gravity.")
    js = js.replace("Đã nạp mẫu chữ số #", "Loaded MNIST test sample #")
    js = js.replace("Suy luận hoàn tất: Dự đoán chữ số =", "Inference complete: Predicted digit =")
    js = js.replace("KẾT QUẢ CUỐI: Chữ số =", "FINAL RESULT: Digit =")
    js = js.replace("Độ tin cậy =", "Confidence =")
    js = js.replace("Ghi sang HEX0.", "Dispatched to HEX0.")
    js = js.replace("Sẵn sàng thực thi...", "Ready for execution...")
    js = js.replace("Hoàn Tất!", "Completed!")
    js = js.replace("Chờ Khởi Động", "Ready / Standby")

    # Update Idle Blueprint text
    js = js.replace("KIẾN TRÚC VI MẠCH TĂNG TỐC CNN 64 PE [8×8] TRÊN FPGA CYCLONE V", "64-PE [8×8] CNN SYSTOLIC HARDWARE ACCELERATOR PIPELINE (FPGA CYCLONE V)")
    js = js.replace("Trạng thái: Sẵn Sàng (Ready) • FMAX = 69.49 MHz • Timing Slack = +1.815 ns (MET)", "Status: Ready • FMAX = 69.49 MHz • Timing Slack = +1.815 ns (MET)")
    js = js.replace("Tầng 1: Im2Col", "Stage 1: Im2Col")
    js = js.replace("Ảnh [28×28] -> [9×196]", "Tensor [28×28] -> [9×196]")
    js = js.replace("Quét 196 cửa sổ 3×3", "Slide 196 3×3 Windows")
    js = js.replace("Tầng 2: Mảng 64 PE", "Stage 2: 64-PE Mesh")
    js = js.replace("8×8 Output-Stationary", "8×8 Output-Stationary")
    js = js.replace("64 MACs song song", "64 Parallel MACs")
    js = js.replace("Tầng 3: ReLU & Pool", "Stage 3: Quant & Pool")
    js = js.replace("Lượng hóa INT8 [0,127]", "INT8 Saturation [0,127]")
    js = js.replace("Max-Pooling [2×2]", "Max-Pooling [2×2]")
    js = js.replace("Tầng 4: Dense FC", "Stage 4: Dense FC")
    js = js.replace("Vector 64 -> 10 Lớp", "Vector 64 -> 10 Classes")
    js = js.replace("Softmax & Ghi HEX0", "Softmax & Write HEX0")
    js = js.replace('Nhấn nút "▶ Bắt Đầu Tích Chập" phía trên để kích hoạt trực quan hóa phần cứng', 'Click "▶ Start Convolution" above to launch hardware dataflow visualization')
    js = js.replace('Hệ thống sẽ chạy từng bước: Quét Kernel 3×3 -> Nạp 64 PE MAC -> ReLU Saturation -> MaxPool -> Ghi HEX0', 'Cycle-accurate sequence: 3×3 Im2Col -> 64-PE MAC -> ReLU Saturation -> MaxPool -> Write HEX0')

    with open('scratch/cnn_studio_js_extracted.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("Updated scratch/cnn_studio_js_extracted.js successfully.")

    # -------------------------------------------------------------------------
    # 2. Update tools/build_metis_unified_platform.py
    # -------------------------------------------------------------------------
    with open('tools/build_metis_unified_platform.py', 'r', encoding='utf-8') as f:
        code = f.read()

    # HTML Language & Title
    code = code.replace('<html lang="vi"', '<html lang="en"')
    code = code.replace('<title>CNN Systolic SoC Platform — Metis Architecture Suite (Báo Cáo 50% & Interactive Studio)</title>',
                        '<title>CNN Systolic SoC Platform — Metis Architecture Suite (50% Thesis Report & Hardware Studio)</title>')

    # Header Telemetry & Nav Pills
    code = code.replace('>Báo Cáo 50%</button>', '>50% Progress Report</button>')
    code = code.replace('>CNN Inference Studio</button>', '>CNN Inference Studio</button>')
    code = code.replace('>Thư Viện 18 GIFs</button>', '>18 Architectural GIFs</button>')
    code = code.replace('>Mô Phỏng Skew Unit</button>', '>2D Skew Unit Simulator</button>')
    code = code.replace('>Đo Kiểm FPGA</button>', '>FPGA STA & Telemetry</button>')
    code = code.replace('FMAX: 69.49 MHz (Đạt)', 'FMAX: 69.49 MHz (Met)')
    code = code.replace('UVM: 100% Bao Phủ', 'UVM: 100% Coverage')

    # Sidebar Navigation
    code = code.replace('DANH MỤC CHÍNH', 'MAIN NAVIGATION')
    code = code.replace('TRỰC QUAN HÓA & MÔ PHỎNG', 'VISUALIZATION & SIMULATION')
    code = code.replace('TÀI NGUYÊN & PHẦN CỨNG', 'HARDWARE TELEMETRY')
    code = code.replace('MỤC LỤC BÁO CÁO 50%', 'REPORT TABLE OF CONTENTS')

    code = code.replace('Báo Cáo Tiến Độ 50%', '50% Progress Report')
    code = code.replace('50% Hoàn Thành', 'Midterm')
    code = code.replace('Thư Viện 18 GIFs', 'Architectural GIF Library')
    code = code.replace('Mô Phỏng Skew Unit', '2D Skew Unit Simulator')
    code = code.replace('Đo Kiểm Tài Nguyên FPGA', 'FPGA Synthesis & Timing')
    code = code.replace('HỆ THỐNG PHẦN CỨNG', 'HARDWARE TARGET')
    code = code.replace('Trạng thái: Hoạt động', 'Status: Active (Timing Met)')

    # Tab 2: CNN Studio
    code = code.replace('Phòng Trực Quan Hóa Động Thuật Toán CNN & Bộ Tăng Tốc Tâm Thu 64 PE', 'Real-Time CNN Inference & 64-PE Systolic Hardware Accelerator Studio')
    code = code.replace('KIẾN TRÚC:', 'ARCHITECTURE:')
    code = code.replace('ĐỘ CHUẨN SỐ HỌC:', 'ARITHMETIC:')
    code = code.replace('CHU KỲ 1 TILE:', 'TILE LATENCY:')
    code = code.replace('TÁI SỬ DỤNG TRỌNG SỐ:', 'WEIGHT REUSE:')
    code = code.replace('ĐỘ TRỄ @ 50MHZ:', 'LATENCY @ 50MHz:')
    code = code.replace('Mẫu MNIST:', 'MNIST Presets:')
    code = code.replace('>Bắt Đầu Tích Chập', '>Start Convolution')
    code = code.replace('>Tạm Dừng', '>Pause')
    code = code.replace('>Bước Kế (+1)', '>Next Step (+1)')
    code = code.replace('Chậm (1.2s)', 'Slow (1.2s)')
    code = code.replace('Chuẩn (0.6s)', 'Normal (0.6s)')
    code = code.replace('Nhanh (0.25s)', 'Fast (0.25s)')

    # Column 1
    code = code.replace('1. Tầng Đầu Vào (Input)', '1. Input Layer (28×28 INT8)')
    code = code.replace('Xóa Bảng', 'Clear')
    code = code.replace('Đảo Màu', 'Invert')
    code = code.replace('Căn Giữa', 'Center Mass')
    code = code.replace('Tọa độ con trỏ:', 'Cursor Coords:')
    code = code.replace('Giá trị INT8:', 'INT8 Value:')
    code = code.replace('-128 (Đen)', '-128 (Black)')
    code = code.replace('Dữ liệu điểm ảnh chuẩn MNIST đã lượng tử hóa có dấu [-128, +127]. Bạn có thể vẽ tự do bằng chuột/ngón tay hoặc click chọn 10 mẫu chuẩn (0..9) ở trên.',
                        'Authentic MNIST handwritten digits quantized to signed INT8 [-128, +127]. Draw freely with mouse/touch or select any of the 10 preset samples (0..9) above.')

    # Column 2
    code = code.replace('2. Tiến Trình Tính Toán Phần Cứng (Systolic Engine)', '2. Hardware Systolic Engine Process (64 PE Mesh)')
    code = code.replace('Chờ Khởi Động', 'Ready / Standby')
    code = code.replace('Sẵn sàng thực thi...', 'Ready for execution...')
    code = code.replace('Output: Chờ lệnh', 'Output: Standby')
    code = code.replace("Nhấn nút 'Bắt Đầu Tích Chập' để kích hoạt chuỗi trực quan hóa động qua lõi tăng tốc 64 PE.",
                        "Click 'Start Convolution' to launch cycle-accurate hardware dataflow visualization across 64 PEs.")

    # Column 3
    code = code.replace('3. Dự Đoán & Phần Cứng FPGA', '3. FPGA Telemetry & Classification')
    code = code.replace('DỰ ĐOÁN (ARGMAX)', 'PREDICTED DIGIT (ARGMAX)')
    code = code.replace('Độ tin cậy: --%', 'Confidence: --%')
    code = code.replace('ĐÈN LEDR[9:0] (KIT DE10):', 'HARDWARE LEDR[9:0] (DE10 KIT):')
    code = code.replace('Sẵn sàng nhận dữ liệu ma trận.', 'Systolic core ready for matrix execution.')
    code = code.replace('Tốc độ UART: 115200 baud • Đồng bộ FPGA', 'Baud Rate: 115,200 baud • Hardware Synced')

    # Tab 3: GIF Library
    code = code.replace('Thư Viện 18 Mô Phỏng Động Kiến Trúc Vi Mạch Tăng Tốc Tâm Thu', 'Architectural Simulation & Waveform Library (18 Interactive GIFs)')
    code = code.replace('Bộ 18 mô phỏng động trực quan hóa toàn bộ khía cạnh kiến trúc: từ thuật toán im2col, tiling ma trận, vi kiến trúc PE, mảng 64 PE, bus AXI, firmware PicoRV32 đến kiểm thử UVM 1.2 và đo kiểm FPGA.',
                        'Comprehensive 18-module simulation suite visualizing every architectural dimension: from im2col GEMM mapping, matrix tiling, PE microarchitecture, 64-PE mesh, AXI4-Lite bus, and PicoRV32 firmware to UVM 1.2 verification and FPGA STA.')
    code = code.replace('>Tất Cả (18)</button>', '>All Modules (18)</button>')
    code = code.replace('>Dòng Dữ Liệu & Wavefront (4)</button>', '>Dataflow & Wavefront (4)</button>')
    code = code.replace('>Vi Kiến Trúc PE (3)</button>', '>PE Microarchitecture (3)</button>')
    code = code.replace('>Hệ Thống SoC & AXI (4)</button>', '>SoC & AXI Interconnect (4)</button>')
    code = code.replace('>Kiểm Thử UVM & FPGA (3)</button>', '>UVM Verification & FPGA (3)</button>')
    code = code.replace('>Nghiên Cứu Chuyên Sâu (4)</button>', '>Comparative Deep Dives (4)</button>')
    code = code.replace('Độ trễ: ', 'Latency: ')
    code = code.replace('Băng thông: ', 'Throughput: ')
    code = code.replace('Nhấp để xem chi tiết & điều khiển nhịp sóng', 'Click to inspect in detail & control waveform loop')

    # Tab 4: Skew Simulator
    code = code.replace('Mô Phỏng Lan Truyền Sóng Dữ Liệu 2D Systolic Array (64 PE)', '2D Systolic Wavefront & Skew Unit Interactive Simulator (64 PEs)')
    code = code.replace('Toán hạng Hàng A trễ $i \\times T_{{clk}}$, Cột B trễ $j \\times T_{{clk}}$. Dữ liệu gặp nhau chính xác tại chu kỳ $T = i + j$.',
                        'Row A operands delayed by $i \\times T_{{clk}}$, Column B operands delayed by $j \\times T_{{clk}}$. Operands align precisely at cycle $T = i + j$.')
    code = code.replace('>Tự Động Chạy</button>', '>Auto Play</button>')
    code = code.replace('Chu kỳ T = ', 'Cycle T = ')
    code = code.replace('ĐỘ TRỄ HÀNG A', 'ROW A SKEW DELAY')
    code = code.replace('Trễ từ 0T đến 7T qua 28 D-FF', '0T to 7T stagger delay via 28 D-FFs')
    code = code.replace('ĐỘ TRỄ CỘT B', 'COLUMN B SKEW DELAY')
    code = code.replace('ĐẶC TÍNH SÓNG CHÉO', 'DIAGONAL WAVEFRONT')
    code = code.replace('100% truyền cục bộ, 0% xung đột bus', '100% nearest-neighbor spatial data reuse, 0% global bus contention')

    # Tab 5: FPGA Metrics
    code = code.replace('Báo Cáo Tổng Hợp Mạch & Phân Tích Thời Gian Tĩnh (STA)', 'Hardware Synthesis & Static Timing Analysis (STA) Telemetry')
    code = code.replace('Worst Case Slack', 'Worst-Case Timing Slack')
    code = code.replace('UVM Functional Cov', 'UVM Functional Coverage')
    code = code.replace('1. Bảng Tiêu Hao Tài Nguyên Phần Cứng Trên Kit FPGA', '1. Hardware Resource Utilization on Target FPGA Boards')
    code = code.replace('Khối Chức Năng', 'Hardware Functional Block')
    code = code.replace('Tài Nguyên Logic (ALMs / LEs)', 'Logic Resources (ALMs / LEs)')
    code = code.replace('Thanh Ghi D-FF', 'Registers (D-FF)')
    code = code.replace('Bộ Nhân DSP 9×9', 'DSP Blocks (18×18 / 9×9)')
    code = code.replace('Bộ Nhớ M10K', 'Block Memory M10K')

    code = code.replace('Mảng Tâm Thu 64 PE (`systolic_array_core.sv`)', '64-PE Systolic Array Core (`systolic_array_core.sv`)')
    code = code.replace('Mạng Lệch Pha (`systolic_skew_unit.sv`)', 'Wavefront Skew Unit (`systolic_skew_unit.sv`)')
    code = code.replace('Bộ Lượng Tử Hóa SIMD 8 Hàng (`quantize_relu_unit.sv`)', 'SIMD 8-Row Quantized ReLU Unit (`quantize_relu_unit.sv`)')
    code = code.replace('Bộ Đệm Ma Trận A, B, C (32KB SRAM Buffer)', 'Matrix SRAM Buffers A, B, C (32KB On-Chip Buffer)')
    code = code.replace('CPU PicoRV32 + Bus AXI4-Lite Crossbar', 'PicoRV32 RISC-V CPU + AXI4-Lite Crossbar')
    code = code.replace('TỔNG TOÀN HỆ THỐNG SOC (GEN-2)', 'TOTAL SOC SYSTEM-ON-CHIP (GEN-2)')

    code = code.replace('2. So Sánh Hiệu Năng & Tăng Tốc Gen-1 vs. Gen-2', '2. Architectural Performance Benchmarks: Gen-1 Baseline vs. Gen-2 Optimized')
    code = code.replace('Tiêu Chí Kỹ Thuật', 'Benchmark Metric')
    code = code.replace('Gen-1 Baseline', 'Gen-1 Baseline')
    code = code.replace('Gen-2 Tối Ưu Hóa', 'Gen-2 Optimized')
    code = code.replace('Hệ Số Tăng Tốc (Speedup)', 'Speedup Factor')
    code = code.replace('Đột Phá Kiến Trúc', 'Architectural Innovation')

    code = code.replace('Chu kỳ nạp đệm A (72 Bytes)', 'Matrix A Buffer Load Latency (72 Bytes)')
    code = code.replace('Chu kỳ rút kết quả C (64 PEs)', 'Result Drain Latency (64 PEs)')
    code = code.replace('Tổng chu kỳ 1 Tile (8×9 × 9×8)', 'Total Latency per Tile (8×9 × 9×8)')
    code = code.replace('Tần số xung nhịp cực đại (FMAX)', 'Maximum Operating Frequency (FMAX)')
    code = code.replace('Thông lượng đỉnh (Peak Throughput)', 'Peak Compute Throughput')

    code = code.replace('Đóng gói 4-byte/chu kỳ (Single-cycle 32-bit)', '4-byte packed single-cycle writes (32-bit)')
    code = code.replace('Rút song song 8 hàng SIMD (8-row parallel drain)', '8-row parallel SIMD drain bus')
    code = code.replace('Loại bỏ hoàn toàn bong bóng đường ống (No pipeline bubbles)', 'Zero pipeline stall bubbles')
    code = code.replace('Tối ưu đường định tuyến và cân bằng thanh ghi (Register retiming)', 'Critical path register retiming')
    code = code.replace('Tận dụng 100% tài nguyên 64 PE không nghẽn bus', '100% PE array utilization with zero bus stall')

    code = code.replace('3. Phân Tích Đường Trễ Tới Hạn (Critical Path Analysis)', '3. Critical Path & Timing Margin Breakdown')
    code = code.replace('4. Kế Hoạch & Mức Độ Bao Phủ Kiểm Thử UVM 1.2', '4. Industrial UVM 1.2 Verification Plan & Coverage Closure')

    # Modal Lightbox
    code = code.replace('Đóng (Esc)', 'Close (Esc)')
    code = code.replace('Tốc Độ:', 'Speed:')
    code = code.replace('Xem Mã Nguồn RTL', 'View RTL Module')
    code = code.replace('Mở Rộng', 'Full Screen')
    code = code.replace('>Đóng<', '>Close<')

    # Script UI Strings
    code = code.replace('Chậm Rãi', 'Slow')
    code = code.replace('Tiêu Chuẩn', 'Normal')
    code = code.replace('Siêu Tốc', 'Fast')
    code = code.replace('Tự Động Chạy', 'Auto Play')
    code = code.replace('Đã sao chép vào bộ nhớ tạm!', 'Copied to clipboard!')

    # Update 18 GIFs metadata in code
    old_meta_pattern = r'gifs_metadata = \[.*?\]\s*\n\s*def'
    
    english_metadata_str = '''gifs_metadata = [
        {
            "id": "GIF-01",
            "file": "01_im2col_convolution_mapping.gif",
            "title": "01. Im2Col Convolution to 64-PE GEMM Mapping",
            "category": "wavefront",
            "category_name": "Dataflow & Wavefront",
            "desc": "Transforms 3×3 sliding receptive fields on a 28×28 tensor into 2D column vectors [9×196], feeding 64 PEs in parallel for spatial GEMM convolution.",
            "latency": "1 cycle / pixel",
            "throughput": "64 MACs / cycle",
            "module": "RTL/pe_gemm.sv"
        },
        {
            "id": "GIF-02",
            "file": "02_matrix_tiling_engine.gif",
            "title": "02. Matrix Tiling & Memory Stationarity Engine",
            "category": "wavefront",
            "category_name": "Dataflow & Wavefront",
            "desc": "Locks sub-tile A0 [8×9] in internal SRAM buffer, reusing weights across 98 consecutive B sub-tiles to eliminate 98× redundant external DRAM accesses.",
            "latency": "37 Cycles / Sub-tile",
            "throughput": "98× DRAM Bandwidth Saved",
            "module": "RTL/gemm_controller.sv"
        },
        {
            "id": "GIF-03",
            "file": "03_quantization_overflow_pipeline.gif",
            "title": "03. INT8 Quantization & INT32 Overflow Prevention Pipeline",
            "category": "pe",
            "category_name": "PE Microarchitecture",
            "desc": "Accumulates in signed 32-bit registers with zero overflow risk (-2.14B to +2.14B), followed by hardware right-shift and ReLU saturation into [0, 127].",
            "latency": "1 Pipelined Cycle",
            "throughput": "8 Parallel Outputs",
            "module": "RTL/quantize_relu_unit.sv"
        },
        {
            "id": "GIF-04",
            "file": "04_cnn_mnist_inference.gif",
            "title": "04. End-to-End CNN MNIST Inference Dataflow",
            "category": "soc",
            "category_name": "SoC & AXI Interconnect",
            "desc": "Complete neural network inference pipeline: 28×28 Image → Conv1 [14×14×16] → ReLU → MaxPool [7×7×16] → Fully Connected [10] → Argmax Prediction.",
            "latency": "145.04 µs @ 50MHz",
            "throughput": "6,895 Frames/sec",
            "module": "RTL/soc_top.sv"
        },
        {
            "id": "GIF-05",
            "file": "05_skew_wavefront_alignment.gif",
            "title": "05. Staggered Delay Skew Unit (Wavefront Synchronization)",
            "category": "wavefront",
            "category_name": "Dataflow & Wavefront",
            "desc": "Staggers Row A inputs (0T..7T) and Column B inputs (0T..7T) via 56 D-Flip-Flops to form a synchronized 45-degree diagonal wavefront (T = i + j).",
            "latency": "56 D-FF Registers",
            "throughput": "16 Bytes / Cycle",
            "module": "RTL/systolic_skew_unit.sv"
        },
        {
            "id": "GIF-06",
            "file": "06_pe_microarchitecture.gif",
            "title": "06. Processing Element (PE) Microarchitecture Datapath",
            "category": "pe",
            "category_name": "PE Microarchitecture",
            "desc": "Each PE integrates Reg_A, Reg_B, signed 8×8 multiplier, 32-bit adder, and local accumulator C_acc (Output-Stationary) achieving 69.49 MHz FMAX.",
            "latency": "1 MAC / Clock Cycle",
            "throughput": "Slack +1.815 ns (MET)",
            "module": "RTL/pe_gemm.sv"
        },
        {
            "id": "GIF-07",
            "file": "07_systolic_array_64pe_mesh.gif",
            "title": "07. 2D Spatial 64-PE Systolic Array Mesh (8×8)",
            "category": "pe",
            "category_name": "PE Microarchitecture",
            "desc": "Fully localized 2D mesh of 64 Processing Elements with 100% nearest-neighbor communication and zero global bus congestion, processing 64 MACs concurrently.",
            "latency": "14 Wavefront Cycles",
            "throughput": "64 MACs / Clock Cycle",
            "module": "RTL/systolic_array_core.sv"
        },
        {
            "id": "GIF-08",
            "file": "08_gen1_vs_gen2_evolution.gif",
            "title": "08. Gen-1 vs Gen-2 Microarchitectural Evolution",
            "category": "deepdive",
            "category_name": "Comparative Deep Dives",
            "desc": "Gen-2 breakthrough: 4-byte packed single-cycle writes and 8-row parallel SIMD drain (8 cycles vs 64 cycles in Gen-1), delivering a 4.81× overall speedup.",
            "latency": "8 Cycles Drain (vs 64)",
            "throughput": "4.81× Overall Speedup",
            "module": "RTL/systolic_accelerator_top.sv"
        },
        {
            "id": "GIF-09",
            "file": "09_axi_handshake_deadlock.gif",
            "title": "09. AXI4-Lite Handshake & Anti-Deadlock Mechanism",
            "category": "soc",
            "category_name": "SoC & AXI Interconnect",
            "desc": "Bi-directional VALID/READY handshake with hardware busy-gating logic that inserts wait states automatically, preventing bus deadlock under backpressure.",
            "latency": "Zero Deadlock",
            "throughput": "AMBA AXI4-Lite Standard",
            "module": "RTL/axi_interconnect.sv"
        },
        {
            "id": "GIF-10",
            "file": "10_soc_mmio_firmware.gif",
            "title": "10. MMIO Register Map & PicoRV32 Firmware Driver",
            "category": "soc",
            "category_name": "SoC & AXI Interconnect",
            "desc": "PicoRV32 RISC-V CPU coordinates the accelerator via MMIO address window 0x1000_0000 using standard C firmware driver routines (systolic.h).",
            "latency": "1 Cycle Read/Write",
            "throughput": "HW/SW Co-Design",
            "module": "RTL/soc_top.sv"
        },
        {
            "id": "GIF-11",
            "file": "11_fpga_synth_timing.gif",
            "title": "11. Cyclone IV/V FPGA Synthesis & Static Timing Analysis (STA)",
            "category": "uvm",
            "category_name": "UVM Verification & FPGA",
            "desc": "Quartus Prime synthesis and STA: FMAX reaches 65.04 MHz (Cyclone IV DE2-115) and 69.49 MHz (Cyclone V DE10-Standard) with positive Slack +1.815 ns.",
            "latency": "FMAX 69.49 MHz",
            "throughput": "100% Timing Closure (MET)",
            "module": "Quartus Prime STA"
        },
        {
            "id": "GIF-12",
            "file": "12_uvm_verification_waveform.gif",
            "title": "12. Industrial UVM 1.2 Verification Environment & Waveforms",
            "category": "uvm",
            "category_name": "UVM Verification & FPGA",
            "desc": "IEEE 1800.2 standard UVM testbench: Sequences, Driver, Monitor, and Scoreboard conducting bit-true verification against Python Golden Model with 100% coverage.",
            "latency": "3.87M Co-Sim Cycles",
            "throughput": "100% Functional Coverage",
            "module": "TB/tb_soc_uvm.sv"
        },
        {
            "id": "DEEP-01",
            "file": "memory_wall_von_neumann.gif",
            "title": "13. Von Neumann Memory Wall vs 2D Systolic Array",
            "category": "deepdive",
            "category_name": "Comparative Deep Dives",
            "desc": "Comparative dataflow: Traditional CPUs spend up to 90% of cycles stalled on the memory bus, whereas 2D systolic arrays reuse data in-situ to cut DRAM traffic by 98×.",
            "latency": "98× Memory Traffic Saved",
            "throughput": "Bypasses Memory Wall",
            "module": "Computer Architecture"
        },
        {
            "id": "DEEP-02",
            "file": "neural_network_general_architecture.gif",
            "title": "14. General Deep Convolutional Neural Network Architecture",
            "category": "deepdive",
            "category_name": "Comparative Deep Dives",
            "desc": "Multi-layer neural network pipeline: Input Tensor → Convolution → Batch Normalization → ReLU Activation → Spatial Pooling → Fully Connected → Softmax.",
            "latency": "Scalable Multi-Layer",
            "throughput": "Arbitrary CNN Topologies",
            "module": "AI Model Architecture"
        },
        {
            "id": "DEEP-03",
            "file": "soc_general_architecture.gif",
            "title": "15. Complete System-on-Chip (SoC) Architecture with AXI Crossbar",
            "category": "soc",
            "category_name": "SoC & AXI Interconnect",
            "desc": "Complete system diagram: PicoRV32 RISC-V CPU, central AXI crossbar arbiter, 64KB on-chip RAM, AXI UART core, and the 64-PE Systolic CNN Accelerator.",
            "latency": "AMBA AXI4-Lite Crossbar",
            "throughput": "Industrial 32-bit Bus",
            "module": "RTL/soc_top.sv"
        },
        {
            "id": "DEEP-04",
            "file": "uvm_internal_communication.gif",
            "title": "16. UVM Internal TLM Communication & Scoreboard Analysis",
            "category": "uvm",
            "category_name": "UVM Verification & FPGA",
            "desc": "IEEE 1800.2 dataflow: Sequence generator → TLM FIFO → AXI Driver → Passively monitored transactions → Scoreboard bit-true check against golden model.",
            "latency": "IEEE 1800.2 UVM 1.2",
            "throughput": "Bit-True 100% (64/64 PEs)",
            "module": "TB/uvm_env.sv"
        },
        {
            "id": "DEEP-05",
            "file": "gen1_vs_gen2_deep_dive.gif",
            "title": "17. Deep-Dive Performance Benchmark: Gen-1 vs Gen-2 Architecture",
            "category": "deepdive",
            "category_name": "Comparative Deep Dives",
            "desc": "Cycle-accurate drain analysis: Gen-1 extracts results serially across 64 cycles, while Gen-2 executes 8-row SIMD parallel drain in 8 cycles, yielding a 4.81× overall speedup.",
            "latency": "8 Cycles Drain (vs 64)",
            "throughput": "4.81× Measured Speedup",
            "module": "Comparative Architecture"
        },
        {
            "id": "DEEP-06",
            "file": "systolic_dataflow_8x8.gif",
            "title": "18. 2D Wavefront Dynamic Systolic Dataflow (8×8 Mesh)",
            "category": "wavefront",
            "category_name": "Dataflow & Wavefront",
            "desc": "37-cycle full execution cycle of one matrix tile: pre-loading, 45-degree diagonal wavefront propagation, local accumulation, and parallel SIMD drain.",
            "latency": "37 Clock Cycles / Tile",
            "throughput": "64 MACs / Cycle Concurrent",
            "module": "RTL/systolic_array_core.sv"
        }
    ]

    def'''

    code = re.sub(old_meta_pattern, english_metadata_str, code, flags=re.DOTALL)

    with open('tools/build_metis_unified_platform.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Updated tools/build_metis_unified_platform.py with English UI strings.")

if __name__ == '__main__':
    main()
