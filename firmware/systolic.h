#ifndef SYSTOLIC_H
#define SYSTOLIC_H

#include <stdint.h>
#include <stddef.h>

// Hardware Memory Map for RISC-V SoC

// Base Addresses
#define BRAM_BASE          0x00000000
#define ACCEL_BASE         0x10000000
#define UART_BASE          0x20000000

// Systolic Accelerator MMIO Registers
#define REG_ACCEL_CTRL     (*(volatile uint32_t*)(ACCEL_BASE + 0x000))
#define REG_ACCEL_STATUS   (*(volatile uint32_t*)(ACCEL_BASE + 0x004))
#define REG_ACCEL_KDIM     (*(volatile uint32_t*)(ACCEL_BASE + 0x008))
#define REG_ACCEL_CYCLES   (*(volatile uint32_t*)(ACCEL_BASE + 0x00C))
#define REG_ACCEL_VERSION  (*(volatile uint32_t*)(ACCEL_BASE + 0x010))

// Memory-Mapped Tile Buffers (8x8 Systolic Architecture)
// Matrix A (Weights): up to 128 words (8 rows x 16 cols, word-aligned, 0x100 to 0x2FC)
#define REG_ACCEL_A(idx)     (*(volatile uint32_t*)(ACCEL_BASE + 0x100 + ((idx) << 2)))

// Matrix B (Activations): up to 128 words (16 rows x 8 cols, word-aligned, 0x300 to 0x4FC)
#define REG_ACCEL_B(idx)     (*(volatile uint32_t*)(ACCEL_BASE + 0x300 + ((idx) << 2)))

// Matrix C (INT8 Post-ReLU Activations): 64 words (8 rows x 8 cols, word-aligned, 0x500 to 0x5FC)
#define REG_ACCEL_C(idx)     (*(volatile uint32_t*)(ACCEL_BASE + 0x500 + ((idx) << 2)))

// Matrix C (INT32 Raw Accumulators): 64 words (8 rows x 8 cols, word-aligned, 0x600 to 0x6FC)
#define REG_ACCEL_C_ACC(idx) (*(volatile uint32_t*)(ACCEL_BASE + 0x600 + ((idx) << 2)))

// Gen-2 Packed 4-INT8 Buffers (32-bit words packing 4 signed bytes)
// Matrix A: up to 32 words (8 rows x 16 cols / 4 bytes, 0x700 to 0x77C)
#define REG_ACCEL_PACKED_A(w_idx)  (*(volatile uint32_t*)(ACCEL_BASE + 0x700 + ((w_idx) << 2)))

// Matrix B: up to 32 words (16 rows x 8 cols / 4 bytes, 0x780 to 0x7FC)
#define REG_ACCEL_PACKED_B(w_idx)  (*(volatile uint32_t*)(ACCEL_BASE + 0x780 + ((w_idx) << 2)))

// Matrix C (INT8 Post-ReLU): 16 words (8 rows x 8 cols / 4 bytes, 0x800 to 0x83C)
#define REG_ACCEL_PACKED_C(w_idx)  (*(volatile uint32_t*)(ACCEL_BASE + 0x800 + ((w_idx) << 2)))

// Control Register Bit Masks
#define CTRL_START         (1 << 0)
#define CTRL_BYPASS_RELU   (1 << 1)
#define CTRL_SHIFT_BITS(s) (((s) & 0x1F) << 2)

// Status Register Bit Masks
#define STATUS_DONE        (1 << 0)
#define STATUS_BUSY        (1 << 1)
#define STATUS_ERROR       (1 << 2)

// UART / Console Registers
#define REG_UART_DATA      (*(volatile uint32_t*)(UART_BASE + 0x000))
#define REG_UART_STATUS    (*(volatile uint32_t*)(UART_BASE + 0x004))
#define REG_UART_HEX       (*(volatile uint32_t*)(UART_BASE + 0x008))
#define REG_UART_LEDS      (*(volatile uint32_t*)(UART_BASE + 0x00C))

#define UART_STATUS_TX_READY (1 << 0)
#define UART_STATUS_RX_VALID (1 << 1)

// Freestanding memory utilities with global linkage
void *memcpy(void *dest, const void *src, size_t n) {
    char *d = (char *)dest;
    const char *s = (const char *)src;
    while (n--) *d++ = *s++;
    return dest;
}

void *memset(void *s, int c, size_t n) {
    char *p = (char *)s;
    while (n--) *p++ = (char)c;
    return s;
}

