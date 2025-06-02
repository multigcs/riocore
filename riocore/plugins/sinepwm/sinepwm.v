/* verilator lint_off WIDTH */
/* verilator lint_off DECLFILENAME */

module sinepwm
    #(parameter START = 0, parameter DIVIDER = 1000)
     (
         input clk,
         input enable,
         input signed [31:0] freq,
         output en,
         output pwm_out
     );

    assign en = enable;

    reg [31:0] clk_cnt = 0;
    reg [31:0] freq_abs = 0;
    reg [7:0] cnt = START;
    reg [7:0] dty = 0;

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

    always@ (posedge(pwmclk))
    begin
        clk_cnt <= clk_cnt + 1;
        if (freq < 0) begin
            freq_abs <= -freq;
        end else begin
            freq_abs <= freq;
        end
        if (clk_cnt >= freq_abs) begin
            clk_cnt <= 0;
            if (enable) begin
                dty <= sine_tbl[cnt];
                if (freq_abs != 0) begin
                    if (freq < 0) begin
                        if (cnt == 0) begin
                            cnt <= 29;
                        end else begin
                            cnt <= cnt - 8'd1;
                        end
                    end else begin
                        if (cnt == 29) begin
                            cnt <= 0;
                        end else begin
                            cnt <= cnt + 8'd1;
                        end
                    end
                end
            end else begin
                dty <= 0;
            end
        end
    end

    reg [7:0] sine_tbl [0:29];
    initial begin
        sine_tbl[0] = 128;
        sine_tbl[1] = 153;
        sine_tbl[2] = 177;
        sine_tbl[3] = 199;
        sine_tbl[4] = 217;
        sine_tbl[5] = 232;
        sine_tbl[6] = 242;
        sine_tbl[7] = 247;
        sine_tbl[8] = 247;
        sine_tbl[9] = 242;
        sine_tbl[10] = 232;
        sine_tbl[11] = 217;
        sine_tbl[12] = 199;
        sine_tbl[13] = 177;
        sine_tbl[14] = 153;
        sine_tbl[15] = 128;
        sine_tbl[16] = 103;
        sine_tbl[17] = 79;
        sine_tbl[18] = 57;
        sine_tbl[19] = 39;
        sine_tbl[20] = 24;
        sine_tbl[21] = 14;
        sine_tbl[22] = 9;
        sine_tbl[23] = 9;
        sine_tbl[24] = 14;
        sine_tbl[25] = 24;
        sine_tbl[26] = 39;
        sine_tbl[27] = 57;
        sine_tbl[28] = 79;
        sine_tbl[29] = 103;
    end

    wire dir1;
    sine_pwm sine_pwm1 (
      .clk (pwmclk),
      .dty ({24'h000000, dty}),
      .dir (dir1),
      .pwm (pwm_out)
    );

endmodule

module sine_pwm
    #(parameter DIVIDER = 255)
     (
         input clk,
         input signed [31:0] dty,
         output dir,
         output pwm
     );
    reg [31:0] dtyAbs = 32'd0;

    reg pulse = 0;
    assign pwm = pulse;
    reg direction = 0;
    assign dir = direction;
    reg [31:0] counter = 32'd0;
    always @ (posedge clk) begin
        if (dty > 32'd0) begin
            dtyAbs <= dty;
            direction <= 1'd1;
        end else begin
            dtyAbs <= -dty;
            direction <= 1'd0;
        end
        if (dtyAbs != 0) begin
            counter <= counter + 1;
            if (counter == DIVIDER) begin
                pulse <= 1'd1;
                counter <= 32'd0;
            end else if (counter >= dtyAbs) begin
                pulse <= 1'd0;
            end
        end else begin
            pulse <= 1'd0;
        end
    end
endmodule

