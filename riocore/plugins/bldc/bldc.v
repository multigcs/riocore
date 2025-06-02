
module bldc
    #(
         parameter START = 0,
         parameter VEL_RANGE = 256,
         parameter PWM_DIVIDER = 1000,
         parameter FEEDBACK_DIVIDER = 16,
         parameter SINE_LEN_BITS = 6,
         parameter SINE_RES_BITS = 8,
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

    localparam SINE_LEN = (1<<(SINE_LEN_BITS));
    localparam SINE_CENTER = (1<<SINE_RES_BITS) / 2 - 1;
    localparam TABLE_LEN = (1<<(SINE_LEN_BITS-1));
    localparam THALF = SINE_LEN / 2;
    localparam TMAX = SINE_LEN / 4 - 1;
    localparam TOFF_V = SINE_LEN / 3 - 1;
    localparam TOFF_W = SINE_LEN / 3 * 2 - 1;

    reg direction = 0;
    reg [SINE_RES_BITS:0] voltage = 0;
    reg [SINE_LEN_BITS-1:0] tpos_u = 0;
    reg [SINE_LEN_BITS-1:0] tpos_v = 0;
    reg [SINE_LEN_BITS-1:0] tpos_w = 0;
    reg signed [7:0] tangle = 0;

    reg [31:0] clk_cnt = 0;
    reg [SINE_RES_BITS:0] dty_u = 0;
    reg [SINE_RES_BITS:0] dty_v = 0;
    reg [SINE_RES_BITS:0] dty_w = 0;

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
                tangle <= -TMAX;
            end else if (velocity < 0) begin
                tangle <= TMAX;
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


    reg [SINE_RES_BITS-1:0] sine_tbl [0:TABLE_LEN-1];
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
                if (tpos_u >= THALF) begin
                    in_a <= SINE_CENTER - sine_tbl[tpos_u - THALF];
                end else begin
                    in_a <= SINE_CENTER + sine_tbl[tpos_u];
                end
                in_b <= voltage;
                load <= 1;
            end else if (calc_stat == 1) begin
                if (tpos_v >= THALF) begin
                    in_a <= SINE_CENTER - sine_tbl[tpos_v - THALF];
                end else begin
                    in_a <= SINE_CENTER + sine_tbl[tpos_v];
                end
                in_b <= voltage;
                load <= 1;
            end else if (calc_stat == 2) begin
                if (tpos_w >= THALF) begin
                    in_a <= SINE_CENTER - sine_tbl[tpos_w - THALF];
                end else begin
                    in_a <= SINE_CENTER + sine_tbl[tpos_w];
                end
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

    assign u_p = u & enable;
    assign v_p = v & enable;
    assign w_p = w & enable;
    assign u_n = ~u & enable;
    assign v_n = ~v & enable;
    assign w_n = ~w & enable;

    sine_pwm #(.PWM_RES_BITS(SINE_RES_BITS)) sine_pwm_u (
      .clk (pwmclk),
      .dty (dty_u),
      .pwm (u)
    );

    sine_pwm  #(.PWM_RES_BITS(SINE_RES_BITS)) sine_pwm_v (
      .clk (pwmclk),
      .dty (dty_v),
      .pwm (v)
    );

    sine_pwm  #(.PWM_RES_BITS(SINE_RES_BITS)) sine_pwm_w (
      .clk (pwmclk),
      .dty (dty_w),
      .pwm (w)
    );

endmodule

module sine_pwm
    #(
        parameter PWM_RES_BITS = 8
     )
     (
         input clk,
         input [PWM_RES_BITS-1:0] dty,
         output pwm
     );

    localparam PWM_RANGE = (1<<(PWM_RES_BITS-1));

    reg pulse = 0;
    assign pwm = pulse;
    reg [PWM_RES_BITS-1:0] counter = 0;
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