// Low-Level UART & Board Peripherals
static __attribute__((noinline)) void uart_putchar(char c) {
    while (!(REG_UART_STATUS & UART_STATUS_TX_READY));
    REG_UART_DATA = (uint32_t)(uint8_t)c;
}

static inline int uart_has_data(void) {
    return (REG_UART_STATUS & UART_STATUS_RX_VALID) ? 1 : 0;
}

static __attribute__((noinline)) uint8_t uart_getchar(void) {
    while (!(REG_UART_STATUS & UART_STATUS_RX_VALID));
    return (uint8_t)(REG_UART_DATA & 0xFF);
}

static inline void set_board_hex(uint8_t hex1, uint8_t hex0) {
    REG_UART_HEX = ((uint32_t)(hex1 & 0x0F) << 4) | (uint32_t)(hex0 & 0x0F);
}

static inline void set_board_leds(uint8_t leds) {
    REG_UART_LEDS = (uint32_t)leds;
}

static __attribute__((noinline)) void print_str(const char *s) {
    while (*s) {
        if (*s == '\n') uart_putchar('\r');
        uart_putchar(*s++);
    }
}

static __attribute__((noinline)) void print_hex(uint32_t val, int digits) {
    const char hex_chars[] = "0123456789ABCDEF";
    for (int i = digits - 1; i >= 0; i--) {
        uart_putchar(hex_chars[(val >> (i * 4)) & 0xF]);
    }
}

static __attribute__((noinline)) void print_dec(int val) {
    if (val < 0) {
        uart_putchar('-');
        val = -val;
    }
    char buf[12];
    int i = 0;
    if (val == 0) {
        uart_putchar('0');
        return;
    }
    while (val > 0) {
        buf[i++] = '0' + (val % 10);
        val /= 10;
    }
    while (--i >= 0) {
        uart_putchar(buf[i]);
    }
}

// Hardware Performance Counters (RISC-V standard rdcycle & rdinstret)
static inline uint32_t get_cycles(void) {
    uint32_t c;
    asm volatile ("rdcycle %0" : "=r"(c));
    return c;
}

static inline uint32_t get_instrs(void) {
    uint32_t ins;
    asm volatile ("rdinstret %0" : "=r"(ins));
    return ins;
}

// Pure Hardware Accelerator Execution Cycle Counter (MMIO REG_ACCEL_CYCLES at offset 0x00C)
// Measures exact hardware clock cycles spent inside the systolic array from core_start to core_done
static inline uint32_t get_accelerator_hw_cycles(void) {
    return REG_ACCEL_CYCLES;
}

// Formatted signed integer printing with right alignment
static __attribute__((noinline)) void print_signed(int val, int width) {
    char buf[12];
    int neg = 0;
    int uval = val;
    if (val < 0) {
        neg = 1;
        uval = -val;
    }
    int len = 0;
    if (uval == 0) {
        buf[len++] = '0';
    } else {
        while (uval > 0) {
            buf[len++] = '0' + (uval % 10);
            uval /= 10;
        }
    }
    if (neg) buf[len++] = '-';
    for (int p = len; p < width; p++) {
        uart_putchar(' ');
    }
    while (--len >= 0) {
        uart_putchar(buf[len]);
    }
}

// Low-level hardware accelerator invocation
// Run Systolic GEMM Accelerator: returns 0 on success, -1 on dimension error (STATUS_ERROR)
static __attribute__((noinline)) int run_accelerator_gemm(const int8_t *A, const int8_t *B, int k_dim, int shift, int bypass_relu) {
    // Hardware Guardband Pre-validation:
    // If K is out of valid range [1, 16], trigger hardware rejection directly
    // WITHOUT writing into tile buffers A/B to prevent MMIO buffer overflow into adjacent peripheral regions!
    if (k_dim < 1 || k_dim > 16) {
        REG_ACCEL_KDIM = (uint32_t)k_dim;
        REG_ACCEL_CTRL = CTRL_START; // Trigger hardware guardband rejection
        while (!(REG_ACCEL_STATUS & STATUS_DONE));
        if (REG_ACCEL_STATUS & STATUS_ERROR) {
            return -1; // Hardware guardband violation confirmed via AXI STATUS_ERROR (bit 2)
        }
        return -2; // Anomaly: Core finished without asserting STATUS_ERROR
    }

    REG_ACCEL_KDIM = (uint32_t)k_dim;

    // Stream Matrix A: 8 rows x k_dim columns = 8 * k_dim elements
    int total_a = 8 * k_dim;
    for (int i = 0; i < total_a; i++) {
        REG_ACCEL_A(i) = (uint32_t)(uint8_t)A[i];
    }

    // Stream Matrix B: k_dim rows x 8 columns = k_dim * 8 elements
    int total_b = k_dim * 8;
    for (int i = 0; i < total_b; i++) {
        REG_ACCEL_B(i) = (uint32_t)(uint8_t)B[i];
    }

    uint32_t ctrl = CTRL_START | CTRL_SHIFT_BITS(shift);
    if (bypass_relu) {
        ctrl |= CTRL_BYPASS_RELU;
    }
    REG_ACCEL_CTRL = ctrl;

    while (!(REG_ACCEL_STATUS & STATUS_DONE));

    if (REG_ACCEL_STATUS & STATUS_ERROR) {
        return -1; // Hardware guardband violation (e.g., invalid K)
    }
    return 0; // Success
}

