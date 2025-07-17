
module interval
    #(parameter DIVIDER = 255)
     (
         input clk,
         input enable,
         input [23:0] ontime,
         input [23:0] interval,
         output reg out = 0
     );

    localparam DIVIDER_BITS = clog2(DIVIDER + 1);
    reg [DIVIDER_BITS:0] counter = 0;
    reg [23:0] timer = 0;

    always @ (posedge clk) begin
        if (counter == DIVIDER) begin
            counter <= 0;
            // each second
            if (enable) begin
                timer <= timer + 1;
                if (timer >= interval) begin
                    timer <= 0;
                end else if (timer <= ontime) begin
                    out <= 1;
                end else begin
                    out <= 0;
                end
            end else begin
                timer <= 0;
                out <= 0;
            end
        end else begin
            counter <= counter + 8'd1;
        end
    end
endmodule
