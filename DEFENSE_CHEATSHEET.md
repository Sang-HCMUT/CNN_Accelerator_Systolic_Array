# PHAO CỨU SINH BẢO VỆ KHÓA LUẬN TỐT NGHIỆP
## ĐỀ TÀI: THIẾT KẾ VÀ HIỆN THỰC BỘ TĂNG TỐC CNN MẢNG TÂM THU 8x8 TRÊN FPGA
> **Dành riêng cho sinh viên**: Bản hướng dẫn sống còn từ bản chất nguyên lý, kịch bản thuyết trình, giải thích trực quan đến 30 câu hỏi vấn đáp tử huyệt của Hội đồng chấm thi (Cập nhật chuẩn 8x8, DE2/DE10, minh bạch baseline & bộ đệm).
/grill-me
---

# PHẦN 1: BÀI THUYẾT TRÌNH 2 PHÚT (ELEVATOR PITCH)
*Khi bước lên bục bảo vệ, hãy hít thở sâu và nói dõng dạc đoạn này. Đây là khung xương sống giúp bạn định hình tâm lý vững vàng ngay từ phút đầu tiên:*

> "Kính thưa quý Thầy Cô trong Hội đồng chấm Luận văn tốt nghiệp,
> 
> Trong kỷ nguyên Trí tuệ Nhân tạo hiện nay, việc đưa các mô hình Deep Learning xuống các thiết bị nhúng biên (Edge AI) gặp phải một rào cản chí mạng: **Nút thắt cổ chai bộ nhớ (Memory Wall) của kiến trúc Von Neumann truyền thống**. Trong mạng CNN, phép tích chập Conv2D chiếm tới $90\%$ thời lượng tính toán. Nếu dùng CPU thông thường, hơn $90\%$ năng lượng và thời gian bị lãng phí chỉ để vận chuyển dữ liệu trên bus bộ nhớ.
> 
> Để giải quyết triệt để vấn đề này, đề tài của em đã nghiên cứu, thiết kế và hiện thực thành công một **Hệ thống trên Vi mạch (SoC) hoàn chỉnh tăng tốc mạng CNN** dựa trên **3 trụ cột công nghệ**:
> 1. **Về Toán học**: Ứng dụng giải thuật **`im2col`** biến đổi phép chập nhiều tầng thành phép nhân ma trận tổng quát **GEMM ($C = A \times B$)**, kết hợp kỹ thuật **Lượng tử hóa INT8** giảm $75\%$ dung lượng bộ nhớ mà vẫn giữ vững độ chính xác **$97.06\%$** trên tập MNIST.
> 2. **Về Kiến trúc Vi mạch**: Tự thiết kế từ đầu (from scratch) lõi **Mảng tâm thu 2D (Systolic Array) quy mô $8 \times 8$ (64 PEs song song)** theo cơ chế **Output-Stationary** với mạng trễ sóng **Wavefront Skewing ($0T..7T$)**, giúp dữ liệu được tái sử dụng tối đa (Data Reuse) giữa các PE, hoàn thành phép tính trong đúng **37 chu kỳ xung nhịp** ($K=8$ ở chế độ Gen-2 đọc song song 8 hàng) hoặc 93 chu kỳ ở chế độ Legacy.
> 3. **Về Tích hợp Hệ thống**: Tích hợp vi xử lý mã nguồn mở **RISC-V (PicoRV32)** qua trục bus chuẩn công nghiệp **AXI4-Lite 32-bit**, tổng hợp thành công bitstream trên **Altera Cyclone II (Kit DE2)** đạt tần số cực đại **$64.88\text{ MHz}$** và mở rộng trên **Intel Cyclone V (Kit DE10-Standard)** đạt **$62.24\text{ MHz}$**, cùng ứng dụng máy tính Host GUI vẽ số tay nhận dạng thời gian thực qua UART.
> 
> Toàn bộ hệ thống đã được kiểm chứng **100% Bit-True** qua 61/61 kiểm thử module đơn vị độc lập, bộ UVM 1.1c 88 bins chức năng, và chạy đồng mô phỏng SoC hoàn chỉnh. Sau đây em xin phép được trình bày chi tiết từng giai đoạn thực hiện."

---

# PHẦN 2: BẢN ĐỒ KHÁI NIỆM — "HIỂU BẢN CHẤT BẰNG HÌNH ẢNH ĐỜI THƯỜNG"

*Đừng cố nhớ từng dòng code! Hãy nhớ 6 hình ảnh ẩn dụ đời thường này:*

| Thuật Ngữ Vi Mạch | Bản Chất Toán Học | Ẩn Dụ Đời Thường Dễ Hiểu |
| :--- | :--- | :--- |
| **Phép Tích Chập Conv2D** | Trượt Kernel $3 \times 3$ qua ảnh, nhân từng cặp rồi cộng dồn (MAC). | Giống như cầm một chiếc **đèn pin nhỏ quét lần lượt từng góc** trên bức tranh lớn. |
| **Giải thuật `im2col`** | Trải phẳng các ô cửa sổ trượt thành các cột dọc ma trận. | Giống như **duỗi thẳng từng lát cắt** của bức tranh và xếp thành các cột đứng để đưa vào máy ép ma trận. |
| **Mảng Tâm Thu (Systolic Array)** | Dữ liệu được nhịp Clock "bơm" chuyền tay nhau giữa các PE lân cận. | Giống như một **đội lính cứu hỏa đứng xếp hàng chuyền tay nhau xô nước** dập lửa: Nước chỉ múc từ giếng 1 lần ở đầu hàng, các người sau chỉ việc chuyền tay, không ai phải chạy ngược về giếng múc lại! |
| **Output-Stationary (OS)** | Tích lũy $C_{ij}$ ghim cứng tại PE, trọng số $A$ trôi ngang, kích hoạt $B$ trôi dọc. | Giống như **người thợ xây ngồi yên 1 chỗ (kết quả ở yên trong PE)**, cát đá gạch (dữ liệu A, B) được băng chuyền đưa ngang qua, thợ cứ thế xây đắp dồn lên. |
| **Wavefront Skewing ($0T..7T$)** | Làm trễ dữ liệu đầu vào theo hình bậc thang: Hàng 0 trễ $0T$, Hàng 1 trễ $1T$,... Hàng 7 trễ $7T$. | Giống như **xếp hàng vào cửa soát vé so le hình bậc thang**: Người hàng sau bước vào chậm 1 bước nhịp để khi vào phòng chiếu không bị đụng đầu nhau! |
| **Lượng tử hóa INT8 (Quantization)** | Ép số thực `Float32` về số nguyên có dấu 8-bit $[-128, +127]$. | Giống như **đổi từ tiền đô la lẻ có nhiều số thập phân sang tiền xu tròn trĩnh**: Bỏ vừa một chiếc ví nhỏ hơn $4$ lần, đếm tiền nhanh hơn nhiều mà giá trị tài sản gần như không đổi. |
| **CPU PicoRV32 + AXI4-Lite** | CPU nạp ma trận vào BRAM qua MMIO, phát `start`, chờ `done`. | Giống như **ông Đội trưởng cầm bộ đàm ra lệnh**: Bấm nút "Bắt đầu làm việc", ngồi đợi 93 chu kỳ lính làm xong báo cờ "Xong việc", đội trưởng ra thu gom sản phẩm đi gửi bưu điện (UART). |

---

# PHẦN 3: TOP 30 CÂU HỎI TỬ HUYỆT CỦA HỘI ĐỒNG & CÂU TRẢ LỜI CHUẨN ĐIỂM 10

---

## NHÓM A: THẦY/CÔ CHUYÊN PHẦN CỨNG & VI MẠCH (DIGITAL IC / HARDWARE)

### Câu 1: Tại sao lại cần bộ Skewing làm trễ bậc thang $0T, 1T, ..., 7T$? Nếu nạp dữ liệu đồng thời ở chu kỳ $0T$ thì sao?
* **Bản chất**: Để đồng bộ nhịp sóng đường chéo (Wavefront Flow).
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô, trong mảng tâm thu 2D, dữ liệu $A$ truyền ngang từ cột này sang cột kế tiếp phải mất đúng 1 chu kỳ clock qua thanh ghi đệm; tương tự dữ liệu $B$ truyền dọc cũng mất 1 chu kỳ clock. 
  > Nếu ta nạp tất cả các hàng và cột cùng lúc tại $t=0$, thì $\text{PE}_{0,0}$ sẽ nhận đúng dữ liệu, nhưng các PE ở sâu hơn như $\text{PE}_{1,1}$ hay $\text{PE}_{7,7}$ sẽ nhận sai dữ liệu vì cặp dữ liệu tương ứng chưa kịp truyền tới nơi hoặc bị lệch pha! 
  > Bộ Skewing làm trễ hàng $i$ đi $i \times T$ chu kỳ và cột $j$ đi $j \times T$ chu kỳ để đảm bảo tại chu kỳ $t = k + i + j$, mọi $\text{PE}_{i,j}$ đều gặp đúng cặp dữ liệu $A[i][k]$ và $B[k][j]$ cần nhân chập ạ."*

