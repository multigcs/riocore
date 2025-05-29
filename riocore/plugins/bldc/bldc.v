
module bldc
    #(
         parameter START = 0,
         parameter VEL_RANGE = 256,
         parameter PWM_RANGE = 256,
         parameter PWM_DIVIDER = 1000,
         parameter FEEDBACK_DIVIDER = 16,
         parameter TLEN_BITS = 6,
         parameter TDEPTH_BITS = 8,
         parameter PWM_MODE = 0,
         parameter SINE_TBL = "sine.mem"
     )
     (
         input clk,
         input enable,
         input [7:0] mode,
         input signed [15:0] velocity,
         input signed [15:0] offset,
         input [15:0] feedback,
         output en,
         output u_p,
         output v_p,
         output w_p,
         output u_n,
         output v_n,
         output w_n
     );

    assign en = enable;

    localparam PWM_RANGE_BITS = clog2(PWM_RANGE + 1);
    localparam TLEN = (1<<(TLEN_BITS));
    localparam TMAX = TLEN / 4 - 1;
    localparam TOFF_V = TLEN / 3 - 1;
    localparam TOFF_W = TLEN / 3 * 2 - 1;

    reg direction = 0;
    reg [PWM_RANGE_BITS-1:0] voltage = 0;
    reg [TLEN_BITS-1:0] tpos_u = 0;
    reg [TLEN_BITS-1:0] tpos_v = 0;
    reg [TLEN_BITS-1:0] tpos_w = 0;
    reg signed [7:0] tangle = 0;

    reg [31:0] clk_cnt = 0;
    reg [PWM_RANGE_BITS-1:0] dty_u = 0;
    reg [PWM_RANGE_BITS-1:0] dty_v = 0;
    reg [PWM_RANGE_BITS-1:0] dty_w = 0;

    reg [31:0] counter = 0;
    reg pwmclk = 0;
    always @(posedge clk) begin
        if (counter == 0) begin
            counter <= PWM_DIVIDER;
            pwmclk <= ~pwmclk;
        end else begin
            counter <= counter - 1;
        end
    end

    always@ (posedge(clk)) begin
        if (mode == 1) begin
            // position mode (no feedback)
            tpos_u <= offset;
            tpos_v <= offset + TOFF_V;
            tpos_w <= offset + TOFF_W;
        end else begin
            if (mode == 2) begin
                // calibration mode (to find offset)
                tangle <= 0;
            end else if (velocity > 0) begin
                tangle <= TMAX;
            end else if (velocity < 0) begin
                tangle <= -TMAX;
            end else begin
                tangle <= 0;
            end
            tpos_u <= (feedback / FEEDBACK_DIVIDER) + offset + tangle;
            tpos_v <= (feedback / FEEDBACK_DIVIDER) + offset + tangle + TOFF_V;
            tpos_w <= (feedback / FEEDBACK_DIVIDER) + offset + tangle + TOFF_W;
        end
        if (velocity > 0) begin
            voltage <= velocity;
        end else if (velocity < 0) begin
            voltage <= -velocity;
        end else begin
            voltage <= 0;
        end
    end


    reg [TDEPTH_BITS-1:0] sine_tbl [0:TLEN-1];
    initial begin
        $readmemh(SINE_TBL, sine_tbl);
    end

    reg [7:0] calc_stat = 0;
    reg [15:0] in_a = 0;
    reg [15:0] in_b = 0;
    reg load = 0;
    wire out_valid;
    wire [31:0] out_prod;
    multiplier multiplier0 (
      .clk (clk),
      .in_a (in_a),
      .in_b (in_b),
      .load (load),
      .out_valid (out_valid),
      .out_prod (out_prod)
    );
    always@ (posedge(clk)) begin
        // do serial calculation to not use DSP blocks
        // dty_u <= sine_tbl[tpos_u] * voltage / VEL_RANGE;
        // dty_v <= sine_tbl[tpos_v] * voltage / VEL_RANGE;
        // dty_w <= sine_tbl[tpos_w] * voltage / VEL_RANGE;
        if (load == 0) begin
            if (calc_stat == 0) begin
                in_a <= sine_tbl[tpos_u];
                in_b <= voltage;
                load <= 1;
            end else if (calc_stat == 1) begin
                in_a <= sine_tbl[tpos_v];
                in_b <= voltage;
                load <= 1;
            end else if (calc_stat == 2) begin
                in_a <= sine_tbl[tpos_w];
                in_b <= voltage;
                load <= 1;
            end
        end else if (out_valid == 1) begin
            load <= 0;
            if (calc_stat == 0) begin
                calc_stat <= 1;
                dty_u <= out_prod / VEL_RANGE;
            end else if (calc_stat == 1) begin
                calc_stat <= 2;
                dty_v <= out_prod / VEL_RANGE;
            end else if (calc_stat == 2) begin
                calc_stat <= 0;
                dty_w <= out_prod / VEL_RANGE;
            end
        end
    end

    wire u;
    wire v;
    wire w;

    if (PWM_MODE == 1) begin
        assign u_p = u & enable & (sine_tbl[tpos_u] > 195);
        assign v_p = v & enable & (sine_tbl[tpos_v] > 195);
        assign w_p = w & enable & (sine_tbl[tpos_w] > 195);
        assign u_n = enable & (sine_tbl[tpos_u] < 65);
        assign v_n = enable & (sine_tbl[tpos_v] < 65);
        assign w_n = enable & (sine_tbl[tpos_w] < 65);
    end else if (PWM_MODE == 2) begin
        assign u_p = u & enable & (sine_tbl[tpos_u] > 195);
        assign v_p = v & enable & (sine_tbl[tpos_v] > 195);
        assign w_p = w & enable & (sine_tbl[tpos_w] > 195);
        assign u_n = ~u & enable & (sine_tbl[tpos_u] < 65);
        assign v_n = ~v & enable & (sine_tbl[tpos_v] < 65);
        assign w_n = ~w & enable & (sine_tbl[tpos_w] < 65);
    end else if (PWM_MODE == 3) begin
        assign u_p = u & enable & (sine_tbl[tpos_u] > 195);
        assign v_p = v & enable & (sine_tbl[tpos_v] > 195);
        assign w_p = w & enable & (sine_tbl[tpos_w] > 195);
        assign u_n = enable & ((sine_tbl[tpos_u] < 65) | ~u_p & (sine_tbl[tpos_u] > 195));
        assign v_n = enable & ((sine_tbl[tpos_v] < 65) | ~v_p & (sine_tbl[tpos_v] > 195));
        assign w_n = enable & ((sine_tbl[tpos_w] < 65) | ~w_p & (sine_tbl[tpos_w] > 195));
    end else begin
        assign u_p = u & enable;
        assign v_p = v & enable;
        assign w_p = w & enable;
        assign u_n = ~u & enable;
        assign v_n = ~v & enable;
        assign w_n = ~w & enable;
    end

    sine_pwm #(.PWM_RANGE(PWM_RANGE), .PWM_RANGE_BITS(PWM_RANGE_BITS)) sine_pwm_u (
      .clk (pwmclk),
      .dty (dty_u),
      .pwm (u)
    );

    sine_pwm  #(.PWM_RANGE(PWM_RANGE), .PWM_RANGE_BITS(PWM_RANGE_BITS)) sine_pwm_v (
      .clk (pwmclk),
      .dty (dty_v),
      .pwm (v)
    );

    sine_pwm  #(.PWM_RANGE(PWM_RANGE), .PWM_RANGE_BITS(PWM_RANGE_BITS)) sine_pwm_w (
      .clk (pwmclk),
      .dty (dty_w),
      .pwm (w)
    );

endmodule

module sine_pwm
    #(
        parameter PWM_RANGE = 256,
        parameter PWM_RANGE_BITS = 8
     )
     (
         input clk,
         input [PWM_RANGE_BITS-1:0] dty,
         output pwm
     );

    reg pulse = 0;
    assign pwm = pulse;
    reg [PWM_RANGE_BITS:0] counter = 0;
    always @ (posedge clk) begin
        if (dty != 0) begin
            counter <= counter + 1;
            if (counter == (PWM_RANGE - 1)) begin
                pulse <= 1'd1;
                counter <= 0;
            end else if (counter >= dty) begin
                pulse <= 1'd0;
            end
        end else begin
            pulse <= 1'd0;
        end
    end
endmodule

module multiplier
    (
        input [15:0] in_a,
        input [15:0] in_b,
        input clk,
        input load,
        output reg out_valid,
        output reg [31:0] out_prod
    );

    always @ (posedge clk) begin
        out_valid <= 1'b0;
        if (load) begin
            out_prod <= in_a * in_b;
            out_valid <= 1'b1;
        end
    end
endmodule
