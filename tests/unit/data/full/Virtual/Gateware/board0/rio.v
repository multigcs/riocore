/*
    ######### Tangbob #########


    Toolchain : gowin
    Family    : GW1N-9C
    Type      : GW1NR-LV9QN88PC6/I5
    Package   : 
    Clock     : 27.0 Mhz

    PINOUT_BOARD0_W5500_MOSI -> 32 
    PININ_BOARD0_W5500_MISO <- 48 
    PINOUT_BOARD0_W5500_SCLK -> 31 
    PINOUT_BOARD0_W5500_SEL -> 49 
    PINOUT_BOARD0_WLED_DATA -> 54 
    PINOUT_STEPDIR0_STEP -> 85 
    PINOUT_STEPDIR0_DIR -> 83 
    PINOUT_STEPDIR1_STEP -> 81 
    PINOUT_STEPDIR1_DIR -> 79 
    PINOUT_STEPDIR2_STEP -> 77 
    PINOUT_STEPDIR2_DIR -> 76 

*/

/* verilator lint_off UNUSEDSIGNAL */

module rio (
        // RIO
        input sysclk_in,
        output PINOUT_BOARD0_W5500_MOSI,
        input PININ_BOARD0_W5500_MISO,
        output PINOUT_BOARD0_W5500_SCLK,
        output PINOUT_BOARD0_W5500_SEL,
        output PINOUT_BOARD0_WLED_DATA,
        output PINOUT_STEPDIR0_STEP,
        output PINOUT_STEPDIR0_DIR,
        output PINOUT_STEPDIR1_STEP,
        output PINOUT_STEPDIR1_DIR,
        output PINOUT_STEPDIR2_STEP,
        output PINOUT_STEPDIR2_DIR
    );

    localparam BUFFER_SIZE_TX = 16'd160; // 20 bytes
    localparam BUFFER_SIZE_RX = 16'd160; // 20 bytes

    reg INTERFACE_TIMEOUT = 0;
    wire INTERFACE_SYNC;
    wire ERROR;
    assign ERROR = (INTERFACE_TIMEOUT);

    wire sysclk;
    assign sysclk = sysclk_in;

    reg[2:0] INTERFACE_SYNCr;  always @(posedge sysclk) INTERFACE_SYNCr <= {INTERFACE_SYNCr[1:0], INTERFACE_SYNC};
    wire INTERFACE_SYNC_RISINGEDGE = (INTERFACE_SYNCr[2:1]==2'b01);

    parameter TIMEOUT = 2700000;
    localparam TIMEOUT_BITS = clog2(TIMEOUT + 1);
    reg [TIMEOUT_BITS:0] timeout_counter = 0;

    always @(posedge sysclk) begin
        if (INTERFACE_SYNC_RISINGEDGE == 1) begin
            timeout_counter <= 0;
        end else begin
            if (timeout_counter < TIMEOUT) begin
                timeout_counter <= timeout_counter + 1'd1;
                INTERFACE_TIMEOUT <= 0;
            end else begin
                INTERFACE_TIMEOUT <= 1;
            end
        end
    end

    wire [BUFFER_SIZE_RX-1:0] rx_data;
    wire [BUFFER_SIZE_TX-1:0] tx_data;

    reg [31:0] timestamp = 0;
    reg signed [31:0] header_tx = 32'h64617461;
    always @(posedge sysclk) begin
        timestamp <= timestamp + 1'd1;
    end

    wire VAROUT1_BOARD0_WLED_0_GREEN;
    wire VAROUT1_BOARD0_WLED_0_BLUE;
    wire VAROUT1_BOARD0_WLED_0_RED;
    wire [31:0] VAROUT32_STEPDIR0_VELOCITY;
    wire VAROUT1_STEPDIR0_ENABLE;
    wire [31:0] VARIN32_STEPDIR0_POSITION;
    wire [31:0] VAROUT32_STEPDIR1_VELOCITY;
    wire VAROUT1_STEPDIR1_ENABLE;
    wire [31:0] VARIN32_STEPDIR1_POSITION;
    wire [31:0] VAROUT32_STEPDIR2_VELOCITY;
    wire VAROUT1_STEPDIR2_ENABLE;
    wire [31:0] VARIN32_STEPDIR2_POSITION;

    // PC -> FPGA / OUT (134 + FILL = 160)
    // assign header_rx = {rx_data[135:128], rx_data[143:136], rx_data[151:144], rx_data[159:152]};
    assign VAROUT32_STEPDIR0_VELOCITY = {rx_data[103:96], rx_data[111:104], rx_data[119:112], rx_data[127:120]};
    assign VAROUT32_STEPDIR1_VELOCITY = {rx_data[71:64], rx_data[79:72], rx_data[87:80], rx_data[95:88]};
    assign VAROUT32_STEPDIR2_VELOCITY = {rx_data[39:32], rx_data[47:40], rx_data[55:48], rx_data[63:56]};
    assign VAROUT1_BOARD0_WLED_0_GREEN = {rx_data[31]};
    assign VAROUT1_BOARD0_WLED_0_BLUE = {rx_data[30]};
    assign VAROUT1_BOARD0_WLED_0_RED = {rx_data[29]};
    assign VAROUT1_STEPDIR0_ENABLE = {rx_data[28]};
    assign VAROUT1_STEPDIR1_ENABLE = {rx_data[27]};
    assign VAROUT1_STEPDIR2_ENABLE = {rx_data[26]};
    // assign FILL = rx_data[25:0];

    // FPGA -> PC IN (160 + FILL = 160)
    assign tx_data = {
        header_tx[7:0], header_tx[15:8], header_tx[23:16], header_tx[31:24],
        timestamp[7:0], timestamp[15:8], timestamp[23:16], timestamp[31:24],
        VARIN32_STEPDIR0_POSITION[7:0], VARIN32_STEPDIR0_POSITION[15:8], VARIN32_STEPDIR0_POSITION[23:16], VARIN32_STEPDIR0_POSITION[31:24],
        VARIN32_STEPDIR1_POSITION[7:0], VARIN32_STEPDIR1_POSITION[15:8], VARIN32_STEPDIR1_POSITION[23:16], VARIN32_STEPDIR1_POSITION[31:24],
        VARIN32_STEPDIR2_POSITION[7:0], VARIN32_STEPDIR2_POSITION[15:8], VARIN32_STEPDIR2_POSITION[23:16], VARIN32_STEPDIR2_POSITION[31:24]
    };



    // Name: board0_w5500 (w5500)
    wire PINOUT_BOARD0_W5500_MOSI_RAW;
    wire PINOUT_BOARD0_W5500_SCLK_RAW;
    wire PINOUT_BOARD0_W5500_SEL_RAW;
    wire UNUSED_PIN_BOARD0_W5500_RST;
    assign PINOUT_BOARD0_W5500_MOSI = PINOUT_BOARD0_W5500_MOSI_RAW;
    assign PINOUT_BOARD0_W5500_SCLK = PINOUT_BOARD0_W5500_SCLK_RAW;
    assign PINOUT_BOARD0_W5500_SEL = PINOUT_BOARD0_W5500_SEL_RAW;
    w5500 #(
        .MAC_ADDR({8'hAA, 8'hAF, 8'hFA, 8'hCC, 8'hE3, 8'h1C}),
        .IP_ADDR({8'd192, 8'd168, 8'd11, 8'd194}),
        .NET_MASK({8'd255, 8'd255, 8'd255, 8'd0}),
        .GW_ADDR({8'd192, 8'd168, 8'd10, 8'd1}),
        .PORT(2390),
        .BUFFER_SIZE_RX(BUFFER_SIZE_RX),
        .BUFFER_SIZE_TX(BUFFER_SIZE_TX),
        .MSGID(32'h74697277),
        .DIVIDER(0)
    ) board0_w5500 (
        .clk(sysclk),
        .mosi(PINOUT_BOARD0_W5500_MOSI_RAW),
        .miso(PININ_BOARD0_W5500_MISO),
        .sclk(PINOUT_BOARD0_W5500_SCLK_RAW),
        .sel(PINOUT_BOARD0_W5500_SEL_RAW),
        .rst(UNUSED_PIN_BOARD0_W5500_RST),
        .intr(1'd0),
        .rx_data(rx_data),
        .tx_data(tx_data),
        .sync(INTERFACE_SYNC)
    );

    // Name: board0_wled (wled)
    wire PINOUT_BOARD0_WLED_DATA_RAW;
    wire [0:0] BOARD0_WLED_GREEN;
    wire [0:0] BOARD0_WLED_BLUE;
    wire [0:0] BOARD0_WLED_RED;
    assign PINOUT_BOARD0_WLED_DATA = PINOUT_BOARD0_WLED_DATA_RAW;
    assign BOARD0_WLED_GREEN[0] = VAROUT1_BOARD0_WLED_0_GREEN;
    assign BOARD0_WLED_BLUE[0] = VAROUT1_BOARD0_WLED_0_BLUE;
    assign BOARD0_WLED_RED[0] = VAROUT1_BOARD0_WLED_0_RED;
    wled #(
        .NUM_LEDS(1),
        .LEVEL(127),
        .CLK_MHZ(27)
    ) board0_wled (
        .clk(sysclk),
        .data(PINOUT_BOARD0_WLED_DATA_RAW),
        .green(BOARD0_WLED_GREEN),
        .blue(BOARD0_WLED_BLUE),
        .red(BOARD0_WLED_RED)
    );

    // Name: stepdir0 (stepdir)
    wire PINOUT_STEPDIR0_STEP_RAW;
    wire PINOUT_STEPDIR0_DIR_RAW;
    wire UNUSED_PIN_STEPDIR0_EN;
    assign PINOUT_STEPDIR0_STEP = PINOUT_STEPDIR0_STEP_RAW;
    assign PINOUT_STEPDIR0_DIR = PINOUT_STEPDIR0_DIR_RAW;
    stepdir #(
        .PULSE_LEN(108),
        .DIR_DELAY(18)
    ) stepdir0 (
        .clk(sysclk),
        .step(PINOUT_STEPDIR0_STEP_RAW),
        .dir(PINOUT_STEPDIR0_DIR_RAW),
        .en(UNUSED_PIN_STEPDIR0_EN),
        .velocity(VAROUT32_STEPDIR0_VELOCITY),
        .enable(VAROUT1_STEPDIR0_ENABLE & ~ERROR),
        .position(VARIN32_STEPDIR0_POSITION)
    );

    // Name:  (stepdir)
    wire PINOUT_STEPDIR1_STEP_RAW;
    wire PINOUT_STEPDIR1_DIR_RAW;
    wire UNUSED_PIN_STEPDIR1_EN;
    assign PINOUT_STEPDIR1_STEP = PINOUT_STEPDIR1_STEP_RAW;
    assign PINOUT_STEPDIR1_DIR = PINOUT_STEPDIR1_DIR_RAW;
    stepdir #(
        .PULSE_LEN(108),
        .DIR_DELAY(18)
    ) stepdir1 (
        .clk(sysclk),
        .step(PINOUT_STEPDIR1_STEP_RAW),
        .dir(PINOUT_STEPDIR1_DIR_RAW),
        .en(UNUSED_PIN_STEPDIR1_EN),
        .velocity(VAROUT32_STEPDIR1_VELOCITY),
        .enable(VAROUT1_STEPDIR1_ENABLE & ~ERROR),
        .position(VARIN32_STEPDIR1_POSITION)
    );

    // Name:  (stepdir)
    wire PINOUT_STEPDIR2_STEP_RAW;
    wire PINOUT_STEPDIR2_DIR_RAW;
    wire UNUSED_PIN_STEPDIR2_EN;
    assign PINOUT_STEPDIR2_STEP = PINOUT_STEPDIR2_STEP_RAW;
    assign PINOUT_STEPDIR2_DIR = PINOUT_STEPDIR2_DIR_RAW;
    stepdir #(
        .PULSE_LEN(108),
        .DIR_DELAY(18)
    ) stepdir2 (
        .clk(sysclk),
        .step(PINOUT_STEPDIR2_STEP_RAW),
        .dir(PINOUT_STEPDIR2_DIR_RAW),
        .en(UNUSED_PIN_STEPDIR2_EN),
        .velocity(VAROUT32_STEPDIR2_VELOCITY),
        .enable(VAROUT1_STEPDIR2_ENABLE & ~ERROR),
        .position(VARIN32_STEPDIR2_POSITION)
    );

endmodule
