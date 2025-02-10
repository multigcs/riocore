
`timescale 1ns/100ps

module testb;
    reg clk = 1;
    always #1 clk = !clk;

    // pins
    wire bit;
    // interface
    reg set = 0;
    reg reset = 0;

    initial begin
        $dumpfile("testb.vcd");
        $dumpvars(0, clk);
        // pins
        $dumpvars(1, bit);
        // interface
        $dumpvars(2, set);
        $dumpvars(3, reset);

        #6
        set = 1;
        #2
        set = 0;
        #6

        reset = 1;
        #2
        reset = 0;
        #6

        set = 1;
        #6
        reset = 1;
        #2
        reset = 0;
        #6
        set = 0;


        #5 $finish;
    end

    flipflop_in #(
        .DEFAULT(0)
    ) flipflop_inflipflop_in (
        .clk(clk),
        .set(set),
        .reset(reset),
        .bit(bit)
    );

endmodule
