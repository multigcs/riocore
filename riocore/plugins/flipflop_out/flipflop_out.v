
module flipflop_out
    #(parameter DEFAULT = 0)
     (
         input  clk,
         input  set,
         input  reset,
         output reg bit = DEFAULT
     );

    always @(posedge clk) begin
        if (reset) begin
            bit <= 0;
        end else if (set) begin
            bit <= 1;
        end
    end
endmodule
