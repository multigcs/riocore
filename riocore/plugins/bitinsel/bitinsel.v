/* verilator lint_off WIDTHTRUNC */
module bitinsel
    #(
         parameter BITS = 16,
         parameter WIDTH = 4,
         parameter DIVIDER = 100000
     )
     (
         input clk,
         output reg [BITS-1:0] data_in = 0,
         input bit_in,
         output reg [WIDTH-1:0] addr = 0
     );
    reg [BITS-1:0] selector = 0;
    reg [31:0] counter = 0;

    always @(posedge clk) begin
        if (counter == 0) begin
            counter <= DIVIDER;
            data_in[addr] <= bit_in;
            addr <= addr + 1;
        end else begin
            counter <= counter - 1;
        end
    end
endmodule
