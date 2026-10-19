`timescale 1ns / 1ps

// Module: axi_ram.sv
// AXI4-Lite On-Chip Block RAM (32 KB) for RISC-V SoC.
// Inferred Block RAM on Intel/Altera Cyclone IV/V FPGAs (M9K/M10K).
// Supports 32-bit word and byte-enable (wstrb[3:0]) operations.
// Initializes memory via MEM_INIT_FILE ($readmemh).

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

    localparam ADDR_BITS = $clog2(MEM_WORDS);

    // Memory array with Quartus Block RAM synthesis directive
    // Multi-dimensional packed array [3:0][7:0] is mandatory for Quartus byte-enabled BRAM inference
    (* ramstyle = "no_rw_check" *) logic [3:0][7:0] mem [0:MEM_WORDS-1];

    // Initialization directly with $readmemh (avoid runtime string condition)
    initial begin
        $readmemh(MEM_INIT_FILE, mem);
    end

    // Internal RAM signals for synchronous Block RAM inference
    logic                 ram_we;
    logic [ADDR_BITS-1:0] ram_waddr;
    logic [31:0]          ram_wdata;
    logic [3:0]           ram_wstrb;
    logic [31:0]          ram_rdata;

    // Embedded Block RAM (M4K / M9K / M10K) Synchronous Array (NO RESET)
    wire [ADDR_BITS-1:0] rd_word_idx = s_axi_araddr[ADDR_BITS+1:2];

    always_ff @(posedge clk) begin
        if (ram_we) begin
            if (ram_wstrb[0]) mem[ram_waddr][0] <= ram_wdata[7:0];
            if (ram_wstrb[1]) mem[ram_waddr][1] <= ram_wdata[15:8];
            if (ram_wstrb[2]) mem[ram_waddr][2] <= ram_wdata[23:16];
            if (ram_wstrb[3]) mem[ram_waddr][3] <= ram_wdata[31:24];
        end
        ram_rdata <= mem[rd_word_idx];
    end

    assign s_axi_rdata = ram_rdata;

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

    task automatic trigger_ram_write(input [31:0] addr, input [31:0] data, input [3:0] strb);
        ram_we    <= 1'b1;
        ram_waddr <= addr[ADDR_BITS+1:2];
        ram_wdata <= data;
        ram_wstrb <= strb;
    endtask

    // Write State Machine
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            s_axi_awready  <= 1'b0;
            s_axi_wready   <= 1'b0;
            s_axi_bvalid   <= 1'b0;
            s_axi_bresp    <= 2'b00;
            latched_awaddr <= '0;
            latched_wdata  <= '0;
            latched_wstrb  <= '0;
            ram_we         <= 1'b0;
            ram_waddr      <= '0;
            ram_wdata      <= '0;
            ram_wstrb      <= '0;
            wr_state       <= WR_IDLE;
        end else begin
            ram_we <= 1'b0;

            case (wr_state)
                WR_IDLE: begin
                    s_axi_bvalid <= 1'b0;
                    if (s_axi_awvalid && s_axi_wvalid) begin
                        s_axi_awready <= 1'b1;
                        s_axi_wready  <= 1'b1;
                        trigger_ram_write(s_axi_awaddr, s_axi_wdata, s_axi_wstrb);
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
                        trigger_ram_write(latched_awaddr, s_axi_wdata, s_axi_wstrb);
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
                        trigger_ram_write(s_axi_awaddr, latched_wdata, latched_wstrb);
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

    // Read State Machine
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            s_axi_arready <= 1'b0;
            s_axi_rvalid  <= 1'b0;
            s_axi_rresp   <= 2'b00;
        end else begin
            if (~s_axi_rvalid) begin
                if (s_axi_arvalid && ~s_axi_arready) begin
                    s_axi_arready <= 1'b1;
                end else if (s_axi_arready && s_axi_arvalid) begin
                    s_axi_arready <= 1'b0;
                    s_axi_rvalid  <= 1'b1;
                    s_axi_rresp   <= 2'b00;
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
