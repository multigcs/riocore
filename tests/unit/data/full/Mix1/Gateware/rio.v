/*
    ######### Mix1 #########


    Toolchain : icestorm
    Family    : ice40
    Type      : up5k
    Package   : sg48
    Clock     : 30.0 Mhz

    PINOUT_W55000_MOSI -> 14 
    PININ_W55000_MISO <- 17 
    PINOUT_W55000_SCLK -> 15 
    PINOUT_W55000_SEL -> 12 
    PINOUT_STEPDIR0_STEP -> 45 
    PINOUT_STEPDIR0_DIR -> 44 
    PINOUT_STEPDIR1_STEP -> 47 
    PINOUT_STEPDIR1_DIR -> 46 
    PINOUT_BLINK0_LED -> 11 
    PINOUT_BITOUT0_BIT -> 4 
    PININ_BITIN0_BIT <- 10 

*/

/* verilator lint_off UNUSEDSIGNAL */

module rio (
        // RIO
        input sysclk_in,
        output PINOUT_W55000_MOSI,
        input PININ_W55000_MISO,
        output PINOUT_W55000_SCLK,
        output PINOUT_W55000_SEL,
        output PINOUT_STEPDIR0_STEP,
        output PINOUT_STEPDIR0_DIR,
        output PINOUT_STEPDIR1_STEP,
        output PINOUT_STEPDIR1_DIR,
        output PINOUT_BLINK0_LED,
        output PINOUT_BITOUT0_BIT,
        input PININ_BITIN0_BIT
    );

    localparam BUFFER_SIZE = 16'd136; // 17 bytes

    reg INTERFACE_TIMEOUT = 0;
    wire INTERFACE_SYNC;
    wire ERROR;
    assign ERROR = (INTERFACE_TIMEOUT);

    wire sysclk;
    wire locked;
    pll mypll(sysclk_in, sysclk, locked);

    reg[2:0] INTERFACE_SYNCr;  always @(posedge sysclk) INTERFACE_SYNCr <= {INTERFACE_SYNCr[1:0], INTERFACE_SYNC};
    wire INTERFACE_SYNC_RISINGEDGE = (INTERFACE_SYNCr[2:1]==2'b01);

    parameter TIMEOUT = 3000000;
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

    wire [BUFFER_SIZE-1:0] rx_data;
    wire [BUFFER_SIZE-1:0] tx_data;

    reg [31:0] timestamp = 0;
    reg signed [31:0] header_tx = 32'h64617461;
    always @(posedge sysclk) begin
        timestamp <= timestamp + 1'd1;
    end

    wire [31:0] VAROUT32_STEPDIR0_VELOCITY;
    wire VAROUT1_STEPDIR0_ENABLE;
    wire [31:0] VARIN32_STEPDIR0_POSITION;
    wire [31:0] VAROUT32_STEPDIR1_VELOCITY;
    wire VAROUT1_STEPDIR1_ENABLE;
    wire [31:0] VARIN32_STEPDIR1_POSITION;
    wire VAROUT1_BITOUT0_BIT;
    wire VARIN1_BITIN0_BIT;

    // PC -> FPGA (99 + FILL)
    // assign header_rx = {rx_data[111:104], rx_data[119:112], rx_data[127:120], rx_data[135:128]};
    assign VAROUT32_STEPDIR0_VELOCITY = {rx_data[79:72], rx_data[87:80], rx_data[95:88], rx_data[103:96]};
    assign VAROUT32_STEPDIR1_VELOCITY = {rx_data[47:40], rx_data[55:48], rx_data[63:56], rx_data[71:64]};
    assign VAROUT1_STEPDIR0_ENABLE = {rx_data[39]};
    assign VAROUT1_STEPDIR1_ENABLE = {rx_data[38]};
    assign VAROUT1_BITOUT0_BIT = {rx_data[37]};
    // assign FILL = rx_data[36:0];

    // FPGA -> PC (129 + FILL)
    assign tx_data = {
        header_tx[7:0], header_tx[15:8], header_tx[23:16], header_tx[31:24],
        timestamp[7:0], timestamp[15:8], timestamp[23:16], timestamp[31:24],
        VARIN32_STEPDIR0_POSITION[7:0], VARIN32_STEPDIR0_POSITION[15:8], VARIN32_STEPDIR0_POSITION[23:16], VARIN32_STEPDIR0_POSITION[31:24],
        VARIN32_STEPDIR1_POSITION[7:0], VARIN32_STEPDIR1_POSITION[15:8], VARIN32_STEPDIR1_POSITION[23:16], VARIN32_STEPDIR1_POSITION[31:24],
        VARIN1_BITIN0_BIT,
        7'd0
    };



    // Name: w55000 (w5500)
    wire PINOUT_W55000_MOSI_RAW;
    wire PINOUT_W55000_SCLK_RAW;
    wire PINOUT_W55000_SEL_RAW;
    wire UNUSED_PIN_W55000_RST;
    assign PINOUT_W55000_MOSI = PINOUT_W55000_MOSI_RAW;
    assign PINOUT_W55000_SCLK = PINOUT_W55000_SCLK_RAW;
    assign PINOUT_W55000_SEL = PINOUT_W55000_SEL_RAW;
    w5500 #(
        .MAC_ADDR({8'hAA, 8'hAF, 8'hFA, 8'hCC, 8'hE3, 8'h1C}),
        .IP_ADDR({8'd192, 8'd168, 8'd11, 8'd194}),
        .NET_MASK({8'd255, 8'd255, 8'd255, 8'd0}),
        .GW_ADDR({8'd192, 8'd168, 8'd11, 8'd1}),
        .PORT(2390),
        .BUFFER_SIZE(BUFFER_SIZE),
        .MSGID(32'h74697277),
        .DIVIDER(0)
    ) w55000 (
        .clk(sysclk),
        .mosi(PINOUT_W55000_MOSI_RAW),
        .miso(PININ_W55000_MISO),
        .sclk(PINOUT_W55000_SCLK_RAW),
        .sel(PINOUT_W55000_SEL_RAW),
        .rst(UNUSED_PIN_W55000_RST),
        .intr(1'd0),
        .rx_data(rx_data),
        .tx_data(tx_data),
        .sync(INTERFACE_SYNC)
    );

    // Name: stepdir0 (stepdir)
    wire PINOUT_STEPDIR0_STEP_RAW;
    wire PINOUT_STEPDIR0_DIR_RAW;
    wire UNUSED_PIN_STEPDIR0_EN;
    assign PINOUT_STEPDIR0_STEP = PINOUT_STEPDIR0_STEP_RAW;
    assign PINOUT_STEPDIR0_DIR = PINOUT_STEPDIR0_DIR_RAW;
    stepdir #(
        .PULSE_LEN(120),
        .DIR_DELAY(21)
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
        .PULSE_LEN(120),
        .DIR_DELAY(21)
    ) stepdir1 (
        .clk(sysclk),
        .step(PINOUT_STEPDIR1_STEP_RAW),
        .dir(PINOUT_STEPDIR1_DIR_RAW),
        .en(UNUSED_PIN_STEPDIR1_EN),
        .velocity(VAROUT32_STEPDIR1_VELOCITY),
        .enable(VAROUT1_STEPDIR1_ENABLE & ~ERROR),
        .position(VARIN32_STEPDIR1_POSITION)
    );

    // Name: blink0 (blink)
    wire PINOUT_BLINK0_LED_RAW;
    assign PINOUT_BLINK0_LED = PINOUT_BLINK0_LED_RAW;
    blink #(
        .DIVIDER(15000000)
    ) blink0 (
        .clk(sysclk),
        .led(PINOUT_BLINK0_LED_RAW)
    );

    // Name: bitout0 (bitout)
    wire PINOUT_BITOUT0_BIT_RAW;
    assign PINOUT_BITOUT0_BIT = PINOUT_BITOUT0_BIT_RAW;
    assign PINOUT_BITOUT0_BIT_RAW = VAROUT1_BITOUT0_BIT;

    // Name: bitin0 (bitin)
    assign VARIN1_BITIN0_BIT = PININ_BITIN0_BIT;

endmodule
