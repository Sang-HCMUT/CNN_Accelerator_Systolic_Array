import os

report_path = "BaoCao_TienDo_50_CNN_Systolic_SoC.md"
with open(report_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Add Subsection 3 to Section 4.0.2
anchor_402_end = """* **Đồng mô phỏng toàn hệ thống SoC (`tb_soc_top.sv` — 3.87 triệu chu kỳ)**: Nạp trực tiếp firmware C thật (`firmware.hex`) vào BRAM để CPU RISC-V PicoRV32 điều phối mảng tâm thu giải bài toán AI thực tế (nhận dạng chữ số MNIST và tầng Conv1 256 activations)."""

sub_3_content = """

#### 3. Bảng Hướng Dẫn Chi Tiết Lệnh Thực Thi Các Bộ Kiểm Thử (Verification Execution Cheat Sheet):

Để phục vụ công tác tái lập (reproducibility) và hỗ trợ thao tác trực tiếp trước Hội đồng, toàn bộ các câu lệnh thực thi của cả hai hệ thống kiểm chứng được tổng hợp như sau:

| Hệ thống kiểm thử | Bài kiểm thử | Đối tượng xác minh | Lệnh chạy dòng lệnh (Terminal Batch) | Lệnh mở dạng sóng đồ họa (ModelSim GUI) | Tiêu chí nghiệm thu & Kết quả mẫu |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Mô hình Vàng (Python)** | Hạt nhân GEMM | Sinh 4 file vector `.hex` chuẩn 8x8 | `python software_ref/gemm_golden.py` | — | Xuất 4 tệp hex 64 phần tử không lỗi |
| | Suy luận MNIST | Đo độ chính xác ảnh chữ số viết tay | `python software_ref/test_single_image.py 0` | — | Dự đoán đúng số 7, độ chính xác **97.06%** |
| **Kiểm chứng thông thường (Conventional)** | Kiểm thử đơn vị | 8 khối vi mạch con (PE, Skew, Buffers) | `.\run_unit_test.bat`<br>*(hoặc `cd VEFIFY; .\run_unit_sim.bat`)* | `cd VEFIFY; .\open_wave_unit.bat` | **61/61 checks PASSED** (15 giây) |
| | Mảng tâm thu 8x8 | Nhịp sóng $0T..7T$, Scoreboard 64 PE | `cd VEFIFY; vsim -c -do "do run_gemm_sim.do; quit -f"` | `.\open_wave_gemm.bat` | **64/64 elements matched** (100% Bit-True) |
| | Stress & Biên | 8 kịch bản chịu tải, tràn số, bão hòa | `cd VEFIFY; vsim -c -do "do run_stress_sim.do; quit -f"` | `cd VEFIFY; .\open_wave_stress.bat` | **8/8 scenarios PASSED** |
| | Giao thức AXI4-Lite | Backpressure 1..8 chu kỳ, Decoupled AW/W | `.\run_axi_test.bat`<br>*(hoặc `cd VEFIFY; .\run_axi_backpressure_sim.bat`)* | `.\open_wave_axi.bat` | **100% COMPLIANT** (0 error, 44 balance) |
| | Toàn hệ thống SoC | CPU RISC-V PicoRV32 chạy firmware C | `cd VEFIFY; .\run_soc_sim.bat` | `.\open_wave_soc.bat` | **7/7 Demos PASSED** (3.87M chu kỳ) |
| **Kiểm chứng UVM 1.1c** | Single UVM Test | Kiểm thử ngẫu nhiên khối IP lõi | `.\run_uvm_test.bat`<br>*(hoặc `cd uvm_verify; .\run_uvm.bat`)* | — | **71/71 tx PASSED**, 0 errors |
| | Multi-seed Regression | Hồi quy 10 seed ngẫu nhiên liên tiếp | `cd uvm_verify; python run_regression.py --seeds 10` | Báo cáo: `reports/uvm_regression_summary.rpt` | **10/10 seeds PASSED**, 88/88 Bins (100%) |"""

if anchor_402_end in text and "#### 3. Bảng Hướng Dẫn Chi Tiết Lệnh Thực Thi" not in text:
    text = text.replace(anchor_402_end, anchor_402_end + sub_3_content)
    print("Subsection 4.0.3 table added successfully!")

# 2. Add Demo 2b: AXI Waveform to Part II
demo2_anchor = """### Demo 3: Trình Chiếu Kết Quả SoC Co-Simulation 7 Kịch Bản AI"""

demo2b_content = """### Demo 2b: Trình Chiếu Dạng Sóng Bắt Tay Bus AXI4-Lite & Backpressure (ModelSim GUI)
* **Mục đích**: Quan sát trực quan cơ chế bắt tay giao thức AXI4-Lite của khối wrapper, chứng minh khả năng xử lý kênh địa chỉ/dữ liệu đến lệch pha (Decoupled AW/W) và giữ ổn định dữ liệu khi CPU chèn trễ (Master Backpressure).
* **Cách thao tác**:
  1. Chạy trực tiếp từ thư mục gốc dự án:
     ```cmd
     .\open_wave_axi.bat
     # Hoặc: cd VEFIFY; .\open_wave_axi.bat
     ```
  2. Giao diện ModelSim GUI sẽ tự động mở và nạp sẵn 5 nhóm tín hiệu AXI phân màu rõ ràng.
* **Trọng tâm trình bày**:
  - Nhóm 2 (Kênh Ghi): Phân tích trường hợp địa chỉ `AW` đến trước dữ liệu `W` (và ngược lại), FSM wrapper chốt địa chỉ/dữ liệu vào thanh ghi tạm và chỉ thực thi khi cả 2 kênh hoàn tất bắt tay.
  - Nhóm 3 (Kênh Đọc): Quan sát tín hiệu `s_axi_rdata` và `s_axi_rvalid` giữ cố định 100% trong suốt 1 đến 8 chu kỳ khi Master chưa kích hoạt `s_axi_rready`.
  - Nhóm 5 (Packed Transfers): Thấy rõ 1 word 32-bit nạp đồng thời 4 phần tử INT8 vào bộ đệm của mảng tâm thu.

---

"""

if demo2_anchor in text and "### Demo 2b:" not in text:
    text = text.replace(demo2_anchor, demo2b_content + demo2_anchor)
    print("Demo 2b inserted successfully!")

# 3. Update Table of Contents
toc_anchor_part2 = """  - [Demo 2: Trình Chiếu Dạng Sóng Mảng Tâm Thu ModelSim GUI](#demo-2-trình-chiếu-dạng-sóng-mảng-tâm-thu-modelsim-gui)"""
toc_demo2b = """  - [Demo 2: Trình Chiếu Dạng Sóng Mảng Tâm Thu ModelSim GUI](#demo-2-trình-chiếu-dạng-sóng-mảng-tâm-thu-modelsim-gui)
  - [Demo 2b: Trình Chiếu Dạng Sóng Bắt Tay Bus AXI4-Lite & Backpressure](#demo-2b-trình-chiếu-dạng-sóng-bắt-tay-bus-axi4-lite--backpressure-modelsim-gui)"""

if toc_anchor_part2 in text and "Demo 2b:" not in text:
    text = text.replace(toc_anchor_part2, toc_demo2b)
    print("TOC updated with Demo 2b!")

with open(report_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Report enriched with full execution instructions!")
