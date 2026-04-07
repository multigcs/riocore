
module blink
    #(parameter DIVIDER = 100000)
    (
        input clk,
        output led
    );
    reg rled = 0;
    localparam DIVIDER_BITS = clog2(DIVIDER + 1);
    reg [DIVIDER_BITS:0] counter = 0;
    assign led = rled;
    always @(posedge clk) begin
        if (counter == 0) begin
            counter <= DIVIDER;
            rled <= ~rled;
        end else begin
            counter <= counter - 1;
        end
    end
endmodule
