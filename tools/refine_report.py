import sys
import re
import os

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

report_path = "BaoCao_TienDo_50_CNN_Systolic_SoC.md"
with open(report_path, "r", encoding="utf-8") as f:
    text = f.read()

replacements = [
    # 1. Headings & Subheadings
    ("## 2. Chi Tiết TẦNG THIẾT KẾ VI MẠCH RTL (Gen-2 Architecture)",
     "## 2. Thiết Kế Vi Mạch Phần Cứng RTL (Kiến Trúc Gen-2)"),
    ("## 3. Chi Tiết TẦNG TÍCH HỢP HỆ THỐNG SOC & GIAO TIẾP BUS",
     "## 3. Tích Hợp Hệ Thống Trên Chip (SoC) Và Giao Tiếp Bus"),
    ("## 4. Chi Tiết TẦNG KIỂM CHỨNG VI MẠCH ĐA TẦNG (Verification Pyramid & Bit-True Assurance)",
     "## 4. Phương Pháp Luận Và Kết Quả Kiểm Chứng Vi Mạch Phân Tầng"),
    ("## 5. Kết Quả Tổng Hợp Phần Cứng & Đóng Thời Gian (Synthesis & STA)",
     "## 5. Kết Quả Tổng Hợp Mạch Và Phân Tích Thời Gian Tĩnh (STA)"),
    ("### 2.4. Cụm 8 Bộ Lượng Tử Hóa Song Song `quantize_relu_unit.sv` (Gen-2 Upgrade)",
     "### 2.4. Cụm 8 Bộ Lượng Tử Hóa Song Song `quantize_relu_unit.sv` (Kiến Trúc Gen-2)"),
    ("### 2.5. Bộ Đệm Ma Trận `matrix_buffer_a.sv`, `b.sv`, `c.sv` & Cơ Chế Đóng Gói 4 Byte",
     "### 2.5. Bộ Đệm Ma Trận `matrix_buffer_a/b/c.sv` Và Cơ Chế Đóng Gói Dữ Liệu 4 Byte"),
    ("### 2.6. Bộ Điều Khiển Trung Tâm `gemm_controller.sv` & Chu Trình FSM 7 Trạng Thái",
     "### 2.6. Bộ Điều Khiển Trung Tâm `gemm_controller.sv` Và Chu Trình FSM 7 Trạng Thái"),
    ("### SLIDE 9: ĐỘT PHÁ NÂNG CẤP GEN-2: ĐÓNG GÓI 4-BYTE & ĐỌC SONG SONG 8 HÀNG",
     "### SLIDE 9: CẢI TIẾN THIẾT KẾ GEN-2: ĐÓNG GÓI 4-BYTE VÀ ĐỌC SONG SONG 8 HÀNG"),

    # 2. General information buzzwords
    ("Toàn bộ mã nguồn phần cứng được tự thiết kế 100% bằng SystemVerilog (IEEE 1800-2012) từ đầu (*From Scratch*), không dùng IP kéo thả độc quyền, tuân thủ nguyên tắc thiết kế đồng bộ thuần túy (**Pure Synchronous Design**: 0 Latch, 0 Gated Clock, 0 Combinational Loop).",
     "Toàn bộ các khối phần cứng trong đề tài được tác giả hiện thực trực tiếp bằng ngôn ngữ SystemVerilog (chuẩn IEEE 1800-2012), không sử dụng IP đóng gói sẵn từ nhà sản xuất chip, nhằm làm chủ hoàn toàn cấu trúc vi mạch và bảo đảm tính di động giữa nhiều dòng FPGA. Thiết kế tuân thủ nghiêm ngặt nguyên tắc thiết kế đồng bộ (Synchronous Design): không tạo chốt ngoài ý muốn (0 Latch), không dùng xung nhịp có cổng (0 Gated Clock) và không có vòng lặp tổ hợp (0 Combinational Loop)."),
    ("giải quyết triệt để nút thắt này thông qua cơ chế **Tái sử dụng dữ liệu (Data Reuse)**",
     "giảm thiểu đáng kể nút thắt này nhờ cơ chế **Tái sử dụng dữ liệu (Data Reuse)**"),
    ("được Quartus tự động ánh xạ vào các khối **Embedded Multiplier 9-bit** phần cứng trên FPGA.",
     "được công cụ tổng hợp tự động ánh xạ vào các khối **Embedded Multiplier 9-bit** phần cứng trên FPGA."),
    ("đảm bảo triệt tiêu hoàn toàn khả năng tràn số trong suốt chiều sâu nhân $K \\le 16$.",
     "bảo đảm không xảy ra hiện tượng tràn số trong suốt chiều sâu tích lũy $K \\le 16$."),
    ("loại bỏ hoàn toàn các cây cộng gom (Adder Tree) cồng kềnh bên ngoài.",
     "không đòi hỏi cây cộng gom (Adder Tree) ở ngõ ra, giúp đường định tuyến ngắn và gọn hơn."),
    ("đảm bảo đường trễ tới hạn (Critical Path) cực ngắn và Fmax đạt cao.",
     "giúp rút ngắn đường trễ tới hạn (Critical Path) và cải thiện tần số hoạt động cực đại $F_{\\max}$."),
    ("Triệt tiêu hoàn toàn hiện tượng tràn số đổi dấu (Wrap-around Overflow).",
     "Ngăn ngừa hiện tượng tràn số đổi dấu (Wrap-around Overflow)."),
    ("Nạp ma trận A đóng gói 4 byte siêu tốc",
     "Hàm nạp ma trận A dạng đóng gói 4 byte (Packed Transfer)"),
    ("bảo vệ tuyệt đối tính vẹn toàn của dữ liệu đang chạy đường ống.",
     "ngăn ngừa nguy cơ CPU ghi đè làm sai lệch dữ liệu đang xử lý trên đường ống."),
    ("giảm 4x lệnh CPU", "giảm 4 lần số lệnh truy xuất MMIO của CPU"),
    ("giảm 4x lệnh CPU", "giảm 4 lần số lệnh truy xuất MMIO của CPU"),

    # 3. Verification section buzzwords
    ("Kim tự tháp kiểm chứng 3 tầng khép kín (Three-Tier Hardware Verification Pyramid), đảm bảo tiêu chí nghiệm thu **100% Bit-True** (khớp chính xác từng bit với mô hình toán học tham chiếu):",
     "Mô hình kiểm chứng phân tầng 3 cấp độ (Three-Tier Verification Hierarchy), bảo đảm tiêu chí khớp số học bit-true (zero mismatch) so với mô hình tham chiếu:"),
    ("Kim tự tháp 5 tầng", "Mô hình phân tầng 5 lớp"),
    ("0 lỗi sai lệch bit (Zero Tolerance for Bit Mismatches)", "khớp chính xác bit-true hoàn toàn (sai số bằng 0, zero mismatch)"),
    ("Vượt qua 6/6 kịch bản thử thách góc kẹt", "Đạt 6/6 kịch bản kiểm tra giá trị biên số học"),
    ("Các Kịch Bản Thử Thách Cực Biên (Corner Cases)", "Các Trường Hợp Biên (Corner Cases)"),
    ("kịch bản thử thách góc kẹt", "trường hợp biên số học"),
    ("Bảo Vệ Biên Số Học", "Kiểm Tra Giá Trị Biên Số Học"),
    ("bảo vệ mạng nơ-ron không bị sụp đổ độ chính xác", "bảo đảm mô hình không bị sai lệch kết quả phân loại do tràn số"),
    ("Đóng 100% Point Coverage & Cross Coverage", "Đạt 100% độ bao phủ điểm (Point) và chéo (Cross)"),
    ("88 / 88 bins (100.00% Full Industrial Coverage Closure)", "88 / 88 bins (Đạt 100.00% độ bao phủ tính năng UVM)"),
    ("khẳng định độ tin cậy tuyệt đối của lõi thiết kế", "xác nhận thiết kế đáp ứng đúng đặc tả chức năng và các trường hợp biên"),

    # 4. Synthesis table buzzwords
    ("Tuyến đường dây thông thoáng", "Mật độ logic vừa phải (19.8% - 57.5%), thuận lợi cho định tuyến"),
    ("Tỷ lệ thanh ghi cân đối hoàn hảo", "Tỷ lệ sử dụng thanh ghi phân bổ hợp lý"),
    ("100% các PE đều map vào DSP cứng", "Toàn bộ 64 PE đều được ánh xạ vào khối DSP phần cứng"),
    ("Vượt tần số danh định 50 MHz", "Đáp ứng tốt yêu cầu xung nhịp danh định 50 MHz"),
    ("Năng lực đỉnh lý thuyết tại 50 MHz", "Thông lượng tính toán lý thuyết cực đại tại 50 MHz"),
    ("Sẵn sàng nạp xuống phần cứng", "Đã tạo bitstream .sof, sẵn sàng thực nghiệm trên bo mạch"),
    ("Hoàn hảo", "Đã tối ưu"),
    ("tiết kiệm 60.2% thời gian trễ lõi, thông lượng đạt 1.38 GOPS",
     "giảm 60.2% độ trễ tính toán lõi, thông lượng đạt 1.38 GOPS"),

    # 5. Demo section tone
    ("Khi đứng trước Hội đồng đánh giá tiến độ giữa kỳ, bạn hãy tự tin thực hiện **5 nội dung Demo trực tiếp** theo thứ tự từ Kiểm thử đơn vị $\\to$ Dạng sóng vi mạch $\\to$ Đồng mô phỏng SoC $\\to$ Báo cáo Quartus FPGA $\\to$ Quy trình nạp kit thật:",
     "Quy trình thực hiện 5 kịch bản Demo trước Hội đồng đánh giá: Phần này trình bày các bước thao tác, lệnh thực thi và nội dung thuyết minh tương ứng cho từng kịch bản demo minh chứng:"),
    ("Ý nghĩa: Minh chứng mọi module con phần cứng đều hoàn hảo, vượt qua mọi góc kẹt số học biên.",
     "Mục đích: Xác nhận các khối chức năng RTL hoạt động độc lập chính xác, vượt qua các trường hợp kiểm thử giá trị biên số học."),
    ("Ý nghĩa: Chứng minh dòng chảy nhịp sóng Wavefront Skewing và cơ chế tích lũy Output-Stationary trong PE bằng dạng sóng trực quan.",
     "Mục đích: Minh họa trực quan dòng chảy dữ liệu nhịp sóng Wavefront Skewing và cơ chế tích lũy Output-Stationary của mảng PE trên dạng sóng tín hiệu."),
    ("Ý nghĩa: Minh chứng toàn bộ hệ thống SoC (CPU PicoRV32 + AXI Interconnect + Accelerator) thực thi firmware C thật và nhận dạng đúng ảnh MNIST.",
     "Mục đích: Chứng minh toàn bộ hệ thống SoC (CPU PicoRV32, bus AXI và bộ tăng tốc) thực thi đúng mã nhị phân firmware C và nhận dạng chính xác ảnh chữ số MNIST."),
    ("Ý nghĩa: Minh chứng thiết kế đã được biên dịch thành công thành bitstream thật, đóng Timing an toàn.",
     "Mục đích: Cung cấp bằng chứng thiết kế đã được biên dịch vật lý thành công, đạt đóng thời gian (timing closure) trên cả hai dòng FPGA."),
    ("Ý nghĩa: Khẳng định đề tài đã chuẩn bị đầy đủ mã nguồn Python giao tiếp và sẵn sàng nạp xuống phần cứng vật lý.",
     "Mục đích: Trình bày quy trình và công cụ tự động hóa giao tiếp phần cứng (UART HIL Suite) phục vụ giai đoạn thực nghiệm tiếp theo."),

    # 6. Speaker notes icon & formatting
    ("> 🎙️ **Speaker Notes**:", "> **Gợi ý trình bày (Speaker Notes)**:"),
    ("* 🖼️ **Hình ảnh minh họa đề xuất**:", "* **Hình ảnh minh họa trên slide**:"),
]

