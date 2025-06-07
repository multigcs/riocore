
module uart
    #(parameter BUFFER_SIZE=80, parameter MSGID=32'h74697277, parameter ClkFrequency=12000000, parameter Baud=2000000, parameter CSUM=0)
     (
         input clk,
         output reg [BUFFER_SIZE-1:0] rx_data,
         input [BUFFER_SIZE-1:0] tx_data,
         output reg sync = 0,
         output reg tx_enable = 0,
         output tx,
         input rx
     );

    reg [BUFFER_SIZE-1:0] tx_data_buffer;
    reg [BUFFER_SIZE-1:0] rx_data_buffer;

    reg TxD_start = 0;
    wire TxD_busy;

    reg [7:0] TxD_data;
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

    uart_tx #(ClkFrequency, Baud) uart_tx1 (
                .clk (clk),
                .TxD_start (TxD_start),
                .TxD_data (TxD_data),
                .TxD (tx),
                .TxD_busy (TxD_busy)
            );

    reg tx_state = 0;
    reg [7:0] rx_counter = 0;
    reg [7:0] tx_counter = 0;

    reg [15:0] tx_csum = 0;
    reg [15:0] rx_csum = 0;

    always @(posedge clk) begin
        sync <= 0;
        if (RxD_endofpacket == 1) begin
            rx_counter <= 0;
        end else if (tx_state == 1) begin
            if (TxD_busy == 0) begin
                TxD_data <= tx_data_buffer[BUFFER_SIZE-1:BUFFER_SIZE-1-7];
                TxD_start <= 1;
            end else if (TxD_start == 1) begin
                TxD_start <= 0;
                if (tx_counter < BUFFER_SIZE/8-1) begin
                    tx_counter <= tx_counter + 1'd1;
                    tx_data_buffer <= {tx_data_buffer[BUFFER_SIZE-1-8:0], 8'd0};
                    tx_csum <= tx_csum + tx_data_buffer[BUFFER_SIZE-1-8:BUFFER_SIZE-1-7-8];
                end else if (CSUM && tx_counter < BUFFER_SIZE/8-1 + 1) begin
                    tx_counter <= tx_counter + 1'd1;
                    tx_data_buffer[BUFFER_SIZE-1:BUFFER_SIZE-1-7] <= tx_csum[15:8];
                end else if (CSUM && tx_counter < BUFFER_SIZE/8-1 + 2) begin
                    tx_counter <= tx_counter + 1'd1;
                    tx_data_buffer[BUFFER_SIZE-1:BUFFER_SIZE-1-7] <= tx_csum[7:0];
                end else begin
                    tx_state <= 0;
                end
            end
        end else if (tx_enable) begin
            if (TxD_busy == 0) begin
                tx_enable <= 0;
            end
        end else if (RxD_data_ready == 1) begin
            if (rx_counter < BUFFER_SIZE/8-1) begin
                rx_data_buffer <= {rx_data_buffer[BUFFER_SIZE-1-8:0], RxD_data};
                rx_counter <= rx_counter + 1'd1;
            end else begin
                // TODO: check MSGID
                rx_data <= {rx_data_buffer[BUFFER_SIZE-1-8:0], RxD_data};
                tx_enable <= 1;
                tx_counter <= 0;
                tx_data_buffer <= tx_data;
                tx_csum <= tx_data[BUFFER_SIZE-1:BUFFER_SIZE-1-7];
                tx_state <= 1;
                sync <= 1;
            end
        end
    end
endmodule

