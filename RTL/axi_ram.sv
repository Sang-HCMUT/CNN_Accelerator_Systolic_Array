`timescale 1ns / 1ps

// ============================================================================
// Module: axi_ram.sv
// Description: AXI4-Lite On-Chip Block RAM (32 KB) for RISC-V SoC.
//              - Inferred Block RAM on Intel/Altera Cyclone IV/V FPGAs (M9K/M10K).
//              - Supports 32-bit word and byte-enable (wstrb[3:0]) operations.
//              - Initializes memory via MEM_INIT_FILE ($readmemh).
// ============================================================================

module axi_ram #(
    parameter DATA_WIDTH     = 32,
    parameter ADDR_WIDTH     = 15,          // 32 KB (8192 x 32-bit words)
    parameter MEM_WORDS      = 8192,
    parameter MEM_INIT_FILE  = "firmware.hex"
)(
    input  logic                   clk,
    input  logic                   rst_n,

    // AXI4-Lite Write Address Channel
    input  logic [31:0]            s_axi_awaddr,
    input  logic [2:0]             s_axi_awprot,
    input  logic                   s_axi_awvalid,
    output logic                   s_axi_awready,

    // AXI4-Lite Write Data Channel
    input  logic [DATA_WIDTH-1:0]  s_axi_wdata,
    input  logic [3:0]             s_axi_wstrb,
    input  logic                   s_axi_wvalid,
    output logic                   s_axi_wready,

    // AXI4-Lite Write Response Channel
    output logic [1:0]             s_axi_bresp,
    output logic                   s_axi_bvalid,
    input  logic                   s_axi_bready,

    // AXI4-Lite Read Address Channel
    input  logic [31:0]            s_axi_araddr,
    input  logic [2:0]             s_axi_arprot,
    input  logic                   s_axi_arvalid,
    output logic                   s_axi_arready,

    // AXI4-Lite Read Data Channel
    output logic [DATA_WIDTH-1:0]  s_axi_rdata,
    output logic [1:0]             s_axi_rresp,
    output logic                   s_axi_rvalid,
    input  logic                   s_axi_rready
);

    // Memory array (8192 words of 32 bits = 32 KB)
    logic [31:0] mem [0:MEM_WORDS-1];

    // Optional initialization from file
    initial begin
        if (MEM_INIT_FILE != "") begin
            $readmemh(MEM_INIT_FILE, mem);
        end
    end

    // Internal handshakes & FSM
    typedef enum logic [1:0] {
        WR_IDLE,
        WR_WAIT_DATA,
        WR_WAIT_ADDR,
        WR_RESP
    } wr_state_t;

    wr_state_t wr_state;
    logic [31:0] latched_awaddr;
    logic [31:0] latched_wdata;
    logic [3:0]  latched_wstrb;

    // Word address: addr[14:2] maps to 8192 words
    wire [12:0] rd_word_idx = s_axi_araddr[14:2];

    task automatic do_ram_write(input [31:0] addr, input [31:0] data, input [3:0] strb);
        logic [12:0] target_word;
        target_word = addr[14:2];
        if (target_word < MEM_WORDS) begin
            if (strb[0]) mem[target_word][7:0]   <= data[7:0];
            if (strb[1]) mem[target_word][15:8]  <= data[15:8];
            if (strb[2]) mem[target_word][23:16] <= data[23:16];
            if (strb[3]) mem[target_word][31:24] <= data[31:24];
        end
    endtask

    // ------------------------------------------------------------------------
    // Write State Machine
    // ------------------------------------------------------------------------
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            s_axi_awready  <= 1'b0;
            s_axi_wready   <= 1'b0;
            s_axi_bvalid   <= 1'b0;
            s_axi_bresp    <= 2'b00;
            latched_awaddr <= '0;
            latched_wdata  <= '0;
            latched_wstrb  <= '0;
            wr_state       <= WR_IDLE;
        end else begin
            case (wr_state)
                WR_IDLE: begin
                    s_axi_bvalid <= 1'b0;
                    if (s_axi_awvalid && s_axi_wvalid) begin
                        s_axi_awready <= 1'b1;
                        s_axi_wready  <= 1'b1;
                        do_ram_write(s_axi_awaddr, s_axi_wdata, s_axi_wstrb);
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
                        latched_wstrb  <= s_axi_wstrb;
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
                        do_ram_write(latched_awaddr, s_axi_wdata, s_axi_wstrb);
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
                        do_ram_write(s_axi_awaddr, latched_wdata, latched_wstrb);
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

    // ------------------------------------------------------------------------
    // Read State Machine
    // ------------------------------------------------------------------------
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
                    if (rd_word_idx < MEM_WORDS)
                        s_axi_rdata <= mem[rd_word_idx];
                    else
                        s_axi_rdata <= 32'hDEAD_BEEF;
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
