
module hbridge
    #(parameter DIVIDER = 255)
     (
         input clk,
         input signed [31:0] dty,
         input enable,
         output reg out1,
         output reg out2,
         output en
     );

    localparam DIVIDER_BITS = clog2(DIVIDER + 1);
    reg [DIVIDER_BITS:0] counter = 0;

    reg [31:0] dtyAbs = 32'd0;
    reg pulse = 0;
    assign en = enable;
    always @ (posedge clk) begin
        if (dty > 0) begin
            dtyAbs <= dty;
        end else begin
            dtyAbs <= -dty;
        end
        if (dtyAbs != 0) begin
            counter <= counter + 8'd1;
            if (counter == DIVIDER) begin
                if (enable) begin
                    if (dty > 0) begin
                        out1 <= 1;
                        out2 <= 0;
                    end else begin
                        out1 <= 0;
                        out2 <= 1;
                    end
                end
                counter <= 0;
            end else if (counter == dtyAbs) begin
                out1 <= 0;
                out2 <= 0;
            end
        end else begin
            out1 <= 0;
            out2 <= 0;
        end
    end
endmodule
