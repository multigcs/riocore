
module prv32_rio_vin (
        input wire         clk,
        input wire         reset_n,
        input wire         vin_sel,
        input wire [31:0]  vin_data_i,
        input wire         we,
        output wire        vin_ready,
        output wire [31:0]  vin_data_o,
        output reg [31:0]  vin
    );

    assign vin_ready = vin_sel;
    assign vin_data_o = vin;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            vin <= 'b0;
        end else if (vin_sel && we) begin
            vin <= vin_data_i;
        end
    end
endmodule

module prv32_rio_vout (
        input wire         clk,
        input wire         reset_n,
        input wire         vout_sel,
        input wire [31:0]  vout_data_i,
        input wire         we,
        output wire        vout_ready,
        output wire [31:0] vout_data_o,
        input wire [31:0]  vout
    );

    assign vout_ready = vout_sel;
    assign vout_data_o = vout;
endmodule

module prv32_utimer (
        input wire         clk,
        input wire         reset_n,
        input wire         utimer_sel,
        input wire [31:0]  utimer_data_i,
        input wire         we,
        output wire        utimer_ready,
        output wire [31:0] utimer_data_o,
        input wire [31:0] systimer
    );

    assign utimer_ready = utimer_sel;
    assign utimer_data_o = systimer;
endmodule

module prv32_pwm (
        input wire         clk,
        input wire         reset_n,
        input wire         pwm_sel,
        input wire [31:0]  pwm_data_i,
        input wire [2:0]   pwm_addr,
        input wire         we,
        output wire        pwm_ready,
        output wire [31:0] pwm_data_o,
        output reg         pwm
    );

    reg [31:0] pwm_total;
    reg [31:0] pwm_value;
    assign pwm_ready = pwm_sel;
    assign pwm_data_o = pwm_value;

    reg [31:0] clk_counter;
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            pwm_total <= 'd0;
            pwm_value <= 'd0;
            pwm <= 'd0;
            clk_counter <= 0;
        end else begin
            clk_counter <= clk_counter + 'd1;
            if (pwm_sel && we) begin
                if (pwm_addr == 0) begin
                    pwm_value <= pwm_data_i;
                end else begin
                    pwm_total <= pwm_data_i;
                end
            end
            if (clk_counter >= pwm_total) begin
                clk_counter <= 'd0;
            end else if (clk_counter >= pwm_value) begin
                pwm <= 'd0;
            end else begin
                pwm <= 'd1;
            end
        end
    end
endmodule
