
module riodrive
    #(parameter DIVIDER=53, parameter IDIVIDER=53)
    (
        input clk,
        input sync,
        output reg error = 1'd0,
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

    localparam RX_DATA_BYTES = 8;
    localparam RX_ARIB = 11'h01E;
    localparam TX_DATA_BYTES = 4;
    localparam TX_ARIB = 11'h00d;

    wire rx_ack;
    wire tx_out;
    assign tx = (rx_ack && tx_out);

    wire rx_valid;
    wire [3:0] rx_dlc;
    wire [10:0] rx_arib;
    wire [(RX_DATA_BYTES*8)-1:0] rx_data;
    reg [31:0] rx_timeout = IDIVIDER * 3;
    always @(posedge clk) begin
        if (rx_valid == 1 && rx_arib == RX_ARIB && rx_dlc == RX_DATA_BYTES) begin
            position <= {rx_data[39:32], rx_data[47:40], rx_data[55:48], rx_data[63:56]};
            power <= {rx_data[23:16], rx_data[31:24]};
            temp <= rx_data[15:8];
            traj <= rx_data[7];
            mot <= rx_data[6];
            enc <= rx_data[5];
            ctrl <= rx_data[4];
            state <= rx_data[3:0];
            rx_timeout <= IDIVIDER * 3;
            error <= (mot | enc | ctrl);
        end else if (rx_timeout == 0) begin
            error <= 1'd1;
            state <= 'd0;
        end else begin
            rx_timeout <= rx_timeout - 1;
        end
    end

    wire tx_busy;
    reg tx_start = 1'd0;
    reg [3:0] tx_dlc = TX_DATA_BYTES;
    reg [(TX_DATA_BYTES*8)-1:0] tx_data = 'd0;
    reg [31:0] tx_counter = 'd0;

    always @(posedge clk) begin
        tx_start <= 1'd0;
        if (tx_counter == 0 || sync == 1) begin
            tx_counter <= IDIVIDER;
            if (enable == 1) begin
                tx_data <= {velocity[7:0], velocity[15:8], velocity[23:16], velocity[31:24]};
            end else begin
                tx_data <= 32'd0;
            end
            tx_dlc <= TX_DATA_BYTES;
            tx_start <= 1'd1;
        end else begin
            tx_counter <= tx_counter - 1'd1;
        end
    end


    canbus_rx #(
        .DIVIDER(DIVIDER), .DATA_BYTES(RX_DATA_BYTES)
    ) canbus_rx0 (
        .clk(clk),
        .tx(rx_ack),
        .rx(rx),
        .rx_data(rx_data),
        .arib(rx_arib),
        .dlc(rx_dlc),
        .valid(rx_valid)
    );

    canbus_tx #(
        .DIVIDER(DIVIDER), .DATA_BYTES(TX_DATA_BYTES)
    ) canbus_tx0 (
        .clk(clk),
        .tx(tx_out),
        .tx_data(tx_data),
        .tx_arib(TX_ARIB),
        .tx_dlc(tx_dlc),
        .start(tx_start),
        .busy(tx_busy)
    );

endmodule



