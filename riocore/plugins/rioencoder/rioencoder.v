
module rioencoder
    #(parameter ClkFrequency=12000000, parameter Baud=2000000)
    (
        input clk,
        input rx,
        output reg rw = 0,
        output reg [15:0] angle,
        output reg signed [15:0] temperature,
        output reg signed [31:0] revs
    );

    parameter PKG_SIZZE = 80;

    reg [PKG_SIZZE-1:0] rxbuffer = 0;
    reg [31:0] counter = 0;
    reg [7:0] rxlen = 0;

    wire [7:0] RxD_data;
    wire [15:0] csum;
    wire [15:0] csum_calc;
    wire RxD_data_ready;
    wire RxD_idle;
    wire RxD_endofpacket;

    assign csum = {rxbuffer[7:0], rxbuffer[15:8]};
    assign csum_calc = rxbuffer[79:72] ^ rxbuffer[71:64] ^ rxbuffer[63:56] ^ rxbuffer[55:48] ^ rxbuffer[47:40] ^ rxbuffer[39:32] ^ rxbuffer[31:24] ^ rxbuffer[23:16];

    uart_rx #(ClkFrequency, Baud) uart_rx1 (
        .clk (clk),
        .RxD (rx),
        .RxD_data_ready (RxD_data_ready),
        .RxD_data (RxD_data),
        .RxD_idle (RxD_idle),
        .RxD_endofpacket (RxD_endofpacket)
    );

    always @(posedge clk) begin
        rw <= 0;
        if (RxD_endofpacket == 1) begin
            if (csum == csum_calc) begin
                revs <= {rxbuffer[55:48], rxbuffer[63:56], rxbuffer[71:64], rxbuffer[79:72]};
                angle <= {rxbuffer[39:32], rxbuffer[47:40]};
                temperature <= {rxbuffer[23:16], rxbuffer[31:24]};
            end
            rxbuffer <= 0;
            rxlen <= 0;
        end else if (RxD_data_ready == 1) begin
            if (rxlen < 10) begin
                rxbuffer <= {rxbuffer[PKG_SIZZE-8-1:0], RxD_data};
                rxlen <= rxlen + 1;
            end
        end
    end

endmodule

