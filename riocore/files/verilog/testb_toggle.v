
`timescale 1ns/100ps

module testb_toggle;
    reg clk = 0;
    always #1 clk = !clk;

    reg din = 0;
    wire dout;

    initial begin
        $dumpfile("testb_toggle.vcd");
        $dumpvars(0, clk);

        $dumpvars(1, din);
        $dumpvars(2, dout);

        #3
        din = 1;
        #10
        din = 0;
        #20
        din = 1;
        #10
        din = 0;
        #10
        din = 1;
        #20
        din = 0;
        #20
        din = 1;
        #30
        din = 0;
        # 20 $finish;
    end

    toggle toggle0 (
        .clk(clk),
        .din(din),
        .dout(dout)
    );

endmodule
