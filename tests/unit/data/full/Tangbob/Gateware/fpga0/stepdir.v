
module stepdir
    #(parameter PULSE_LEN = 2, parameter DIR_DELAY = 1)
    (
        input clk,
        input enable,
        input signed [31:0] velocity,
        output reg signed [31:0] position = 32'd0,
        output reg dir = 0,
        output reg step = 0,
        output en
    );
    wire dirFlag;
    assign dirFlag = (velocity >= 0);
    reg dir_changed = 0;
    reg [31:0] jointCounter = 32'd0;
    reg [31:0] velocityAbs = 32'd0;
    reg [31:0] pulseEnd = 32'd0;
    assign en = enable;

    always @ (posedge clk) begin
        if (dirFlag) begin
            velocityAbs <= velocity;
        end else begin
            velocityAbs <= -velocity;
        end
    end

    always @ (posedge clk) begin
        if (PULSE_LEN == 0) begin
            pulseEnd <= velocityAbs / 2;
        end else begin
            pulseEnd <= PULSE_LEN;
        end
    end

    always @ (posedge clk) begin
        if (velocity != 0 && enable == 1 && jointCounter < velocityAbs) begin
            if (step == 0 && dir != dirFlag) begin
                dir <= dirFlag;
                dir_changed <= 1;
                jointCounter <= 0;

            end else if (dir_changed && jointCounter < DIR_DELAY) begin
                jointCounter <= jointCounter + 1;

            end else if (dir_changed) begin
                dir_changed <= 0;
                jointCounter <= 0;

            end else begin
                if (jointCounter == 0) begin
                    if (dir) begin
                        position <= position + 1;
                    end else begin
                        position <= position - 1;
                    end
                end

                if (jointCounter < pulseEnd) begin
                    step <= 1;
                end else begin
                    step <= 0;
                end

                jointCounter <= jointCounter + 1;

            end

        end else begin
            jointCounter <= 0;
        end
    end
endmodule

