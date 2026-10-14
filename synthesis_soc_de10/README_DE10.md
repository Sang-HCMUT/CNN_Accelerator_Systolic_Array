# DE10-Standard Synthesis Project — 8×8 Systolic Array SoC

## Mục Đích
Project này là bản **mở rộng quy mô (Scale-up)** từ DE1 (Cyclone II, 4×4) lên DE10-Standard (Cyclone V, 8×8).
Sử dụng **cùng một RTL source**, chỉ thay tham số `ARRAY_SIZE = 8` và chip đích.

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
| Reset | KEY[0] | Active-low — Pin AH17 |

## Sơ Đồ Kết Nối UART (GPIO_0 Header)

```
Host PC (USB-to-UART Adapter)         DE10-Standard GPIO_0
┌─────────────────────┐               ┌───────────────────┐
│  CP2102 / CH340G    │               │   J1 Header       │
│                     │               │                   │
│  TXD ──────────────────────────────► GPIO_0[1] = Pin AF17│  uart_rx
│  RXD ◄──────────────────────────────  GPIO_0[0] = Pin AF15│  uart_tx
│  GND ──────────────────────────────── GND                │
└─────────────────────┘               └───────────────────┘
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

## Ước Tính Tài Nguyên (Chưa Synthesis Thực Tế)

| Tài Nguyên | Ước Tính | Cyclone V Limit | Tỉ Lệ |
|---|---|---|---|
| ALMs | ~22,000 | 41,910 | ~52% |
| DSP Blocks | 64 | 112 | ~57% |
| BRAM | ~600 Kbits | 5,662 Kbits | ~11% |

> **Ghi chú**: Đây là ước tính chưa synthesis. Cần chạy Quartus để có số liệu thực tế.

## So Sánh Hiệu Năng Lý Thuyết

| Chỉ Số | DE1 4×4 | DE10 8×8 |
|---|---|---|
| **PEs** | 16 | 64 |
| **MACs/cycle** | 16 | 64 |
| **Fmax (dự kiến)** | 64.14 MHz | ~60-70 MHz |
| **Throughput lý thuyết** | 16×64.14M = **1.03 GMAC/s** | 64×60M = **3.84 GMAC/s** |
