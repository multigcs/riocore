
module canbus_rx
    #(parameter DIVIDER=54, parameter DATA_BYTES=8)
    (
        input clk,
        input rx,
        output reg tx = 1'b1,
        output reg [DATA_BITS-1:0] rx_data = 'd0,
        output reg [10:0] arib = 11'd0,
        output reg [3:0] dlc = 4'd0,
        output reg valid = 1'd0
    );

    localparam DATA_BITS = (DATA_BYTES * 8);
    localparam FRAME_SIZE = (34 + DATA_BITS);
    localparam IDLE  = 4'd0,
               SYNC  = 4'd1,
               RECV  = 4'd2,
               ACK   = 4'd3,
               END   = 4'd4;

    reg csumok = 1'b0;
    reg [5:0] stuff_check = 6'b100111;
    reg [3:0] state = IDLE;
    reg [7:0] bit_count = 0;
    reg [DATA_BITS-1+15:0] rx_frm = 0;
    reg [14:0] crc = 15'd0;
    reg [14:0] rx_crc = 15'd0;
    wire[14:0] rx_crc_next;
    assign rx_crc_next = {rx_crc[13:0], 1'b0} ^ (rx_crc[14] ^ rx ? 15'h4599 : 15'h0);

    reg [31:0] clk_counter = 0;
    always @(posedge clk) begin
        valid <= 1'd0;

        if (clk_counter == 0) begin

            tx <= 1'b1;
            stuff_check <= {stuff_check[4:0], rx};

            if (state == IDLE) begin
                clk_counter <= 1;
            end else if (state == SYNC) begin
                clk_counter <= DIVIDER;
            end else begin
                clk_counter <= DIVIDER;
            end
    
            case (state)
                IDLE: begin
                    if (rx == 0) begin
                        state <= SYNC;
                        stuff_check <= 6'b000111;
                        bit_count <= 0;
                        dlc <= 0;
                        rx_crc <= 0;
                        rx_frm <= 0;
                        csumok <= 1'b0;
                    end
                end

                SYNC: begin
                    state <= RECV;
                end

                RECV: begin
                    if (stuff_check == 6'b111111) begin
                        // end of frame
                        state <= IDLE;
                    end else if (stuff_check[4:0] == 5'b00000) begin
                        // stuff bit
                    end else if (stuff_check[4:0] == 5'b11111) begin
                        // stuff bit
                    end else begin
                        rx_frm <= {rx_frm[DATA_BITS-1+15-1:0], rx};
                        rx_crc <= rx_crc_next;
                        if (bit_count == 11) begin
                            arib <= rx_frm[10:0];
                        end else if (bit_count == 18 && rx_frm[3:0] == 8) begin
                            dlc <= rx_frm[3:0];
                        end else if (bit_count == 18 + (dlc*8)) begin
                            crc <= rx_crc;
                        end else if (bit_count == 18 + (dlc*8) + 15) begin
                            if (crc == rx_frm[14:0]) begin
                                // crc is ok
                                rx_data <= rx_frm[DATA_BITS-1+15:15];
                                csumok <= 1'b1;
                            end
                        end else if (bit_count == 18 + (dlc*8) + 15 + 1) begin
                            if (csumok == 1'd1) begin
                                // set ACK bit
                                tx <= 1'b0;
                                valid <= 1'd1;
                            end
                        end
                        bit_count <= bit_count + 1;
                    end
                end

            endcase
        end else begin
            clk_counter <= clk_counter - 1'd1;
        end

    end
endmodule

