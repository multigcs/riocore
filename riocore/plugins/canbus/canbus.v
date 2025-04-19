
module canbus
    #(parameter DIVIDER=53, parameter IDIVIDER=53)
    (
        input clk,
        input rx,
        output wire tx,
        input enable,
        input wire [31:0] velocity,
        output reg [31:0] position = 'd0,
        output reg [15:0] power = 'd0,
        output reg [7:0] temp = 'd0,
        output reg [3:0] state = 'd0,
        output reg traj,
        output reg mot,
        output reg enc,
        output reg ctrl
    );

    wire rx_ack;
    wire tx2;
    assign tx = (rx_ack && tx2);

    wire rx_valid;
    wire [3:0] rx_dlc;
    wire [10:0] rx_arib;
    wire [63:0] rx_data;
    always @(posedge clk) begin
        if (rx_valid == 1 && rx_arib == 11'h01E && rx_dlc == 4'd8) begin
            position <= {rx_data[39:32], rx_data[47:40], rx_data[55:48], rx_data[63:56]};
            power <= {rx_data[23:16], rx_data[31:24]};
            temp <= rx_data[15:8];
            traj <= rx_data[7];
            mot <= rx_data[6];
            enc <= rx_data[5];
            ctrl <= rx_data[4];
            state <= rx_data[3:0];
        end
    end

    canbus_rx #(
        .DIVIDER(DIVIDER)
    ) canbus_rx0 (
        .clk(clk),
        .tx(rx_ack),
        .rx(rx),
        .rx_data(rx_data),
        .arib(rx_arib),
        .dlc(rx_dlc),
        .valid(rx_valid)
    );


    wire tx_busy;
    reg tx_start = 1'd0;
    reg [3:0] tx_dlc = 4'd4;
    reg [10:0] tx_arib = 11'h00d;
    reg [31:0] tx_data = 31'd0;
    reg [31:0] tx_counter = 32'd0;

    always @(posedge clk) begin
        tx_start <= 1'd0;
        if (tx_counter == 0) begin
            tx_counter <= IDIVIDER;
            if (enable == 1) begin
                tx_data <= {velocity[7:0], velocity[15:8], velocity[23:16], velocity[31:24]};
            end else begin
                tx_data <= 32'd0;
            end
            tx_dlc <= 4'd4;
            tx_arib <= 11'h00d;
            tx_start <= 1'd1;
        end else begin
            tx_counter <= tx_counter - 1'd1;
        end
    end

    canbus_tx #(
        .DIVIDER(DIVIDER)
    ) canbus_tx0 (
        .clk(clk),
        .tx(tx2),
        .tx_data(tx_data),
        .tx_arib(tx_arib),
        .tx_dlc(tx_dlc),
        .start(tx_start),
        .busy(tx_busy)
    );


endmodule



