import os
import sys
import shutil

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

report_path = "BaoCao_TienDo_50_CNN_Systolic_SoC.md"
with open(report_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Section 2.6
target1 = r"- (So với bản Gen-1 mất 93 chu kỳ $\implies$ **tiết kiệm 60.2% thời gian trễ lõi, thông lượng đạt 1.38 GOPS**)."
rep1 = target1 + "\n\n" + """![Hình 2.2: Phân Rã Độ Trễ Hệ Thống Giữa Kiến Trúc Gen-1 và Gen-2](figures/chart2_latency_breakdown.png)
*Hình 2.2: Biểu đồ Donut phân rã thời gian chu kỳ — Pha Readout và thời gian nạp dữ liệu giảm rõ rệt nhờ cơ chế 8 Quantizer song song và Packed 4-INT8.*

![Hình 2.3: Quy Luật Tăng Trưởng Độ Trễ Tính Toán Lõi Theo Chiều Sâu K](figures/chart4_latency_scaling_k.png)
*Hình 2.3: Độ trễ tính toán lõi tuyến tính theo chiều sâu $K \\in [1..16]$, thể hiện khoảng cách vượt trội của kiến trúc Gen-2 (30–45 chu kỳ) so với Gen-1 (86–101 chu kỳ).*"""

# 2. Section 4.4 table
target2 = "| **10**| Suy luận toàn phần nhận dạng chữ số MNIST | SoC Co-sim | `tb_soc_top.sv` (Demo 6) | Dự đoán đúng số 7, độ tin cậy 69%, hiển thị HEX0 | **PASS (Digit 7)** |"
rep2 = target2 + "\n\n" + """![Hình 4.1: Bảng Điều Khiển Tổng Hợp Kết Quả Kiểm Chứng Vi Mạch Đa Tầng](figures/chart5_verification_coverage.png)
*Hình 4.1: Dashboard kiểm chứng 4 góc: 61/61 Unit checks (100%), 88/88 UVM coverage bins (100%), 256/256 điểm kích hoạt Conv1 Bit-True khớp PyTorch, và Logits phân loại chữ số MNIST đạt cực đại tại Class 7 (Logit 104, độ tin cậy 69.4%).*

![Hình 4.2: Biểu Đồ So Sánh Hiệu Năng & Gia Tốc Speedup Thực Nghiệm](figures/chart1_speedup_benchmark.png)
*Hình 4.2: So sánh chu kỳ thực thi toàn hệ thống và tốc độ gia tốc: Gen-2 đạt 173.7x speedup so với phần mềm CPU thuần túy và rút ngắn trễ tính toán lõi từ 93 xuống 37 chu kỳ.*"""

# 3. Section 5 table
target3 = "| **File Bitstream tạo ra** | [`synthesis_soc_de2/soc_top_de2.sof`](file:///e:/DATN/CNN_Systolic_Architecture/synthesis_soc_de2/soc_top_de2.sof) | [`synthesis_soc_de10/soc_top_de10.sof`](file:///e:/DATN/CNN_Systolic_Architecture/synthesis_soc_de10/soc_top_de10.sof) | Sẵn sàng nạp xuống phần cứng |"
rep3 = target3 + "\n\n" + """![Hình 5.1: Báo Cáo Tài Nguyên & Phân Tích Thời Gian Tĩnh STA Trên 2 Dòng Chip FPGA](figures/chart3_fpga_resources.png)
*Hình 5.1: Tỷ lệ sử dụng tài nguyên (Logic LEs/ALMs, DSP, BRAM) và biên độ an toàn thời gian tĩnh (Setup Slack +4.626ns trên DE2, +5.609ns trên DE10) bảo đảm hệ thống đóng timing hoàn hảo ở 50 MHz.*"""

# 4. Slide deck visual tips
target_slide9 = "### SLIDE 9: ĐỘT PHÁ NÂNG CẤP GEN-2: ĐÓNG GÓI 4-BYTE & ĐỌC SONG SONG 8 HÀNG"
rep_slide9 = target_slide9 + "\n* 🖼️ **Hình ảnh minh họa đề xuất**: Chèn file `figures/chart2_latency_breakdown.png` (Biểu đồ phân rã thời gian chu kỳ Gen-1 vs Gen-2)."

target_slide13 = "### SLIDE 13: KẾT QUẢ KIỂM THỬ ĐƠN VỊ & UVM 1.1C COVERAGE"
rep_slide13 = target_slide13 + "\n* 🖼️ **Hình ảnh minh họa đề xuất**: Chèn file `figures/chart5_verification_coverage.png` (Nửa trên: 61 Unit checks & 88 UVM coverage bins)."

target_slide14 = "### SLIDE 14: KẾT QUẢ ĐỒNG MÔ PHỎNG SOC (CO-SIMULATION)"
rep_slide14 = target_slide14 + "\n* 🖼️ **Hình ảnh minh họa đề xuất**: Chèn file `figures/chart5_verification_coverage.png` (Nửa dưới: Conv1 Bit-True & MNIST Class 7 logit)."

target_slide15 = "### SLIDE 15: KẾT QUẢ TỔNG HỢP & ĐÓNG TIMING TRÊN KIT TERASIC DE2"
rep_slide15 = target_slide15 + "\n* 🖼️ **Hình ảnh minh họa đề xuất**: Chèn file `figures/chart3_fpga_resources.png` (Biểu đồ tài nguyên LE/ALM, DSP, Slack DE2 vs DE10)."

target_slide17 = "### SLIDE 17: BẢNG TỔNG HỢP SỐ LIỆU ĐO ĐẠC & BENCHMARK HIỆU NĂNG"
rep_slide17 = target_slide17 + "\n* 🖼️ **Hình ảnh minh họa đề xuất**: Chèn file `figures/chart1_speedup_benchmark.png` (Speedup 173.7x) và `figures/chart4_latency_scaling_k.png` (Scaling theo K)."

replacements = [
    (target1, rep1),
    (target2, rep2),
    (target3, rep3),
    (target_slide9, rep_slide9),
    (target_slide13, rep_slide13),
    (target_slide14, rep_slide14),
    (target_slide15, rep_slide15),
    (target_slide17, rep_slide17),
]

for i, (t, r) in enumerate(replacements):
    if t in content:
        content = content.replace(t, r, 1)
        print(f"[OK] Replaced item {i+1}")
    else:
        print(f"[FAIL] Target not found for item {i+1}")

with open(report_path, "w", encoding="utf-8") as f:
    f.write(content)

# Copy to artifact
artifact_path = r"C:\Users\hoang\.gemini\antigravity\brain\9f77ab99-8f96-4134-8b24-d1c001f13ee8\BaoCao_TienDo_50_CNN_Systolic_SoC.md"
shutil.copy(report_path, artifact_path)
print("[SUCCESS] Updated report and copied to artifact!")
