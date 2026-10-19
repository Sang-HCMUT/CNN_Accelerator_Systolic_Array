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

// Memory-Mapped Tile Buffers
// Matrix A (Weights): 16 words (word-aligned, 0x100 to 0x13C)
#define REG_ACCEL_A(idx)   (*(volatile uint32_t*)(ACCEL_BASE + 0x100 + ((idx) << 2)))

// Matrix B (Activations): 16 words (word-aligned, 0x200 to 0x23C)
#define REG_ACCEL_B(idx)   (*(volatile uint32_t*)(ACCEL_BASE + 0x200 + ((idx) << 2)))

// Matrix C (INT8 Post-ReLU Activations): 16 words (word-aligned, 0x300 to 0x33C)
#define REG_ACCEL_C(idx)   (*(volatile uint32_t*)(ACCEL_BASE + 0x300 + ((idx) << 2)))

// Matrix C (INT32 Raw Accumulators): 16 words (word-aligned, 0x400 to 0x43C)
#define REG_ACCEL_C_ACC(idx) (*(volatile uint32_t*)(ACCEL_BASE + 0x400 + ((idx) << 2)))

// Control Register Bit Masks
#define CTRL_START         (1 << 0)
#define CTRL_BYPASS_RELU   (1 << 1)
#define CTRL_SHIFT_BITS(s) (((s) & 0x1F) << 2)

// Status Register Bit Masks
#define STATUS_DONE        (1 << 0)
#define STATUS_BUSY        (1 << 1)

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
static __attribute__((noinline)) void run_accelerator_gemm(const int8_t *A, const int8_t *B, int k_dim, int shift, int bypass_relu) {
    REG_ACCEL_KDIM = (uint32_t)k_dim;

    int total_elements = 4 * k_dim;
    for (int i = 0; i < total_elements; i++) {
        REG_ACCEL_A(i) = (uint32_t)(uint8_t)A[i];
        REG_ACCEL_B(i) = (uint32_t)(uint8_t)B[i];
    }

    uint32_t ctrl = CTRL_START | CTRL_SHIFT_BITS(shift);
    if (bypass_relu) {
        ctrl |= CTRL_BYPASS_RELU;
    }
    REG_ACCEL_CTRL = ctrl;

    while (!(REG_ACCEL_STATUS & STATUS_DONE));
}

// Read back quantized INT8 results (16 elements)
static __attribute__((noinline)) void read_accelerator_c_int8(int8_t *out_c) {
    for (int i = 0; i < 16; i++) {
        out_c[i] = (int8_t)(REG_ACCEL_C(i) & 0xFF);
    }
}

// Read back unquantized INT32 accumulators (16 elements)
static __attribute__((noinline)) void read_accelerator_c_int32(int32_t *out_acc) {
    for (int i = 0; i < 16; i++) {
        out_acc[i] = (int32_t)REG_ACCEL_C_ACC(i);
    }
}

// Pretty print 4x4 INT8 matrix
static __attribute__((noinline)) void print_matrix_4x4(const int8_t *mat, const char *title) {
    if (title) {
        print_str(title);
        print_str(":\n");
    }
    for (int r = 0; r < 4; r++) {
        print_str("  [");
        for (int c = 0; c < 4; c++) {
            print_signed((int)mat[r * 4 + c], 5);
            if (c < 3) print_str(" ");
        }
        print_str(" ]\n");
    }
}

// Pretty print 4x4 INT32 matrix
static __attribute__((noinline)) void print_matrix_4x4_int32(const int32_t *mat, const char *title) {
    if (title) {
        print_str(title);
        print_str(":\n");
    }
    for (int r = 0; r < 4; r++) {
        print_str("  [");
        for (int c = 0; c < 4; c++) {
            print_signed((int)mat[r * 4 + c], 7);
            if (c < 3) print_str(" ");
        }
        print_str(" ]\n");
    }
}

#endif // SYSTOLIC_H
