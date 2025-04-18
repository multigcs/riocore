
module canbus
    #(parameter DIVIDER=53)
    (
        input clk,
        input rx,
        output wire tx,
        output wire oclk,
        input wire [31:0] velocity,
        output wire [31:0] position
    );


    wire tx1;
    wire tx2;
    assign tx = (tx1 && tx2);


    canbus_rx #(
        .DIVIDER(DIVIDER)
    ) canbus_rx0 (
        .clk(clk),
        .oclk(oclk),
        .tx(tx1),
        .rx(rx),
        .position(position)
    );


    canbus_tx #(
        .DIVIDER(DIVIDER)
    ) canbus_tx0 (
        .clk(clk),
        .tx(tx2),
        .velocity(velocity)
    );


endmodule

module canbus_tx
    #(parameter DIVIDER=53)
    (
        input clk,
        output reg tx = 1'b1,
        input wire [31:0] velocity
    );


    reg [31:0] clk_counter = 0;
    reg mclk = 0;
    always @(posedge clk) begin
        if (clk_counter == 0) begin
            clk_counter <= DIVIDER;
            mclk <= ~mclk;
        end else begin
            clk_counter <= clk_counter - 1'd1;
        end
    end




    localparam ARIB = 'h00d;

    localparam DATA_BYTES = 4;
    localparam DATA_BITS = (DATA_BYTES * 8);
    localparam FRAME_SIZE = (34 + DATA_BITS);

    localparam IDLE  = 4'd0,
               START = 4'd2,
               SEND  = 4'd3,
               ACK   = 4'd4,
               END   = 4'd5;

    reg [3:0] state = IDLE;
    reg [31:0] bit_count = 0;

    reg [10:0] reg_arib = ARIB;
    reg rtr = 1'b0;
    reg ide = 1'b0;
    reg r0 = 1'b0;

    reg [3:0] dlc = DATA_BYTES;
    reg [DATA_BITS-1:0] data = 'd0;

    reg [14:0] tx_crc = 15'd0;
    reg crcdel = 1'b1;

    wire [FRAME_SIZE-1:0] tx_frm;
    assign tx_frm = { reg_arib, rtr , ide, r0, dlc , data[DATA_BITS-1:0], tx_crc, crcdel };

    reg [4:0] stuff_check = 5'b10011;

    wire tx_next;
    assign tx_next = tx_frm[(FRAME_SIZE-1) - bit_count];
    wire[14:0] tx_crc_next;
    assign tx_crc_next = {tx_crc[13:0], 1'b0} ^ (tx_crc[14] ^ tx_next ? 15'h4599 : 15'h0);

    always @(posedge mclk) begin
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
                if (bit_count == 11240) begin
                    bit_count <= 0;
                    state <= IDLE;
                    data <= velocity;
                end
            end

        endcase
    end
endmodule




module canbus_rx
    #(parameter DIVIDER=53)
    (
        input clk,
        output reg oclk = 0,
        input rx,
        output reg tx = 1'b1,
        output reg [31:0] position
    );


    reg [31:0] clk_counter = 0;
    reg mclk = 0;
    always @(posedge clk) begin
        if (clk_counter == 0) begin
            if (state == IDLE) begin
                clk_counter <= 1;
            end else if (state == SYNC) begin
                //clk_counter <= (DIVIDER / 2);
                clk_counter <= DIVIDER;
            end else begin
                clk_counter <= DIVIDER;
            end
            mclk <= ~mclk;
        end else begin
            clk_counter <= clk_counter - 1'd1;
        end
    end

    localparam DATA_BYTES = 8;
    localparam DATA_BITS = (DATA_BYTES * 8);
    localparam FRAME_SIZE = (34 + DATA_BITS);
    localparam IDLE  = 4'd0,
               SYNC  = 4'd1,
               RECV  = 4'd2,
               ACK   = 4'd3,
               END   = 4'd4;

    reg valid = 1'b0;
    reg [5:0] stuff_check = 6'b100111;
    reg [3:0] state = IDLE;
    reg [31:0] bit_count = 0;
    reg [63:0] data = 0;
    reg [127:0] rx_frm = 0;
    reg [10:0] arib = 0;
    reg [3:0] dlc = 0;
    reg [14:0] crc = 15'd0;
    reg [14:0] rx_crc = 15'd0;
    wire[14:0] rx_crc_next;
    assign rx_crc_next = {rx_crc[13:0], 1'b0} ^ (rx_crc[14] ^ rx ? 15'h4599 : 15'h0);

    always @(posedge mclk) begin

        tx <= 1'b1;
        stuff_check <= {stuff_check[4:0], rx};

        case (state)
            IDLE: begin
                oclk <= 0;
                if (rx == 0) begin
                    state <= SYNC;
                    stuff_check <= 6'b000111;
                    bit_count <= 0;
                    dlc <= 0;
                    rx_crc <= 0;
                    rx_frm <= 0;
                    valid <= 1'd0;
                end
            
            end

            SYNC: begin
                oclk <= 1;
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
                    rx_frm <= {rx_frm[126:0], rx};
                    rx_crc <= rx_crc_next;
                    if (bit_count == 11) begin
                        arib <= rx_frm[10:0];
                    end else if (bit_count == 18 && rx_frm[3:0] == 8) begin
                        dlc <= rx_frm[3:0];
                    end else if (bit_count == 18 + (dlc*8)) begin
                        oclk <= 0;
                        data <= rx_frm[63:0];
                        crc <= rx_crc;
                    end else if (bit_count == 18 + (dlc*8) + 15) begin
                        if (crc == rx_frm[14:0] && arib == 'h009) begin
                            // crc and arib is ok
                            //position <= data[31:0];
                            position <= data[63:32];
                            valid <= 1'd1;
                        end
                    end else if (bit_count == 18 + (dlc*8) + 15 + 1) begin
                        if (valid == 1'd1) begin
                            oclk <= 1;
                            tx <= 1'b0;
                            valid <= 1'd0;
                        end
                    end
                    bit_count <= bit_count + 1;
                end
            end

        endcase

    end
endmodule

