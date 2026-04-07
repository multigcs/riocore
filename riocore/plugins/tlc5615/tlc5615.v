
module tlc5615
    #(parameter DIVIDER = 100000)
     (
         input clk,
         output reg mosi = 0,
         output reg sclk = 0,
         output reg sel = 1,
         input wire [9:0] value
     );

    localparam STATE_START = 0;
    localparam STATE_SEND  = 1;
    localparam STATE_STOP  = 2;
    localparam DIVIDER_BITS = clog2(DIVIDER + 1);

    reg [7:0] state = 0;
    reg [7:0] data_pos = 0;
    reg [11:0] data = 12'd0;
    reg next_clk = 0;

    reg [DIVIDER_BITS-1:0] clk_counter = 0;
    reg mclk = 0;
    always @(posedge clk) begin
        if (clk_counter == 0) begin
            clk_counter <= DIVIDER;
            mclk <= ~mclk;
        end else begin
            clk_counter <= clk_counter - 1;
        end
    end

    always @(posedge mclk) begin
        case(state)
            STATE_START: begin
                sclk <= 0;
                sel <= 0;
                data_pos <= 0;
                data <= {value, 2'd3}; 
                state <= 1;
                next_clk <= 0;
            end
            STATE_SEND: begin
                if (next_clk == 1) begin
                    next_clk <= 0;
                    sclk <= 1;
                end else if (data_pos < 12) begin
                    sclk <= 0;
                    next_clk <= 1;
                    mosi <= data[11 - data_pos];
                    data_pos <= data_pos + 1;
                end else begin
                    state <= 2;
                    mosi <= 0;
                    sclk <= 0;
                end
            end
            STATE_STOP: begin
                sel <= 1;
                state <= state + 1;
            end
            default: begin
                state <= 0;
            end
        endcase
    end
endmodule

