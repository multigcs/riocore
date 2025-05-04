
module bldc
    #(parameter START = 0, parameter DIVIDER = 1000, parameter FEEDBACK_DIVIDER = 16)
     (
         input clk,
         input enable,
         input testmode,
         input signed [15:0] velocity,
         input signed [7:0] offset,
         input [7:0] torque,
         input [15:0] feedback,
         output en,
         output u,
         output v,
         output w
     );

    assign en = enable;

    localparam TLEN = 64;
    localparam TOFF_V = TLEN / 3;
    localparam TOFF_W = TLEN / 3 * 2;

    reg direction = 0;
    reg [7:0] velocity_abs = 0;
    reg [31:0] clk_cnt = 0;
    reg [31:0] dty_u = 0;
    reg [31:0] dty_v = 0;
    reg [31:0] dty_w = 0;

    reg [31:0] counter = 0;
    reg pwmclk = 0;
    always @(posedge clk) begin
        if (counter == 0) begin
            counter <= DIVIDER;
            pwmclk <= ~pwmclk;
        end else begin
            counter <= counter - 1;
        end
    end

    reg [5:0] tpos_u = 0;
    reg [5:0] tpos_v = 0;
    reg [5:0] tpos_w = 0;

    always@ (posedge(clk))
    begin
        if (testmode) begin
                tpos_u <= offset;
                tpos_v <= offset + TOFF_V;
                tpos_w <= offset + TOFF_W;
        end else begin
            if (direction) begin
                tpos_u <= (feedback / FEEDBACK_DIVIDER) + offset - torque;
                tpos_v <= (feedback / FEEDBACK_DIVIDER) + offset - torque + TOFF_V;
                tpos_w <= (feedback / FEEDBACK_DIVIDER) + offset - torque + TOFF_W;
            end else begin
                tpos_u <= (feedback / FEEDBACK_DIVIDER) + offset + torque;
                tpos_v <= (feedback / FEEDBACK_DIVIDER) + offset + torque + TOFF_V;
                tpos_w <= (feedback / FEEDBACK_DIVIDER) + offset + torque + TOFF_W;
            end
        end
        if (velocity < 0) begin
            velocity_abs <= velocity * -1;
            direction <= 1;
        end else begin
            velocity_abs <= velocity;
            direction <= 0;
        end
    
        dty_u <= sine_tbl[tpos_u] * velocity_abs / 100;
        dty_v <= sine_tbl[tpos_v] * velocity_abs / 100;
        dty_w <= sine_tbl[tpos_w] * velocity_abs / 100;
    end

    reg [7:0] sine_tbl [0:TLEN-1];
    initial begin
        sine_tbl[0] = 127;
        sine_tbl[1] = 139;
        sine_tbl[2] = 151;
        sine_tbl[3] = 163;
        sine_tbl[4] = 175;
        sine_tbl[5] = 186;
        sine_tbl[6] = 197;
        sine_tbl[7] = 207;
        sine_tbl[8] = 216;
        sine_tbl[9] = 225;
        sine_tbl[10] = 232;
        sine_tbl[11] = 239;
        sine_tbl[12] = 244;
        sine_tbl[13] = 248;
        sine_tbl[14] = 251;
        sine_tbl[15] = 253;
        sine_tbl[16] = 254;
        sine_tbl[17] = 253;
        sine_tbl[18] = 251;
        sine_tbl[19] = 248;
        sine_tbl[20] = 244;
        sine_tbl[21] = 239;
        sine_tbl[22] = 232;
        sine_tbl[23] = 225;
        sine_tbl[24] = 216;
        sine_tbl[25] = 207;
        sine_tbl[26] = 197;
        sine_tbl[27] = 186;
        sine_tbl[28] = 175;
        sine_tbl[29] = 163;
        sine_tbl[30] = 151;
        sine_tbl[31] = 139;
        sine_tbl[32] = 127;
        sine_tbl[33] = 114;
        sine_tbl[34] = 102;
        sine_tbl[35] = 90;
        sine_tbl[36] = 78;
        sine_tbl[37] = 67;
        sine_tbl[38] = 56;
        sine_tbl[39] = 46;
        sine_tbl[40] = 37;
        sine_tbl[41] = 28;
        sine_tbl[42] = 21;
        sine_tbl[43] = 14;
        sine_tbl[44] = 9;
        sine_tbl[45] = 5;
        sine_tbl[46] = 2;
        sine_tbl[47] = 0;
        sine_tbl[48] = 0;
        sine_tbl[49] = 0;
        sine_tbl[50] = 2;
        sine_tbl[51] = 5;
        sine_tbl[52] = 9;
        sine_tbl[53] = 14;
        sine_tbl[54] = 21;
        sine_tbl[55] = 28;
        sine_tbl[56] = 37;
        sine_tbl[57] = 46;
        sine_tbl[58] = 56;
        sine_tbl[59] = 67;
        sine_tbl[60] = 78;
        sine_tbl[61] = 90;
        sine_tbl[62] = 102;
        sine_tbl[63] = 114;
    end

    sine_pwm sine_pwm_u (
      .clk (pwmclk),
      .dty (dty_u),
      .pwm (u)
    );

    sine_pwm sine_pwm_v (
      .clk (pwmclk),
      .dty (dty_v),
      .pwm (v)
    );

    sine_pwm sine_pwm_w (
      .clk (pwmclk),
      .dty (dty_w),
      .pwm (w)
    );

endmodule

module sine_pwm
    #(parameter DIVIDER = 255)
     (
         input clk,
         input signed [31:0] dty,
         output pwm
     );

    reg pulse = 0;
    assign pwm = ~pulse;
    reg [31:0] counter = 32'd0;
    always @ (posedge clk) begin
        if (dty != 0) begin
            counter <= counter + 1;
            if (counter == DIVIDER) begin
                pulse <= 1'd1;
                counter <= 32'd0;
            end else if (counter >= dty) begin
                pulse <= 1'd0;
            end
        end else begin
            pulse <= 1'd0;
        end
    end
endmodule

