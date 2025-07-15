
`timescale 1ns/100ps

module testb;
    reg clk = 0;
    always #1 clk = !clk;

    // pins
    wire out;
    // interface
    reg enable = 1;
    reg [23:0] ontime = 24'd0;
    reg [23:0] interval = 24'd0;

    initial begin
        $dumpfile("testb.vcd");
        $dumpvars(0, clk);
        // pins
        $dumpvars(1, out);
        // interface
        $dumpvars(2, enable);
        $dumpvars(3, ontime);
        $dumpvars(4, interval);

        enable = 1;
        interval = 50;
        ontime = 10;
        #1000
        ontime = 20;

        #1000
        interval = 30;
        ontime = 10;


        #4000 $finish;
    end

    interval #(
        .DIVIDER(1)
    ) intervalinterval (
        .clk(clk),
        .enable(enable),
        .ontime(ontime),
        .interval(interval),
        .out(out)
    );

endmodule
