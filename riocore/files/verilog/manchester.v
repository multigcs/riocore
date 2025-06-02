
module manchester_encode
     (
         input clk,
         input clock_in,
         output reg clock_out = 0,
         input data_in,
         output reg data_out = 0
     );

    reg[2:0] CLOCKr;  always @(posedge clk) CLOCKr <= {CLOCKr[1:0], clock_in};
    wire CLOCK_risingedge = (CLOCKr[2:1]==2'b01);
    wire CLOCK_fallingedge = (CLOCKr[2:1]==2'b10);

    always @(posedge clk) begin
        if (CLOCK_risingedge) begin
            clock_out <= 1;
            data_out <= data_in;
        end else if (CLOCK_fallingedge) begin
            clock_out <= 0;
            data_out <= ~data_out;
        end
    end
endmodule

module manchester_decode
     (
         input clk,
         input clock_in,
         output reg clock_out = 0,
         input data_in,
         output reg data_out = 0,
         output reg error = 0
     );

    reg[2:0] CLOCKr;  always @(posedge clk) CLOCKr <= {CLOCKr[1:0], clock_in};
    wire CLOCK_risingedge = (CLOCKr[2:1]==2'b01);
    wire CLOCK_fallingedge = (CLOCKr[2:1]==2'b10);
    reg last = 0;

    always @(posedge clk) begin
        if (CLOCK_risingedge) begin
            clock_out <= 1;
            last <= data_in;
        end else if (CLOCK_fallingedge) begin
            clock_out <= 0;
            if (last != data_in) begin
                data_out <= last;
                error <= 0;
            end else begin
                error <= 1;
            end
        end
    end
endmodule
