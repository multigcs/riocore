
module rioencoder
    #(parameter ClkFrequency=12000000, parameter Baud=2000000)
    (
        input clk,
        input rx,
        output reg rw = 0,
        output reg [15:0] angle
    );

    reg [23:0] rxbuffer = 0;
    reg [31:0] counter = 0;
    reg [7:0] rxlen = 0;

    wire [7:0] RxD_data;
    wire RxD_data_ready;
    wire RxD_idle;
    wire RxD_endofpacket;
    wire [7:0] csum;
    
    
    
    assign csum = (rxbuffer[23:16] | rxbuffer[15:8]);

    uart_rx #(ClkFrequency, Baud) uart_rx1 (
        .clk (clk),
        .RxD (rx),
        .RxD_data_ready (RxD_data_ready),
        .RxD_data (RxD_data),
        .RxD_idle (RxD_idle),
        .RxD_endofpacket (RxD_endofpacket)
    );

    always @(posedge clk) begin
        rw <= 0;
        if (RxD_endofpacket == 1) begin
            if (csum == rxbuffer[7:0]) begin
                angle <= rxbuffer[23:8];
            end
            rxbuffer <= 0;
            rxlen <= 0;
        end else if (RxD_data_ready == 1) begin
            if (rxlen < 3) begin
                rxbuffer <= {rxbuffer[15:0], RxD_data};
                rxlen <= rxlen + 1;
            end
        end

    end


endmodule

