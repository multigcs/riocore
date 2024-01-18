/* verilator lint_off WIDTH */

module max7219
    #(parameter DIVIDER = 12)
     (
         input clk,
         output reg mosi = 0,
         output reg sclk = 0,
         output reg sel = 1,
         input wire [31:0] value
     );
    parameter cmd = 8'd0;
    reg [7:0] state = 0;
    reg [7:0] data_pos = 0;
    reg [31:0] counter = 0;
    reg mclk = 0;
    reg next_clk = 0;

    reg [7:0] initcnt = 0;


//    wire [15:0] cmddata = {cmd, value};

    reg [15:0] cmddata = 0;

    localparam INIT_DECODEMODE_NONE = {8'h09, 8'h00};
    localparam INIT_INTENSE         = {8'h0a, 8'h0f};
    localparam INIT_SCANLIMIT       = {8'h0b, 8'h07};
    localparam INIT_SD_NORMALOP     = {8'h0c, 8'h01};
    localparam INIT_DT_NORMALOP     = {8'h0c, 8'h01};

    localparam TESTME     = {8'h05, 8'h05};



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
            sclk = 0;
            sel = 0;
            data_pos = 0;
            state = 1;
            next_clk = 0;
        end else if (state == 1) begin
            if (next_clk == 1) begin
                next_clk = 0;
                sclk = 1;
            end else if (data_pos < 16) begin
                sclk = 0;
                mosi = cmddata[15 - data_pos];
                next_clk = 1;
                data_pos = data_pos + 1;
            end else begin
                state = 2;
                mosi = 0;
                sclk = 0;
            end
        end else if (state == 2) begin
            sel = 1;
            state = state + 1;
        end else if (state == 3) begin


            case(initcnt)
                0: begin
                    cmddata <= INIT_DECODEMODE_NONE;
                    initcnt <= initcnt + 1;
                end
                1: begin
                    cmddata <= INIT_INTENSE;
                    initcnt <= initcnt + 1;
                end
                2: begin
                    cmddata <= INIT_SCANLIMIT;
                    initcnt <= initcnt + 1;
                end
                3: begin
                    cmddata <= INIT_SD_NORMALOP;
                    initcnt <= initcnt + 1;
                end
                4: begin
                    cmddata <= TESTME;
                    initcnt <= initcnt + 1;
                end
                5: begin
                    cmddata <= INIT_DT_NORMALOP;
                    initcnt <= 0;
                end
            endcase



            state = 0;
        end
    end
endmodule

