
module prv32_gpio (
        input wire         clk,
        input wire         reset_n,
        input wire         gpios_sel,
        input wire [31:0]  gpios_data_i,
        input wire         we,
        output wire        gpios_ready,
        output wire [31:0] gpios_data_o,
        inout wire gpio0,
        inout wire gpio1,
        inout wire gpio2,
        inout wire gpio3,
        inout wire gpio4,
        inout wire gpio5,
        inout wire gpio6,
        inout wire gpio7,
        inout wire gpio8,
        inout wire gpio9,
        inout wire gpio10,
        inout wire gpio11,
        inout wire gpio12,
        inout wire gpio13,
        inout wire gpio14,
        inout wire gpio15
   );

    assign gpios_ready = gpios_sel;
    assign gpios_data_o = {
        gdir,
        gpio15,
        gpio14,
        gpio13,
        gpio12,
        gpio11,
        gpio10,
        gpio9,
        gpio8,
        gpio7,
        gpio6,
        gpio5,
        gpio4,
        gpio3,
        gpio2,
        gpio1,
        gpio0
    };

    reg [15:0] gdir = 'd0;
    reg [15:0] gout = 'd0;

    assign gpio0 = gdir[0] ? gout[0] : 1'bz;
    assign gpio1 = gdir[1] ? gout[1] : 1'bz;
    assign gpio2 = gdir[2] ? gout[2] : 1'bz;
    assign gpio3 = gdir[3] ? gout[3] : 1'bz;
    assign gpio4 = gdir[4] ? gout[4] : 1'bz;
    assign gpio5 = gdir[5] ? gout[5] : 1'bz;
    assign gpio6 = gdir[6] ? gout[6] : 1'bz;
    assign gpio7 = gdir[7] ? gout[7] : 1'bz;
    assign gpio8 = gdir[8] ? gout[8] : 1'bz;
    assign gpio9 = gdir[9] ? gout[9] : 1'bz;
    assign gpio10 = gdir[10] ? gout[10] : 1'bz;
    assign gpio11 = gdir[11] ? gout[11] : 1'bz;
    assign gpio12 = gdir[12] ? gout[12] : 1'bz;
    assign gpio13 = gdir[13] ? gout[13] : 1'bz;
    assign gpio14 = gdir[14] ? gout[14] : 1'bz;
    assign gpio15 = gdir[15] ? gout[15] : 1'bz;

   always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            gout <= 'b0;
            gdir <= 'b0;
        end else if (gpios_sel) begin
            if (we) begin
                gout <= gpios_data_i[15:0];
                gdir <= gpios_data_i[31:16];
            end
        end
    end
endmodule
