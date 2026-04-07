
`timescale 1ns/100ps

module testb;
    reg clk = 0;
    always #1 clk = !clk;

    // pins
    wire mosi;
    wire sclk;
    wire sel;
    // interface
    reg [9:0] value;

    initial begin
        $dumpfile("testb.vcd");
        $dumpvars(0, clk);
        // pins
        $dumpvars(1, mosi);
        $dumpvars(2, sclk);
        $dumpvars(3, sel);
        // interface
        $dumpvars(4, value);

        value = 1023;
        #500
        value = 1;
        #500
        value = 512;

        #1000 $finish;

    end

    tlc5615 #(
        .DIVIDER(1)
    ) tlc5615 (
        .clk(clk),
        .value(value),
        .mosi(mosi),
        .sclk(sclk),
        .sel(sel)
    );

endmodule
