
module blink
    #(parameter DIVIDER = 100000)
    (
        input clk,
        output led
    );
    reg rled;
    reg [31:0] counter;
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
