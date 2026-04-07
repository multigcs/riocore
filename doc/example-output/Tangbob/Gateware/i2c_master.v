

module i2c_master 
    #(parameter MAX_BITS = 64, parameter MAX_DIN = 64)
    (
        input clk,
        inout sda,
        input wire [31:0] set_divider,
        output reg scl = 1,
        input wire start,
        output reg busy = 0,
        input wire [6:0] set_addr,
        input wire set_rw,
        input wire stop,
        input wire wakeup,
        input wire [4:0] set_bytes,
        input wire [MAX_BITS-1:0] set_data_out,
        output reg [MAX_DIN-1:0] data_in,
        output reg error = 0
    );

    localparam RW_WRITE = 0;
    localparam RW_READ = 1;
    localparam MODE_ADDR = 0;
    localparam MODE_DATA = 1;
    localparam STATE_WAIT = 0;
    localparam STATE_INIT = 1;
    localparam STATE_START = 2;
    localparam STATE_RTX = 3;
    localparam STATE_ACK = 4;
    localparam STATE_STOP = 5;
    localparam STATE_WAKEUP = 6;

    reg [7:0] mystate = 0;
    reg [7:0] send_cnt = 0;
    reg [7:0] send_byte_n = 0;
    reg [31:0] delay = 0;
    reg [31:0] divider = 0;

    reg clk_bus;
    reg [31:0]counter_bus;
    always @(posedge clk) begin
        if (counter_bus == 0) begin
            counter_bus <= divider;
            clk_bus <= ~clk_bus;
        end else begin
            counter_bus <= counter_bus - 1;
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
    reg [6:0] addr = 0;
    reg [MAX_BITS-1:0] data_out = 0;
    reg rw = RW_WRITE;
    reg [4:0] bytes = 0;

    always @(posedge clk_bus) begin
        step <= 0;


        if (mystate == STATE_WAIT) begin
            sdaOut <= 1;
            isSending <= 0;
            busy <= 0;

            if (sdaIn == 0) begin
                // wait for free bus / reset
                scl <= ~scl;
                busy <= 1;
            end else if (wakeup) begin
                mystate <= STATE_WAKEUP;
                busy <= 1;
            end else if (start) begin
                scl <= 1;
                error <= 0;
                busy <= 1;
                addr <= set_addr;
                rw <= set_rw;
                divider <= set_divider;
                bytes <= set_bytes;
                data_out <= set_data_out;
                mystate <= STATE_START;
            end

        end else if (mystate == STATE_WAKEUP) begin
            // wakeup condition
            if (step == 0) begin
                step <= 1;
                isSending <= 1;
                sdaOut <= 1;
                scl <= 0;
                delay <= 5000;
            end else if (step == 1) begin
                if (delay == 0) begin
                    step <= 2;
                    delay <= 5000;
                    isSending <= 1;
                    sdaOut <= 0;
                    scl <= 1;
                end else begin
                    delay <= delay - 1'd1;
                    step <= 1;
                end
            end else if (step == 2) begin
                if (delay == 0) begin
                    step <= 0;
                    isSending <= 1;
                    sdaOut <= 1;
                    scl <= 1;
                    mystate <= STATE_STOP;
                end else begin
                    delay <= delay - 1'd1;
                    step <= 2;
                end
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
                data_rtx <= {addr, rw};
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
                end else if (rw == RW_WRITE) begin
                    isSending <= 1;
                    sdaOut <= data_rtx[7 - send_cnt]; // set addr
                end else begin
                    isSending <= 0;
                end
            end else if (step == 1) begin
                step <= 2;
                scl <= 1;
                if (rw == RW_READ && send_mode == MODE_DATA) begin
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
                    if (rw == RW_READ) begin
                        data_in <= {data_in[MAX_DIN-1-8:0], data_rtx[7:0]};
                    end
                    send_cnt <= 0;

                end else begin
                    send_cnt <= send_cnt + 8'd1;
                end
            end

        end else if (mystate == STATE_ACK) begin
            if (step == 0) begin
                step <= 1;

                if (send_mode == MODE_DATA && rw == RW_READ && send_byte_n < bytes) begin
                    sdaOut <= 0;
                    isSending <= 1;
                end else begin
                    sdaOut <= 1;
                    isSending <= 0;
                end

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
                        error <= 1;
                    end else begin
                        send_mode <= MODE_DATA;
                        if (rw == RW_WRITE) begin
                            data_rtx <= data_out[MAX_BITS-1:MAX_BITS-8];
                            data_out <= {data_out[MAX_BITS-1-8:0], 8'd0};
                        end else begin
                            data_rtx <= 0;
                        end
                        send_byte_n <= send_byte_n + 8'd1;
                        mystate <= STATE_RTX;
                    end
                end else begin
                    if (stop == 0) begin
                        busy <= 0;
                        isSending <= 0;
                        mystate <= STATE_WAIT;
                    end else begin
                        mystate <= STATE_STOP;
                    end

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
