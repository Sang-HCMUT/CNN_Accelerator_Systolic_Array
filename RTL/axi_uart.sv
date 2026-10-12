`timescale 1ns / 1ps

// ============================================================================
// Module: axi_uart.sv
// Description: Enhanced AXI4-Lite UART & Peripheral Controller for Terasic DE1.
//              - Transmits 8N1 serial stream on uart_tx pin.
//              - Receives 8N1 serial stream on uart_rx pin with 2-stage sync.
//              - Controls 7-segment hex digit display and status LEDs.
//              - Base Address: 0x2000_0000.
//                - 0x00: Data Register (Write char -> TX / Read -> RX byte)
//                - 0x04: Status Register (Bit 0: TX Ready, Bit 1: RX Valid)
//                - 0x08: HEX Display Register (Bits [3:0] digit for HEX0)
//                - 0x0C: LED Register (Bits [7:0] general purpose LEDs)
// ============================================================================

module axi_uart #(
    parameter CLK_FREQ_HZ  = 50_000_000,
    parameter BAUD_RATE    = 115200,
    parameter CLKS_PER_BIT = CLK_FREQ_HZ / BAUD_RATE
)(
    input  logic        clk,
    input  logic        rst_n,

    // Hardware serial pins
    input  logic        uart_rx,
    output logic        uart_tx,

    // Hardware board outputs
    output logic [3:0]  hex_digit_0,
    output logic [3:0]  hex_digit_1,
    output logic [7:0]  board_leds,
    output logic        rx_valid_flag,

    // AXI4-Lite Write Address Channel
    input  logic [31:0] s_axi_awaddr,
    input  logic [2:0]  s_axi_awprot,
    input  logic        s_axi_awvalid,
    output logic        s_axi_awready,

    // AXI4-Lite Write Data Channel
    input  logic [31:0] s_axi_wdata,
    input  logic [3:0]  s_axi_wstrb,
    input  logic        s_axi_wvalid,
    output logic        s_axi_wready,

    // AXI4-Lite Write Response Channel
    output logic [1:0]  s_axi_bresp,
    output logic        s_axi_bvalid,
    input  logic        s_axi_bready,

    // AXI4-Lite Read Address Channel
    input  logic [31:0] s_axi_araddr,
    input  logic [2:0]  s_axi_arprot,
    input  logic        s_axi_arvalid,
    output logic        s_axi_arready,

    // AXI4-Lite Read Data Channel
    output logic [31:0] s_axi_rdata,
    output logic [1:0]  s_axi_rresp,
    output logic        s_axi_rvalid,
    input  logic        s_axi_rready
);

    // ========================================================================
    // 1. Hardware UART Transmitter (TX)
    // ========================================================================
    logic [9:0]  tx_shift_reg;
    logic [3:0]  tx_bit_cnt;
    logic [15:0] tx_clk_cnt;
    logic        tx_busy;
    logic        tx_start;
    logic [7:0]  tx_byte_latch;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            uart_tx      <= 1'b1;
            tx_shift_reg <= 10'h3FF;
            tx_bit_cnt   <= '0;
            tx_clk_cnt   <= '0;
            tx_busy      <= 1'b0;
        end else begin
            if (tx_start && !tx_busy) begin
                tx_shift_reg <= {1'b1, tx_byte_latch, 1'b0}; // Stop bit (1), 8 data bits, Start bit (0)
                tx_bit_cnt   <= 4'd10;
                tx_clk_cnt   <= '0;
                tx_busy      <= 1'b1;
            end else if (tx_busy) begin
                if (tx_clk_cnt < CLKS_PER_BIT - 1) begin
                    tx_clk_cnt <= tx_clk_cnt + 1'b1;
                end else begin
                    tx_clk_cnt   <= '0;
                    uart_tx      <= tx_shift_reg[0];
                    tx_shift_reg <= {1'b1, tx_shift_reg[9:1]};
                    if (tx_bit_cnt > 1) begin
                        tx_bit_cnt <= tx_bit_cnt - 1'b1;
                    end else begin
                        tx_busy <= 1'b0;
                        uart_tx <= 1'b1;
                    end
                end
            end else begin
                uart_tx <= 1'b1;
            end
        end
    end

    // ========================================================================
    // 2. Hardware UART Receiver (RX)
    // ========================================================================
    logic rx_sync_1, rx_sync_2;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rx_sync_1 <= 1'b1;
            rx_sync_2 <= 1'b1;
        end else begin
            rx_sync_1 <= uart_rx;
            rx_sync_2 <= rx_sync_1;
        end
    end

    typedef enum logic [1:0] {
        RX_IDLE,
        RX_START,
        RX_DATA,
        RX_STOP
    } rx_state_t;

    rx_state_t  rx_state;
    logic [15:0] rx_clk_cnt;
    logic [2:0]  rx_bit_idx;
    logic [7:0]  rx_shift_reg;
    logic [7:0]  rx_byte_buf;
    logic        rx_valid;
    logic        rx_read_pulse;

    assign rx_valid_flag = rx_valid;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rx_state     <= RX_IDLE;
            rx_clk_cnt   <= '0;
            rx_bit_idx   <= '0;
            rx_shift_reg <= '0;
            rx_byte_buf  <= '0;
            rx_valid     <= 1'b0;
        end else begin
            if (rx_read_pulse) begin
                rx_valid <= 1'b0;
            end

            case (rx_state)
                RX_IDLE: begin
                    rx_clk_cnt <= '0;
                    rx_bit_idx <= '0;
                    if (!rx_sync_2) begin // Detected falling edge of start bit
                        rx_state <= RX_START;
                    end
                end

                RX_START: begin
                    if (rx_clk_cnt == (CLKS_PER_BIT / 2)) begin
                        if (!rx_sync_2) begin
                            rx_clk_cnt <= '0;
                            rx_state   <= RX_DATA;
                        end else begin
                            rx_state <= RX_IDLE; // False glitch
                        end
                    end else begin
                        rx_clk_cnt <= rx_clk_cnt + 1'b1;
                    end
                end

                RX_DATA: begin
                    if (rx_clk_cnt == CLKS_PER_BIT - 1) begin
                        rx_clk_cnt               <= '0;
                        rx_shift_reg[rx_bit_idx] <= rx_sync_2;
                        if (rx_bit_idx == 3'd7) begin
                            rx_state <= RX_STOP;
                        end else begin
                            rx_bit_idx <= rx_bit_idx + 1'b1;
                        end
                    end else begin
                        rx_clk_cnt <= rx_clk_cnt + 1'b1;
                    end
                end

                RX_STOP: begin
                    if (rx_clk_cnt == CLKS_PER_BIT - 1) begin
                        rx_clk_cnt  <= '0;
                        rx_state    <= RX_IDLE;
                        rx_byte_buf <= rx_shift_reg;
                        rx_valid    <= 1'b1;
                    end else begin
                        rx_clk_cnt <= rx_clk_cnt + 1'b1;
                    end
                end

                default: rx_state <= RX_IDLE;
            endcase
        end
    end

    // ========================================================================
    // 3. AXI4-Lite Write Logic & GPIO Registers
    // ========================================================================
    typedef enum logic [1:0] {
        WR_IDLE,
        WR_WAIT_DATA,
        WR_WAIT_ADDR,
        WR_RESP
    } wr_state_t;

    wr_state_t wr_state;
    logic [31:0] latched_awaddr;
    logic [31:0] latched_wdata;

    // Board hardware output registers
    logic [3:0] reg_hex_0;
    logic [3:0] reg_hex_1;
    logic [7:0] reg_leds;

    assign hex_digit_0 = reg_hex_0;
    assign hex_digit_1 = reg_hex_1;
    assign board_leds  = reg_leds;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            s_axi_awready  <= 1'b0;
            s_axi_wready   <= 1'b0;
            s_axi_bvalid   <= 1'b0;
            s_axi_bresp    <= 2'b00;
            latched_awaddr <= '0;
            latched_wdata  <= '0;
            tx_start       <= 1'b0;
            tx_byte_latch  <= '0;
            reg_hex_0      <= 4'h0;
            reg_hex_1      <= 4'h0;
            reg_leds       <= 8'h00;
            wr_state       <= WR_IDLE;
        end else begin
            tx_start <= 1'b0;

            case (wr_state)
                WR_IDLE: begin
                    s_axi_bvalid <= 1'b0;
                    if (s_axi_awvalid && s_axi_wvalid) begin
                        s_axi_awready <= 1'b1;
                        s_axi_wready  <= 1'b1;
                        case (s_axi_awaddr[3:0])
                            4'h0: begin // 0x2000_0000: TX Data
                                tx_byte_latch <= s_axi_wdata[7:0];
                                tx_start      <= 1'b1;
                            end
                            4'h8: begin // 0x2000_0008: HEX Displays
                                reg_hex_0 <= s_axi_wdata[3:0];
                                reg_hex_1 <= s_axi_wdata[7:4];
                            end
                            4'hC: begin // 0x2000_000C: LEDs
                                reg_leds  <= s_axi_wdata[7:0];
                            end
                            default: ;
                        endcase
                        s_axi_bvalid  <= 1'b1;
                        s_axi_bresp   <= 2'b00;
                        wr_state      <= WR_RESP;
                    end else if (s_axi_awvalid) begin
                        s_axi_awready  <= 1'b1;
                        s_axi_wready   <= 1'b0;
                        latched_awaddr <= s_axi_awaddr;
                        wr_state       <= WR_WAIT_DATA;
                    end else if (s_axi_wvalid) begin
                        s_axi_awready  <= 1'b0;
                        s_axi_wready   <= 1'b1;
                        latched_wdata  <= s_axi_wdata;
                        wr_state       <= WR_WAIT_ADDR;
                    end else begin
                        s_axi_awready  <= 1'b0;
                        s_axi_wready   <= 1'b0;
                    end
                end

                WR_WAIT_DATA: begin
                    s_axi_awready <= 1'b0;
                    if (s_axi_wvalid) begin
                        s_axi_wready <= 1'b1;
                        case (latched_awaddr[3:0])
                            4'h0: begin
                                tx_byte_latch <= s_axi_wdata[7:0];
                                tx_start      <= 1'b1;
                            end
                            4'h8: begin
                                reg_hex_0 <= s_axi_wdata[3:0];
                                reg_hex_1 <= s_axi_wdata[7:4];
                            end
                            4'hC: begin
                                reg_leds  <= s_axi_wdata[7:0];
                            end
                            default: ;
                        endcase
                        s_axi_bvalid <= 1'b1;
                        s_axi_bresp  <= 2'b00;
                        wr_state     <= WR_RESP;
                    end else begin
                        s_axi_wready <= 1'b0;
                    end
                end

                WR_WAIT_ADDR: begin
                    s_axi_wready <= 1'b0;
                    if (s_axi_awvalid) begin
                        s_axi_awready <= 1'b1;
                        case (s_axi_awaddr[3:0])
                            4'h0: begin
                                tx_byte_latch <= latched_wdata[7:0];
                                tx_start      <= 1'b1;
                            end
                            4'h8: begin
                                reg_hex_0 <= latched_wdata[3:0];
                                reg_hex_1 <= latched_wdata[7:4];
                            end
                            4'hC: begin
                                reg_leds  <= latched_wdata[7:0];
                            end
                            default: ;
                        endcase
                        s_axi_bvalid  <= 1'b1;
                        s_axi_bresp   <= 2'b00;
                        wr_state      <= WR_RESP;
                    end else begin
                        s_axi_awready <= 1'b0;
                    end
                end

                WR_RESP: begin
                    s_axi_awready <= 1'b0;
                    s_axi_wready  <= 1'b0;
                    s_axi_bvalid  <= 1'b0;
                    wr_state      <= WR_IDLE;
                end

                default: wr_state <= WR_IDLE;
            endcase
        end
    end

    // ========================================================================
    // 4. AXI4-Lite Read Logic
    // ========================================================================
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            s_axi_arready <= 1'b0;
            s_axi_rvalid  <= 1'b0;
            s_axi_rresp   <= 2'b00;
            s_axi_rdata   <= '0;
            rx_read_pulse <= 1'b0;
        end else begin
            rx_read_pulse <= 1'b0;

            if (~s_axi_rvalid) begin
                if (s_axi_arvalid && ~s_axi_arready) begin
                    s_axi_arready <= 1'b1;
                end else if (s_axi_arready && s_axi_arvalid) begin
                    s_axi_arready <= 1'b0;
                    s_axi_rvalid  <= 1'b1;
                    s_axi_rresp   <= 2'b00;

                    case (s_axi_araddr[3:0])
                        4'h0: begin
                            // Read RX byte and clear rx_valid
                            s_axi_rdata   <= {24'd0, rx_byte_buf};
                            rx_read_pulse <= 1'b1;
                        end
                        4'h4: begin
                            // Status: Bit 0 = TX Ready (!busy), Bit 1 = RX Valid
                            s_axi_rdata <= {30'd0, rx_valid, ~tx_busy};
                        end
                        4'h8: begin
                            s_axi_rdata <= {24'd0, reg_hex_1, reg_hex_0};
                        end
                        4'hC: begin
                            s_axi_rdata <= {24'd0, reg_leds};
                        end
                        default: begin
                            s_axi_rdata <= 32'd0;
                        end
                    endcase
                end else begin
                    s_axi_arready <= 1'b0;
                end
            end else begin
                s_axi_arready <= 1'b0;
                s_axi_rvalid  <= 1'b0;
            end
        end
    end

endmodule
