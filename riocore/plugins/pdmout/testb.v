
`timescale 1ns/100ps

module testb;
    reg clk = 0;
    always #1 clk = !clk;

    // pins
    wire pdm;
    wire en;
    // interface
    reg signed [15:0] value = 16'd0;
    reg enable = 0;

    initial begin
        $dumpfile("testb.vcd");
        $dumpvars(0, clk);
        // pins
        $dumpvars(1, pdm);
        $dumpvars(2, enable);
        $dumpvars(3, en);
        $dumpvars(4, value);

        value = 65535;
        #30
        enable = 1;
        #30
        value = 62000;
        #60
        value = 55536;
        #60
        value = 45536;
        #60
        value = 32768;
        #60
        value = 22768;
        #60
        value = 12768;
        #60
        value = 2768;
        #60
        value = 0;

        #60 $finish;
    end

    pdmout #(
        .RESOLUTION(16)
    ) pdmoutpdmout (
        .clk(clk),
        .enable(enable),
        .value(value),
        .pdm(pdm),
        .en(en)
    );

endmodule
