
module debouncer
    #(parameter DELAY = 16)
    (
        input clk,
        input din,
        output reg dout = 0
    );

    localparam DELAY_BITS = clog2(DELAY + 1);
    reg [DELAY_BITS:0] din_cnt = 0;

    always @(posedge clk) begin
        if (dout == 1) begin
            if (din == 0) begin
                if (din_cnt > 0) begin
                    din_cnt <= din_cnt - 1;
                end else begin
                    dout <= 0;
                end
            end else begin
                din_cnt <= DELAY;
            end
        end else begin
            if (din == 1) begin
                if (din_cnt > DELAY) begin
                    dout <= 1;
                end else begin
                    din_cnt <= din_cnt + 1;
                end
            end else begin
                din_cnt <= 0;
            end
        end
    end
endmodule
