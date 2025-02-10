
`timescale 1ns/100ps

module testb_debouncer;
    reg clk = 0;
    always #1 clk = !clk;

    reg din = 0;
    wire dout;

    initial begin
        $dumpfile("testb_debouncer.vcd");
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
        #20
        din = 0;
        #1
        din = 1;
        #100
        din = 0;
        #10


        # 100 $finish;
    end

    debouncer #(.WIDTH(5)) debouncer0 (
        .clk(clk),
        .din(din),
        .dout(dout)
    );

endmodule
