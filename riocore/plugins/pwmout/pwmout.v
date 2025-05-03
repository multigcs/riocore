
module pwmout
    #(parameter DIVIDER = 255)
     (
         input clk,
         input signed [31:0] dty,
         input enable,
         output reg dir = 0,
         output pwm,
         output en
     );

    localparam DIVIDER_BITS = clog2(DIVIDER + 1);
    reg [DIVIDER_BITS:0] counter = 0;

    reg [31:0] dtyAbs = 32'd0;
    reg pulse = 0;
    assign en = enable;
    assign pwm = pulse;
    always @ (posedge clk) begin
        if (dty > 0) begin
            dtyAbs <= dty;
            dir <= 1;
        end else begin
            dtyAbs <= -dty;
            dir <= 0;
        end
        if (enable == 0) begin
            pulse <= 0;
        end else if (dtyAbs != 0) begin
            counter <= counter + 8'd1;
            if (counter == DIVIDER) begin
                if (enable) begin
                    pulse <= 1;
                end
                counter <= 0;
            end else if (counter => dtyAbs) begin
                pulse <= 0;
            end
        end else begin
            pulse <= 0;
        end
    end
endmodule
