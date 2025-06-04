
`timescale 1ns/100ps

module testb;
    reg clk = 0;
    always #1 clk = !clk;

    // pins
    reg a = 0;
    reg b = 0;
    reg c = 0;
    // interface
    wire signed [15:0] angle;
    wire signed [31:0] position;

    initial begin
        $dumpfile("testb.vcd");
        $dumpvars(0, clk);
        // pins
        $dumpvars(1, a);
        $dumpvars(2, b);
        $dumpvars(2, c);
        // interface
        $dumpvars(3, position);
        $dumpvars(4, angle);

        #100
        a = 1;
        #100
        b = 1;
        #100
        c = 1;

        #100
        a = 0;
        #100
        b = 0;
        #100
        c = 0;

        #100
        a = 1;
        #100
        b = 1;
        #100
        c = 1;

        #100
        a = 0;
        #100
        b = 0;
        #100
        c = 0;

        #100
        a = 1;
        #100
        b = 1;
        #100
        c = 1;

        #100
        a = 0;
        #100
        b = 0;
        #100
        c = 0;

        #100
        a = 1;
        #100
        b = 1;
        #100
        c = 1;

        #100
        a = 0;
        #100
        b = 0;
        #100
        c = 0;

        #100
        a = 1;
        #100
        b = 1;
        #100
        c = 1;

        #100
        a = 0;
        #100
        b = 0;
        #100
        c = 0;




        #100
        c = 1;
        #100
        b = 1;
        #100
        a = 1;

        #100
        c = 0;
        #100
        b = 0;
        #100
        a = 0;

        #100
        c = 1;
        #100
        b = 1;
        #100
        a = 1;

        #100
        c = 0;
        #100
        b = 0;
        #100
        a = 0;

        #100
        c = 1;
        #100
        b = 1;
        #100
        a = 1;

        #100
        c = 0;
        #100
        b = 0;
        #100
        a = 0;

        #100
        c = 1;
        #100
        b = 1;
        #100
        a = 1;

        #100
        c = 0;
        #100
        b = 0;
        #100
        a = 0;



        # 60 $finish;

    end

    hallsensor #(
        .BITS(32)
    ) hallsensor (
        .clk(clk),
        .angle(angle),
        .position(position),
        .a(a),
        .b(b),
        .c(c)
    );

endmodule
