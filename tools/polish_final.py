import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

report_path = "BaoCao_TienDo_50_CNN_Systolic_SoC.md"
with open(report_path, "r", encoding="utf-8") as f:
    text = f.read()

replacements = [
    (
        "* **Ý nghĩa**: Minh chứng mọi module con phần cứng đều hoàn hảo, vượt qua mọi góc kẹt số học biên.",
        "* **Mục đích**: Xác nhận các khối chức năng RTL hoạt động chính xác độc lập và vượt qua các bài kiểm thử giá trị biên số học."
    ),
    (
        "* **Ý nghĩa**: Chứng minh dòng chảy nhịp sóng Wavefront Skewing và cơ chế tích lũy Output-Stationary trong PE bằng dạng sóng trực quan.",
        "* **Mục đích**: Quan sát trực quan dòng chảy dữ liệu nhịp sóng Wavefront Skewing và quá trình tích lũy Output-Stationary của mảng PE trên dạng sóng tín hiệu."
    ),
    (
        "* **Ý nghĩa**: Minh chứng toàn bộ hệ thống SoC (CPU PicoRV32 + AXI Interconnect + Accelerator) thực thi firmware C thật và nhận dạng đúng ảnh MNIST.",
        "* **Mục đích**: Kiểm tra toàn diện hệ thống SoC (CPU PicoRV32, bus AXI và bộ tăng tốc) khi thực thi mã nhị phân firmware C trên bài toán nhận dạng chữ số MNIST."
    ),
    (
        "* **Ý nghĩa**: Chứng minh thiết kế đã được tổng hợp vật lý thật trên FPGA (không phải mô phỏng suông), đạt chỉ tiêu đóng thời gian an toàn.",
        "* **Mục đích**: Trình bày báo cáo tổng hợp vật lý và phân tích thời gian tĩnh (STA) trên công cụ Quartus Prime."
    ),
    (
        "* **Ý nghĩa**: Chứng minh sự sẵn sàng 100% để bước sang giai đoạn 2 (thực nghiệm trên bo mạch vật lý).",
        "* **Mục đích**: Giới thiệu bộ công cụ tự động hóa nạp chip và kịch bản đo đạc phần cứng qua giao tiếp UART (Hardware-in-the-Loop)."
    ),
    (
        "* **Câu nói thuyết minh**:",
        "* **Gợi ý thuyết minh**:"
    ),
    (
        "Kết quả kiểm chứng tầng 1 ghi nhận toàn bộ 61/61 test đơn vị đều đạt Pass 100%. Ở tầng 2, bộ kiểm chứng UVM 1.1c đạt chỉ tiêu đóng độ bao phủ chức năng 100% trên toàn bộ 88 bins không gian tham số toán học và trạng thái bão hòa, xác nhận thiết kế đáp ứng đúng đặc tả chức năng và các trường hợp biên.",
        "Kết quả kiểm chứng ở tầng 1 cho thấy toàn bộ 61/61 trường hợp kiểm thử đơn vị đều đạt yêu cầu. Ở tầng 2, bộ kiểm thử UVM đạt 100% độ bao phủ tính năng trên 88 bins tham số và trạng thái bão hòa, xác nhận các khối chức năng hoạt động đúng theo đặc tả thiết kế ạ."
    ),
    (
        "Thưa Thầy Cô, đây là mạng trễ sóng Wavefront: Hàng 0 vào ngay ở nhịp 0, Hàng 1 trễ 1 nhịp, Hàng 2 trễ 2 nhịp... Hàng 7 trễ đúng 7 nhịp tạo thành hình bậc thang rất đều đặn.",
        "Kính thưa Thầy Cô, đây là dạng sóng của khối Skew Unit: hàng 0 vào ngay ở nhịp 0, hàng 1 trễ 1 nhịp, hàng 2 trễ 2 nhịp... đến hàng 7 trễ đúng 7 nhịp, tạo thành độ trễ bậc thang đều đặn để đồng bộ dữ liệu vào mảng PE."
    ),
    (
        "Và đây là cải tiến Gen-2: sau khi tính xong, tín hiệu `wr_row_en` bật lên trong đúng 8 chu kỳ, mỗi chu kỳ ghi đồng thời trọn vẹn 8 phần tử của 1 hàng vào Buffer C, rút ngắn pha đọc từ 64 chu kỳ xuống đúng 8 chu kỳ ạ.",
        "Và đây là tín hiệu ghi kết quả của kiến trúc Gen-2: sau khi tính toán xong, tín hiệu `wr_row_en` tích cực trong 8 chu kỳ, mỗi chu kỳ ghi đồng thời 8 phần tử của một hàng vào bộ đệm ngõ ra Buffer C, giúp rút ngắn thời gian đọc từ 64 chu kỳ xuống 8 chu kỳ ạ."
    ),
    (
        "Thưa Thầy Cô, đây là kết quả đồng mô phỏng SoC chạy hơn 3.8 triệu chu kỳ clock với firmware C thật. Hệ thống vượt qua 7 kịch bản ứng dụng, tính toán tầng Conv1 khớp 100% từng bit với PyTorch và nhận dạng chính xác ảnh chữ số 7 của tập MNIST với độ tin cậy 69% ạ.",
        "Kính thưa Thầy Cô, đây là kết quả đồng mô phỏng SoC chạy hơn 3.8 triệu chu kỳ xung nhịp cùng mã firmware C. Hệ thống đã thực thi hoàn chỉnh 7 kịch bản kiểm chứng, trong đó tầng tích chập Conv1 khớp bit-true với mô hình PyTorch và nhận dạng chính xác ảnh chữ số 7 của tập MNIST với độ tin cậy đạt 69.4% ạ."
    ),
    (
        "Hoàn thành xuất sắc",
        "Hoàn thành tốt"
    ),
    (
        "hoàn thành xuất sắc",
        "hoàn thành đầy đủ"
    ),
]

for s, d in replacements:
    if s in text:
        text = text.replace(s, d)
        print(f"[OK] Replaced: {s[:35]}...")
    else:
        print(f"[WARN] Not found: {s[:35]}...")

with open(report_path, "w", encoding="utf-8") as f:
    f.write(text)

print("[SUCCESS] Applied final polish to BaoCao_TienDo_50_CNN_Systolic_SoC.md!")
