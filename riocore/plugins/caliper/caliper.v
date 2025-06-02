
module caliper
    #(parameter TIMEOUT=10000)
    (
        input clk,
        input data,
        input clock,
        output reg mode = 0,
        output reg [23:0] position = 0
    );

    localparam TIMEOUT_BITS = clog2(TIMEOUT + 1);
    reg [TIMEOUT_BITS-1:0] counter = 0;
    reg [7:0] data_pos = 0;
    reg [21:0] tmp_position = 0;
    reg[2:0] CLOCKr; always @(posedge clk) CLOCKr <= {CLOCKr[1:0], clock};
    wire CLOCK_risingedge = (CLOCKr[2:1]==2'b01);

    always @(posedge clk) begin
        if (counter == 0) begin
            data_pos <= 0;
            tmp_position <= 0;
        end else begin
            counter <= counter - 1;
        end

        if (CLOCK_risingedge == 1) begin
            counter <= TIMEOUT;
            if (data_pos < 21) begin
                tmp_position <= {data, tmp_position[20:1]};
            end
            if (data_pos == 23) begin
                mode <= data;
                position <= tmp_position;
            end
            data_pos <= data_pos + 1;
        end
    end
endmodule
