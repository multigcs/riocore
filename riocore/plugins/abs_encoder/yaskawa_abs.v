
module yaskawa_abs
    #(parameter DELAY=3, parameter DELAY_NEXT=4)
    (
        input clk,
        input rx,
        output reg tx = 0,
        output reg tx_enable = 0,
        output reg debug_bit = 0,
        output rx_synced,
        output reg batt_error = 0,
        output reg [7:0] temp = 0,
        // output reg [7:0] scounter = 0,
        // output reg [15:0] fcounter = 0,
        // output reg [15:0] speed = 0,
        // output reg [7:0] fine_pos = 0,
        output reg [15:0] angle = 0,
        output reg [31:0] position = 0,
        output reg [15:0] csum = 0,
        output reg [31:0] debug_data = 0
    );

    reg [59:0] request_seq = 60'b01111110_1_011111_011111_011111_01111110_0101010101010101010101010;
    reg [127:0] rx_data = 0;
    reg [7:0] bit_pos = 0;
    reg receiving = 0;
    reg manchester_bit = 0;

    reg [31:0] delay_counter = 0;
    reg [1:0] sync_stat = 0;
    reg [15:0] timeout = 0;

    reg last_bit = 0;
    reg [7:0] stuffing = 0;

    reg [1:0] rx_ss;
    always @(posedge clk) rx_ss[0] <= rx;
    always @(posedge clk) rx_ss[1] <= rx_ss[0];
    assign rx_synced = rx_ss[1];

    always @(posedge clk) begin
        if (tx_enable == 1) begin

            // sending request sequence (60bit)
            if (delay_counter == 0) begin
                if (bit_pos < 60) begin
                    if (manchester_bit == 0) begin
                        tx <= request_seq[bit_pos];
                        manchester_bit <= 1;
                    end else begin
                        tx <= ~tx;
                        manchester_bit <= 0;
                        bit_pos <= bit_pos + 8'd1;
                    end
                 end else begin
                    tx_enable <= 0;
                    receiving <= 1;
                    bit_pos <= 0;
                 end
                delay_counter <= DELAY;
            end else begin
                delay_counter <= delay_counter - 1;
            end

        end else begin

            // receive
            if (sync_stat != 0) begin
                if (rx_synced == sync_stat[1]) begin
                    sync_stat <= 0;
                    delay_counter <= DELAY_NEXT;
                end else if (timeout == 0) begin
                    sync_stat <= 0;
                    delay_counter <= DELAY_NEXT;
                    receiving <= 0;
debug_bit <= ~debug_bit;
                end else begin
                    timeout <= timeout - 16'd1;
                end

            end else if (delay_counter == 0) begin

                if (receiving == 1) begin
                    // rx (skip first 13 bits)
                    rx_data[bit_pos - 13] <= rx_synced;

                    // skipping stuffing bit (after 5x1)
                    if (rx_synced == 1 && last_bit == 1) begin
                        stuffing <= stuffing + 8'd1;
                        bit_pos <= bit_pos + 8'd1;
                    end else begin
                        if (stuffing != 4) begin
                            bit_pos <= bit_pos + 8'd1;
                        end
                        stuffing <= 0;
                    end
                    last_bit <= rx_synced;

                    // resync
                    sync_stat <= {~rx_synced, rx_synced};
                    timeout <= (DELAY * 10);

                end else begin
                    // end rx
                    if (bit_pos == 134) begin
                        // TODO check csum
                        // ??? <= rx_data[0]; 1
                        // ??? <= rx_data[1]; 0
                        batt_error <= rx_data[2];
                        // ??? <= rx_data[3]; 0
                        // ??? <= rx_data[4]; 0
                        // ??? <= rx_data[5]; 0
                        // ??? <= rx_data[6]; 0
                        // ??? <= rx_data[7]; 0
                        temp <= rx_data[15:8];
                        // scounter <= rx_data[23:16];
                        // fcounter <= rx_data[39:24];
                        // speed <= rx_data[55:40];
                        // ??? <= rx_data[59:56];
                        // fine_pos <= {4'd0, rx_data[59:56]};
                        angle <= rx_data[75+1:60+1]; // part of the position (cut to 16bit)
                        position <= rx_data[91:60];
                        // ??? <= rx_data[95:92];
                        csum <= rx_data[111:96];
                    end

                    debug_data <= bit_pos; // debug_data

                    // start new request
                    stuffing <= 0;
                    bit_pos <= 0;
                    sync_stat <= 0;
                    manchester_bit <= 0;
                    tx_enable <= 1;
                    receiving <= 0;
                end

            end else begin
                delay_counter <= delay_counter - 1;
            end

        end

    end

endmodule

