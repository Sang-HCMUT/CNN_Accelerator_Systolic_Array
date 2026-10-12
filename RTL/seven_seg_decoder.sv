`timescale 1ns / 1ps

// ============================================================================
// Module: seven_seg_decoder.sv
// Description: Active-Low 7-Segment Display Decoder for Terasic DE1 (HEX displays).
//              - Input:  4-bit binary digit (0 - 15 / 0x0 - 0xF)
//              - Output: 7-bit active-low segments [6:0] -> [g, f, e, d, c, b, a]
//              0 = Segment ON, 1 = Segment OFF.
// ============================================================================

module seven_seg_decoder (
    input  logic [3:0] digit,
    input  logic       blank,      // 1 = Turn off display
    output logic [6:0] seg
);

    always_comb begin
        if (blank) begin
            seg = 7'b1111111; // All OFF
        end else begin
            case (digit)
                4'h0: seg = 7'b1000000; // 0
                4'h1: seg = 7'b1111001; // 1
                4'h2: seg = 7'b0100100; // 2
                4'h3: seg = 7'b0110000; // 3
                4'h4: seg = 7'b0011001; // 4
                4'h5: seg = 7'b0010010; // 5
                4'h6: seg = 7'b0000010; // 6
                4'h7: seg = 7'b1111000; // 7
                4'h8: seg = 7'b0000000; // 8
                4'h9: seg = 7'b0010000; // 9
                4'hA: seg = 7'b0001000; // A
                4'hB: seg = 7'b0000011; // b
                4'hC: seg = 7'b1000110; // C
                4'hD: seg = 7'b0100001; // d
                4'hE: seg = 7'b0000110; // E
                4'hF: seg = 7'b0001110; // F
                default: seg = 7'b1111111;
            endcase
        end
    end

endmodule