### Câu 2: Tại sao em lại chọn kiến trúc Output-Stationary mà không dùng Weight-Stationary như Google TPU?
* **Bản chất**: Tiết kiệm diện tích logic và tối ưu cho FPGA tài nguyên nhỏ.
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô, Google TPU chọn Weight-Stationary vì chip của họ là ASIC cực lớn (hàng trăm triệu cổng), bộ nhớ đệm SRAM khổng lồ, họ muốn giữ nguyên trọng số để xử lý các lô ảnh Batch Size rất lớn.
  > Trong đề tài của em, mục tiêu là hướng tới thiết bị biên (Edge AI) chạy trên chip FPGA giá rẻ (Cyclone II chỉ có 18,752 LEs):
  > - Nếu dùng Weight-Stationary, mỗi PE phải có mạch định tuyến phức tạp và phải có một cây gom tổng (Adder Tree) ở ngõ ra rất cồng kềnh.
  > - Với **Output-Stationary**, thanh ghi tích lũy 32-bit nằm ngay trong PE, dữ liệu trung gian không bao giờ phải gửi ra ngoài cho đến khi hoàn tất. Thiết kế này giúp tiết kiệm tối đa diện tích cổng logic (chỉ tốn 17,230 LEs (51.9%) cho toàn bộ SoC mảng $8 \times 8$ trên DE2) và đường dây chạy ngắn nhất, giúp đạt Fmax cao hơn ạ."*

### Câu 3: Chu kỳ tính toán của mảng $8 \times 8$ ($K=8$) là bao nhiêu và tính từ công thức nào?
* **Bản chất**: Kiến trúc Gen-1 (đọc tuần tự 64 phần tử qua 1 Quantizer = 93 chu kỳ) và Nâng cấp Gen-2 (đọc song song 8 hàng qua 8 Quantizers = 37 chu kỳ).
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô:
  > 1. Thời gian tính toán thuần túy của mảng tâm thu kích thước $N \times N$ với chiều sâu nhân $K$ tuân theo công thức kinh điển: 
  >    $$T_{compute} = 3N + K - 2$$
  >    Với $N=8, K=8 \implies T_{compute} = 3(8) + 8 - 2 = 30\text{ chu kỳ}$.
  > 2. Trong hiện thực phần cứng thực tế:
  >    - **Ở phiên bản Gen-1 (Legacy)**: FSM nạp 1 chu kỳ, bơm luồng 8 chu kỳ, drain mảng 16 chu kỳ, đọc tuần tự từng phần tử qua 1 quantizer mất 64 chu kỳ, và kết thúc 2 chu kỳ $\implies$ Tổng cộng **93 chu kỳ**.
  >    - **Ở phiên bản Gen-2 (Đột phá mới)**: Nhận thấy 64 chu kỳ readout chiếm tới $68.8\%$ thời gian tính toán của lõi, em đã tích hợp **8 bộ Quantizer/ReLU song song** và hỗ trợ ghi theo hàng (Parallel Row Writeback) vào Buffer C. Nhờ đó, pha `ST_READOUT` rút ngắn từ 64 chu kỳ xuống **chỉ còn đúng 8 chu kỳ**!
  >    $$\implies T_{compute\_gen2} = 1\text{ (Clear)} + 8\text{ (Stream)} + 16\text{ (Drain)} + 8\text{ (Parallel Readout)} + 2\text{ (Flush)} + 2 = \mathbf{37\text{ chu kỳ xung nhịp}}!$$
  >    Thời gian tính toán của lõi giảm tới $60.2\%$, nâng thông lượng tính toán thuần lên **1,383 MOPS (1.38 GOPS)**. Đồng thời kết hợp với cơ chế nạp/đọc đóng gói 4 byte (Packed 4-INT8 Word Transfer), thời gian trễ end-to-end của toàn hệ thống SoC trong Demo 1 giảm từ **8,484 chu kỳ xuống 1,920 chu kỳ (tăng tốc 4.4 lần, nhanh gấp 173.7 lần CPU phần mềm)** ạ!"*

### Câu 4: Mạch kẹp bão hòa (Saturation Clamping) hoạt động thế nào và tại sao lại sống còn đối với AI?
* **Bản chất**: Chống hiện tượng tràn bit lật dấu (Wrap-around Overflow).
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô, thanh ghi tích lũy có độ rộng 32-bit. Sau khi nhân chập và dịch bit tỉ lệ, giá trị có thể vượt quá trần biểu diễn của số nguyên 8-bit $[-128, +127]$ (ví dụ giá trị là $+200$).
  > Nếu ta chỉ cắt thô 8 bit thấp (`acc[7:0]`), bit dấu sẽ bị đảo lộn khiến một số dương cực lớn bị biến thành số âm cực nhỏ (Wrap-around Overflow)! Hiện tượng này sẽ làm sụp đổ hoàn toàn độ chính xác của mạng AI.
  > Mạch Saturation Clamping trong khối `quantize_relu_unit` kiểm tra: Nếu kết quả $> +127$, nó ép cứng về $+127$; nếu $< -128$, nó ép cứng về $-128$. Em đã chứng minh điều này trên **Waveform 2 (Scenario 2)**: khi tổng tích lũy đạt $64516$, ngõ ra vẫn ghìm chuẩn xác tại $+127$ ạ."*

### Câu 5: Đường trễ dài nhất (Critical Path) của thiết kế nằm ở đâu và Fmax $64.88\text{ MHz}$ đạt được nhờ yếu tố nào?
* **Bản chất**: Phân tích báo cáo Static Timing Analysis (TimeQuest STA).
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô, theo báo cáo Timing Analyzer trong Quartus II:
  > - Đường trễ Critical Path dài nhất nằm ở tuyến từ ngõ ra bộ nhân Embedded Multiplier 9-bit đi qua bộ cộng tích lũy 32-bit và nạp vào thanh ghi `c_acc` trong phần tử `pe_gemm`.
  > - Thiết kế đạt Fmax **$64.88\text{ MHz}$** trên DE2 (Worst-Case Setup Slack đạt dương **$+4.588\text{ ns}$**, Hold Slack **$+0.391\text{ ns}$**, TNS = **$0.000\text{ ns}$** ở 50 MHz) và **$62.24\text{ MHz}$** trên DE10 (Setup Slack **$+3.932\text{ ns}$**) là nhờ:
  >   1. Toàn bộ thiết kế tuân thủ nguyên tắc thiết kế đồng bộ thuần túy (Pure Synchronous Design), không dùng chốt (No Latches), không dùng xung clock tự chế (No Gated Clocks).
  >   2. Chèn các thanh ghi đệm đường ống (Pipeline Registers) phân tầng giữa Buffer, Skew Unit và Quantization Unit, giúp chia nhỏ đường trễ tổ hợp ạ."*

### Câu 6: Tại sao mảng $8 \times 8$ lại bị bão hòa tài nguyên DSP trên chip Cyclone II EP2C20 (DE1), và giải pháp triển khai là gì?
* **Bản chất**: Giới hạn phần cứng silicon của chip mục tiêu và chiến lược nâng cấp kiến trúc.
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô: Chip Cyclone II EP2C20 trên Kit DE1 chỉ có tổng cộng **26 bộ nhân nhúng 9-bit Embedded Multiplier Blocks** (tương đương 52 khối nhân phần cứng 9-bit).
  > - Mảng $8 \times 8$ (64 PE) đòi hỏi tối thiểu **64 khối nhân phần cứng đồng thời**, vượt quá giới hạn vật lý 52 bộ nhân của chip EP2C20 trên DE1.
  > - Do đó, trong đồ án, em đã:
  >   1. **Lưu trữ (Deprecate) bản 4×4 trên DE1** như một mốc nghiên cứu cơ sở ban đầu.
  >   2. **Chuẩn hóa toàn bộ kiến trúc đề tài lên Mảng Tâm Thu $8 \times 8$ (64 PEs)** và triển khai thành công trên 2 nền tảng phần cứng chính:
  >      - **Terasic DE2 (Cyclone II EP2C35F672C6 - Nền tảng chính)**: Có 70 bộ nhân 9-bit, dùng 64/70 khối nhân (91.4%), đạt Fmax 64.88 MHz, peak 6.40 GOPS.
  >      - **Terasic DE10-Standard (Cyclone V 5CSXFC6D6F31C6N - Nền tảng mở rộng)**: Có 112 khối DSP đa năng, dùng 64/112 DSP (57.1%), đạt Fmax 62.24 MHz, peak 6.40 GOPS.
  >   Nhờ đó, toàn bộ kiến trúc RTL, firmware C và mô hình lượng tử hóa đạt sự đồng nhất 100% ở quy mô $8 \times 8$ ạ."*

