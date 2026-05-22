
`timescale 1ns/100ps

module testb_debounce;
    reg clk = 0;
    always #1 clk = !clk;

    reg din = 0;
    wire dout;

    initial begin
        $dumpfile("testb_debounce.vcd");
        $dumpvars(0, clk);

        $dumpvars(1, din);
        $dumpvars(2, dout);

        #3
        din = 1;
        #3
        din = 0;
        #10
        din = 1;
        #3
        din = 0;
        #10

        din = 1;
        #40
        din = 0;
        #11
        din = 1;
        #3
        din = 0;
        #6
        din = 1;
        #1
        din = 0;
        #11
        din = 1;
        #100
        din = 0;
        #10


        # 100 $finish;
    end

    debounce #(.DELAY(10)) debounce0 (
        .clk(clk),
        .din(din),
        .dout(dout)
    );

endmodule
