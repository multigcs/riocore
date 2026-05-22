
`timescale 1ns/100ps

module testb_pwm;
    reg clk = 0;
    always #1 clk = !clk;

    reg din = 0;
    wire dout1;
    wire dout2;

    initial begin
        $dumpfile("testb_pwm.vcd");
        $dumpvars(0, clk);

        $dumpvars(1, din);
        $dumpvars(2, dout1);
        $dumpvars(3, dout2);

        #3
        din = 1;
        #200
        din = 0;
        #100
        din = 1;
        #100
        din = 0;
        #50 $finish;
    end

    pwm #(.DIVIDER_FREQ(10), .DIVIDER_DTY(3)) pwm1 (
        .clk(clk),
        .din(din),
        .dout(dout1)
    );

    pwm #(.DIVIDER_FREQ(20), .DIVIDER_DTY(10)) pwm2 (
        .clk(clk),
        .din(din),
        .dout(dout2)
    );

endmodule
