
`timescale 1ns/100ps

module testb_oneshot;
    reg clk = 0;
    always #1 clk = !clk;

    reg din = 0;
    wire dout1;
    wire dout2;
    wire dout3;
    wire dout4;

    initial begin
        $dumpfile("testb_oneshot.vcd");
        $dumpvars(0, clk);

        $dumpvars(1, din);
        $dumpvars(2, dout1);
        $dumpvars(3, dout2);
        $dumpvars(4, dout3);
        $dumpvars(5, dout4);

        #3
        din = 1;
        #10
        din = 0;
        #200
        din = 1;
        #30
        din = 0;
        #200
        din = 1;
        #3
        din = 0;
        #70
        din = 1;
        #3
        din = 0;
        #200
        din = 1;
        #190
        din = 0;

        # 200 $finish;
    end

    oneshot #(.PULSE_LEN(60), .RETRIGGER(0), .HOLD(0)) oneshot0 (
        .clk(clk),
        .din(din),
        .dout(dout1)
    );

    oneshot #(.PULSE_LEN(60), .RETRIGGER(1), .HOLD(0)) oneshot1 (
        .clk(clk),
        .din(din),
        .dout(dout2)
    );

    oneshot #(.PULSE_LEN(1), .RETRIGGER(0), .HOLD(1)) oneshot2 (
        .clk(clk),
        .din(din),
        .dout(dout3)
    );

    oneshot #(.PULSE_LEN(1), .RETRIGGER(0), .HOLD(0)) oneshot3 (
        .clk(clk),
        .din(din),
        .dout(dout4)
    );


endmodule
