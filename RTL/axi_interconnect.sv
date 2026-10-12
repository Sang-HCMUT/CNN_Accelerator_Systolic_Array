`timescale 1ns / 1ps

// ============================================================================
// Module: axi_interconnect.sv
// Description: 1-Master to 3-Slave AXI4-Lite Crossbar/Interconnect.
//              - Master: PicoRV32 RISC-V CPU Core.
//              - Slave 0: 0x0000_0000 - 0x0FFF_FFFF -> BRAM RAM (32 KB).
//              - Slave 1: 0x1000_0000 - 0x1FFF_FFFF -> Systolic Accelerator.
//              - Slave 2: 0x2000_0000 - 0x2FFF_FFFF -> UART / Console.
// ============================================================================

module axi_interconnect (
    input  logic        clk,
    input  logic        rst_n,

    // ========================================================================
    // Master Interface (PicoRV32 AXI Master)
    // ========================================================================
    input  logic [31:0] s_axi_awaddr,
    input  logic [2:0]  s_axi_awprot,
    input  logic        s_axi_awvalid,
    output logic        s_axi_awready,

    input  logic [31:0] s_axi_wdata,
    input  logic [3:0]  s_axi_wstrb,
    input  logic        s_axi_wvalid,
    output logic        s_axi_wready,

    output logic [1:0]  s_axi_bresp,
    output logic        s_axi_bvalid,
    input  logic        s_axi_bready,

    input  logic [31:0] s_axi_araddr,
    input  logic [2:0]  s_axi_arprot,
    input  logic        s_axi_arvalid,
    output logic        s_axi_arready,

    output logic [31:0] s_axi_rdata,
    output logic [1:0]  s_axi_rresp,
    output logic        s_axi_rvalid,
    input  logic        s_axi_rready,

    // ========================================================================
    // Slave 0 Interface: BRAM RAM (0x0000_0000)
    // ========================================================================
    output logic [31:0] m0_axi_awaddr,
    output logic [2:0]  m0_axi_awprot,
    output logic        m0_axi_awvalid,
    input  logic        m0_axi_awready,

    output logic [31:0] m0_axi_wdata,
    output logic [3:0]  m0_axi_wstrb,
    output logic        m0_axi_wvalid,
    input  logic        m0_axi_wready,

    input  logic [1:0]  m0_axi_bresp,
    input  logic        m0_axi_bvalid,
    output logic        m0_axi_bready,

    output logic [31:0] m0_axi_araddr,
    output logic [2:0]  m0_axi_arprot,
    output logic        m0_axi_arvalid,
    input  logic        m0_axi_arready,

    input  logic [31:0] m0_axi_rdata,
    input  logic [1:0]  m0_axi_rresp,
    input  logic        m0_axi_rvalid,
    output logic        m0_axi_rready,

    // ========================================================================
    // Slave 1 Interface: Systolic Accelerator (0x1000_0000)
    // ========================================================================
    output logic [31:0] m1_axi_awaddr,
    output logic [2:0]  m1_axi_awprot,
    output logic        m1_axi_awvalid,
    input  logic        m1_axi_awready,

    output logic [31:0] m1_axi_wdata,
    output logic [3:0]  m1_axi_wstrb,
    output logic        m1_axi_wvalid,
    input  logic        m1_axi_wready,

    input  logic [1:0]  m1_axi_bresp,
    input  logic        m1_axi_bvalid,
    output logic        m1_axi_bready,

    output logic [31:0] m1_axi_araddr,
    output logic [2:0]  m1_axi_arprot,
    output logic        m1_axi_arvalid,
    input  logic        m1_axi_arready,

    input  logic [31:0] m1_axi_rdata,
    input  logic [1:0]  m1_axi_rresp,
    input  logic        m1_axi_rvalid,
    output logic        m1_axi_rready,

    // ========================================================================
    // Slave 2 Interface: UART / Console (0x2000_0000)
    // ========================================================================
    output logic [31:0] m2_axi_awaddr,
    output logic [2:0]  m2_axi_awprot,
    output logic        m2_axi_awvalid,
    input  logic        m2_axi_awready,

    output logic [31:0] m2_axi_wdata,
    output logic [3:0]  m2_axi_wstrb,
    output logic        m2_axi_wvalid,
    input  logic        m2_axi_wready,

    input  logic [1:0]  m2_axi_bresp,
    input  logic        m2_axi_bvalid,
    output logic        m2_axi_bready,

    output logic [31:0] m2_axi_araddr,
    output logic [2:0]  m2_axi_arprot,
    output logic        m2_axi_arvalid,
    input  logic        m2_axi_arready,

    input  logic [31:0] m2_axi_rdata,
    input  logic [1:0]  m2_axi_rresp,
    input  logic        m2_axi_rvalid,
    output logic        m2_axi_rready
);

    // ========================================================================
    // Write Channel Decoding & Routing
    // ========================================================================
    logic [1:0] wr_sel_latched;
    logic       wr_active;

    function automatic [1:0] decode_addr(input [31:0] addr);
        case (addr[31:28])
            4'h0:    return 2'd0; // RAM
            4'h1:    return 2'd1; // Accelerator
            4'h2:    return 2'd2; // UART
            default: return 2'd0; // Default fallback to RAM
        endcase
    endfunction

    wire [1:0] wr_sel = wr_active ? wr_sel_latched : decode_addr(s_axi_awaddr);

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_sel_latched <= 2'd0;
            wr_active      <= 1'b0;
        end else begin
            if (s_axi_awvalid && !wr_active) begin
                wr_sel_latched <= decode_addr(s_axi_awaddr);
                wr_active      <= 1'b1;
            end else if (s_axi_bvalid) begin
                wr_active      <= 1'b0;
            end
        end
    end

    // Broadcast write addresses and data to all slaves
    assign m0_axi_awaddr = s_axi_awaddr;
    assign m0_axi_awprot = s_axi_awprot;
    assign m0_axi_wdata  = s_axi_wdata;
    assign m0_axi_wstrb  = s_axi_wstrb;

    assign m1_axi_awaddr = s_axi_awaddr;
    assign m1_axi_awprot = s_axi_awprot;
    assign m1_axi_wdata  = s_axi_wdata;
    assign m1_axi_wstrb  = s_axi_wstrb;

    assign m2_axi_awaddr = s_axi_awaddr;
    assign m2_axi_awprot = s_axi_awprot;
    assign m2_axi_wdata  = s_axi_wdata;
    assign m2_axi_wstrb  = s_axi_wstrb;

    // Demux Write Valids
    assign m0_axi_awvalid = (wr_sel == 2'd0) ? s_axi_awvalid : 1'b0;
    assign m0_axi_wvalid  = (wr_sel == 2'd0) ? s_axi_wvalid  : 1'b0;
    assign m0_axi_bready  = (wr_sel == 2'd0) ? s_axi_bready  : 1'b0;

    assign m1_axi_awvalid = (wr_sel == 2'd1) ? s_axi_awvalid : 1'b0;
    assign m1_axi_wvalid  = (wr_sel == 2'd1) ? s_axi_wvalid  : 1'b0;
    assign m1_axi_bready  = (wr_sel == 2'd1) ? s_axi_bready  : 1'b0;

    assign m2_axi_awvalid = (wr_sel == 2'd2) ? s_axi_awvalid : 1'b0;
    assign m2_axi_wvalid  = (wr_sel == 2'd2) ? s_axi_wvalid  : 1'b0;
    assign m2_axi_bready  = (wr_sel == 2'd2) ? s_axi_bready  : 1'b0;

    // Mux Write Ready & Response to Master
    always_comb begin
        case (wr_sel)
            2'd0: begin
                s_axi_awready = m0_axi_awready;
                s_axi_wready  = m0_axi_wready;
                s_axi_bvalid  = m0_axi_bvalid;
                s_axi_bresp   = m0_axi_bresp;
            end
            2'd1: begin
                s_axi_awready = m1_axi_awready;
                s_axi_wready  = m1_axi_wready;
                s_axi_bvalid  = m1_axi_bvalid;
                s_axi_bresp   = m1_axi_bresp;
            end
            2'd2: begin
                s_axi_awready = m2_axi_awready;
                s_axi_wready  = m2_axi_wready;
                s_axi_bvalid  = m2_axi_bvalid;
                s_axi_bresp   = m2_axi_bresp;
            end
            default: begin
                s_axi_awready = 1'b0;
                s_axi_wready  = 1'b0;
                s_axi_bvalid  = 1'b0;
                s_axi_bresp   = 2'b00;
            end
        endcase
    end

    // ========================================================================
    // Read Channel Decoding & Routing
    // ========================================================================
    logic [1:0] rd_sel_latched;
    logic       rd_active;

    wire [1:0] rd_sel = rd_active ? rd_sel_latched : decode_addr(s_axi_araddr);

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rd_sel_latched <= 2'd0;
            rd_active      <= 1'b0;
        end else begin
            if (s_axi_arvalid && !rd_active) begin
                rd_sel_latched <= decode_addr(s_axi_araddr);
                rd_active      <= 1'b1;
            end else if (s_axi_rvalid) begin
                rd_active      <= 1'b0;
            end
        end
    end

    // Broadcast Read Address to all slaves
    assign m0_axi_araddr = s_axi_araddr;
    assign m0_axi_arprot = s_axi_arprot;
    assign m1_axi_araddr = s_axi_araddr;
    assign m1_axi_arprot = s_axi_arprot;
    assign m2_axi_araddr = s_axi_araddr;
    assign m2_axi_arprot = s_axi_arprot;

    // Demux Read Valids
    assign m0_axi_arvalid = (rd_sel == 2'd0) ? s_axi_arvalid : 1'b0;
    assign m0_axi_rready  = (rd_sel == 2'd0) ? s_axi_rready  : 1'b0;

    assign m1_axi_arvalid = (rd_sel == 2'd1) ? s_axi_arvalid : 1'b0;
    assign m1_axi_rready  = (rd_sel == 2'd1) ? s_axi_rready  : 1'b0;

    assign m2_axi_arvalid = (rd_sel == 2'd2) ? s_axi_arvalid : 1'b0;
    assign m2_axi_rready  = (rd_sel == 2'd2) ? s_axi_rready  : 1'b0;

    // Mux Read Ready & Response to Master
    always_comb begin
        case (rd_sel)
            2'd0: begin
                s_axi_arready = m0_axi_arready;
                s_axi_rvalid  = m0_axi_rvalid;
                s_axi_rdata   = m0_axi_rdata;
                s_axi_rresp   = m0_axi_rresp;
            end
            2'd1: begin
                s_axi_arready = m1_axi_arready;
                s_axi_rvalid  = m1_axi_rvalid;
                s_axi_rdata   = m1_axi_rdata;
                s_axi_rresp   = m1_axi_rresp;
            end
            2'd2: begin
                s_axi_arready = m2_axi_arready;
                s_axi_rvalid  = m2_axi_rvalid;
                s_axi_rdata   = m2_axi_rdata;
                s_axi_rresp   = m2_axi_rresp;
            end
            default: begin
                s_axi_arready = 1'b0;
                s_axi_rvalid  = 1'b0;
                s_axi_rdata   = 32'hDEAD_BEEF;
                s_axi_rresp   = 2'b11;
            end
        endcase
    end

endmodule
