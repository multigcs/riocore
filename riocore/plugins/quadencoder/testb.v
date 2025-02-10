
`timescale 1ns/100ps

module testb;
    reg clk = 0;
    always #1 clk = !clk;

    // pins
    reg a = 0;
    reg b = 0;
    // interface
    wire signed [31:0] position;

    initial begin
        $dumpfile("testb.vcd");
        $dumpvars(0, clk);
        // pins
        $dumpvars(1, a);
        $dumpvars(2, b);
        // interface
        $dumpvars(3, position);

        #60
        a = 1;
        #60
        b = 1;
        #60
        a = 0;
        #60
        b = 0;
        #60
        #60
        a = 1;
        #60
        b = 1;
        #60
        a = 0;
        #60
        b = 0;
        #60
        #60
        a = 1;
        #60
        b = 1;
        #60
        a = 0;
        #60
        b = 0;
        #60
        a = 1;
        #60
        b = 1;
        #60
        a = 0;
        #60
        b = 0;
        #60
        a = 1;
        #60
        b = 1;
        #60
        a = 0;
        #60
        b = 0;
        #60
        a = 1;
        #60
        b = 1;
        #60
        a = 0;
        #60
        b = 0;
        #60


        b = 1;
        #60
        a = 1;
        #60
        b = 0;
        #60
        a = 0;
        #60
        b = 1;
        #60
        a = 1;
        #60
        b = 0;
        #60
        a = 0;
        #60
        b = 1;
        #60
        a = 1;
        #60
        b = 0;
        #60
        a = 0;
        #60
        b = 1;
        #60
        a = 1;
        #60
        b = 0;
        #60
        a = 0;
        #60
        b = 1;
        #60
        a = 1;
        #60
        b = 0;
        #60
        a = 0;
        #60
        b = 1;
        #60
        a = 1;
        #60
        b = 0;
        #60
        a = 0;
        #60



        # 60 $finish;

    end

    quadencoder #(
        .QUAD_TYPE(2)
    ) quadencoder (
        .clk(clk),
        .position(position),
        .a(a),
        .b(b)
    );

endmodule
