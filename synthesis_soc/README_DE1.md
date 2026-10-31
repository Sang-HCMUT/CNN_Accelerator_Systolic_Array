# [DEPRECATED / ARCHIVED] Terasic DE1 Synthesis Project

> [!WARNING]
> **DỰ ÁN NÀY ĐÃ ĐƯỢC LƯU TRỮ VÀ NGỪNG SỬ DỤNG (DEPRECATED & ARCHIVED)**  
> Thư mục `synthesis_soc/` là dự án tham chiếu 4×4 cũ trên bo mạch Terasic DE1 (Altera Cyclone II `EP2C20F484C7`).  
> **KHÔNG SỬ DỤNG THƯ MỤC NÀY ĐỂ BUILD HOẶC NẠP BITSTREAM CHO ĐỒ ÁN HIỆN HÀNH.**

---

## 1. Lý Do Kỹ Thuật (Architectural Incompatibility)

1. **Giới Hạn Khối Nhân DSP Phần Cứng**:
   - Chip Cyclone II `EP2C20` trên bo DE1 chỉ có **52 khối nhân 9-bit** (26 khối DSP 18-bit).
   - Toàn bộ đề tài đã thống nhất chuẩn hóa kiến trúc **Mảng Tâm Thu $8 \times 8$ (64 Processing Elements)**, đòi hỏi tối thiểu **64 khối nhân phần cứng 9-bit**.
   - Vì vậy, mảng $8 \times 8$ **vượt quá khả năng vật lý của bo DE1** (thiếu 12 multipliers) và không thể triển khai được trên chip EP2C20.

2. **Kích Thước Bộ Nhớ BRAM & Firmware**:
   - BRAM trên DE1 chỉ cấu hình 4,096 từ (16 KB), trong khi bộ firmware $8 \times 8$ mới (40,961 bytes / 4,427 words) sử dụng không gian nhớ $8 \times 8$ (Buffer A tại 0x100, B tại 0x300, C tại 0x500, C_ACC tại 0x600).
   - Nạp firmware $8 \times 8$ vào core $4 \times 4$ trên DE1 sẽ gây lỗi tràn bộ đệm và sai lệch kết quả suy luận.

---

## 2. Nền Tảng Triển Khai Mục Tiêu Hiện Hành (Active Deployment Targets)

Đề tài hiện tập trung vào 2 nền tảng phần cứng $8 \times 8$ đã được tổng hợp, đóng thời gian (timing-closed), và xác nhận thành công 100%:

- **Nền Tảng Phần Cứng Chính (Primary)**:
  👉 Thư mục dự án: [`synthesis_soc_de2/`](file:///e:/DATN/CNN_Systolic_Architecture/synthesis_soc_de2/)  
  Bo mạch: **Terasic DE2** (Altera Cyclone II `EP2C35F672C6`)  
  Cấu hình: **$8 \times 8$ Systolic Array (64 PEs, 64/70 Multipliers used, 32 KB BRAM)**  
  Tần số & Định thời: 50 MHz, Slack Setup **+4.588 ns**, Fmax = **64.88 MHz**, Thông lượng **6.40 GOPS**  
  Lệnh build: `compile_soc_de2.bat` $\to$ Bitstream: `soc_top_de2.sof`

- **Nền Tảng Mở Rộng Quy Mô (Scale-Up)**:
  👉 Thư mục dự án: [`synthesis_soc_de10/`](file:///e:/DATN/CNN_Systolic_Architecture/synthesis_soc_de10/)  
  Bo mạch: **Terasic DE10-Standard** (Intel Cyclone V `5CSXFC6D6F31C6N`)  
  Cấu hình: **$8 \times 8$ Systolic Array (64 PEs, 64/112 DSP Blocks used, 32 KB BRAM)**  
  Tần số & Định thời: 50 MHz, Slack Setup **+3.932 ns**, Fmax = **62.24 MHz**, Thông lượng **6.40 GOPS**  
  Lệnh build: `compile_soc_de10.bat` $\to$ Bitstream: `soc_top_de10.sof`
