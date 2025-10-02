
`timescale 1ns/100ps

module testb_delay;
    reg clk = 0;
    always #1 clk = !clk;

    reg din = 0;
    wire dout1;
    wire dout2;

    initial begin
        $dumpfile("testb_delay.vcd");
        $dumpvars(0, clk);

        $dumpvars(1, din);
        $dumpvars(2, dout1);
        $dumpvars(3, dout2);

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
        #100
        din = 0;
        #10


        # 100 $finish;
    end

    delay #(.DELAY(5), .RISING(1), .FALLING(0)) delay1 (
        .clk(clk),
        .din(din),
        .dout(dout1)
    );

    delay #(.DELAY(3), .RISING(0), .FALLING(1)) delay2 (
        .clk(clk),
        .din(din),
        .dout(dout2)
    );

endmodule
