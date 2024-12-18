
`timescale 1ns/100ps

module testb_oneshot;
    reg clk = 0;
    always #1 clk = !clk;

    reg din = 0;
    wire dout;

    initial begin
        $dumpfile("testb_oneshot.vcd");
        $dumpvars(0, clk);

        $dumpvars(1, din);
        $dumpvars(2, dout);

        #3
        din = 1;
        #10
        din = 0;
        #20
        din = 1;
        #30
        din = 0;
        #20
        din = 1;
        #3
        din = 0;
        #7
        din = 1;
        #3
        din = 0;
        #20
        din = 1;
        #3
        din = 0;

        # 100 $finish;
    end

    oneshot #(.PULSE_LEN(6), .RETRIGGER(0)) oneshot0 (
        .clk(clk),
        .din(din),
        .dout(dout)
    );

endmodule
