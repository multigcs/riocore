
`timescale 1ns/100ps

module testb;
    reg clk = 0;
    always #1 clk = !clk;

    // pins
    reg a = 0;
    reg b = 0;
    reg z = 0;
    reg indexenable = 0;
    wire indexout;
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
        $dumpvars(4, z);
        $dumpvars(5, indexenable);
        $dumpvars(6, indexout);

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
        indexenable = 1;
        #60
        a = 1;
        #60
        b = 1;
        #60
        a = 0;
        #60
        b = 0;
        z = 1;
        #60
        z = 0;



        #60
        indexenable = 0;
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
        z = 1;
        #30
        indexenable = 1;
        #30
        z = 0;




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
        z = 1;
        #60
        z = 0;





        #60
        indexenable = 0;
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
        z = 1;
        #60
        z = 0;



        #60
        indexenable = 1;
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
        z = 1;
        #60
        z = 0;










        #60
        indexenable = 0;
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
        z = 1;
        #60
        z = 0;





        #60
        indexenable = 0;
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
        z = 1;
        #60
        z = 0;






        # 60 $finish;

    end

    quadencoderz #(
        .QUAD_TYPE(2)
    ) quadencoder (
        .clk(clk),
        .position(position),
        .a(a),
        .b(b),
        .z(z),
        .indexenable(indexenable),
        .indexout(indexout)
    );

endmodule
