
module pdmout
    #(parameter RESOLUTION = 16) (
        input wire clk,         
        input wire enable,
        input wire [RESOLUTION-1:0] value,
        output wire pdm,
        output wire en
    );

    reg [RESOLUTION:0] PWM_accumulator = 0;
    assign en = enable;
    assign pdm = PWM_accumulator[RESOLUTION];

    always @(posedge clk) begin
        if (enable) begin
            PWM_accumulator <= PWM_accumulator[RESOLUTION-1:0] + value;
        end else begin
            PWM_accumulator <= 0;
        end
    end


endmodule


