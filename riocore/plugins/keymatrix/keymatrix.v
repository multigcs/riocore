
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
    reg [DIVIDER_BITS - 1:0] delay;

    reg [1:0] step = 0;
    reg [ROW_BITS - 1:0] row = 0;
    reg [COL_BITS - 1:0] col = 0;
    reg [VALUE_BITS - 1:0] read = 0;
    always @ (posedge clk) begin
        if (step == 0) begin
            if (col == 0 && row == 0) begin
                value <= read;
                read <= 0;
            end
            cols <= ~(1<<col);
            step <= 1;
        end else if (step == 1) begin
            if (delay == 0) begin
                delay <= DIVIDER;
                step <= 2;
            end else begin
                delay <= delay - 1;
            end
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
            step <= 0;
        end
    end

endmodule
