
module oneshot
    #(parameter PULSE_LEN = 10, parameter RETRIGGER = 0, parameter HOLD = 1, parameter EDGE = 0)
    (
        input clk,
        input din,
        output reg dout = 0
    );

    reg[31:0] pulse_cnt = 0;
    reg[2:0] dinr;
    always @(posedge clk) begin
        dinr <= {dinr[1:0], din};
    end

    wire din_risingedge = (dinr[2:1]==2'b01);
    wire din_falingedge = (dinr[2:1]==2'b10);

    always @(posedge clk) begin
        if ((EDGE == 0 || EDGE == 2) && (din_risingedge && ((pulse_cnt == 0 && RETRIGGER == 0) || RETRIGGER == 1))) begin
            dout <= 1;
            pulse_cnt <= PULSE_LEN;
        end else if ((EDGE == 1 || EDGE == 2) && (din_falingedge && ((pulse_cnt == 0 && RETRIGGER == 0) || RETRIGGER == 1))) begin
            dout <= 1;
            pulse_cnt <= PULSE_LEN;
        end else if (pulse_cnt > 0) begin
            pulse_cnt <= pulse_cnt - 1;
        end else begin
            if (HOLD == 0 || dinr[0] == 0) begin
                dout <= 0;
            end
        end
    end
endmodule
