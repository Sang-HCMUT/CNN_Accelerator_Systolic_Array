#ifndef SYSTOLIC_H
#define SYSTOLIC_H

#include <stdint.h>

// ============================================================================
// Hardware Memory Map for RISC-V SoC
// ============================================================================

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

// ============================================================================
// Inline Helper Functions
// ============================================================================

static inline void uart_putchar(char c) {
    while (!(REG_UART_STATUS & UART_STATUS_TX_READY)); // Wait for TX ready
    REG_UART_DATA = (uint32_t)(uint8_t)c;
}

static inline int uart_has_data(void) {
    return (REG_UART_STATUS & UART_STATUS_RX_VALID) ? 1 : 0;
}

static inline uint8_t uart_getchar(void) {
    while (!(REG_UART_STATUS & UART_STATUS_RX_VALID)); // Wait for RX valid
    return (uint8_t)(REG_UART_DATA & 0xFF);
}

static inline void set_board_hex(uint8_t hex1, uint8_t hex0) {
    REG_UART_HEX = ((uint32_t)(hex1 & 0x0F) << 4) | (uint32_t)(hex0 & 0x0F);
}

static inline void set_board_leds(uint8_t leds) {
    REG_UART_LEDS = (uint32_t)leds;
}

static inline void print_str(const char *s) {
    while (*s) {
        if (*s == '\n') uart_putchar('\r');
        uart_putchar(*s++);
    }
}

static inline void print_hex(uint32_t val, int digits) {
    const char hex_chars[] = "0123456789ABCDEF";
    for (int i = digits - 1; i >= 0; i--) {
        uart_putchar(hex_chars[(val >> (i * 4)) & 0xF]);
    }
}

static inline void print_dec(int val) {
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

#endif // SYSTOLIC_H
