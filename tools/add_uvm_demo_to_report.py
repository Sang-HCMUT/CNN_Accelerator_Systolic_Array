import os

report_path = "BaoCao_TienDo_50_CNN_Systolic_SoC.md"
with open(report_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Clean up residual actor speech in Demo 2
old_demo2_bullets = """   3. **Nhóm 2 - Internal 2D Accumulators (`c_matrix_core[0..7][0..7]` — Đầy Đủ 64 PEs)**:
     * *"Nhấp vào dấu `+` để mở rộng `c_matrix_core`: Thầy Cô sẽ thấy đầy đủ 8 hàng `[0]..[7]`, mỗi hàng gồm 8 cột `[0]..[7]`. Đây là 64 thanh ghi tích lũy 32-bit bên trong 64 PEs đang tăng dồn liên tục theo cơ chế Output-Stationary, khẳng định quy mô mảng tăng tốc chuẩn công nghiệp 64 PEs hoàn chỉnh."*
   4. **Nhóm 3 - Gen-2 Parallel Row Readout (`wr_row_en`, `wr_row_idx`, `wr_row_data_int8`)**:
     * *"Và đây là minh chứng đắt giá cho cải tiến Gen-2: sau khi tính xong, xung `wr_row_en` tích cực đúng 8 chu kỳ (tương ứng `wr_row_idx` từ 0 đến 7). Mỗi chu kỳ, 8 bộ lượng tử hóa song song đẩy đồng thời 8 byte INT8 của một hàng vào Buffer C, rút ngắn thời gian xả ma trận từ 64 chu kỳ tuần tự xuống đúng 8 chu kỳ song song."*
   5. **Nhóm 4 - Host Output Buffer C Readout & Log Scoreboard 64/64**:
     * *"Tại ngõ ra của Buffer C, các tín hiệu `rd_c_addr` và `rd_c_data` sẵn sàng để CPU đọc dữ liệu. Bảng log ModelSim bên dưới xác nhận: `[TB] Test PASSED: 64/64 elements matched` (100% Bit-True với Python Golden Model)."*"""

clean_demo2_bullets = """   3. **Nhóm 2 - Internal 2D Accumulators (`c_matrix_core[0..7][0..7]` — 64 PEs)**:
     * *Phân tích tín hiệu*: Mở rộng tín hiệu `c_matrix_core` để thấy đầy đủ 8 hàng `[0]..[7]`, mỗi hàng 8 cột `[0]..[7]` (64 thanh ghi tích lũy 32-bit). Dữ liệu tích lũy tăng dồn liên tục theo cơ chế Output-Stationary.
   4. **Nhóm 3 - Gen-2 Parallel Row Readout (`wr_row_en`, `wr_row_idx`, `wr_row_data_int8`)**:
     * *Phân tích tín hiệu*: Tín hiệu `wr_row_en` tích cực trong đúng 8 chu kỳ (chỉ số `wr_row_idx` chạy từ 0 đến 7). Mỗi chu kỳ, 8 bộ lượng tử hóa song song ghi đồng thời 8 giá trị INT8 vào Buffer C, hoàn tất xả ma trận trong 8 chu kỳ (thay vì 64 chu kỳ ở Gen-1).
   5. **Nhóm 4 - Host Output Buffer C Readout & Log Scoreboard 64/64**:
     * *Phân tích tín hiệu*: Quan sát đọc dữ liệu ngõ ra trên `rd_c_addr` và `rd_c_data`. Bảng log ModelSim xác nhận `[TB] Test PASSED: 64/64 elements matched` (khớp hoàn toàn với mô hình tham chiếu Python)."""

text = text.replace(old_demo2_bullets, clean_demo2_bullets)

# 2. Add Demo 1b: UVM Verification
demo1_anchor = """### Demo 1: Kiểm Thử Đơn Vị Độc Lập 61/61 Checks (15 giây)"""

demo1b_content = """### Demo 1b: Kiểm Thử Khối Lõi Bằng UVM 1.1c & Đo Độ Bao Phủ Chức Năng (10 giây)
* **Mục đích**: Chứng minh khối IP lõi mảng tâm thu (`systolic_accelerator_top`) đạt chuẩn kiểm chứng ngẫu nhiên có ràng buộc (Constrained-Random Verification) và bao phủ 100% các trường hợp kiểm thử chức năng (88/88 coverage bins) theo chuẩn công nghiệp UVM 1.1c.
* **Cách thao tác**:
  1. Mở PowerShell hoặc Command Prompt tại thư mục dự án và chạy:
     ```cmd
     # Cách 1: Chạy từ thư mục gốc
     .\run_uvm_test.bat

     # Cách 2: Chạy trực tiếp trong thư mục uvm_verify
     cd uvm_verify
     .\run_uvm.bat
     ```
  2. Thời gian chạy hoàn tất trong khoảng 8 - 10 giây.
* **Màn hình hiển thị kết quả**:
  ```text
  # UVM_INFO gemm_scoreboard.sv: [SCB] --- Scoreboard Summary ---
  # UVM_INFO gemm_scoreboard.sv: [SCB] Total: 71 | Passed: 71 | Failed: 0
  # UVM_INFO gemm_scoreboard.sv: [SCB] Status: PASSED
  # 
  # --- Coverage Summary ---
  # POINT COVERAGE SCORE : 39 / 39 Target Bins Covered ( 100.00% )
  # CROSS COVERAGE SCORE : 49 / 49 Target Bins Covered ( 100.00% )
  # COMBINED SCORE       : 88 / 88 Total Bins Covered ( 100.00% )
  # 
  # --- UVM Report Summary ---
  # UVM_INFO : 119 | UVM_WARNING : 0 | UVM_ERROR : 0 | UVM_FATAL : 0
  ```
* **Trọng tâm trình bày**:
  - Trình chiếu môi trường UVM hoàn chỉnh gồm Driver, Monitor, Scoreboard và Covergroup chạy trên mảng $8 \times 8$ (64 PEs).
  - Phân tích chỉ số `UVM_ERROR : 0` xác nhận 71 giao dịch ngẫu nhiên đều được kiểm chứng chính xác.
  - Phân tích 88 Coverage Bins: bao phủ toàn bộ các miền giá trị biên cực đại ($-128, +127, 0$), các mức dịch bit ($0..8$), chế độ ReLU/Bypass và các kích thước ma trận $K \in [1..16]$.

---

"""

if demo1_anchor in text and "### Demo 1b:" not in text:
    text = text.replace(demo1_anchor, demo1b_content + demo1_anchor)
    print("Demo 1b inserted successfully!")

# 3. Update Table of Contents
toc_anchor = """  - [Demo 1: Kiểm Thử Đơn Vị Độc Lập 61/61 Checks (15 giây)](#demo-1-kiểm-thử-đơn-vị-độc-lập-6161-checks-15-giây)"""
toc_demo1b = """  - [Demo 1b: Kiểm Thử Khối Lõi Bằng UVM 1.1c & Đo Độ Bao Phủ (10 giây)](#demo-1b-kiểm-thử-khối-lõi-bằng-uvm-11c--đo-độ-bao-phủ-chức-năng-10-giây)
  - [Demo 1: Kiểm Thử Đơn Vị Độc Lập 61/61 Checks (15 giây)](#demo-1-kiểm-thử-đơn-vị-độc-lập-6161-checks-15-giây)"""

if toc_anchor in text and "Demo 1b:" not in text:
    text = text.replace(toc_anchor, toc_demo1b)
    print("TOC updated with Demo 1b!")

with open(report_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Report updated with UVM Demo successfully!")
