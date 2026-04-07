
module delay
    #(parameter DELAY = 16, parameter RISING = 1, parameter FALLING = 0)
    (
        input clk,
        input din,
        output reg dout = 0
    );

    //localparam DELAY_BITS = clog2(DELAY + 1);
    localparam DELAY_BITS = 31;
    reg [DELAY_BITS:0] din_cnt = 0;

    always @(posedge clk) begin
        if (dout == 1) begin
            if (din == 0) begin
                if (FALLING == 0) begin
                    din_cnt <= 0;
                    dout <= 0;
                end else if (din_cnt > 0) begin
                    din_cnt <= din_cnt - 1;
                end else begin
                    dout <= 0;
                end
            end else begin
                din_cnt <= DELAY;
            end
        end else begin
            if (din == 1) begin
                if (RISING == 0) begin
                    din_cnt <= DELAY;
                    dout <= 1;
                end else if (din_cnt >= DELAY) begin
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
