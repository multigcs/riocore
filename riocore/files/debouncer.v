
module debouncer
    #(parameter WIDTH = 16)
    (
        input clk,
        input din,
        output reg dout = 0
    );

    localparam WIDTH_BITS = clog2(WIDTH + 1);

    reg [WIDTH_BITS:0] din_cnt = 0;

    always @(posedge clk) begin
        if (din == 0) begin
            if (din_cnt > 0) begin
                din_cnt <= din_cnt - 1;
            end else begin
                dout <= 0;
            end
        end else begin
            if (din_cnt > WIDTH) begin
                dout <= 1;
            end else begin
                din_cnt <= din_cnt + 1;
            end
        end
    end
endmodule
