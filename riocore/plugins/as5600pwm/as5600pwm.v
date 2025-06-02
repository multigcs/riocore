
module as5600pwm
    #(parameter DIVIDER = 250)
     (
         input clk,
         input pwm,
         output reg valid,
         output reg [15:0] angle = 0
     );
    reg [31:0] angle_cnt = 0;
    reg [31:0] counter = 0;

    reg[2:0] SIGr;
    wire SIG_risingedge = (SIGr[2:1]==2'b01);
    wire SIG_fallingedge = (SIGr[2:1]==2'b10);

    always @(posedge clk) begin

        if (counter == 0) begin
            counter <= DIVIDER;
            
            SIGr <= {SIGr[1:0], pwm};

            if (SIG_fallingedge) begin

                angle <= ((angle_cnt + 1)<<5) - 128;

                valid <= 1;
            end else if (SIG_risingedge) begin
                angle_cnt <= 0;
            end else begin
                angle_cnt <= angle_cnt + 1;
                if (angle_cnt > 20000000) begin
                    angle <= 20000000;
                    valid <= 0;
                    angle_cnt <= 0;
                end
            end

        end else begin
            counter <= counter - 1;
        end
    end
endmodule
