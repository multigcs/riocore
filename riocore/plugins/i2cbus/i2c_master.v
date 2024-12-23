

module i2c_master 
    #(parameter DIVIDER = 42)
    (
        input clk,
        inout sda,
        output reg scl = 0,
        input wire start,
        output reg busy = 0,
        input wire [7:0] set_addr,
        input wire set_rw,
        input wire [4:0] set_bytes,
        input wire [31:0] set_data_out,
        output reg [31:0] data_in,
        output reg valid = 0
    );

    parameter MODE_ADDR = 0;
    parameter MODE_DATA = 1;
    parameter STATE_WAIT = 0;
    parameter STATE_INIT = 1;
    parameter STATE_START = 2;
    parameter STATE_RTX = 3;
    parameter STATE_ACK = 4;
    parameter STATE_STOP = 5;
    parameter STATE_DONE = 6;


    reg [7:0] mystate = 0;
    reg [7:0] send_cnt = 0;
    reg [7:0] send_byte_n = 0;

    reg clk_400;
    reg [31:0]counter_400;
    always @(posedge clk) begin
        if (counter_400 == 0) begin
            counter_400 <= DIVIDER;
            clk_400 <= ~clk_400;
        end else begin
            counter_400 <= counter_400 - 1;
        end
    end


    wire sdaIn;
    reg sdaOut = 0;
    reg isSending = 0;
    assign sda = (isSending & ~sdaOut) ? 1'b0 : 1'bz;
    assign sdaIn = sda ? 1'b1 : 1'b0;

    reg [7:0] step = 0;
    reg send_mode = 0;
    reg [31:0] data_rtx = 0;

    reg [7:0] addr = 0;
    reg [31:0] data_out = 0;
    reg rw = 0;
    reg [4:0] bytes;

    always @(posedge clk_400) begin
        step <= 0;

        if (mystate == STATE_WAIT) begin
            sdaOut <= 1;
            isSending <= 0;

            if (sdaIn == 0) begin
                // wait for free bus / reset
                scl <= ~scl;

            end else if (start) begin
                scl <= 1;
                valid <= 0;
                busy <= 1;
                addr <= set_addr;
                rw <= set_rw;
                bytes <= set_bytes;
                data_out <= set_data_out;
                mystate <= STATE_START;
            end


        end else if (mystate == STATE_START) begin
            // start condition
            if (step == 0) begin
                step <= 1;
                isSending <= 1;
                sdaOut <= 1;
                scl <= 1;
            end else if (step == 1) begin
                step <= 2;
                isSending <= 1;
                sdaOut <= 0;
            end else if (step == 2) begin
                step <= 0;
                scl <= 0;
                step <= 0;
                send_mode <= MODE_ADDR;
                data_rtx <= {addr[7:1], rw};
                send_cnt <= 0;
                send_byte_n <= 0;
                mystate <= STATE_RTX;
            end

        end else if (mystate == STATE_RTX) begin
            // send 8bit
            if (step == 0) begin
                step <= 1;
                if (send_mode == MODE_ADDR) begin
                    isSending <= 1;
                    sdaOut <= data_rtx[7 - send_cnt]; // set addr
                end else if (rw == 0) begin
                    isSending <= 1;
                    sdaOut <= data_rtx[7 - send_cnt]; // set addr
                end else begin
                    isSending <= 0;
                end
            end else if (step == 1) begin
                step <= 2;
                scl <= 1;

                if (rw == 1 && send_mode == MODE_DATA) begin
                    // read
                    data_rtx[7 - send_cnt] = sdaIn;
                end

            end else if (step == 2) begin
                step <= 0;
                scl <= 0;
                if (send_mode == MODE_ADDR && send_cnt == 7) begin
                    mystate <= STATE_ACK;
                    send_cnt <= 0;

                end else if (send_mode == MODE_DATA && send_cnt == 7) begin
                    mystate <= STATE_ACK;
                    if (rw == 1) begin
                        data_in <= {data_in[23:0], data_rtx[7:0]};
                        valid <= 1;
                    end
                    send_cnt <= 0;


                end else begin
                    send_cnt <= send_cnt + 8'd1;
                end
            end

        end else if (mystate == STATE_ACK) begin
            if (step == 0) begin
                step <= 1;
                sdaOut <= 1;
                isSending <= 0;
            end else if (step == 1) begin
                step <= 2;
                scl <= 1;
            end else if (step == 2) begin
                step <= 0;
                scl <= 0;
                sdaOut <= 0;
                isSending <= 1;
                if (send_byte_n < bytes) begin
                    if (send_mode == MODE_ADDR && sdaIn == 1) begin
                        // nack
                        mystate <= STATE_STOP;
                    end else begin
                        send_mode <= MODE_DATA;
                        if (rw == 0) begin
                            data_rtx <= data_out[((bytes - send_byte_n)*8-1):((bytes - send_byte_n)*8-8)];
                        end else begin
                            data_rtx <= 0;
                        end
                        send_byte_n <= send_byte_n + 1;
                        mystate <= STATE_RTX;
                    end
                end else begin
                    mystate <= STATE_STOP;
                end
            end

        end else if (mystate == STATE_STOP) begin
            if (step == 0) begin
                step <= 1;
            end else if (step == 1) begin
                step <= 2;
                scl <= 1;
            end else if (step == 2) begin
                step <= 3;
                sdaOut <= 1;
                isSending <= 0;
            end else if (step == 3) begin
                step <= 0;
                busy <= 0;
                mystate <= STATE_WAIT;
            end


        end

    end

endmodule