for src, dst in replacements:
    if src in text:
        text = text.replace(src, dst)
        print(f"[OK] Replaced: {src[:40]}...")
    else:
        print(f"[WARN] Not found: {src[:40]}...")

# Now refine the 19 Speaker Notes to natural, academic, modest tone
refined_notes = [
    # Slide 1
    ("Kính thưa quý Thầy Cô trong Hội đồng đánh giá tiến độ đồ án tốt nghiệp. Hôm nay, em xin phép được báo cáo tiến độ 50% của đề tài: 'Thiết kế và hiện thực bộ tăng tốc mạng nơ-ron chập dựa trên kiến trúc mảng tâm thu trên FPGA'. Trong giai đoạn này, đề tài đã hoàn thành trọn vẹn toàn bộ chu trình thiết kế vi mạch từ mô hình toán học, thiết kế RTL, tích hợp hệ sinh thái SoC RISC-V, kiểm chứng vi mạch đa tầng bit-true và tổng hợp thành công bitstream đạt đóng thời gian trên hai nền tảng FPGA DE2 và DE10-Standard.",
     "Kính thưa quý Thầy Cô trong Hội đồng đánh giá tiến độ đồ án tốt nghiệp. Hôm nay, em xin phép được báo cáo kết quả thực hiện mốc 50% của đề tài: 'Thiết kế và hiện thực bộ tăng tốc mạng nơ-ron chập dựa trên kiến trúc mảng tâm thu trên FPGA'. Nội dung báo cáo giữa kỳ hôm nay tập trung vào các kết quả đã đạt được từ mô hình giải thuật, thiết kế RTL mảng tâm thu, tích hợp hệ thống SoC cùng vi xử lý RISC-V, quy trình kiểm chứng mô phỏng bit-true và kết quả tổng hợp đóng thời gian thành công trên hai kit FPGA DE2 và DE10-Standard ạ."),

    # Slide 2
    ("Kính thưa Thầy Cô, khi đưa các mô hình Deep Learning xuống thiết bị nhúng biên, rào cản lớn nhất là hiện tượng Memory Wall. Với CPU thông thường, phần lớn thời gian bị lãng phí để nạp và lưu dữ liệu. Để giải quyết triệt để vấn đề này, đề tài xây dựng một bộ gia tốc mảng tâm thu 2D giúp tái sử dụng dữ liệu trực tiếp giữa các phần tử xử lý lân cận, kết hợp với định dạng số học INT8 để tối ưu hóa diện tích phần cứng mà vẫn bảo toàn độ chính xác của mạng nơ-ron.",
     "Kính thưa Thầy Cô, khi triển khai các mô hình mạng nơ-ron lên thiết bị phần cứng hạn chế tài nguyên, thách thức chính nằm ở hiện tượng nghẽn cổ chai bộ nhớ (Memory Wall), khi CPU tiêu tốn nhiều thời gian và năng lượng cho việc truyền dữ liệu. Để khắc phục điểm nghẽn này, đề tài lựa chọn kiến trúc mảng tâm thu 2D nhằm tăng cường tái sử dụng dữ liệu giữa các phần tử tính toán lân cận, kết hợp phương pháp lượng tử hóa INT8 để tiết kiệm tài nguyên logic mà vẫn bảo đảm độ chính xác phân loại của mô hình."),

    # Slide 3
    ("Đề tài đặt mục tiêu tự thiết kế 100% từ đầu một vi mạch gia tốc AI mảng tâm thu 8x8 với 64 PE song song, đóng gói giao tiếp bus AXI4-Lite chuẩn công nghiệp và tích hợp với vi xử lý mã nguồn mở RISC-V PicoRV32. Mục tiêu tiến độ 50% là hoàn thành thiết kế RTL, vượt qua kiểm chứng Bit-True và đóng timing thành công trên chip thật.",
     "Mục tiêu cụ thể của đề tài là tự hiện thực phần cứng bộ tăng tốc mảng tâm thu 8x8 gồm 64 PE bằng ngôn ngữ SystemVerilog, không sử dụng IP đóng gói sẵn từ nhà sản xuất; tích hợp giao tiếp chuẩn bus AMBA AXI4-Lite cùng vi xử lý mã nguồn mở RISC-V PicoRV32. Đến mốc 50% hiện tại, đề tài đã hoàn thành thiết kế RTL, vượt qua các bài kiểm chứng mô phỏng bit-true và tổng hợp đạt chỉ tiêu thời gian trên FPGA."),

    # Slide 4
    ("Về mặt toán học, giải thuật im2col giúp duỗi phẳng các cửa sổ trượt thành các cột ma trận, biến toàn bộ bài toán nhân chập thành phép nhân ma trận GEMM để tận dụng tối đa năng lực xử lý mảng. Đồng thời, kỹ thuật lượng tử hóa INT8 giúp tiết kiệm 75% bộ nhớ và giảm 80% diện tích bộ nhân silicon nhưng vẫn giữ vững độ chính xác 97.06% trên tập dữ liệu chuẩn MNIST.",
     "Về mặt giải thuật, phương pháp im2col biến đổi phép nhân chập Conv2D nhiều chiều thành phép nhân ma trận GEMM chuẩn, cho phép tận dụng tối đa năng lực tính toán song song của mảng. Đồng thời, định dạng số nguyên có dấu Signed INT8 giúp giảm 4 lần dung lượng lưu trữ trọng số và tiết kiệm tài nguyên bộ nhân phần cứng, trong khi độ chính xác phân loại trên tập dữ liệu chuẩn MNIST vẫn đạt 97.06%, tương đương mô hình số thực dấu phẩy động ban đầu."),

    # Slide 5
    ("Đây là sơ đồ kiến trúc tổng quan của toàn bộ hệ thống SoC. Trung tâm là vi xử lý RISC-V PicoRV32 kết nối qua trục bus AXI4-Lite Crossbar với bộ nhớ nội BRAM 32 KB, khối truyền thông UART và bộ tăng tốc AI mảng tâm thu 8x8. Toàn bộ thiết kế được phân lớp rõ ràng, đảm bảo tính mô-đun hóa cao.",
     "Đây là sơ đồ kiến trúc tổng thể của hệ thống SoC. Thành phần điều khiển trung tâm là vi xử lý RISC-V PicoRV32, kết nối qua bộ phân xử bus AMBA AXI4-Lite tới bộ nhớ BRAM 32 KB, khối ngoại vi UART và bộ tăng tốc mảng tâm thu 8x8. Kiến trúc được thiết kế theo cấu trúc module phân tầng, bảo đảm tính độc lập và thuận tiện cho việc kiểm thử cũng như mở rộng chức năng sau này."),

    # Slide 6
    ("Khác với kiến trúc Weight-Stationary của Google TPU đòi hỏi các cây cộng gom rất lớn ở ngõ ra, em lựa chọn kiến trúc Output-Stationary. Kết quả nhân chập được cộng dồn tại chỗ trong thanh ghi 32-bit của PE, dữ liệu trung gian không bao giờ phải đưa ra ngoài trong suốt quá trình nhân. Nhờ đó, đường dây định tuyến rất ngắn và diện tích logic được tối ưu hóa tối đa.",
     "Về cơ chế luồng dữ liệu, em lựa chọn kiến trúc Output-Stationary. Kết quả nhân tích lũy được lưu cố định trong thanh ghi 32-bit bên trong từng PE cho đến khi hoàn tất chuỗi nhân. Ưu điểm của phương pháp này là không cần cây cộng gom (Adder Tree) ở ngõ ra, giúp đường định tuyến giữa các phần tử ngắn hơn và giảm thiểu hiện tượng nghẽn dây khi tổng hợp lên FPGA."),

    # Slide 7
    ("Để đồng bộ dòng chảy dữ liệu trên mảng 2D, khối Skew Unit đóng vai trò làm trễ bậc thang: hàng i trễ i chu kỳ, cột j trễ j chu kỳ. Nhờ đó, dữ liệu chảy chéo dạng nhịp sóng nhịp nhàng, 64 bộ nhân PE hoạt động đồng thời 100% công suất mà không bị bất kỳ xung đột dữ liệu nào.",
     "Để đồng bộ thời điểm đến của dữ liệu trên mảng 2D, khối Skew Unit thực hiện tạo trễ dạng bậc thang: hàng thứ i trễ i chu kỳ, cột thứ j trễ j chu kỳ. Nhờ đó, dữ liệu di chuyển theo dạng đường chéo sóng nhịp (wavefront), bảo đảm tại mỗi chu kỳ xung nhịp, mỗi PE đều nhận đúng cặp toán hạng tương ứng mà không xảy ra xung đột dữ liệu."),

    # Slide 8
    ("Sau khi nhân chập trong PE, dữ liệu 32-bit đi qua khối lượng tử hóa để dịch bit tỉ lệ, kích hoạt hàm phi tuyến ReLU và đi qua mạch kẹp bão hòa Saturation Clamping. Mạch này ghìm chặt kết quả trong dải 8-bit [-128, +127], loại bỏ hoàn toàn nguy cơ lật bit đổi dấu làm sai lệch kết quả phân loại.",
     "Sau khi hoàn tất tích lũy trong PE, dữ liệu 32-bit được đưa qua khối lượng tử hóa để dịch bit tỉ lệ, áp dụng hàm kích hoạt phi tuyến ReLU và đi qua mạch kẹp bão hòa (Saturation Clamping). Mạch kẹp giữ kết quả chặt chẽ trong dải giá trị 8-bit từ -128 đến +127, tránh hiện tượng tràn số đổi dấu làm sai lệch kết quả phân loại của mạng nơ-ron."),

    # Slide 9
    ("Một điểm đột phá quan trọng ở phiên bản Gen-2 là em đã tích hợp 8 bộ Quantizer chạy song song và cơ chế nạp đóng gói 4 byte. Nhờ đó, pha đọc kết quả từ PE giảm từ 64 chu kỳ xuống chỉ còn 8 chu kỳ. Độ trễ tính toán của lõi giảm 60.2%, chỉ mất đúng 37 chu kỳ, và tốc độ toàn hệ thống SoC tăng vọt 4.4 lần so với phiên bản ban đầu.",
     "Kính thưa Thầy Cô, ở phiên bản ban đầu, qua việc đo đạc chu kỳ thực tế, em nhận thấy khâu đọc ma trận kết quả từ mảng PE tốn tới 64 chu kỳ do đọc tuần tự từng phần tử. Để khắc phục điểm nghẽn này, ở phiên bản Gen-2, em đã cải tiến hai điểm: thứ nhất là bố trí 8 bộ lượng tử hóa đọc song song theo hàng, và thứ hai là hỗ trợ cơ chế nạp dữ liệu gộp 4 byte INT8 vào một từ 32-bit. Cải tiến này giúp pha đọc kết quả giảm từ 64 chu kỳ xuống còn 8 chu kỳ; độ trễ tính toán của lõi giảm từ 93 xuống 37 chu kỳ; và thời gian thực thi toàn hệ thống SoC giảm 4.4 lần."),

    # Slide 10
    ("Để điều phối toàn hệ sinh thái, em tích hợp CPU RISC-V PicoRV32 theo chuẩn mở RV32I kết nối qua bus AMBA AXI4-Lite. Toàn bộ firmware C được viết bare-metal thao tác trực tiếp trên thanh ghi MMIO và biên dịch bằng toolchain chuẩn GNU GCC, đảm bảo tính linh hoạt tối đa.",
     "Để điều phối toàn bộ hoạt động của hệ thống, em tích hợp vi xử lý RISC-V PicoRV32 theo chuẩn mở RV32I kết nối qua bus AMBA AXI4-Lite. Phần mềm điều khiển được viết bằng ngôn ngữ C bare-metal, giao tiếp với phần cứng qua các thanh ghi ánh xạ bộ nhớ (MMIO) và được biên dịch bằng bộ công cụ chuẩn GNU GCC."),

    # Slide 11
    ("Kiến trúc tích hợp thanh ghi đếm chu kỳ độc lập REG_ACCEL_CYCLES giúp đo đếm chính xác thời gian mảng tâm thu thực thi. Đồng thời, mạch Busy-Gating trong phần cứng tự động chặn mọi thao tác ghi đè khi mảng đang tính toán, bảo vệ tuyệt đối tính an toàn của dữ liệu đường ống.",
     "Thiết kế tích hợp thanh ghi đếm chu kỳ phần cứng REG_ACCEL_CYCLES, cho phép đo chính xác thời gian mảng tâm thu thực thi độc lập với thời gian truyền thông bus. Đồng thời, mạch khóa Busy-Gating tự động từ chối các thao tác ghi của CPU khi mảng đang tính toán, nhằm ngăn ngừa việc ghi đè làm sai lệch dữ liệu đường ống."),

    # Slide 12
    ("Để đảm bảo tính đúng đắn tuyệt đối, em xây dựng quy trình kiểm chứng 3 tầng theo chuẩn công nghiệp: từ kiểm thử đơn vị từng module, kiểm thử độ bao phủ UVM 1.1c, đến đồng mô phỏng toàn hệ thống SoC. Mọi kết quả phần cứng đều được đối soát từng bit với mô hình Golden Reference viết bằng Python.",
     "Nhằm bảo đảm tính đúng đắn của thiết kế, em áp dụng quy trình kiểm thử phân tầng gồm 3 cấp độ: kiểm thử đơn vị từng khối RTL, kiểm thử giao thức và độ bao phủ tính năng UVM, và đồng mô phỏng toàn hệ thống SoC. Mọi kết quả ngõ ra phần cứng đều được so sánh bit-true (sai số bằng 0) so với mô hình tham chiếu Python."),

    # Slide 13
    ("Kết quả kiểm chứng tầng 1 ghi nhận toàn bộ 61/61 test đơn vị đều đạt Pass 100%. Ở tầng 2, bộ kiểm chứng UVM 1.1c đạt chỉ tiêu đóng độ bao phủ chức năng 100% trên toàn bộ 88 bins không gian tham số toán học và trạng thái bão hòa, khẳng định độ tin cậy tuyệt đối của lõi thiết kế.",
     "Kết quả kiểm chứng ở tầng 1 cho thấy tất cả 61/61 trường hợp kiểm thử đơn vị đều đạt yêu cầu. Ở tầng 2, bộ kiểm thử UVM đạt 100% độ bao phủ tính năng trên toàn bộ 88 bins không gian tham số toán học và các trạng thái bão hòa, xác nhận các khối chức năng hoạt động đúng theo đặc tả thiết kế."),

    # Slide 14
    ("Trên môi trường đồng mô phỏng SoC, hệ thống đã chạy hơn 3.8 triệu chu kỳ clock và hoàn thành xuất sắc toàn bộ 7 kịch bản ứng dụng AI. Nổi bật là Demo 3 khớp 100% với tầng Conv1 của PyTorch và Demo 6 nhận dạng chính xác ảnh chữ số viết tay số 7 của tập MNIST với độ tin cậy 69%.",
     "Trên môi trường đồng mô phỏng SoC, hệ thống đã chạy hơn 3.8 triệu chu kỳ xung nhịp và thực thi thành công 7 kịch bản kiểm thử. Tiêu biểu là Demo 3 khớp bit-true 100% với tầng tích chập Conv1 của mô hình PyTorch, và Demo 6 nhận dạng chính xác ảnh chữ số viết tay số 7 của tập MNIST với độ tin cậy đạt 69.4%."),

    # Slide 15
    ("Về mặt hiện thực phần cứng, trên chip Cyclone II của kit DE2, thiết kế mảng 8x8 chiếm 57.5% logic và tận dụng tối đa 64 bộ nhân DSP cứng. Phân tích thời gian TimeQuest cho thấy Setup Slack đạt dương +4.626 ns và Fmax đạt 65.04 MHz, đảm bảo hệ thống vận hành cực kỳ ổn định ở tần số 50 MHz mà không lo vi phạm thời gian.",
     "Về kết quả tổng hợp phần cứng trên chip Cyclone II của kit DE2, thiết kế chiếm 57.5% tài nguyên logic và sử dụng 64 bộ nhân DSP phần cứng. Báo cáo phân tích thời gian tĩnh TimeQuest ghi nhận Setup Slack đạt giá trị dương +4.626 ns và Fmax đạt 65.04 MHz, đáp ứng tốt yêu cầu xung nhịp danh định 50 MHz của bo mạch mà không xảy ra vi phạm thời gian."),

    # Slide 16
    ("Để chứng minh tính di động và khả năng mở rộng của kiến trúc, em đã tổng hợp cùng một mã nguồn RTL lên dòng chip hiện đại Cyclone V trên kit DE10-Standard. Thiết kế chỉ chiếm 19.8% ALMs, Setup Slack đạt tới +5.609 ns và Fmax đạt 69.49 MHz, khẳng định khả năng sẵn sàng đáp ứng cho các ứng dụng phức tạp hơn.",
     "Nhằm đánh giá tính di động của mã nguồn RTL, em đã tổng hợp cùng một thiết kế lên dòng chip Cyclone V trên kit DE10-Standard. Kết quả cho thấy thiết kế chỉ chiếm 19.8% tài nguyên ALMs, Setup Slack đạt +5.609 ns và Fmax đạt 69.49 MHz, cho thấy phần cứng còn dư địa tài nguyên lớn để mở rộng thêm các tính năng nâng cao."),

    # Slide 17
    ("Bảng số liệu benchmark chứng minh tính hiệu quả vượt bậc: Nhờ cơ chế đóng gói 4 byte và đọc song song 8 hàng, phiên bản Gen-2 đã giảm chu kỳ toàn hệ thống từ 8,484 chu kỳ xuống 1,920 chu kỳ, mang lại gia tốc 173.7 lần so với phần mềm CPU và thông lượng lõi đạt 1.38 GOPS ở xung nhịp 50 MHz.",
     "Bảng số liệu đo đạc thực tế thể hiện rõ hiệu quả của các cải tiến: Nhờ cơ chế đọc song song 8 hàng và nạp dữ liệu gộp 4 byte, phiên bản Gen-2 giảm chu kỳ toàn hệ thống từ 8,484 chu kỳ xuống 1,920 chu kỳ, mang lại tốc độ thực thi nhanh hơn 173.7 lần so với chạy phần mềm trên CPU và thông lượng tính toán lõi đạt 1.38 GOPS ở tần số 50 MHz."),

    # Slide 18
    ("Tóm lại, cho mốc báo cáo 50%, đề tài đã hoàn thành xuất sắc 100% khối lượng công việc đặt ra cho phần thiết kế vi mạch, kiểm chứng đa tầng và tổng hợp đóng timing trên FPGA. Trong 50% chặng đường còn lại, em sẽ tập trung vào việc nạp bitstream đo đạc trên kit thật, phân tích công suất tiêu thụ và hoàn thiện toàn bộ bản thảo luận văn 5 chương.",
     "Tổng kết giai đoạn 50%, đề tài đã hoàn thành các mục tiêu đề ra về mặt thiết kế RTL, kiểm chứng mô phỏng và tổng hợp đóng thời gian trên FPGA. Trong giai đoạn 50% tiếp theo, em sẽ tập trung vào việc nạp bitstream đo đạc thực nghiệm trên kit thật qua UART, ước lượng công suất tiêu thụ và hoàn thiện bản thuyết minh luận văn tốt nghiệp 5 chương."),

    # Slide 19
    ("Em xin chân thành cảm ơn quý Thầy Cô trong Hội đồng đã chú ý lắng nghe. Sau đây em xin phép được trình chiếu các minh chứng kiểm thử và demo các kết quả mô phỏng, tổng hợp trên phần mềm ạ!",
     "Em xin trân trọng cảm ơn quý Thầy Cô trong Hội đồng đã chú ý lắng nghe phần trình bày của em. Sau đây, em xin phép được trình chiếu các minh chứng kiểm thử và demo các kịch bản mô phỏng, tổng hợp trên phần mềm ạ!")
]

for src_note, dst_note in refined_notes:
    if src_note in text:
        text = text.replace(src_note, dst_note)
        print(f"[OK] Refined note: {src_note[:35]}...")
    else:
        print(f"[WARN] Note not found: {src_note[:35]}...")

with open(report_path, "w", encoding="utf-8") as f:
    f.write(text)

print("[SUCCESS] Refined report saved to BaoCao_TienDo_50_CNN_Systolic_SoC.md!")
