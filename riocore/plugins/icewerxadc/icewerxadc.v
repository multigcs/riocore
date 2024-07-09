
module icewerxadc
    #(parameter ClkFrequency=12000000, parameter Baud=250000)
    (
        input clk,
        input rx,
        output tx,
        output reg [9:0] adc1,
        output reg [9:0] adc2,
        output reg [9:0] adc3,
        output reg [9:0] adc4
    );

    reg [15:0] rxbuffer = 0;
    reg [31:0] counter = 0;
    reg [7:0] rxlen = 0;
    reg [1:0] channel = 0;

    wire [7:0] RxD_data;
    wire RxD_data_ready;
    wire RxD_idle;
    wire RxD_endofpacket;

    uart_rx #(ClkFrequency, Baud) uart_rx1 (
        .clk (clk),
        .RxD (rx),
        .RxD_data_ready (RxD_data_ready),
        .RxD_data (RxD_data),
        .RxD_idle (RxD_idle),
        .RxD_endofpacket (RxD_endofpacket)
    );

    always @(posedge clk) begin
        if (RxD_endofpacket == 1) begin
            if (channel == 0) begin
                adc1 <= rxbuffer[9:0];
            end else if (channel == 1) begin
                adc2 <= rxbuffer[9:0];
            end else if (channel == 2) begin
                adc3 <= rxbuffer[9:0];
            end else if (channel == 3) begin
                adc4 <= rxbuffer[9:0];
            end

            rxbuffer <= 0;
            rxlen <= 0;
        end else if (RxD_data_ready == 1) begin
            if (rxlen < 2) begin
                rxbuffer <= {RxD_data, rxbuffer[15:8]};
                rxlen <= rxlen + 1;
            end
        end

    end



    reg TxD_start = 0;
    wire TxD_busy;
    reg [7:0] TxD_data = 0;

    uart_tx #(ClkFrequency, Baud) uart_tx1 (
        .clk (clk),
        .TxD (tx),
        .TxD_data (TxD_data),
        .TxD_start (TxD_start),
        .TxD_busy (TxD_busy)
    );

    reg tx_state = 0;
    reg [7:0] tx_counter = 0;

    always @(posedge clk) begin
        if (tx_state == 1) begin
            if (TxD_busy == 0 && TxD_start == 0) begin
                if (channel == 0) begin
                    TxD_data <= 8'hA1;
                end else if (channel == 1) begin
                    TxD_data <= 8'hA2;
                end else if (channel == 2) begin
                    TxD_data <= 8'hA3;
                end else if (channel == 3) begin
                    TxD_data <= 8'hA4;
                end
                TxD_start <= 1;
            end else begin
                TxD_start <= 0;
                tx_state <= 0;
            end
        end else begin
            if (counter < ClkFrequency / 100) begin
                counter <= counter + 1;
            end else begin

                if (channel == 0) begin
                    channel <= 2'd1;
                end else if (channel == 1) begin
                    channel <= 2'd2;
                end else if (channel == 2) begin
                    channel <= 2'd3;
                end else if (channel == 3) begin
                    channel <= 2'd0;
                end

                tx_state <= 1;
                counter <= 0;
            end
        end
    end


endmodule

