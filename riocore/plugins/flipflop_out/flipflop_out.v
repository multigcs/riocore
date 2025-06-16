
module flipflop_out
    #(parameter DEFAULT = 0)
     (
         input  clk,
         input  setbit,
         input  reset,
         output reg outbit = DEFAULT
     );

    always @(posedge clk) begin
        if (reset) begin
            outbit <= 0;
        end else if (setbit) begin
            outbit <= 1;
        end
    end
endmodule
