
module canbus_tx
    #(parameter DIVIDER=53)
    (
        input clk,
        output reg tx = 1'b1,
        input wire [31:0] indata,
        input wire [10:0] tx_arib,
        input wire [3:0] tx_dlc,
        input wire start,
        output reg busy = 1'd0
    );


    reg [31:0] clk_counter = 0;

    localparam ARIB = 11'h00d;
    localparam DATA_BYTES = 4;
    localparam DATA_BITS = (DATA_BYTES * 8);
    localparam FRAME_SIZE = (34 + DATA_BITS);

    localparam IDLE  = 4'd0,
               START = 4'd2,
               SEND  = 4'd3,
               ACK   = 4'd4,
               END   = 4'd5,
               DONE  = 4'd6;

    reg [3:0] state = IDLE;
    reg [31:0] bit_count = 0;

    reg [10:0] arib = 11'd0;
    reg rtr = 1'b0;
    reg ide = 1'b0;
    reg r0 = 1'b0;

    reg [3:0] dlc = 4'd4;
    reg [DATA_BITS-1:0] data = 'd0;

    reg [14:0] tx_crc = 15'd0;
    reg crcdel = 1'b1;

    wire [FRAME_SIZE-1:0] tx_frm;
    assign tx_frm = { arib, rtr , ide, r0, dlc , data[DATA_BITS-1:0], tx_crc, crcdel };

    reg [4:0] stuff_check = 5'b10011;

    wire tx_next;
    assign tx_next = tx_frm[(FRAME_SIZE-1) - bit_count];
    wire[14:0] tx_crc_next;
    assign tx_crc_next = {tx_crc[13:0], 1'b0} ^ (tx_crc[14] ^ tx_next ? 15'h4599 : 15'h0);

    always @(posedge clk) begin

        if (start == 1) begin
            busy <= 1'd1;

            arib <= tx_arib;
            dlc <= tx_dlc;
            data <= indata;
            state <= IDLE;
        end


        if (clk_counter == 0) begin
            clk_counter <= DIVIDER;
            case (state)
                IDLE: begin
                    tx <= 1'b1;
                    state <= START;
                    bit_count <= 0;
                end

                START: begin
                    tx <= 1'b0;
                    tx_crc <= 0;
                    stuff_check <= {stuff_check[3:0], 1'b0};
                    state <= SEND;
                    bit_count <= 0;
                end

                SEND: begin
                    if ({stuff_check} == 5'b00000) begin
                        tx <= 1'b1;
                        stuff_check <= {stuff_check[3:0], 1'b1};
                    end else if ({stuff_check} == 5'b11111) begin
                        tx <= 1'b0;
                        stuff_check <= {stuff_check[3:0], 1'b0};
                    end else begin
                        tx <= tx_next;
                        stuff_check <= {stuff_check[3:0], tx_next};

                        if (bit_count < FRAME_SIZE-16) begin
                            tx_crc <= tx_crc_next;
                        end

                        bit_count <= bit_count + 1;
                        if (bit_count == FRAME_SIZE-1) begin
                            bit_count <= 0;
                            state <= ACK;
                        end
                    end
                end

                ACK: begin
                    tx <= 1'd1;
                    bit_count <= bit_count + 1;
                    if (bit_count == 1) begin
                        bit_count <= 0;
                        state <= END;
                    end
                end

                END: begin
                    tx <= 1'b1;
                    bit_count <= bit_count + 1;
                    if (bit_count == 10) begin
                        bit_count <= 0;
                        state <= DONE;
                        busy <= 1'd0;
                    end
                end

            endcase


        end else begin
            clk_counter <= clk_counter - 1'd1;
        end
    end


endmodule


