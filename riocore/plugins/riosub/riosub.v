
module riosub
    #(parameter RX_BUFFERSIZE=64, parameter TX_BUFFERSIZE=64, parameter ClkFrequency=12000000, parameter Baud=9600)
    (
        input clk,
        input rx,
        output tx,

        input signed [31:0] pwmout2_dty,
        input pwmout2_enable

    );


    parameter BUFFER_SIZE = 16'd72; // 9 bytes


    reg [7:0] state = 0;
    reg [31:0] counter = 0;
    reg [31:0] tx_byte_counter = 0;

    reg [BUFFER_SIZE-1:0] tx_data = 0;




    always @(posedge clk) begin
        TxD_start <= 0;

        if (state == 0) begin

            tx_data <= {32'h74697277, pwmout2_dty, pwmout2_enable, 7'd0};
            state <= 1;



        end else if (state == 1) begin

            // tx next bytes

            if (TxD_busy == 0 && TxD_start == 0) begin

                TxD_data <= tx_data[BUFFER_SIZE-1:BUFFER_SIZE-8];
                TxD_start <= 1;
                state <= 2;

                tx_data <= {tx_data[BUFFER_SIZE-8:0], 8'd0};

            end

        end else if (state == 2) begin

            if (TxD_busy == 0) begin

                if (tx_byte_counter < 9-1) begin
                    state <= 1;
                    tx_byte_counter <= tx_byte_counter + 1;

                end else begin
                    state <= 3;
                    tx_byte_counter <= 0;
                end


            end

        end else if (state == 3) begin
            if (counter < 1000000) begin
                counter <= counter + 1;
            end else begin
                counter <= 0;
                state <= 0;
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



endmodule

