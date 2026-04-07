
module freqout
    (
        input clk,
        input signed [31:0] frequency,
        input disabled,
        output reg freq = 0
    );

    wire DIR;
    assign DIR = (frequency > 0);
    reg [31:0] freqCounter = 32'd0;
    reg [31:0] frequencyAbs = 32'd0;
    always @ (posedge clk) begin
        if (DIR) begin
            frequencyAbs <= frequency / 2;
        end else begin
            frequencyAbs <= -frequency / 2;
        end
        freqCounter <= freqCounter + 1;
        if (frequency != 0) begin
            if (freqCounter >= frequencyAbs) begin
                freq <= ~freq;
                freqCounter <= 32'b0;
            end
        end else begin
            freq <= 0;
        end
    end
endmodule
