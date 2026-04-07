
module pwmmod
    #(parameter DIVIDER_FREQ = 255, parameter DIVIDER_DTY = 128)
    (
        input clk,
        input din,
        output reg dout = 0
    );
    localparam DIVIDER_BITS = clog2(DIVIDER_FREQ + 1);
    reg [DIVIDER_BITS-1:0] counter = 0;
    always @ (posedge clk) begin
        if (din == 1) begin
            counter <= counter + 1;
            if (counter == DIVIDER_FREQ) begin
                dout <= 1;
                counter <= 0;
            end else if (counter == DIVIDER_DTY) begin
                dout <= 0;
            end
        end else begin
            dout <= 0;
            counter <= DIVIDER_FREQ;
        end
    end
endmodule