### Câu 7: Tại sao bộ nhân cơ sở trong PE lại dùng số bù 2 Signed INT8 mà không dùng Unsigned?
* **Bản chất**: Trọng số mạng nơ-ron luôn có giá trị âm và dương.
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô, sau quá trình huấn luyện và tối ưu hóa (Backpropagation), trọng số của mạng nơ-ron phân bố quanh giá trị 0 theo phân phối chuẩn Gauss, có cả giá trị âm (ức chế nơ-ron) và dương (kích thích nơ-ron). Do đó, trọng số bắt buộc phải được biểu diễn bằng số nguyên có dấu (Signed Two's Complement) từ $-128$ đến $+127$ để phản ánh chính xác cấu trúc mạng ạ."*

---

## NHÓM B: THẦY/CÔ CHUYÊN AI & THUẬT TOÁN (DEEP LEARNING & NUMERICAL)

### Câu 8: Tại sao lại phải biến đổi `im2col`? Nhược điểm lớn nhất của nó là gì và em khắc phục ra sao?
* **Bản chất**: Đánh đổi giữa bộ nhớ và hiệu năng tính toán.
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô:
  > - **Lý do**: Phép tích chập 2D là trượt cửa sổ không gian, rất khó tạo đường ống song song. `im2col` duỗi phẳng các cửa sổ trượt thành các cột ma trận, biến toàn bộ bài toán Conv2D thành phép nhân ma trận chuẩn GEMM ($C = A \times B$). Nhờ đó phần cứng chỉ cần một mảng nhân ma trận duy nhất là xử lý được cả tầng Conv2D và tầng Fully-Connected!
  > - **Nhược điểm lớn nhất**: `im2col` làm phình to dung lượng bộ nhớ (Memory Overhead) do các điểm ảnh ở vùng trượt đè lên nhau bị sao chép lặp lại nhiều lần.
  > - **Cách khắc phục**: Em xây dựng **Cơ chế chia khối (Tiling Engine)** trong Giai đoạn 2: Hệ thống không duỗi toàn bộ ảnh cùng một lúc, mà chỉ cắt từng mảnh tile nhỏ kích thước $8 \times 8$ nạp vào tính toán lần lượt, tính đến đâu ghi đè đến đó, triệt tiêu hoàn toàn nỗi lo tràn RAM ạ."*

### Câu 9: Quá trình Lượng tử hóa sau huấn luyện (Post-Training Quantization - INT8) được thực hiện như thế nào?
* **Bản chất**: Ánh xạ tuyến tính miền số thực sang miền số nguyên có dấu.
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô:
  > 1. Trọng số $W$ và kích hoạt $X$ từ mô hình huấn luyện PyTorch dạng số thực `Float32` được tìm giá trị cực đại trị tuyệt đối: $S_w = \frac{\max(|W|)}{127}$ và $S_x = \frac{\max(|X|)}{127}$.
  > 2. Các giá trị được ép về số nguyên 8-bit theo công thức: 
  >    $$Q = \text{clamp}\left(\text{round}\left(\frac{X}{S}\right), -128, 127\right)$$
  > 3. Tỉ số Scale tích lũy được chuyển thành phép **dịch bit số học (Arithmetic Right Shift)** $x \ggg \text{shift\_bits}$ trong phần cứng để không phải dùng mạch chia số thực.
  > Kết quả kiểm nghiệm thực tế trên 10,000 ảnh tập MNIST cho thấy độ chính xác đạt **$97.06\%$**, chỉ giảm chưa tới $0.5\%$ so với mô hình Float32 ban đầu nhưng giảm $75\%$ dung lượng bộ nhớ ạ."*

### Câu 10: Nếu kích thước ma trận lớn hơn mảng $8 \times 8$ (ví dụ mạng MNIST có $K=9, N=576$ hoặc GEMM 16x16) thì phần cứng chạy thế nào?
* **Bản chất**: Kỹ thuật Tiling (Phân khối ma trận).
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô, hệ thống áp dụng kỹ thuật **Tiling Ma Trận**:
  > - Ma trận lớn $M \times N$ được cắt thành các khối con (Tiles) kích thước $8 \times 8$.
  > - CPU PicoRV32 điều phối nạp từng khối con $A_{tile}$ và $B_{tile}$ vào bộ đệm của mảng tâm thu.
  > - Đối với chiều sâu $K > 8$ (hỗ trợ phần cứng lên đến $K=16$), mảng tâm thu chạy nhiều vòng tích lũy cục bộ liên tiếp mà không xóa thanh ghi tích lũy (nhờ cờ điều khiển `sys_clear_acc`). Khi tích lũy đủ toàn bộ các block của chiều $K$, kết quả mới được lượng tử hóa và xuất ra ngoài ạ."*

### Câu 11: Cấu trúc mô hình CNN nhận dạng MNIST của đề tài gồm những tầng nào?
* **Bản chất**: Kiến trúc mạng CNN chuẩn rút gọn (Tiny-CNN).
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô, mô hình của em gồm:
  > 1. **Ngõ vào**: Ảnh xám kích thước $28 \times 28 \times 1$.
  > 2. **Tầng Conv2D**: 16 bộ lọc kích thước $3 \times 3$, ngõ ra $26 \times 26 \times 16$.
  > 3. **Tầng Kích hoạt**: ReLU (triệt tiêu số âm, giữ số dương).
  > 4. **Tầng Max Pooling**: Cửa sổ $2 \times 2$, giảm kích thước còn $13 \times 13 \times 16$.
  > 5. **Tầng Fully-Connected (Dense)**: Phân loại ra 10 chữ số từ 0 đến 9.
  > Toàn bộ các tầng Conv2D và Dense đều được thực thi trên cùng một lõi phần cứng Systolic GEMM của em ạ."*

---

## NHÓM C: THẦY/CÔ CHUYÊN HỆ THỐNG NHÚNG & VI XỬ LÝ (SOC & EMBEDDED)

### Câu 12: Tại sao đã có Bộ gia tốc mảng tâm thu rồi mà em vẫn phải tích hợp thêm CPU PicoRV32?
* **Bản chất**: Phân định rạch ròi vai trò Control-Path (Điều khiển) và Data-Path (Dữ liệu).
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô:
  > - Bộ gia tốc Systolic Array thuần túy là một khối **Data-Path** — nó cực mạnh trong việc tính toán nhân ma trận, nhưng nó không có khả năng tự giải mã định dạng file ảnh, không biết phân chia khối Tiling, và không thể tự nói chuyện với cổng UART hay máy tính.
  > - Nếu dùng máy trạng thái FSM cứng để điều khiển tất cả, phần cứng sẽ rất cồng kềnh và mỗi khi đổi cấu trúc mạng nơ-ron ta lại phải sửa RTL và nạp lại FPGA!
  > - Việc tích hợp **CPU mềm RISC-V PicoRV32** đóng vai trò **Control-Path (Bộ não)**: CPU chạy chương trình C điều phối, cấu hình siêu tham số, phân khối ma trận linh hoạt, còn mảng Systolic đóng vai trò **Cơ bắp** thực thi tính toán nặng. Đây chính là kiến trúc chuẩn công nghiệp của mọi chip AI SoC hiện đại (như NVIDIA GPU có CPU điều khiển, Google TPU có Host CPU) ạ."*

### Câu 13: Bus AXI4-Lite hoạt động như thế nào và cơ chế bắt tay (Handshake) diễn ra ra sao?
* **Bản chất**: Chuẩn giao tiếp công nghiệp của ARM/AMBA.
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô: Bus AXI4-Lite là phiên bản rút gọn của chuẩn AMBA AXI4, chuyên dùng cho giao tiếp thanh ghi điều khiển MMIO.
  > - Nó sử dụng cơ chế bắt tay 2 chiều thông qua cặp tín hiệu **`VALID`** (bên phát báo dữ liệu sẵn sàng) và **`READY`** (bên nhận báo sẵn sàng tiếp nhận).
  > - Giao dịch truyền dữ liệu chỉ diễn ra tại đúng chu kỳ clock mà cả `VALID = 1` và `READY = 1` cùng lúc. Cơ chế này loại trừ hoàn toàn nguy cơ mất mát dữ liệu hoặc đọc nhầm trạng thái khi hai khối phần cứng chạy lệch tốc độ ạ."*

### Câu 14: CPU PicoRV32 nói chuyện với Bộ gia tốc qua những địa chỉ bộ nhớ nào?
* **Bản chất**: Bản đồ thanh ghi ngoại vi (Memory-Mapped I/O Map).
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô, không gian địa chỉ được phân định rõ trong khối AXI Interconnect:
  > - Vùng `0x0000_0000 - 0x0000_3FFF` (16 KB): Bộ nhớ BRAM chứa mã lệnh và dữ liệu của CPU.
  > - Vùng `0x1000_0000 - 0x1000_07FF`: Bộ gia tốc Systolic Array 8x8, gồm:
  >   * `0x1000_0000`: Thanh ghi Điều khiển `CTRL_START` (bit 0), `BYPASS_RELU` (bit 1), `SHIFT_BITS` (bit 6:2).
  >   * `0x1000_0004`: Thanh ghi Trạng thái `STATUS_DONE` (bit 0), `STATUS_BUSY` (bit 1), `STATUS_ERROR` (bit 2).
  >   * `0x1000_0008`: Cấu hình chiều sâu ma trận `k_dim` (hỗ trợ $1 \le K \le 16$).
  >   * `0x1000_000C`: `REG_ACCEL_CYCLES` - Bộ đếm chu kỳ phần cứng (Hardware Cycle Counter đo chính xác thời gian PE).
  >   * `0x1000_0010`: `REG_ACCEL_VERSION` - Mã phiên bản IP phần cứng (`0x01080820` = v1.0, 8x8, INT8, INT32).
  >   * `0x1000_0100 - 0x1000_02FC`: Bộ đệm Ma trận A (Trọng số 8x16 = 128 words INT8).
  >   * `0x1000_0300 - 0x1000_04FC`: Bộ đệm Ma trận B (Kích hoạt 16x8 = 128 words INT8).
  >   * `0x1000_0500 - 0x1000_05FC`: Bộ đệm Ma trận C INT8 Post-ReLU (64 words INT8).
  >   * `0x1000_0600 - 0x1000_06FC`: Bộ đệm Ma trận C INT32 Raw Accumulators (64 words INT32 unquantized).
  > - Vùng `0x2000_0000`: Ngoại vi UART Console và điều khiển đèn LED/HEX trên bo mạch ạ."*

### Câu 15: Tín hiệu `trap` của CPU PicoRV32 là gì và tại sao trên ModelSim nó phải luôn bằng 0?
* **Bản chất**: Cơ chế tự vệ của CPU RISC-V khi xảy ra lỗi nghiêm trọng.
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô, trong kiến trúc PicoRV32, tín hiệu `trap` sẽ nhảy lên mức 1 nếu CPU gặp lỗi nghiêm trọng như: đọc phải mã lệnh không hợp lệ (Illegal Instruction), truy xuất vùng nhớ ngoài phạm vi phân bổ (Bus Error), hoặc chia cho 0. Khi `trap = 1`, CPU sẽ đóng băng toàn bộ hệ thống.
  > Trên dạng sóng **Waveform 3**, tín hiệu `/tb_soc_top/dut/trap` của em **nằm bẹp dí ở mức 0 suốt toàn bộ hơn 1.63 triệu chu kỳ xung nhịp mô phỏng qua trọn vẹn 7 kịch bản demo** (từ GEMM $8 \times 8$, Tiling $16 \times 16$, Conv2D `im2col`, MLP 2 tầng, Bộ chẩn đoán số học 5 bài test, đến suy luận MNIST và ngoại vi). Điều này chứng minh mã nguồn C biên dịch bằng GCC RISC-V chạy an toàn tuyệt đối, ngăn xếp stack không bị tràn và CPU sống khỏe mạnh 100% ạ."*

### Câu 16: Tại sao LED 7 đoạn HEX0 trên Kit DE2 / DE10 của em lại giải mã ra giá trị `0x40` để hiển thị số 0?
* **Bản chất**: Chuẩn phần cứng Active-Low của Kit Terasic DE1.
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô: Màn hình LED 7 đoạn trên bo mạch Terasic DE1 là loại **Active-Low (cực dương chung)**: Mức 0 là đèn sáng, mức 1 là đèn tắt.
  > - Số 0 gồm 6 thanh xung quanh viền $\{a, b, c, d, e, f\}$ sáng (mức 0), và thanh ngang ở giữa $\{g\}$ tắt (mức 1).
  > - Biểu diễn nhị phân 7 bit $\{g, f, e, d, c, b, a\}$ tương ứng là `7'b1000000`.
  > - Đổi sang hệ Hex chính là **`0x40`**! Dạng sóng Waveform 4 của em bắt được chính xác giá trị `hex0 = 0x40`, chứng minh khối `seven_seg_decoder` giải mã phần cứng chuẩn xác 100% ạ."*

### Câu 17: Giao tiếp UART 115200 Baud giữa FPGA và máy tính được thiết kế như thế nào? Tại sao cần bộ đồng bộ 2 tầng (2-Stage Synchronizer) ở chân `uart_rx`?
* **Bản chất**: Giải quyết hiện tượng bất định (Metastability) khi tín hiệu bất đồng bộ từ bên ngoài đi vào miền xung nhịp Clock của FPGA.
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô:
  > - Đường truyền RS-232 / UART chạy ở tốc độ 115200 Baud, với tần số clock hệ thống là 50 MHz $\implies$ một bit UART kéo dài $50,000,000 / 115,200 \approx 434$ chu kỳ clock (bộ chia Baud Rate Generator đếm từ 0 đến 433).
  > - Tín hiệu `uart_rx` từ cáp USB-to-UART cắm từ máy tính vào là một tín hiệu hoàn toàn bất đồng bộ (Asynchronous) so với xung nhịp 50 MHz trên chip FPGA. Nếu ta đưa trực tiếp tín hiệu này vào máy trạng thái FSM, hiện tượng vi phạm thời gian Setup/Hold (Metastability) sẽ xảy ra, làm flip-flop bị lơ lửng giữa mức 0 và 1, gây treo hệ thống!
  > - Khối `axi_uart` của em sử dụng một **Bộ đồng bộ 2 tầng Flip-Flop (2-Stage Synchronizer)**: Tầng 1 hấp thụ hiện tượng metastability, tầng 2 xuất ra tín hiệu số sạch sẽ, đảm bảo mạch nhận diện chính xác sườn xuống (Start bit) và cờ `rx_valid` mà không bao giờ bị glitch ạ."*

### Câu 18: Bộ giải mã hàm kích hoạt ReLU và dịch bit Quantization được thiết kế như thế nào? Tại sao cần cờ `bypass_relu`?
* **Bản chất**: Tính linh hoạt hỗ trợ đa dạng các tầng mạng (Convolution vs. Dense Output).
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô:
  > - Khối `quantize_relu_unit` nhận ngõ vào là giá trị tích lũy 32-bit `c_acc`. Nó thực hiện 3 thao tác theo thứ tự:
  >   1. **Dịch bit số học (Arithmetic Shift)**: $x = c\_acc \ggg \text{shift\_bits}$ (giữ nguyên bit dấu âm).
  >   2. **Hàm kích hoạt ReLU**: Nếu cờ `bypass_relu = 0`, các giá trị âm bị ép về 0: $x = (x < 0) ? 0 : x$.
  >   3. **Mạch kẹp bão hòa (Saturation Clamp)**: Ghim giá trị trong $[-128, +127]$.
  > - **Tại sao cần cờ `bypass_relu`?**: Trong một mạng CNN hoàn chỉnh:
  >   * Các tầng ẩn Conv2D cần ReLU để tạo tính phi tuyến cho mạng.
  >   * Nhưng tầng kết nối đầy đủ cuối cùng (Fully-Connected / Dense Layer) xuất điểm số phân loại (Logits) **tuyệt đối không được bật ReLU**, vì các điểm số âm mang ý nghĩa xác suất thấp, nếu ép về 0 sẽ làm sai lệch hoàn toàn kết quả Softmax! Cờ `bypass_relu = 1` cho phép bộ gia tốc xử lý trọn vẹn cả tầng Conv2D và tầng Output Logits ạ."*

### Câu 19: Em kiểm chứng tính đúng đắn (Verification) của toàn bộ hệ thống bằng phương pháp nào để khẳng định không có sai sót?
* **Bản chất**: Chu trình kiểm chứng công nghiệp (Gold Model Bit-True Matching & Hardware Stress Testing).
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô, em áp dụng quy trình kiểm chứng vi mạch chuẩn công nghiệp gồm 3 lớp bảo vệ:
  > 1. **Mô hình toán học đối chứng (Golden Model bằng Python)**: Em xây dựng thuật toán song song bằng NumPy, xuất ra các file test vector chuẩn `.hex` (`golden_output_int8.hex`).
  > 2. **Kiểm thử tự động Bit-True trên ModelSim**: Testbench nạp dữ liệu vào phần cứng RTL, tự động so sánh từng phần tử ngõ ra với Golden Model ở mức chu kỳ xung nhịp (Cycle-Accurate). Kết quả đạt **100% Khớp Bit (16/16 phần tử sai số Diff = 0)**.
  > 3. **Bộ kịch bản chịu tải góc kẹt (Stress Test Suite - Waveform 2)**: Chạy 6 kịch bản thử thách khắc nghiệt nhất: Phép nhân âm cực đại $(-128 \times -128)$, Tràn số bão hòa ép $+127$, Bỏ qua ReLU bảo toàn số âm $-100$, Ma trận toàn 0 chống trôi điểm, và chạy liên tục 2 ma trận không có chu kỳ nghỉ (0-idle cycle). Toàn bộ 6/6 kịch bản đều đạt trạng thái PASSED 100% trước khi em tiến hành nạp lên chip thật ạ."*

### Câu 20: Nếu được phát triển tiếp đề tài này lên cấp độ sản phẩm thương mại hoặc băng silicon (ASIC Tape-out), em sẽ cải tiến những điểm then chốt nào?
* **Bản chất**: Tầm nhìn kiến trúc và khả năng mở rộng quy mô (Scalability).
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô, để đưa đề tài từ mức nghiên cứu mẫu thử (PoC) lên sản phẩm thương mại hoặc băng silicon ASIC thực thụ, em sẽ tập trung vào 3 nâng cấp mang tính đột phá:
  > 1. **Tích hợp bộ điều khiển DMA (Direct Memory Access) đa kênh**: Thay vì để CPU PicoRV32 phải ghi từng word qua AXI4-Lite tốn chu kỳ clock, bộ điều khiển DMA sẽ tự động đẩy luồng dữ liệu (Stream) từ BRAM/DDR thẳng vào bộ đệm của mảng tâm thu với thông lượng cực đại qua giao thức AXI4-Stream.
  > 2. **Hỗ trợ định dạng số học linh hoạt (FP16 / Bfloat16 / INT4)**: Tích hợp bộ nhân đa chế độ (Multi-precision PE) để vừa hỗ trợ mạng CNN dạng INT8, vừa sẵn sàng cho các mô hình ngôn ngữ lớn (LLM / Transformer) dùng định dạng BF16.
  > 3. **Cơ chế nén ma trận thưa (Sparse Matrix Acceleration)**: Trong mạng AI sau khi lượng tử hóa, có tới $40\% - 60\%$ trọng số mang giá trị 0. Em sẽ bổ sung mạch Zero-Skipping để bỏ qua các phép tính nhân với số 0, giúp tăng tốc độ xử lý lên gấp đôi và tiết kiệm một nửa công suất tiêu thụ ạ."*

---

## NHÓM D: CÁC CÂU HỎI TỬ HUYỆT VỀ RANH GIỚI HỆ THỐNG & ĐỘ CHÂN THỰC ON-CHIP (DEFENSE CRITICAL QUESTIONS)

### Câu 21: Mạng CNN MNIST của em chạy ở đâu? Trên máy tính Host hay chạy 100% trên chip FPGA? Có phải Demo 6 và lệnh UART 'I' chỉ in sẵn số hoặc nhận số từ PC rồi hiện lên HEX0 không?
* **Bản chất**: Phân định ranh giới giữa Mô hình Tham chiếu Vàng (Python) và Bộ phân loại On-Chip (FPGA SoC), chứng minh không hardcode.
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô, đây là câu hỏi rất quan trọng và em xin được giải trình hoàn toàn minh bạch, có số liệu thực nghiệm chứng minh:
  > 
  > 1. **Đề tài có 2 cấp độ mô hình rõ ràng**:
  >    - **Mô hình CNN đầy đủ (Conv1 16x3x3 + MaxPool + FC10, đạt 97.06% trên 10,000 ảnh)**: Được chạy ở phần mềm Host Python để làm **Mô hình Tham chiếu Vàng (Golden Model)**. Mục đích là để tìm các hệ số lượng tử hóa Signed INT8 (PTQ Calibration), chứng minh thuật toán `im2col` + `tiling_engine` khớp bit 100%, và xuất test vector kiểm chứng từng tile phần cứng.
  >    - **Mô hình On-Chip chạy 100% trên FPGA (Edge INT8 Classifier, đạt 80.2% trên MNIST)**: Đây là mô hình nơ-ron thực sự chạy độc lập trên chip. Trọng số gồm ma trận $W_{64 \times 10}$ (đúng 640 bytes) được lưu thẳng trong bộ nhớ BRAM của FPGA.
  > 2. **Cơ chế chạy hoàn toàn bằng mảng tâm thu trên FPGA**:
  >    - Khi ảnh đầu vào 784 byte được nạp (hoặc từ mẫu nhúng trong Demo 6, hoặc truyền qua UART ở lệnh `'I'`), CPU PicoRV32 trích xuất 64 đặc trưng không gian ($8 \times 8$ pooling).
  >    - Sau đó, CPU phát lệnh cho **Mảng tâm thu phần cứng chạy liên tục 12 tile GEMM ($K=16$)** với chế độ `bypass_relu = 1`.
  >    - Mảng tâm thu tính toán tích vô hướng, ghi giá trị vào các bộ tích lũy 32-bit `REG_ACCEL_C_ACC`. CPU đọc ra để cộng dồn thành 10 giá trị logit của 10 chữ số (0 đến 9), và chạy thuật toán Argmax để tìm ra lớp có điểm cao nhất.   > 3. **Tầng Conv1 thực sự của mạng CNN MNIST chạy trực tiếp trên Accelerator (Demo 3)**:
   >    - Để khẳng định vững chắc bản chất "Bộ tăng tốc CNN", trong **Demo 3**, toàn bộ tầng tích chập Conv1 thật của mạng MNIST CNN (gồm **16 bộ lọc 3x3 INT8** = 144 trọng số thật từ mô hình PyTorch 97.06%, $K=9$) được đưa qua Mảng tâm thu phần cứng thông qua thuật toán `im2col` và Tiling Engine (16 tiles, 2,304 phép tính INT8 MAC).
   >    - Kết quả bản đồ đặc trưng (Feature Maps) ngõ ra sau khi qua mảng PE, cộng Bias, ReLU và lượng tử hóa dịch bit đạt **độ trùng khớp 100% Bit-True Parity (0 lỗi / 256 activations)** so sánh trực tiếp với mô hình PyTorch/NumPy.
   > 4. **Bằng chứng không hề hardcode hay lấy số từ PC**:
  >    - Trong Demo 6, hệ thống in trực tiếp 10 giá trị logit thực tế từ thanh ghi phần cứng (ví dụ: Chữ số 7 có điểm số $+9,793$, vượt trội so với các chữ số khác).
  >    - Với lệnh UART `'I'`, PC chỉ truyền 784 byte tensor ảnh thô kèm nhãn tham chiếu của PC để đối chiếu. Chip FPGA tự tính toán độc lập và in cả 2 dòng: `FPGA On-Chip Prediction: 7` và `Host PC Reference: 7`, sau đó chốt số dự đoán của FPGA lên màn hình LED 7 đoạn HEX0 ạ!"*

### Câu 22: Tại sao các phép tính `im2col`, Max-Pooling và cộng Bias không được làm bằng RTL trong phần cứng mà lại để cho CPU mềm/phần mềm xử lý?
* **Bản chất**: Triết lý thiết kế vi mạch AI chuẩn công nghiệp (The Google TPU Philosophy).
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô, đây là quyết định kiến trúc cốt lõi theo đúng triết lý của **Google TPU v1**:
  > 1. **Quy luật Amdahl**: Trong mạng CNN, phép nhân chập và nhân ma trận kết nối dày đặc (Conv/FC $\implies$ GEMM) chiếm **hơn $90\%$ tổng khối lượng tính toán số học**. Các khâu sắp xếp địa chỉ (`im2col`), tìm cực đại (Max-Pooling) và cộng vector Bias chỉ chiếm $<10\%$.
  > 2. **Tối ưu hóa diện tích vi mạch (Silicon Efficiency)**: Bằng cách dành $100\%$ khối nhân DSP và thanh ghi đường ống cho Mảng tâm thu GEMM Core, ta đạt được mật độ tính toán cực đại trên diện tích chip nhỏ (chỉ chiếm 51.9% chip Cyclone II DE2 / 15.1% ALMs trên Cyclone V DE10).
  > 3. **Tính linh hoạt phần mềm (Software-Defined AI)**: Nếu 'cứng hóa' `im2col` hoặc Pooling vào RTL, phần cứng sẽ bị khóa chết ở một kích thước cố định (ví dụ chỉ chạy được Kernel $3 \times 3$, Stride 1). Khi mạng đổi sang Kernel $1 \times 1, 5 \times 5$ hay Average Pooling, vi mạch sẽ vô dụng. Việc để CPU RISC-V điều phối `im2col` và pooling giúp hệ thống hỗ trợ mọi kiến trúc mạng CNN tùy ý mà không cần sửa một dòng code RTL nào ạ!"*

### Câu 23: Nút thắt cổ chai hệ thống nằm ở đâu? Tại sao em dùng bus AXI4-Lite mà không dùng AXI Full Burst hay DMA? Tỷ lệ thời gian Compute vs MMIO là bao nhiêu?
* **Bản chất**: Phân tích mô hình Roofline, hiện tượng Bức tường bộ nhớ (Memory Wall), và số liệu đo đạc tách biệt giữa Pure Compute ($T_{\text{compute}}$) và End-to-End ($T_{\text{end-to-end}}$).
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô, đây chính là **phát hiện khoa học cốt lõi nhất** của đề tài mà em đã thiết kế thanh ghi phần cứng `REG_ACCEL_CYCLES` (MMIO offset `0x00C`) để đo lường định lượng tách bạch:
  > 1. **Số liệu thực nghiệm đo đạc định lượng (Đồng mô phỏng SoC & Firmware C thật)**:
  >    - **Ma trận đơn lẻ $8 \times 8$ ($K=8$, 1,024 OPs)**:
  >      - **Chỉ số hệ thống cốt lõi (End-to-End Speedup)**: Tăng tốc **$38.5\times$** (8,525 chu kỳ phần cứng SoC vs 328,257 chu kỳ CPU). Đây là con số thực tế bao gồm toàn bộ quá trình CPU nạp dữ liệu, kích hoạt và đọc kết quả.
  >      - **Chỉ số lõi tính toán thuần (Pure Compute Speedup)**: Tăng tốc **$3,529.6\times$** (93 chu kỳ phần cứng vs 328,257 chu kỳ vòng lặp CPU). Em xin giải trình minh bạch: Baseline CPU PicoRV32 được biên dịch ở kiến trúc cơ bản `rv32i` (không bật khối nhân phần cứng `ENABLE_MUL`), do đó mỗi phép nhân INT8 của CPU phải gọi hàm `__mulsi3` của libgcc tiêu tốn trung bình $\approx 641$ chu kỳ/MAC. Con số $3,529\times$ là phép so sánh chính xác giữa mảng 64 PE song song với vòng lặp toán phần mềm thuần túy.
  >      - **Đính chính sâu sắc về vi kiến trúc (Bus Profiler Telemetry trên SoC)**: Phép đo Cycle-Accurate Bus Profiler trên SoC trong đúng cửa sổ 8,535 chu kỳ cho thấy nút thắt hệ thống **không phải do trễ giao tiếp của accelerator** (giao dịch AXI tới mảng chỉ mất 2-3 chu kỳ, tổng 201 giao dịch MMIO chỉ chiếm **~473 chu kỳ, tức ~5.5%**), mà bản chất là **nút thắt cổ chai điều phối của CPU (CPU Orchestration Bottleneck chiếm tới 94.4%)**:
  >        * **$57.6\%$ (4,919 chu kỳ, 1,661 giao dịch)**: CPU fetch mã lệnh và stack từ BRAM qua bus AXI crossbar (mất trung bình 3 chu kỳ/lệnh).
  >        * **$36.8\%$ (3,143 chu kỳ)**: CPU thực thi lệnh tổ hợp trong lõi (vòng lặp load, mask, tính địa chỉ offset $r \times 8 + c$, store — tiêu tốn tới $\approx 42$ chu kỳ lệnh cho mỗi byte dữ liệu).
  >        * **$\approx 5.5\%$ (473 chu kỳ, 201 giao dịch)**: Giao dịch MMIO nạp Buffer A, B, đọc Buffer C và polling cờ `STATUS_DONE`.
  >        * **$\approx 1.1\%$ (93 chu kỳ)**: Mảng tâm thu 64 PE thực sự bận tính toán.
  >        $$\implies$$ Như vậy, **$94.4\%$ thời lượng bị ngốn bởi CPU chuẩn bị dữ liệu và fetch lệnh**, chứng minh mảng tâm thu chạy cực nhanh và hệ thống đang khát dữ liệu từ CPU.
  >    - **Ma trận lớn $16 \times 16$ (Tiling 4 khối $8 \times 8$, $K=16$, 8,192 OPs)**:
  >      - Thời gian toàn hệ thống: **114,046 chu kỳ** (đạt **$26.5\times$** End-to-End Speedup so với ước tính CPU 3,032,928 chu kỳ chiếu theo 4x Tile 0).
  >      - Tính toán thuần phần cứng 4 tile: **404 chu kỳ** ($8.08\ \mu\text{s}$), đạt thông lượng thuần **$1,013.9\text{ MOPS}$ ($1.01\text{ GOPS}$)**. Chi phí MMIO chiếm **$99.6\%$**.
  >    - **Toàn bộ mạng suy luận MNIST (8 tiles)**: Tính toán thuần mảng PE chỉ mất **808 chu kỳ** ($16.16\ \mu\text{s}$, chiếm $\approx 0.4\%$), trong khi $99.6\%$ thời gian (205,100 chu kỳ) dành cho CPU trích xuất đặc trưng Pooling và giao dịch MMIO.
  > 2. **Bản chất kiến trúc (Định luật Amdahl & Bức tường bộ nhớ)**:
  >    - Phần cứng tính toán đã được tối ưu cực hạn gần chạm trần lý thuyết 6.4 GOPS, do đó theo định luật Amdahl, toàn bộ thời gian hệ thống bị chặn bởi băng thông nạp dữ liệu đơn từ (Single-word transfer) của bus AXI4-Lite.
  > 3. **Lộ trình nâng cấp công nghiệp có lộ trình khoa học (Gen-2 Roadmap)**:
  >    - **Đợt 1 (Đã hoàn thành)**: Khóa ghi Busy-gating trên buffer A/B, trả mã lỗi DECERR trên Interconnect, minh bạch hóa baseline CPU và tích hợp bộ đếm chu kỳ phần cứng `REG_ACCEL_CYCLES`.
  >    - **Đợt 2 (Tối ưu phần mềm & đóng gói dữ liệu - Tăng 3-4x End-to-End)**: 
  >      * Ghi/đọc đóng gói **4 INT8 / từ 32-bit (Packed Word)** kết hợp unroll vòng lặp firmware $\implies$ giảm 4 lần số lần lặp của CPU.
  >      * Đọc ra song song theo hàng bằng **8 bộ Quantizer song song** $\implies$ giảm thời gian xả ma trận C từ 64 chu kỳ xuống 8 chu kỳ (latency lõi giảm từ 93 xuống $\approx 37$ chu kỳ).
  >      * Biên dịch firmware với cờ tối ưu `-O2` và giảm chi phí fetch lệnh.
  >    - **Đợt 3 (Đột phá kiến trúc - Tăng 12-17x với DMA)**:
  >      * Tích hợp **bộ điều khiển DMA Master** ngay trong Accelerator: Accelerator tự phát lệnh đọc A/B từ BRAM và ghi C về BRAM, CPU chỉ việc ghi descriptor điều khiển. Giải phóng hoàn toàn CPU khỏi đường dữ liệu ($94.4\%$ thời gian), đưa tổng chu kỳ từ $8,500$ xuống chỉ còn $\approx 500 - 700$ chu kỳ/tile!
  >    - **Đợt 4 (Chồng lấp & Scaling)**:
  >      * Áp dụng **Bộ đệm kép Double-Buffering (Ping-Pong A/B/C)**: nạp tile $n+1$ song song trong khi mảng đang tính tile $n$.
  >      * Chuyển ma trận đệm sang **Multi-Bank Block RAM** khi mở rộng lên mảng $16 \times 16$ để tiết kiệm tài nguyên Logic Elements trên FPGA ạ."*

### Câu 24: Bảng số liệu tổng hợp $8 \times 8$ trên Kit DE10-Standard (Cyclone V) là số liệu thật hay ước lượng? Fmax và tài nguyên ALM đo được là bao nhiêu?
* **Bản chất**: Báo cáo tổng hợp vật lý thực nghiệm trích xuất từ Quartus Prime Lite 20.1.
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô, toàn bộ số liệu của cấu hình $8 \times 8$ trên Kit Terasic DE10-Standard (chip Cyclone V `5CSXFC6D6F31C6`) là **số liệu tổng hợp vật lý thực tế 100% từ Quartus Prime Lite 20.1** (trong thư mục `synthesis_soc_de10/output_files/` của dự án):
  > - **Tài nguyên Logic**: Sử dụng đúng **6,308 ALMs / 41,910 (chiếm 15.1%)**.
  > - **Thanh ghi nội**: **7,062 registers**.
  > - **Bộ nhớ Block RAM**: **266,752 bits (chiếm 4.7%)** tương đương 32.5 KB cho bộ nhớ CPU SoC.
  > - **Khối nhân phần cứng DSP**: Sử dụng đúng **64 / 112 DSP Blocks (57.1%)** cho 64 PE của mảng $8 \times 8$.
  > - **Thời gian và Fmax (theo báo cáo TimeQuest `soc_top_de10.sta.summary`)**:
  >   * Ở điều kiện xấu nhất Slow Model 1100mV 85°C: Worst-Case Setup Slack đạt dương **`+3.932 ns`** ở 50 MHz, Hold Slack **`+0.206 ns`**, TNS = **`0.000 ns`**, tương đương $F_{max} = \mathbf{62.24\text{ MHz}}$.
  >   * Ở điều kiện Fast Model 1100mV 0°C: Setup Slack đạt **`+10.140 ns`**, tương đương $F_{max} = \mathbf{101.4\text{ MHz}}$.
  > 
  > Điểm nổi bật nhất về mặt khoa học: Khi nâng quy mô tính toán lên gấp 4 lần ($16 \to 64$ PEs), $F_{max}$ trên tiến trình 28nm hầu như được bảo toàn ($64.14 \to 62.18\text{ MHz}$, chỉ giảm $3\%$). Điều này chứng minh tính ưu việt của kiến trúc định tuyến lân cận (Nearest-Neighbor) của mảng tâm thu ạ!"*

### Câu 25: Môi trường kiểm chứng UVM 1.1c của em đạt mức độ nào? Có đáp ứng được tiêu chuẩn công nghiệp không?
* **Bản chất**: Cấu trúc phân tầng hoàn chỉnh của UVM, giải pháp thích ứng bản quyền công cụ học thuật, và độ bao phủ toàn dải không gian toán học.
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô:
  > 1. **Cấu trúc UVM hoàn chỉnh đầy đủ thành phần**: Thư mục `uvm_verify/` của em hiện thực đầy đủ kim tự tháp UVM chuẩn công nghiệp gồm: `gemm_sequence_item`, `gemm_sequencer`, `gemm_driver`, `gemm_monitor`, `gemm_scoreboard` (đối soát thẻ `trans_id` và so khớp Bit-True), `gemm_coverage` và các lớp Test (`gemm_directed_test`, `gemm_random_test`, `gemm_stress_test`).
  > 2. **Bao phủ toàn dải K=1..16 và kiến trúc chuẩn Passive Monitor**:
  >    - Sequence item random hóa toàn dải $K \in [1..16]$, kiểm chứng thành công cả biên tối thiểu $K=1$ (chuyển FSM tức thời) và biên tối đa $K=16$ ($100\%$ dung lượng RAM bộ đệm).
  >    - Tuân thủ nguyên lý UVM: `gemm_monitor` thuần túy Passive (Listen-only), chuyển toàn bộ hành vi quét bus đọc kết quả về cho `gemm_driver`.
  >    - Tích hợp các bộ SystemVerilog Assertions (SVA) kiểm tra giao thức thời gian thực: cấm kích `start` khi `busy`, cấm ghi bộ nhớ khi đang tính toán, và kiểm tra phạm vi $K$.
  > 3. **Giải pháp kỹ thuật thích ứng môi trường học thuật**:
  >    - Cấu hình cờ `+define+UVM_NO_DPI` để chạy UVM SystemVerilog thuần túy trên ModelSim ASE mà không bị lỗi thư viện C.
  >    - Khối `gemm_coverage` tự động thu thập phân bố kích thích Signed INT8, ReLU, Shift bits và dải $K$-dimension (đo riêng $K=1$, $K=16$, $K=2..15$).
  > 4. Kết quả: Toàn bộ 81 giao dịch kiểm thử qua 3 bộ test đều đạt **Pass Rate 100% với 0 lỗi mismatch** ạ!"*

### Câu 26: Thiết kế của em đã được kiểm chứng như thế nào để đảm bảo đủ khả năng chạy ổn định trên FPGA thật?
* **Bản chất**: Chiến lược kiểm chứng đa tầng (Multi-tier Verification Hierarchy) kết hợp giải pháp khử siêu ổn định (Metastability) phần cứng.
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô, thiết kế của em đã vượt qua quy trình kiểm chứng 4 tầng nghiêm ngặt trước khi nạp bitstream lên kit Altera DE1:
  > 1. **Tầng 1 & 2 - Core Level (SV & UVM)**: Kiểm chứng tính đúng đắn toán học Bit-True $100\%$ trên 81 giao dịch UVM và các kịch bản cực đoan.
  > 2. **Tầng 3 - SoC Hardware/Software Co-Simulation (`tb_soc_top.sv`)**: Chạy gần 2 triệu chu kỳ đồng hồ với 305,735 lệnh CPU RISC-V PicoRV32 khởi động từ firmware BRAM thật, giao tiếp qua bus AXI4-Lite, điều khiển mảng tâm thu nhận diện chính xác ảnh chữ số MNIST (số 7) với độ tin cậy $69\%$ và xuất dữ liệu qua UART.
  > 3. **Tầng 4 - Khử hiện tượng siêu ổn định (Metastability) trên FPGA vật lý**:
  >    - Tích hợp mạch đồng bộ Reset 2 tầng AASD (Asynchronous Assert, Synchronous Deassert) trong `soc_top.sv`: Đảm bảo khi ấn nhả nút bấm cơ khí `KEY[0]` (`PIN_R22`), xung reset được xác lập tức thời nhưng giải phóng đồng bộ theo đúng sườn xung nhịp 50 MHz, triệt tiêu hoàn toàn vi phạm Reset Recovery/Removal Timing trên toàn bộ 3,403 thanh ghi.
  >    - Tích hợp 2-stage Flip-Flop Synchronizer trên đường truyền `uart_rx` trong `axi_uart.sv`.
  > 4. **Đóng ràng buộc thời gian (Timing Closure)**: Phân tích TimeQuest STA với file SDC đạt tần số $F_{max} = 64.14\text{ MHz} > 50\text{ MHz}$ với Setup Slack dương $+4.41\text{ ns}$, Hold Slack dương $+0.445\text{ ns}$, không có đường trễ unconstrained ạ!"*


### Câu 25: Môi trường kiểm thử UVM của em đã đạt mức Sign-off công nghiệp chưa? Simulator ModelSim ASE có hạn chế gì về SVA và Functional Coverage?
* **Bản chất**: Hiểu rõ sự khác biệt giữa công cụ miễn phí (ModelSim ASE) và môi trường EDA thương mại (QuestaSim / Synopsys VCS / Cadence Xcelium).
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô, em xin giải trình hoàn toàn minh bạch về ranh giới kiểm chứng giữa môi trường học thuật và tiêu chuẩn Tape-out công nghiệp:
  > 
  > 1. **Về SystemVerilog Assertions (SVA) & Cảnh báo `vsim-8311`**:
  >    - Simulator ModelSim Starter Edition (ASE) là bản miễn phí nên nhà sản xuất Mentor Graphics cố tình vô hiệu hóa engine thực thi **Concurrent Assertions (`assert property`)**, phát ra cảnh báo `vsim-8311`.
  >    - Để đảm bảo tính đúng đắn ngay trên ModelSim ASE, em đã thiết kế **Kiến trúc Kiểm tra Hai Tầng (Dual-Tier Assertion Architecture)**:
  >      * **Tầng 1 (Procedural/Immediate Assertions)**: Được viết trực tiếp trong các khối `always @(posedge clk)` và `always @(negedge rst_n)` trong [`gemm_if.sv`](file:///e:/DATN/CNN_Systolic_Architecture/uvm_verify/gemm_if.sv). Toàn bộ các quy tắc: độ rộng xung `start`/`done` đúng 1 chu kỳ, cấm ghi buffer khi `busy`, công thức trễ FSM chính xác từng chu kỳ, và tính bất động (`quiescence`) khi reset đều được kiểm tra thực sự trên mọi nhịp clock.
  >      * **Tầng 2 (Formal Concurrent SVA)**: Giữ nguyên các property chuẩn IEEE 1800 để sẵn sàng biên dịch và ký duyệt (Sign-Off) khi chạy trên QuestaSim hoặc Synopsys VCS.
  > 2. **Về Độ bao phủ Tính năng (Functional Coverage - 39 Bins)**:
  >    - ModelSim ASE cũng hạn chế khối lệnh `covergroup` (cảnh báo `vlog-2186`). Do đó, em đã triển khai bộ thu thập thống kê phần mềm chuyên dụng trong [`gemm_coverage.sv`](file:///e:/DATN/CNN_Systolic_Architecture/uvm_verify/gemm_coverage.sv), bao phủ trọn vẹn **39 bin chức năng 1 chiều**: mọi chiều $K \in [1..16]$, mọi mức dịch `shift_bits` $[0..8]$, chế độ ReLU/Bypass, giá trị cực trị $\pm 128$, và 4 chế độ bão hòa (True Saturation/Clamping) dựa trên giá trị Accumulator thực tế.
  >    - Đối với tiêu chuẩn Sign-Off công nghiệp hoàn chỉnh, bước tiếp theo là khai báo **Cartesian Cross-Coverage** (ví dụ $16 \text{ (K)} \times 9 \text{ (Shift)} \times 2 \text{ (ReLU)} = 288$ cross bins) trên QuestaSim.
  > 3. **Độ tin cậy cốt lõi**: Toàn bộ kết quả dữ liệu ngõ ra, mạch Clocking Block chống race condition, tính năng ngắt reset giữa chừng, và Bit-True Golden Model đã được kiểm chứng 100% khớp tuyệt đối qua hàng trăm ngàn chu kỳ mô phỏng ạ!"*

---

### Câu 27: Tại sao các bộ đệm Matrix Buffer A, B, C lại tổng hợp ra Flip-Flops và MUX (Distributed Logic) thay vì Block RAM M4K/M10K?
* **Bản chất**: Xung đột giữa số lượng cổng đọc đồng thời (Concurrent Multi-port Read) và giới hạn 1-2 cổng vật lý của khối Block RAM.
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô, đây là một bài toán đánh đổi kiến trúc rất sâu sắc:
  > 1. **Nguyên nhân kỹ thuật**: Khối Block RAM nhúng M4K trên Cyclone II hay M10K trên Cyclone V chỉ là bộ nhớ Dual-Port (tối đa 2 cổng truy xuất độc lập cùng lúc). Trong khi đó, để duy trì nhịp sóng mảng tâm thu $8 \times 8$ chạy mượt mà, tại mỗi chu kỳ clock bộ Skewing đòi hỏi phải **đọc đồng thời 8 phần tử của 8 hàng Buffer A và 8 phần tử của 8 cột Buffer B**.
  > 2. **Hệ quả tổng hợp (Synthesis Result)**: Do không thể nhét 8 cổng đọc đồng thời vào 1 khối M4K đơn lẻ, trình biên dịch Quartus Fitter buộc phải phân rã ma trận đệm thành các thanh ghi Flip-Flops phân tán kết hợp với các cây MUX dồn kênh lớn.
  >    - Điều này giải thích tại sao trên chip Cyclone II DE2, thiết kế tiêu thụ **17,230 LEs (51.9%)** và **9,038 registers**, trong khi bộ nhớ Block RAM chỉ ghi nhận **264,192 bits** (dành trọn vẹn cho 32 KB RAM chương trình của CPU PicoRV32 và 2 khối register file).
  > 3. **Giải pháp mở rộng cho mảng $16 \times 16$ (Gen-2 Roadmap)**: Khi nâng lên mảng $16 \times 16$, nếu tiếp tục dùng Flip-Flop thì số lượng LEs sẽ bùng nổ vượt quá diện tích FPGA. Giải pháp kiến trúc của em là **Phân mảnh bộ đệm thành cấu trúc Multi-Bank RAM**: chia Buffer A thành 16 bank M4K độc lập (mỗi hàng một bank riêng), nạp dữ liệu đồng bộ qua thanh ghi đọc 1 chu kỳ trễ, giúp tiết kiệm tới hơn $60\%$ diện tích logic ạ."*

### Câu 28: Bộ Lượng tử hóa Quantizer dùng dịch bit số học (Arithmetic Right Shift - Truncation) hay làm tròn đối xứng (Symmetric Rounding)? Vì sao độ chính xác 97.06% vẫn được bảo toàn?
* **Bản chất**: Tối ưu hóa đường trễ tới hạn (Critical Path Timing Closure) và bản chất chịu lỗi (Noise Tolerance) của mạng nơ-ron.
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô, em xin giải trình cụ thể về khối `quantize_relu_unit`:
  > 1. **Bản chất RTL**: Trong mã nguồn phần cứng, khối lượng tử hóa thực hiện phép dịch bit số học bảo toàn dấu `acc >>> shift_bits` kết hợp mạch kẹp bão hòa Saturation Clamping $[-128, +127]$. Đây về mặt toán học là phép chia số nguyên làm tròn xuống (Floor Truncation) chứ không dùng bộ cộng làm tròn đối xứng (Round-to-Nearest).
  > 2. **Lý do kiến trúc (Timing Closure)**: Nếu triển khai làm tròn đối xứng chuẩn, phần cứng phải cộng thêm một lượng bù $+ (1 \ll (\text{shift}-1))$ trước khi dịch bit. Việc chèn thêm một bộ cộng 32-bit nối tiếp ngay sau bộ nhân PE và trước mạch kẹp sẽ làm kéo dài đường trễ Critical Path, khiến thiết kế không thể đóng Timing ở mức Fmax $64.88\text{ MHz}$. Việc dùng phép dịch bit thuần túy không tốn thêm cổng cộng nào, giúp tín hiệu đi thẳng vào mạch kẹp bão hòa trong đúng 1 chu kỳ clock.
  > 3. **Bảo toàn độ chính xác 97.06%**: Trong mạng Tiny-CNN cho tập MNIST, sai số giữa Truncation và Rounding chỉ tối đa $1\text{ LSB}$. Mạng nơ-ron nhân tạo có tính chất lọc nhiễu tự nhiên rất mạnh, nên sai số $1\text{ LSB}$ ở các tầng ẩn hoàn toàn không ảnh hưởng tới cực đại tương đối của các logits ở tầng cuối cùng. Kết quả thực nghiệm kiểm thử trên 10,000 ảnh MNIST cho thấy độ chính xác đạt $97.06\%$, hoàn toàn không suy giảm so với mô hình tham chiếu ạ."*

### Câu 29: Ranh giới kiểm chứng giữa UVM Functional Coverage (100%, 88 Bins) và Code Coverage? Tại sao cờ `ENABLE_CODE_COV` trong script lại tắt?
* **Bản chất**: Minh bạch về license công cụ học thuật (ModelSim Altera Starter Edition ASE) và phương pháp luận kiểm chứng vi mạch.
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô, em xin báo cáo hoàn toàn trung thực về môi trường kiểm thử:
  > 1. **Hạn chế của License công cụ miễn phí**: Bản quyền ModelSim Altera Starter Edition (ASE) đi kèm bộ Quartus miễn phí không bao gồm tính năng **Code Coverage thương mại** (thiếu license `msimcoverage` vốn chỉ có trên Mentor QuestaSim hoặc Synopsys VCS). Vì vậy trong script `run_code_coverage.do`, biến `ENABLE_CODE_COV` được đặt bằng 0 để tránh trình mô phỏng báo lỗi dừng đột ngột.
  > 2. **Bù đắp bằng Functional Coverage chuẩn UVM (88 Bins, Pass 100%)**: Thay vì đo Code Coverage thụ động, em tự thiết kế bộ thu thập thống kê kiểm thử chức năng chuyên sâu trong `gemm_coverage.sv` bao phủ trọn vẹn **88 bins chức năng**:
  >    - Chiều sâu ma trận toàn dải $K \in [1..16]$ (bao gồm biên $K=1$, $K=16$ và dải trung gian).
  >    - Dải dịch bit `shift_bits` $[0..31]$.
  >    - Chế độ kích hoạt ReLU bật/tắt (`bypass_relu`).
  >    - Kiểm thử các giá trị cực trị $\pm 128$, số 0, số âm cực đại và 4 trạng thái kẹp bão hòa Saturation.
  > 3. **Bộ kiểm thử đơn vị Unit Test 52/52 checks**: Kiểm chứng độc lập từ PE cơ sở, bộ Skewing, Quantizer, các Buffer A, B, C, FSM Controller cho đến bộ giải mã 7 đoạn, đảm bảo không có ngóc ngách logic nào bị bỏ sót ạ."*

### Câu 30: Cơ chế bảo vệ ghi (Write Protection / Busy-Gating) và phân giải địa chỉ (Address Decoding) của AXI Interconnect hoạt động như thế nào?
* **Bản chất**: Cơ chế phòng vệ chống tương tranh ghi đè (Race Condition) và kiến trúc bus tối giản cho bare-metal SoC.
* **Trả lời chuẩn**:
  > *"Dạ thưa Thầy/Cô:
  > 1. **Cơ chế Busy-Gating bảo vệ bộ đệm**: Trong `systolic_gemm_axi_lite.sv`, toàn bộ các tín hiệu ghi dữ liệu ma trận `core_wr_a_en`, `core_wr_b_en` và lệnh khởi động `core_start` đều được chốt khóa bằng điều kiện `!core_busy`. Nếu CPU vô tình gửi lệnh ghi khi mảng tâm thu đang trong quá trình tính toán, giao dịch ghi sẽ bị phần cứng từ chối an toàn, ngăn chặn tuyệt đối nguy cơ làm sai lệch dữ liệu đang chạy đường ống.
  > 2. **Phân giải địa chỉ của AXI Interconnect**: Khối `axi_interconnect.sv` giải mã 4-bit MSB `addr[31:28]` (`0x0` -> RAM, `0x1` -> Accelerator, `0x2` -> UART). Với các địa chỉ chưa ánh xạ, bộ giải mã fallback an toàn về Slave 0 (RAM). Trong hệ thống SoC vi điều khiển bare-metal, cách tiếp cận này tối ưu diện tích logic (chỉ tốn ~150 LEs cho toàn bộ Crossbar Interconnect) và tránh bị treo bus CPU khi gặp con trỏ trôi.
  > 3. **Lộ trình hoàn thiện IP thương mại (Gen-2 Roadmap)**: Trong phiên bản tiếp theo, Interconnect sẽ được bổ sung một FSM tạo lỗi chuyên dụng để xuất mã lỗi chuẩn AXI `s_axi_rresp = 2'b11` (DECERR) và bẫy ngoại lệ Bus Trap về CPU khi truy cập vùng nhớ cấm ạ."*

---

# PHẦN 4: CHIẾN LƯỢC TÂM LÝ & "CÂU NÓI MA THUẬT" KHI BỊ BÍ

Khi đứng trước Hội đồng, nếu bạn gặp một câu hỏi quá sâu, quá hóc búa hoặc bạn đột ngột bị "khựng lại" trong vài giây, **tuyệt đối không im lặng quá 5 giây và không trả lời bừa**! Hãy dùng ngay 3 câu nói ma thuật sau:

### Câu ma thuật 1 (Khi chưa nghe rõ hoặc cần 10 giây để suy nghĩ):
> *"Dạ thưa Thầy/Cô, câu hỏi của Thầy/Cô rất hay và chạm đúng vào bản chất kỹ thuật ạ. Cho phép em xin được nhắc lại câu hỏi để đảm bảo em hiểu đúng ý của Thầy/Cô: Thầy/Cô đang quan tâm đến [nhắc lại vấn đề], đúng không ạ?"*
*(Câu này giúp bạn có thêm 15 giây quý giá để não bộ sắp xếp lại ý trả lời mà vẫn thể hiện sự tôn trọng tối đa).*

### Câu ma thuật 2 (Khi bị hỏi một kiến thức ngoài phạm vi đề tài):
> *"Dạ thưa Thầy/Cô, trong phạm vi nghiên cứu của đề tài tốt nghiệp này, mục tiêu trọng tâm của em là tối ưu hóa phần cứng mảng tâm thu Output-Stationary và tích hợp SoC trên chip Altera Cyclone II. Vấn đề mà Thầy/Cô vừa gợi ý [ví dụ: DMA streaming / FP16 / Transformer] là một hướng phát triển rất giá trị mà em đã nêu trong Chương 5 của Luận văn và em sẽ tiếp tục nghiên cứu nâng cấp trong các giai đoạn tiếp theo ạ!"*

### Câu ma thuật 3 (Vũ khí tối thượng: Kéo Hội đồng về màn hình Demo thực tế):
> *"Dạ thưa Thầy/Cô, để trả lời trực quan nhất cho thắc mắc này, em xin phép kính mời Thầy Cô quan sát trực tiếp trên dạng sóng ModelSim / trên màn hình Kit DE1 đang chạy thực nghiệm ở đây ạ..."*
*(Khi bạn mở dạng sóng ModelSim hoặc mở app Python vẽ số lên, sự chú ý của toàn bộ Hội đồng sẽ chuyển vào sản phẩm thật chạy mượt mà, và điểm số của bạn sẽ lập tức tăng vọt).*

---
> **LỜI KHUYÊN CUỐI CÙNG**: Bạn đã có trong tay một hệ thống phần cứng thật, bitstream thật, dạng sóng thật và mọi số liệu đều Bit-True 100%. Hãy tự tin, ngẩng cao đầu và bảo vệ thành công rực rỡ nhé!
