
module stepperonline_abs
    #(parameter ClkFrequency=32400000, parameter Baud=2500000)
    (
        input clk,
        input rx,
        output tx,
        input [7:0] cmd,
        output reg tx_enable = 1,
        output reg debug_bit = 0,
        output reg [31:0] position,
        output reg [15:0] angle,
        output reg [7:0] tmp1,
        output reg [7:0] tmp2,
        output reg [7:0] csum,
        output reg [31:0] debug_data
    );

    reg [127:0] rxbuffer = 0;
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

    reg TxD_start = 0;
    wire TxD_busy;
    reg [7:0] TxD_data = 0;

    uart_tx #(ClkFrequency, Baud, 1) uart_tx1 (
        .clk (clk),
        .TxD (tx),
        .TxD_data (TxD_data),
        .TxD_start (TxD_start),
        .TxD_busy (TxD_busy)
    );

    reg [7:0] state = 0;
    reg [31:0] counter = 0;

    always @(posedge clk) begin
        TxD_start <= 0;


        if (state == 0) begin
            // start tx
            if (TxD_busy == 0 && TxD_start == 0) begin
                TxD_data <= 8'h7d;
                TxD_start <= 1;
                state <= 1;
            end

        end else if (state == 1) begin
            // stop tx
            state <= 2;
            
            // rx timeout 1.0ms
            counter <= ClkFrequency / 1000;

        end else if (state == 2) begin

            if (TxD_busy == 0) begin
                tx_enable <= 0;

                // wait timeout/rx
                if (counter == 0) begin
                    tx_enable <= 1;
                    state <= 0;
                end else begin
                    counter <= counter - 1;
                end

            end
        end


        if (RxD_endofpacket == 1) begin
            // TODO: csum calc and check
            csum <= rxbuffer[7:0];
            tmp1 <= rxbuffer[15:8];
            angle <= {rxbuffer[16], rxbuffer[31:24], rxbuffer[39:33]};
            position <= {8'd0, rxbuffer[23:16], rxbuffer[31:24], rxbuffer[39:32]};
            tmp2 <= rxbuffer[47:40];
            debug_data <= rxbuffer[47:40];

            // next request in 0.01ms
            counter <= ClkFrequency / 100000;

            //end
            rxbuffer <= 0;
            rxlen <= 0;
        end else if (RxD_data_ready == 1) begin
            if (rxlen < 7) begin
                rxbuffer <= {rxbuffer[127-8:0], RxD_data};
                debug_data <= rxlen;
                rxlen <= rxlen + 1;
            end
        end

    end

endmodule

