
module keymatrix
    #(parameter COLS = 4, parameter ROWS = 4, parameter VALUE_BITS = 4, parameter DIVIDER = 1000)
     (
         input clk,
         output reg [COLS - 1:0] cols,
         input [ROWS - 1:0] rows,
         output reg [VALUE_BITS - 1:0] value
     );

    localparam ROW_BITS = clog2(ROWS + 1);
    localparam COL_BITS = clog2(COLS + 1);
    localparam DIVIDER_BITS = clog2(DIVIDER + 1);
    reg [DIVIDER_BITS:0]counter;

    reg scan_clk;
    always @(posedge clk) begin
        if (counter == 0) begin
            counter <= DIVIDER;
            scan_clk <= ~scan_clk;
        end else begin
            counter <= counter - 1;
        end
    end

    reg set = 0;
    reg [ROW_BITS - 1:0] row = 0;
    reg [COL_BITS - 1:0] col = 0;
    reg [VALUE_BITS - 1:0] read = 0;
    always @ (posedge scan_clk) begin
        set <= ~set;
        if (set == 1) begin
            if (col == 0 && row == 0) begin
                value <= read;
                read <= 0;
            end
            cols <= ~(1<<col);
        end else begin
            if (rows[row] == 0) begin
                read <= row + 1 + col * 4;
            end
            if (col < COLS - 1) begin
                col <= col + 1;
            end else begin
                col <= 0;
                if (row < ROWS - 1) begin
                    row <= row + 1;
                end else begin
                    row <= 0;
                end
            end
        end
    end

endmodule
