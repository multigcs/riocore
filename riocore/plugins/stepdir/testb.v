
`timescale 1ns/100ps

module testb;
    reg clk = 0;
    always #1 clk = !clk;

    // pins
    wire step;
    wire dir;
    wire en;
    wire step2;
    wire dir2;
    wire en2;
    // interface
    reg signed [31:0] velocity = 32'd0;
    reg enable = 1;
    wire signed [31:0] position;
    wire signed [31:0] position2;

    initial begin
        $dumpfile("testb.vcd");
        $dumpvars(0, clk);
        // pins
        $dumpvars(1, step);
        $dumpvars(2, dir);
        $dumpvars(3, en);
        $dumpvars(4, step2);
        $dumpvars(5, dir2);
        $dumpvars(6, en2);
        // interface
        $dumpvars(7, velocity);
        $dumpvars(8, enable);
        $dumpvars(9, position);
        $dumpvars(10, position2);

        velocity = 50;
        #1000
        velocity = 0;
        #100
        velocity = -100;
        #1000
        velocity = -50;
        #1000
        velocity = 50;

        # 1000 $finish;
    end

    stepdir #(.PULSE_LEN(0), .DIR_DELAY(10)) stepdirstepdir (
        .clk(clk),
        .velocity(velocity),
        .enable(enable),
        .position(position),
        .step(step),
        .dir(dir),
        .en(en)
    );

    stepdir #(.PULSE_LEN(10), .DIR_DELAY(5)) stepdirstepdir2 (
        .clk(clk),
        .velocity(velocity),
        .enable(enable),
        .position(position2),
        .step(step2),
        .dir(dir2),
        .en(en2)
    );

endmodule
