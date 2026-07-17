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
        end else if (vin_sel) begin
            if (we) begin
                vin <= vin_data_i;
            end
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
