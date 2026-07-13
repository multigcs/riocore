
module blink
    #(parameter DIVIDER = 100000, parameter DIVIDER_BITS = 24)
    (
        input clk, // clock signal
        output led // output pin
    );
    reg rled = 0;
    reg [DIVIDER_BITS-1:0] counter = 0;
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
