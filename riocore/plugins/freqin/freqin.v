
module freqin
    #(parameter RESET_CNT = 25000000)
     (
         input clk,
         input freq,
         output reg valid = 0,
         output reg [31:0] frequency = 0
     );
    reg [31:0] freq_cnt = 0;
    reg error = 1;

    reg[2:0] SIGr;  always @(posedge clk) SIGr <= {SIGr[1:0], freq};
    wire SIG_risingedge = (SIGr[2:1]==2'b01);

    always @(posedge clk)
    begin
        if (SIG_risingedge) begin
            if (error == 0) begin
                frequency <= freq_cnt + 1;
                valid <= 1;
            end else begin
                error <= 0;
            end
            freq_cnt <= 0;
        end else begin
            freq_cnt <= freq_cnt + 1;
            if (freq_cnt > RESET_CNT) begin
                frequency <= 0;
                valid <= 0;
                error <= 1;
                freq_cnt <= 0;
            end
        end
    end
endmodule
