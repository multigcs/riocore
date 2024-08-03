
module hx711
    #(parameter DIVIDER = 100, parameter MODE = 0)
    (
        input clk,
        input miso,
        output reg sclk = 0,
        output reg [23:0] weight
    );

    localparam DIVIDER_BITS = clog2(DIVIDER + 1);
    reg [DIVIDER_BITS:0] counter = 0;

    reg [23:0] state = 0;
    reg [7:0] data_pos = 0;
    reg [23:0] tmp_data = 0;
    reg mclk = 0;
    always @(posedge clk) begin
        if (counter == 0) begin
            counter <= DIVIDER;
            mclk <= ~mclk;
        end else begin
            counter <= counter - 1;
        end
    end

    always @(posedge mclk) begin
        if (state == 0) begin
            sclk <= 0;

            if (miso == 0) begin
                data_pos <= 0;
                state <= 1;
                tmp_data <= 0;
            end

        end else if (state == 11) begin
            if (sclk == 0) begin
                sclk <= 1;
            end else if (data_pos < 23) begin
                sclk <= 0;
                tmp_data <= {tmp_data[22:0], miso};
                data_pos <= data_pos + 1;

            end else if (data_pos < MODE) begin
                sclk <= 0;
                data_pos <= data_pos + 1;

            end else begin
                sclk <= 0;
                weight <= tmp_data[23:3];
                state <= state + 1;
            end
        end else if (state <= 600) begin
            state <= state + 1;
        end else begin
            state <= 0;
        end
    end



endmodule

