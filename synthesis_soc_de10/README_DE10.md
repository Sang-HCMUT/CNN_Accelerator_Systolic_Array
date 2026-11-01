# DE10-Standard Synthesis Project — 8×8 Systolic Array SoC (Scale-Up)

## Mục Đích
Project này là bản **mở rộng quy mô (Scale-Up)** chuẩn hóa kiến trúc **$8 \times 8$ Systolic Array (64 PEs, 64 DSP Blocks)** lên bo mạch hiện đại **Terasic DE10-Standard** (Intel Cyclone V `5CSXFC6D6F31C6N`).
Sử dụng **cùng kiến trúc RTL và firmware $8 \times 8$ đồng bộ** như bo mạch chính Terasic DE2, chỉ cấu hình lại pinout và chip đích Cyclone V.

*(Lưu ý: Nền tảng cũ DE1 đã được lưu trữ/deprecated tại `synthesis_soc/` do chip EP2C20 chỉ có 52 multiplier, không đủ tài nguyên phần cứng cho mảng 8×8).*

---

## Thông Tin Chip Mục Tiêu

| Thông Số | DE1 (Cyclone II) | DE10-Standard (Cyclone V) |
|---|---|---|
| **Device** | EP2C20F484C7 | 5CSXFC6D6F31C6N |
| **Logic Elements** | 18,752 LEs | 85,000 LEs (41,910 ALMs) |
| **DSP Blocks** | 52 (9-bit) | 112 (18-bit) |
| **Block RAM** | 239,616 bits | 5,662 Kbits |
| **PLLs** | 4 | 6 |

## Cấu Hình SoC (soc_top_de10.sv)

| Tham Số | Giá Trị | Ghi Chú |
|---|---|---|
| `ARRAY_SIZE` | **8** | 8×8 = 64 PEs (vs 4×4=16 trên DE1) |
| `MEM_WORDS` | 8192 | 32 KB BRAM firmware |
| `UART_CLKS_PER_BIT` | 434 | 50 MHz / 115200 baud — giống DE1 |
| Clock | 50 MHz | CLOCK_50[0] — Pin AF14 |
| Reset | KEY[0] | Active-low — Pin AJ4 (Lưu ý: Pin AH17 là HEX0[4]) |

## Sơ Đồ Kết Nối UART (GPIO_0 Header J1 — Khớp với soc_top_de10.qsf)

```
Host PC (USB-to-UART Adapter)         DE10-Standard GPIO_0 (Header J1)
┌─────────────────────┐               ┌───────────────────────────────┐
│  CP2102 / CH340G    │               │   J1 Header (40-pin)          │
│                     │               │                               │
│  TXD ──────────────────────────────► GPIO_0[1] = Pin AK2 (Header P2)│  uart_rx
│  RXD ◄──────────────────────────────  GPIO_0[0] = Pin W15 (Header P1)│  uart_tx
│  GND ──────────────────────────────── GND         (Header P12/P30)  │
└─────────────────────┘               └───────────────────────────────┘
```

## Mapping LED (DE10 chỉ có LEDR, không có LEDG)

| LEDR | Nguồn | Ý Nghĩa |
|---|---|---|
| `LEDR[0]` | `ledr[0]` | CPU Trap error |
| `LEDR[1]` | `ledr[1]` | Systolic Array busy |
| `LEDR[2]` | `ledg[0]` | Tile Done (was LEDG[0] on DE1) |
| `LEDR[3]` | `ledg[1]` | UART RX valid |
| `LEDR[4..7]` | Spare | Diagnostic signals |
| `LEDR[8]` | Heartbeat | 1 Hz blink — xác nhận chip đang chạy |
| `LEDR[9]` | Always ON | Biểu thị đang chạy 8×8 mode |

## Yêu Cầu Quartus Version

> ⚠️ **Quartus II 13.0 SP1 KHÔNG hỗ trợ đầy đủ Cyclone V 5CSXFC6D6F31C6N.**
> Cần sử dụng **Quartus Prime 17.1** (hoặc mới hơn).
>
> **Quartus Prime Lite 17.1** — Miễn phí, tải tại:
> https://www.intel.com/content/www/us/en/collections/products/fpga/software/downloads.html

## Cách Chạy

```bat
rem 1. Chỉnh đường dẫn Quartus trong compile_soc_de10.bat
rem    SET QUARTUS_BIN=C:\intelFPGA_lite\17.1\quartus\bin64

rem 2. Chạy compilation
cd synthesis_soc_de10
.\compile_soc_de10.bat
rem 3. Kết quả: soc_top_de10.sof (bitstream nạp vào DE10-Standard)
```

## Kết Quả Đo Đạc Thực Tế Trên Quartus Prime (Cấu hình 8×8)

| Tài Nguyên Phần Cứng | Số Lượng Sử Dụng | Giới Hạn Cyclone V | Tỉ Lệ Chiếm Dụng |
|---|:---:|:---:|:---:|
| **Logic ALMs** | **8,290** | 41,910 | **19.8%** |
| **Dedicated Logic Registers** | **9,982** | -- | **23.8%** |
| **DSP Blocks** | **64** | 112 | **57.1%** |
| **Block RAM (M10K)** | **264,192 bits** (32 KB BRAM) | 5,662,720 bits | **4.7%** |
| **Clock Danh Định** | **50.00 MHz** (20.0 ns) | -- | CLOCK_50[0] |
| **Worst-Case Setup Slack** | **+5.609 ns** | -- | Timing Closure Met (Slack dương an toàn) |
| **Worst-Case Hold Slack** | **+0.128 ns** | -- | TNS = 0.000 ns, THNS = 0.000 ns |
| **Tần Số Cực Đại ($F_{max}$)**| **69.49 MHz** | -- | Vượt trần 50 MHz danh định |
| **Peak Throughput** | **6.40 GOPS** (3.20 GMAC/s) | -- | Đồng nhất với DE2 8x8 |