// Gen-2 Packed 4-INT8 GEMM Accelerator Execution
// Feeds 4 signed INT8 bytes per 32-bit word, reducing MMIO transactions and loop overhead by 4x!
static inline int run_accelerator_gemm_packed(
    const int8_t *A,
    const int8_t *B,
    int k_dim,
    int shift,
    int bypass_relu
) {
    if (k_dim < 1 || k_dim > 16) {
        REG_ACCEL_KDIM = (uint32_t)k_dim;
        REG_ACCEL_CTRL = CTRL_START;
        while (REG_ACCEL_STATUS & STATUS_BUSY);
        if (REG_ACCEL_STATUS & STATUS_ERROR) return -1;
        return -2;
    }

    REG_ACCEL_KDIM = (uint32_t)k_dim;

    // Stream Matrix A packed: total_words = (8 * k_dim) / 4 = 2 * k_dim words
    const uint32_t *a_words = (const uint32_t *)A;
    int words_a = (8 * k_dim) >> 2;
    for (int w = 0; w < words_a; w++) {
        REG_ACCEL_PACKED_A(w) = a_words[w];
    }

    // Stream Matrix B packed: total_words = (k_dim * 8) / 4 = 2 * k_dim words
    const uint32_t *b_words = (const uint32_t *)B;
    int words_b = (k_dim * 8) >> 2;
    for (int w = 0; w < words_b; w++) {
        REG_ACCEL_PACKED_B(w) = b_words[w];
    }

    uint32_t ctrl = CTRL_START | CTRL_SHIFT_BITS(shift);
    if (bypass_relu) {
        ctrl |= CTRL_BYPASS_RELU;
    }
    REG_ACCEL_CTRL = ctrl;

    while (!(REG_ACCEL_STATUS & STATUS_DONE));

    if (REG_ACCEL_STATUS & STATUS_ERROR) {
        return -1;
    }
    return 0;
}

// Read back quantized INT8 results (64 elements: 8x8)
static __attribute__((noinline)) void read_accelerator_c_int8(int8_t *out_c) {
    for (int i = 0; i < 64; i++) {
        out_c[i] = (int8_t)(REG_ACCEL_C(i) & 0xFF);
    }
}

// Gen-2 Packed Readout: reads 64 INT8 elements as 16 words (4 bytes/word)
static inline void read_accelerator_c_packed_int8(int8_t *out_c) {
    uint32_t *c_words = (uint32_t *)out_c;
    for (int w = 0; w < 16; w++) {
        c_words[w] = REG_ACCEL_PACKED_C(w);
    }
}

// Read back unquantized INT32 accumulators (64 elements: 8x8)
static __attribute__((noinline)) void read_accelerator_c_int32(int32_t *out_acc) {
    for (int i = 0; i < 64; i++) {
        out_acc[i] = (int32_t)REG_ACCEL_C_ACC(i);
    }
}

// Pretty print 8x8 INT8 matrix
static __attribute__((noinline)) void print_matrix_8x8(const int8_t *mat, const char *title) {
    if (title) {
        print_str(title);
        print_str(":\n");
    }
    for (int r = 0; r < 8; r++) {
        print_str("  [");
        for (int c = 0; c < 8; c++) {
            print_signed((int)mat[r * 8 + c], 5);
            if (c < 7) print_str(" ");
        }
        print_str(" ]\n");
    }
}

// Pretty print 8x8 INT32 matrix
static __attribute__((noinline)) void print_matrix_8x8_int32(const int32_t *mat, const char *title) {
    if (title) {
        print_str(title);
        print_str(":\n");
    }
    for (int r = 0; r < 8; r++) {
        print_str("  [");
        for (int c = 0; c < 8; c++) {
            print_signed((int)mat[r * 8 + c], 7);
            if (c < 7) print_str(" ");
        }
        print_str(" ]\n");
    }
}

#endif // SYSTOLIC_H
