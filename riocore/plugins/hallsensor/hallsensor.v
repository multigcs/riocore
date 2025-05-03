
module hallsensor
    #(
         parameter BITS = 32
     )
     (
         input clk,
         input a,
         input b,
         input c,
         output reg signed [BITS-1:0] position = 0
     );

    reg[2:0] Ar;  always @(posedge clk) Ar <= {Ar[1:0], a};
    wire Arise = (Ar[2:1]==2'b01);
    wire Afall = (Ar[2:1]==2'b10);

    reg[2:0] Br;  always @(posedge clk) Br <= {Br[1:0], b};
    wire Brise = (Br[2:1]==2'b01);
    wire Bfall = (Br[2:1]==2'b10);

    reg[2:0] Cr;  always @(posedge clk) Cr <= {Cr[1:0], c};
    wire Crise = (Cr[2:1]==2'b01);
    wire Cfall = (Cr[2:1]==2'b10);

    always @(posedge clk) begin

        if (Arise) begin
            if (b) begin
                position <= position - 1;
            end else begin
                position <= position + 1;
            end
        end else if (Afall) begin
            if (b) begin
                position <= position + 1;
            end else begin
                position <= position - 1;
            end

        end if (Brise) begin
            if (c) begin
                position <= position - 1;
            end else begin
                position <= position + 1;
            end
        end else if (Bfall) begin
            if (c) begin
                position <= position + 1;
            end else begin
                position <= position - 1;
            end

        end if (Crise) begin
            if (b) begin
                position <= position + 1;
            end else begin
                position <= position - 1;
            end
        end else if (Cfall) begin
            if (b) begin
                position <= position - 1;
            end else begin
                position <= position + 1;
            end


        end


    end
endmodule
