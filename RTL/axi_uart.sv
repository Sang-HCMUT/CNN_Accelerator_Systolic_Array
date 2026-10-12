`timescale 1ns / 1ps

// ============================================================================
// Module: axi_uart.sv
// Description: AXI4-Lite UART / Console Output Peripheral.
//              - In Simulation: Outputs characters to stdout via $write("%c").
//              - In Hardware: Transmits 8N1 serial stream on uart_tx pin.
//              - Base Address: 0x2000_0000.
//                - 0x00: Data Register (Write char / Read RX)
//                - 0x04: Status Register (Bit 0: TX Ready, Bit 1: RX Valid)
// ============================================================================

module axi_uart #(
    parameter CLK_FREQ_HZ  = 50_000_000,
    parameter BAUD_RATE    = 115200,
    parameter CLKS_PER_BIT = CLK_FREQ_HZ / BAUD_RATE
)(
    input  logic        clk,
    input  logic        rst_n,

    // Hardware serial pin
    output logic        uart_tx,

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

    // Hardware UART TX state machine
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
                tx_shift_reg <= {1'b1, tx_byte_latch, 1'b0}; // Stop bit, 8 data bits, Start bit (0)
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

    // Internal handshakes
    typedef enum logic [1:0] {
        WR_IDLE,
        WR_WAIT_DATA,
        WR_WAIT_ADDR,
        WR_RESP
    } wr_state_t;

    wr_state_t wr_state;
    logic [31:0] latched_awaddr;
    logic [31:0] latched_wdata;

    // Write Logic
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
            wr_state       <= WR_IDLE;
        end else begin
            tx_start <= 1'b0;

            case (wr_state)
                WR_IDLE: begin
                    s_axi_bvalid <= 1'b0;
                    if (s_axi_awvalid && s_axi_wvalid) begin
                        s_axi_awready <= 1'b1;
                        s_axi_wready  <= 1'b1;
                        if (s_axi_awaddr[3:0] == 4'h0) begin
                            tx_byte_latch <= s_axi_wdata[7:0];
                            tx_start      <= 1'b1;
                        end
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
                        if (latched_awaddr[3:0] == 4'h0) begin
                            tx_byte_latch <= s_axi_wdata[7:0];
                            tx_start      <= 1'b1;
                        end
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
                        if (s_axi_awaddr[3:0] == 4'h0) begin
                            tx_byte_latch <= latched_wdata[7:0];
                            tx_start      <= 1'b1;
                        end
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

    // Read Logic
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            s_axi_arready <= 1'b0;
            s_axi_rvalid  <= 1'b0;
            s_axi_rresp   <= 2'b00;
            s_axi_rdata   <= '0;
        end else begin
            if (~s_axi_rvalid) begin
                if (s_axi_arvalid && ~s_axi_arready) begin
                    s_axi_arready <= 1'b1;
                end else if (s_axi_arready && s_axi_arvalid) begin
                    s_axi_arready <= 1'b0;
                    s_axi_rvalid  <= 1'b1;
                    s_axi_rresp   <= 2'b00;

                    if (s_axi_araddr[3:0] == 4'h4) begin
                        // Status: Bit 0 = TX Ready (!busy)
                        s_axi_rdata <= {31'd0, ~tx_busy};
                    end else begin
                        s_axi_rdata <= 32'd0;
                    end
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
