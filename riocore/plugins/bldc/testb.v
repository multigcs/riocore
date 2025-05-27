
`timescale 1ns/100ps

module testb;
    reg clk = 0;
    always #1 clk = !clk;

    // pins
    wire u_p;
    wire v_p;
    wire w_p;
    wire u_n;
    wire v_n;
    wire w_n;
    wire en;
    // interface
    reg signed [11:0] feedback = 16'd100;
    reg signed [15:0] velocity = 16'd100;
    reg signed [7:0] offset = 8'd0;
    reg enable = 1;
    reg [7:0] mode = 8'd0;

    always #100 feedback = feedback + 2;

    initial begin
        $dumpfile("testb.vcd");
        $dumpvars(0, clk);
        // pins
        $dumpvars(1, u_p);
        $dumpvars(2, v_p);
        $dumpvars(3, w_p);
        $dumpvars(4, u_n);
        $dumpvars(5, v_n);
        $dumpvars(6, w_n);
        $dumpvars(7, en);
        // interface
        $dumpvars(8, velocity);
        $dumpvars(9, feedback);
        $dumpvars(10, enable);
        $dumpvars(11, mode);

        #500000 $finish;
    end

    bldc #(
        .PWMMODE(0),
        .FEEDBACK_DIVIDER(16),
        .DIVIDER(0)
    ) bldcbldc (
        .clk(clk),
        .velocity(velocity),
        .offset(offset),
        .enable(enable),
        .mode(mode),
        .feedback(feedback),
        .u_p(u_p),
        .v_p(v_p),
        .w_p(w_p),
        .u_n(u_n),
        .v_n(v_n),
        .w_n(w_n),
        .en(en)
    );

endmodule
