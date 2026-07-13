
module pwmout
    #(parameter DIVIDER = 255, parameter BITWIDTH = 32)
     (
         input clk, // clock signal
         input signed [BITWIDTH-1:0] dty, // duty cycle
         input enable, // enable signal
         output reg dir = 0, // direction pin
         output pwm, // pwm pin
         output en // enable pin
     );

    localparam DIVIDER_BITS = clog2(DIVIDER + 1);
    reg [DIVIDER_BITS:0] counter = 0;
    reg [BITWIDTH-1:0] dtyAbs = 0;
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
            end else if (counter >= dtyAbs) begin
                pulse <= 0;
            end
        end else begin
            pulse <= 0;
        end
    end
endmodule
