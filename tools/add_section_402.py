import os

report_path = "BaoCao_TienDo_50_CNN_Systolic_SoC.md"
with open(report_path, "r", encoding="utf-8") as f:
    text = f.read()

anchor = "### 4.1. Tầng 1: Kiểm Thử Đơn Vị Độc Lập Từng Khối RTL (`tb_unit_modules.sv` — 61 Checks)"

section_402 = """### 4.0.2. Phân Định Phương Pháp Luận: Kiểm Chứng Thông Thường (Conventional) vs. Kiểm Chứng UVM

Để bảo đảm tính chặt chẽ trong phương pháp luận kiểm chứng vi mạch và phân định rõ vai trò của từng công cụ, đề tài phân định rành mạch giữa **Kiểm chứng thông thường (Conventional / Directed Verification)** và **Kiểm chứng UVM (Coverage-Driven Verification)**:

| Tiêu chí so sánh | Kiểm chứng Thông thường (Conventional Testbench) | Kiểm chứng UVM (Universal Verification Methodology) |
| :--- | :--- | :--- |
| **Thư mục mã nguồn** | [`VEFIFY/`](file:///e:/DATN/CNN_Systolic_Architecture/VEFIFY) | [`uvm_verify/`](file:///e:/DATN/CNN_Systolic_Architecture/uvm_verify) |
| **Đối tượng kiểm chứng** | Từng module con đơn lẻ, bus AXI, và **toàn hệ thống SoC chạy CPU thật** | **Chuyên biệt cho Lõi mảng tâm thu (`systolic_accelerator_top`)** |
| **Bản chất kích thích (Stimulus)** | **Định hướng (Directed)**: Kịch bản cố định, ma trận mẫu từ Python, hoặc mã máy C | **Ngẫu nhiên có ràng buộc (Constrained-Random)**: Tự động sinh hàng ngàn tổ hợp ngẫu nhiên |
| **Tiêu chí nghiệm thu** | Trạng thái Pass/Fail từng kịch bản; đối soát bit-true; dạng sóng vi mô | **Độ bao phủ chức năng (Functional Coverage: 88/88 Bins = 100%)** |
| **Mục đích cốt lõi** | Kiểm tra tính đúng đắn chức năng cơ bản và tích hợp phần cứng với phần mềm | Tìm lỗi góc kẹt tiềm ẩn (Corner Cases); chứng nhận chất lượng khối IP (Sign-off) |

#### 1. Vai Trò Của Kiểm Chứng UVM Trong Đề Tài:
Môi trường UVM trong thư mục `uvm_verify/` được xây dựng theo chuẩn IEEE 1800 UVM 1.1c (gồm Sequencer, Driver, Monitor, Scoreboard, Covergroup), tập trung kiểm chứng **Lõi gia tốc trung tâm**:
* **Kiểm thử ngẫu nhiên có ràng buộc (CRV)**: Tự động phát sinh hàng ngàn ma trận ngẫu nhiên qua 10 seed hồi quy liên tiếp (`Seed 1001..1010`), kiểm tra mọi tổ hợp giá trị biên ($-128, +127, 0$), các mức dịch bit ($0..8$), kích thước $K \in [1..16]$ và chế độ bật/tắt ReLU.
* **Đóng độ bao phủ tính năng (Coverage Closure)**: Đạt **88/88 functional bins (100%)**, gồm 39 point coverage bins và 49 cross coverage bins, chứng minh không bỏ sót trường hợp biên nào ở cấp độ lõi phần cứng.

#### 2. Vai Trò Của Kiểm Chứng Thông Thường (Conventional Testbench):
Các testbench SystemVerilog trong thư mục `VEFIFY/` giải quyết các bài toán tích hợp hệ thống mà UVM không đảm nhận:
* **Kiểm thử đơn vị vi mô (`tb_unit_modules.sv`)**: Kiểm tra độc lập 8 khối RTL con (PE, Skew, Quantizer, Buffers, FSM) đạt 61/61 checks trong 15 giây.
* **Quan sát trực quan dòng dữ liệu (`tb_systolic_gemm.sv`)**: Mở dạng sóng ModelSim GUI để kiểm tra nhịp trễ sóng Wavefront Skewing ($0T \dots 7T$) và quá trình tích lũy Output-Stationary của 64 PE theo từng chu kỳ xung nhịp.
* **Kiểm chứng giao thức bus AXI4-Lite (`tb_axi_backpressure.sv`)**: Kiểm tra khả năng chịu áp lực nghẽn bus (Backpressure trễ 1..8 chu kỳ), kênh địa chỉ/dữ liệu đến lệch pha (Decoupled AW/W), và cơ chế nạp đóng gói 4-INT8.
* **Đồng mô phỏng toàn hệ thống SoC (`tb_soc_top.sv` — 3.87 triệu chu kỳ)**: Nạp trực tiếp firmware C thật (`firmware.hex`) vào BRAM để CPU RISC-V PicoRV32 điều phối mảng tâm thu giải bài toán AI thực tế (nhận dạng chữ số MNIST và tầng Conv1 256 activations).

---

"""

if anchor in text and "### 4.0.2." not in text:
    text = text.replace(anchor, section_402 + anchor)
    print("Section 4.0.2 inserted successfully!")

# Update Table of Contents
toc_anchor = "    - [4. Phương Pháp Luận Và Kết Quả Kiểm Chứng Vi Mạch Phân Tầng](#4-phương-pháp-luận-và-kết-quả-kiểm-chứng-vi-mạch-phân-tầng)"
toc_addition = """    - [4. Phương Pháp Luận Và Kết Quả Kiểm Chứng Vi Mạch Phân Tầng](#4-phương-pháp-luận-và-kết-quả-kiểm-chứng-vi-mạch-phân-tầng)
      - [4.0.2. Phân Định Kiểm Chứng Thông Thường vs. UVM](#402-phân-định-phương-pháp-luận-kiểm-chứng-thông-thường-conventional-vs-kiểm-chứng-uvm)"""

if toc_anchor in text and "4.0.2." not in text:
    text = text.replace(toc_anchor, toc_addition)
    print("TOC updated with Section 4.0.2!")

with open(report_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Report updated successfully!")
