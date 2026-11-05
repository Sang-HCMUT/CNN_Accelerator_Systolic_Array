import os
import re

report_path = "BaoCao_TienDo_50_CNN_Systolic_SoC.md"
with open(report_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Sync Table of Contents titles
text = text.replace(
    "- [2. Chi Tiết TẦNG THIẾT KẾ VI MẠCH RTL (Gen-2 Architecture)]",
    "- [2. Thiết Kế Vi Mạch Phần Cứng RTL (Kiến Trúc Gen-2)]"
)
text = text.replace(
    "- [3. Chi Tiết TẦNG TÍCH HỢP HỆ THỐNG SOC & GIAO TIẾP BUS (Kèm Tuân Thủ AXI4-Lite)]",
    "- [3. Tích Hợp Hệ Thống Trên Chip (SoC) Và Giao Tiếp Bus]"
)
text = text.replace(
    "- [4. Chi Tiết TẦNG KIỂM CHỨNG VI MẠCH ĐA TẦNG (Unit, Backpressure, UVM 10-Seed, Lint)]",
    "- [4. Phương Pháp Luận Và Kết Quả Kiểm Chứng Vi Mạch Phân Tầng]"
)
text = text.replace(
    "- [5. Kết Quả Tổng Hợp Phần Cứng & Đóng Thời Gian (OOC vs Full SoC STA)]",
    "- [5. Kết Quả Tổng Hợp Mạch Và Phân Tích Thời Gian Tĩnh (STA)]"
)

# 2. De-AI Section 1.2 & 1.3
text = text.replace(
    '#### 2. Tại Sao GEMM Là "Trái Tim" Của Trí Tuệ Nhân Tạo & Học Sâu (Why GEMM Powers Deep Learning)',
    '#### 2. Vai Trò Của Phép Toán GEMM Trong Các Mô Hình Học Sâu'
)
text = text.replace(
    '|               ÁNH XẠ TOÀN DIỆN CÁC TẦNG MẠNG HỌC SÂU VỀ PHÉP TOÁN NỀN TẢNG GEMM                   |',
    '|                         ÁNH XẠ CÁC TẦNG MẠNG HỌC SÂU VỀ PHÉP TOÁN GEMM                             |'
)
text = text.replace(
    'bẻ gãy nút thắt cổ chai Memory Wall.',
    'giảm áp lực nút thắt cổ chai bộ nhớ (Memory Wall).'
)
text = text.replace(
    'giải phóng hoàn toàn CPU khỏi khối lượng tính toán phép nhân cộng khổng lồ.',
    'giúp giải phóng CPU khỏi khối lượng tính toán phép nhân cộng.'
)
text = text.replace(
    'Bộ gia tốc mảng tâm thu trong đề tài là một **động cơ nhân ma trận GEMM đa năng (Universal Matrix Multiplier)**, hoàn toàn độc lập với hình dạng cấu trúc tầng mạng và **không bị giới hạn ở 1 lớp tích chập**.',
    'Mảng tâm thu trong đề tài đóng vai trò là một khối tính toán nhân ma trận tổng quát, có thể tái sử dụng cho nhiều tầng mạng khác nhau thông qua phần mềm điều phối.'
)

# 3. De-AI Section 1.5
target_15_intro = """Trong phương pháp luận thiết kế vi mạch chuyên nghiệp (ASIC/FPGA Design Methodology), một thiết kế phần cứng RTL viết bằng SystemVerilog **tuyệt đối không bao giờ được phép tự chứng minh tính đúng đắn của chính nó**. Bắt buộc phải xây dựng một mô hình toán học tham chiếu độc lập hoàn toàn (**Golden Reference Model**) ở cấp độ phần mềm (Software Reference Stack) bằng ngôn ngữ bậc cao (Python 3.13, NumPy, PyTorch) để làm "thước đo chuẩn tuyệt đối" (Ground Truth) nhằm đối soát từng bit dữ liệu (Bit-True Verification)."""

clean_15_intro = """Trong quy trình thiết kế và kiểm chứng vi mạch số, tính đúng đắn của mã nguồn phần cứng RTL cần được đối chiếu độc lập với một mô hình tham chiếu phần mềm (Golden Reference Model). Đề tài xây dựng bộ mô hình tham chiếu bằng ngôn ngữ Python (kết hợp thư viện NumPy và PyTorch) nhằm sinh dữ liệu đầu vào chuẩn và tạo tập kết quả mẫu (Ground Truth) phục vụ đối soát từng bit (bit-true verification) trong môi trường mô phỏng."""

text = text.replace(target_15_intro, clean_15_intro)

text = text.replace(
    "Kịch bản viết bằng Pure Python độc lập hoàn toàn (Zero-dependency, không cần cài đặt thư viện nặng như PyTorch hay TensorFlow), thực hiện chính xác mô phỏng toán học của bộ gia tốc:",
    "Kịch bản viết bằng Python độc lập (không cần cài đặt thư viện ngoài), mô phỏng các phép tính số học tương đương với phần cứng:"
)
text = text.replace(
    "* **Minh chứng đối chuẩn Bit-True 100%**:",
    "* **Đối chiếu kết quả với mô phỏng phần cứng**:"
)

# 4. De-AI Section 2
text = text.replace("Ba Chiều Hướng Cải Thiện Vượt Bậc", "Ba Hướng Cải Tiến Kiến Trúc")
text = text.replace(
    "2. **Chiều Hướng 2: Bẻ Gãy Nút Thắt Bus Giao Tiếp Nhờ Cơ Chế Packed 4-INT8**",
    "2. **Chiều Hướng 2: Tối Ưu Băng Thông Giao Tiếp Bus Nhờ Cơ Chế Packed 4-INT8**"
)
text = text.replace(
    "Kiến trúc Gen-2 (Bản cải tiến đột phá của đề tài):",
    "Kiến trúc Gen-2 (Bản cải tiến đề xuất):"
)
text = text.replace(
    "**Tối ưu tuyệt đối**: Khối Quantizer đặt trực tiếp tại ngõ ra của từng hàng",
    "**Tối ưu hóa**: Khối Quantizer đặt trực tiếp tại ngõ ra của từng hàng"
)
text = text.replace(
    "(`quantize_relu_unit.sv` — Đột phá Gen-2)",
    "(`quantize_relu_unit.sv` — Cải tiến Gen-2)"
)
text = text.replace(
    "Các Cải Tiến Đột Phá Từ Kiến Trúc Gen-1 Lên Gen-2",
    "Các Cải Tiến Kiến Trúc Từ Phiên Bản Gen-1 Lên Gen-2"
)

# 5. De-AI Section 4
text = text.replace(
    "> **KẾT LUẬN NGHIỆM THU SCOREBOARD**: Toàn bộ **64/64 phần tử** ma trận ngõ ra ở cả 2 tầng INT32 và INT8 đều đạt trạng thái **[PASS] 100% Bit-True Parity** so với mô hình toán học Python, xác nhận phần cứng RTL tính toán chuẩn xác tuyệt đối không có bất kỳ sai lệch nào.",
    "**Đánh giá kết quả**: Toàn bộ 64/64 phần tử ngõ ra ở cả hai tầng (tích lũy INT32 và lượng tử hóa INT8) đều trùng khớp với mô hình mẫu Python (đạt trạng thái [PASS], 0 lỗi sai lệch)."
)
text = text.replace(
    "COVERAGE VERDICT     : [100.00% FULL INDUSTRIAL CLOSURE ACHIEVED]",
    "COVERAGE VERDICT     : [100.00% FUNCTIONAL COVERAGE ACHIEVED]"
)
text = text.replace(
    "đồng bộ tuyệt đối với phần cứng thực tế.",
    "đồng bộ với phần cứng thực tế."
)
text = text.replace(
    "đạt tỷ lệ thành công tuyệt đối **100.00% (10/10 seeds passed, 0 lỗi Scoreboard, 0 vi phạm thủ tục)**",
    "đạt tỷ lệ **10/10 seeds passed** (0 lỗi Scoreboard, 0 vi phạm thủ tục)"
)
text = text.replace(
    "đóng 100.00% toàn bộ **88/88 functional bins**",
    "bao phủ đủ **88/88 functional bins**"
)

# 6. De-AI Section 5
text = text.replace(
    "bảo đảm hệ thống đóng timing hoàn hảo ở 50 MHz.",
    "bảo đảm hệ thống đóng timing an toàn ở 50 MHz."
)
text = text.replace(
    "Hoàn toàn sạch vi phạm thời gian",
    "Không có vi phạm thời gian (TNS = 0)"
)

# 7. De-AI Section 6.3 (Academic Scoping)
target_63 = """1. **Phạm vi & Đóng góp của Đồ Án Tốt Nghiệp Kỹ Sư**:
   - Đề tài tập trung giải quyết bài toán kỹ thuật hệ thống toàn diện: Hiện thực từ đầu lõi tăng tốc phần cứng mảng tâm thu 2D INT8, tối ưu hóa pha đọc dữ liệu Gen-2 (Parallel Row Writeback rút ngắn 60.2% chu kỳ tính toán), tích hợp chuẩn bus AMBA AXI4-Lite với vi xử lý RISC-V PicoRV32, xây dựng ngăn xếp phần mềm nhúng bare-metal C độc lập (không phụ thuộc trình sinh mã tự động), phát triển bộ công cụ kiểm chứng đa tầng (Unit, Subsystem Backpressure, UVM 10-seed regression, SoC co-sim 3.87M chu kỳ) và tổng hợp đóng timing thành công trên 2 thế hệ chip FPGA thực tế.
   - Đây là một công trình kỹ thuật hoàn chỉnh, đáp ứng xuất sắc các tiêu chí đào tạo kỹ sư chuyên ngành Thiết kế Vi mạch & Hệ thống Nhúng.
2. **Khoảng Cách Kỹ Thuật Đối Với Một Bài Báo Nghiên Cứu Khoa Học (Scientific Paper)**:
   - Để nâng cấp thiết kế này thành một công trình nghiên cứu khoa học đăng tải trên các hội nghị/tạp chí chuyên ngành vi mạch (như IEEE TCAS, IEEE VLSI, hay FPT/FCCM), đề tài cần bổ sung thêm các yếu tố học thuật chuyên sâu:
     * *Đóng góp mới về mặt kiến trúc vi mô (Architectural Novelty)*: Đề xuất kỹ thuật dataflow lai hoặc kiến trúc tái cấu trúc động (Reconfigurable Systolic Mesh) vượt trội hơn các mô hình kinh điển như TPU (Jouppi et al.) hay Eyeriss (Chen et al.).
     * *Phân tích định lượng công suất/năng lượng thực nghiệm*: Đo đạc công suất vật lý trên kit FPGA hoặc triển khai thiết kế trên quy trình ASIC chuẩn (như TSMC 28nm / SkyWater 130nm) qua bộ công cụ Cadence Innovus / Synopsys PrimeTime để đo Joules/OP.
     * *Khung so sánh đối chuẩn (Benchmarking Baseline)*: Đặt thiết kế trong cùng điều kiện tải công việc chuẩn (MLPerf Tiny, MobileNet) so sánh trực tiếp với các kiến trúc công bố gần đây.
   - Việc phân định minh bạch này khẳng định sự nghiêm túc, khách quan và trung thực học thuật của tác giả, đồng thời vạch rõ lộ trình nghiên cứu mở rộng trong tương lai."""

clean_63 = """1. **Phạm vi kỹ thuật của đồ án tốt nghiệp kỹ sư**:
   - Đề tài tập trung vào việc hiện thực kỹ thuật một hệ thống phần cứng hoàn chỉnh: thiết kế RTL mảng tâm thu 2D INT8, cải tiến pha đọc dữ liệu Gen-2 (Parallel Row Writeback giúp giảm 60.2% chu kỳ tính toán), tích hợp chuẩn bus AMBA AXI4-Lite với vi xử lý RISC-V PicoRV32, xây dựng firmware bare-metal C, thiết lập quy trình kiểm thử phân tầng (Unit tests, AXI backpressure, UVM multi-seed regression, SoC co-simulation) và tổng hợp đóng timing trên hai dòng FPGA Cyclone II và Cyclone V.
   - Trọng tâm của đồ án là làm chủ quy trình thiết kế, tích hợp và kiểm chứng hệ thống vi mạch số trên FPGA.
2. **Các hướng nghiên cứu mở rộng phục vụ công bố khoa học (Academic Research Gap)**:
   - So với các công trình nghiên cứu chuyên sâu đăng tải trên các tạp chí và hội nghị vi mạch (như IEEE TCAS, IEEE VLSI, FPT), thiết kế hiện tại còn một số điểm cần tiếp tục mở rộng:
     * *Cải tiến kiến trúc vi mô*: Nghiên cứu các mô hình dòng dữ liệu lai (Hybrid Dataflow) hoặc cơ chế hỗ trợ tính toán ma trận thưa (Sparsity acceleration).
     * *Đo đạc công suất và năng lượng thực nghiệm*: Phân tích tiêu thụ năng lượng thực tế (Joules/OP) trên phần cứng vật lý hoặc triển khai trên quy trình chế tạo bán dẫn ASIC chuẩn (TSMC / SkyWater) qua các công cụ EDA chuyên dụng.
     * *Mở rộng mô hình đối chuẩn (Benchmarking)*: Đánh giá hệ thống trên các tập dữ liệu và mạng nơ-ron lớn hơn trong chuẩn MLPerf Tiny."""

text = text.replace(target_63, clean_63)

# 8. De-AI Part II Demo Guides (Remove "Kính thưa Thầy Cô... ạ" scripts, replace with technical focus points)
text = text.replace(
"""* **Gợi ý thuyết minh**:
  > *"Kính thưa Thầy Cô, đây là mô hình chạy bằng Python độc lập đóng vai trò Golden Model tham chiếu cho toàn bộ đề tài. Script `gemm_golden.py` tính toán thuần túy trên CPU để sinh ra ma trận A, B và kết quả chuẩn C. Toàn bộ các giá trị này được xuất ra file .hex để testbench ModelSim nạp vào làm thước đo đối soát. Đồng thời, mô hình Python CNN `test_single_image.py` suy luận hoàn chỉnh chữ số 7 đạt độ tin cậy 100%, bảo toàn độ chính xác 97.06% trên tập MNIST trước khi đưa xuống phần cứng ạ."*""",
"""* **Trọng tâm trình bày**:
  - Giới thiệu mô hình tham chiếu phần mềm viết bằng Python độc lập trước khi kiểm thử phần cứng.
  - Minh họa việc sinh ma trận A, B và kết quả chuẩn C qua script `gemm_golden.py` để xuất 4 tệp `.hex` đối soát.
  - Trình bày kết quả suy luận mẫu ảnh chữ số 7 trên mô hình mạng CNN qua script `test_single_image.py` đạt độ chính xác 97.06% trên tập MNIST."""
)

text = text.replace(
"""* **Gợi ý thuyết minh**:
  > *"Kính thưa Thầy Cô, đây là script kiểm thử hồi quy đơn vị tự động. Trong 15 giây, hệ thống đã kiểm tra độc lập toàn bộ 8 khối vi mạch cơ bản từ PE, bộ Skewing, Quantizer, các Buffer A/B/C đến lưới mảng 64 PE. Toàn bộ 61/61 điểm kiểm tra đều đạt Pass 100% với 0 lỗi sai lệch ạ."*""",
"""* **Trọng tâm trình bày**:
  - Trình chiếu kết quả kiểm thử tự động 8 khối RTL độc lập từ cấp độ thấp (PE, Skew Unit, Quantizer, Buffer A/B/C đến mảng 64 PE).
  - Xác nhận toàn bộ 61/61 điểm kiểm tra đạt trạng thái PASSED trong 15 giây mô phỏng."""
)

text = text.replace(
"""     * *"Kính thưa Thầy Cô, đây là dạng sóng của khối Skew Unit 8 hàng và 8 cột: hàng 0 vào ngay nhịp 0, hàng 1 trễ 1 nhịp, hàng 2 trễ 2 nhịp... đến hàng 7 trễ đúng 7 nhịp ($0T \dots 7T$), tạo thành độ trễ bậc thang đường chéo để đồng bộ dòng dữ liệu nhịp nhàng vào 64 PEs."*""",
"""     * *Phân tích tín hiệu*: Quan sát dạng sóng của khối Skew Unit 8 hàng và 8 cột: hàng 0 đưa dữ liệu vào ngay chu kỳ đầu tiên, các hàng tiếp theo trễ dần từ $1T, 2T, \dots, 7T$, tạo độ trễ bậc thang đường chéo nhằm đồng bộ dòng dữ liệu vào lưới mảng tâm thu."""
)

text = text.replace(
"""        * *"Nhấp vào dấu `+` để mở rộng `c_matrix_core`: Thầy Cô sẽ thấy đầy đủ 8 hàng `[0]..[7]`, mỗi hàng gồm 8 cột `[0]..[7]`. Đây là 64 thanh ghi tích lũy 32-bit bên trong 64 PEs đang tăng dồn liên tục theo cơ chế Output-Stationary, khẳng định quy mô mảng tăng tốc chuẩn công nghiệp 64 PEs hoàn chỉnh."*""",
"""        * *Phân tích tín hiệu*: Mở rộng tín hiệu `c_matrix_core` để quan sát 64 thanh ghi tích lũy 32-bit bên trong 64 PEs ($8 \times 8$). Giá trị tích lũy tăng dần theo từng chu kỳ tính toán theo đúng cơ chế Output-Stationary."""
)

text = text.replace(
"""        * *"Và đây là minh chứng đắt giá cho cải tiến Gen-2: sau khi tính xong, xung `wr_row_en` tích cực đúng 8 chu kỳ (tương ứng `wr_row_idx` từ 0 đến 7). Mỗi chu kỳ, 8 bộ lượng tử hóa song song đẩy đồng thời 8 byte INT8 của một hàng vào Buffer C, rút ngắn thời gian xả ma trận từ 64 chu kỳ tuần tự xuống đúng 8 chu kỳ song song."*""",
"""        * *Phân tích tín hiệu*: Quan sát tín hiệu `wr_row_en` tích cực trong đúng 8 chu kỳ. Mỗi chu kỳ, 8 bộ lượng tử hóa song song đẩy đồng thời 8 giá trị INT8 của một hàng vào Buffer C, rút ngắn thời gian ghi kết quả từ 64 chu kỳ xuống 8 chu kỳ."""
)

text = text.replace(
"""* **Gợi ý thuyết minh**:
  > *"Kính thưa Thầy Cô, đây là kết quả đồng mô phỏng SoC chạy hơn 3.8 triệu chu kỳ xung nhịp cùng mã firmware C. Hệ thống đã thực thi hoàn chỉnh 7 kịch bản kiểm chứng, trong đó tầng tích chập Conv1 khớp bit-true với mô hình PyTorch và nhận dạng chính xác ảnh chữ số 7 của tập MNIST với độ tin cậy đạt 69.4% ạ."*""",
"""* **Trọng tâm trình bày**:
  - Trình bày kết quả đồng mô phỏng SoC chạy firmware C với 3.87 triệu chu kỳ.
  - Phân tích 7 kịch bản kiểm chứng: xác nhận tầng Conv1 khớp bit-true với mô hình PyTorch (256/256 điểm kích hoạt) và mô hình suy luận toàn phần nhận dạng đúng chữ số 7 (độ tin cậy 69.4%)."""
)

text = text.replace(
"""* **Gợi ý thuyết minh**:
  > *"Kính thưa Thầy Cô, đây là báo cáo tổng hợp vật lý thực tế trên Quartus Prime cho dòng chip Cyclone V trên kit DE10-Standard: thiết kế chỉ chiếm 19.8% ALMs, tận dụng 64 khối nhân DSP cứng cho 64 PE. Báo cáo Timing Analyzer ghi nhận Setup Slack đạt dương an toàn +5.609 ns ở 50 MHz (tương đương Fmax đạt xấp xỉ 70 MHz), TNS = 0.000 ns và file bitstream .sof đã được đóng gói hoàn tất ạ."*""",
"""* **Trọng tâm trình bày**:
  - Trình chiếu báo cáo tổng hợp Quartus Prime trên dòng chip Cyclone V (kit DE10-Standard): sử dụng 19.8% ALMs và 64 khối nhân DSP phần cứng.
  - Phân tích báo cáo STA: Setup Slack đạt +5.609 ns ở tần số 50 MHz (Fmax đạt 69.49 MHz), TNS = 0.000 ns và file bitstream `.sof` đã được tạo thành công."""
)

text = text.replace(
"""* **Gợi ý thuyết minh**:
  > *"Để chuẩn bị cho giai đoạn thực nghiệm trên phần cứng thật, em đã xây dựng sẵn bộ công cụ nạp chip 1-click và script kiểm thử tự động HIL qua cổng UART. Khi cắm kit vào máy tính, script sẽ tự động nạp bitstream, giao tiếp với SoC, đọc thanh ghi phiên bản và ghi lại toàn bộ log đo đạc thực tế vào file để phục vụ viết thuyết minh tốt nghiệp ạ."*""",
"""* **Trọng tâm trình bày**:
  - Giới thiệu công cụ tự động hóa nạp bitstream và kịch bản kiểm thử phần cứng HIL qua giao tiếp UART (`hil_test_board.py`).
  - Nêu rõ đây là bước chuẩn bị để thu thập dữ liệu đo đạc thực nghiệm trên phần cứng vật lý trong giai đoạn 2."""
)

# 9. Clean up trailing exclamation marks in text
text = text.replace("với 0 lỗi sai lệch ạ!", "với 0 lỗi sai lệch.")
text = text.replace("đạt 173.7x so với phần mềm!", "đạt 173.7x so với phần mềm.")
text = text.replace("(0 sai lệch)!", "(0 sai lệch).")
text = text.replace("100% Bit-True Match!", "100% Bit-True Match.")

with open(report_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Tone refactoring completed successfully!")
