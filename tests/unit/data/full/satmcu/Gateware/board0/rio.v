/*
    ######### ICEBreakerV1.0e #########


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
    PINOUT_STEPDIR0_EN -> 4 
    PINOUT_STEPDIR1_STEP -> 47 
    PINOUT_STEPDIR1_DIR -> 46 
    PINOUT_BLINK0_LED -> 11 
    PININ_BITIN0_BIT <- 10 
    PINOUT_STEPDIR2_STEP -> 2 
    PINOUT_STEPDIR2_DIR -> 48 
    PINOUT_BITOUT0_BIT -> 43 
    PINOUT_BITOUT1_BIT -> 42 
    PININ_BITIN1_BIT <- 32 
    PININ_BITIN2_BIT <- 34 
    PININ_BITIN3_BIT <- 28 
    PININ_BITIN4_BIT <- 38 
    PININ_BITIN5_BIT <- 31 
    PININ_UARTSUB1_RX <- 18 
    PINOUT_UARTSUB1_TX -> 20 
    PININ_UARTSUB0_RX <- 19 
    PINOUT_UARTSUB0_TX -> 21 

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
        output PINOUT_STEPDIR0_EN,
        output PINOUT_STEPDIR1_STEP,
        output PINOUT_STEPDIR1_DIR,
        output PINOUT_BLINK0_LED,
        input PININ_BITIN0_BIT,
        output PINOUT_STEPDIR2_STEP,
        output PINOUT_STEPDIR2_DIR,
        output PINOUT_BITOUT0_BIT,
        output PINOUT_BITOUT1_BIT,
        input PININ_BITIN1_BIT,
        input PININ_BITIN2_BIT,
        input PININ_BITIN3_BIT,
        input PININ_BITIN4_BIT,
        input PININ_BITIN5_BIT,
        input PININ_UARTSUB1_RX,
        output PINOUT_UARTSUB1_TX,
        input PININ_UARTSUB0_RX,
        output PINOUT_UARTSUB0_TX
    );

    localparam BUFFER_SIZE_TX = 16'd304; // 38 bytes
    localparam BUFFER_SIZE_RX = 16'd144; // 18 bytes

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

    wire [BUFFER_SIZE_RX-1:0] rx_data;
    wire [BUFFER_SIZE_TX-1:0] tx_data;

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
    wire VARIN1_BITIN0_BIT;
    wire [31:0] VAROUT32_STEPDIR2_VELOCITY;
    wire VAROUT1_STEPDIR2_ENABLE;
    wire [31:0] VARIN32_STEPDIR2_POSITION;
    wire VAROUT1_BITOUT0_BIT;
    wire VAROUT1_BITOUT1_BIT;
    wire VARIN1_BITIN1_BIT;
    wire VARIN1_BITIN2_BIT;
    wire VARIN1_BITIN3_BIT;
    wire VARIN1_BITIN4_BIT;
    wire VARIN1_BITIN5_BIT;
    wire VARIN1_UARTSUB1_TIMEOUT;
    wire VAROUT1_GPIOOUT0_BIT;
    wire VARIN1_UARTSUB0_TIMEOUT;
    wire VAROUT1_GPIOOUT1_BIT;
    wire VAROUT1_GPIOOUT2_BIT;
    wire VAROUT1_GPIOOUT3_BIT;
    wire VARIN1_GPIOIN0_BIT;
    wire [31:0] VARIN32_ENCODER0_POSITION;
    wire [31:0] VARIN32_ENCODER1_POSITION;
    wire [31:0] VARIN32_ENCODER2_POSITION;
    wire [31:0] VARIN32_ENCODER3_POSITION;
    wire VAROUT1_GPIOOUT4_BIT;
    wire VAROUT1_GPIOOUT5_BIT;
    wire VAROUT1_GPIOOUT6_BIT;
    wire VAROUT1_GPIOOUT7_BIT;
    wire VAROUT1_GPIOOUT8_BIT;
    wire VAROUT1_GPIOOUT9_BIT;
    wire VARIN1_GPIOIN1_BIT;

    // PC -> MASTER_FPGA / OUT (143 + FILL = 144)
    // assign header_rx = {rx_data[119:112], rx_data[127:120], rx_data[135:128], rx_data[143:136]};
    assign VAROUT32_STEPDIR0_VELOCITY = {rx_data[87:80], rx_data[95:88], rx_data[103:96], rx_data[111:104]};
    assign VAROUT32_STEPDIR1_VELOCITY = {rx_data[55:48], rx_data[63:56], rx_data[71:64], rx_data[79:72]};
    assign VAROUT32_STEPDIR2_VELOCITY = {rx_data[23:16], rx_data[31:24], rx_data[39:32], rx_data[47:40]};
    assign VAROUT1_STEPDIR0_ENABLE = {rx_data[15]};
    assign VAROUT1_STEPDIR1_ENABLE = {rx_data[14]};
    assign VAROUT1_STEPDIR2_ENABLE = {rx_data[13]};
    assign VAROUT1_BITOUT0_BIT = {rx_data[12]};
    assign VAROUT1_BITOUT1_BIT = {rx_data[11]};
    assign VAROUT1_GPIOOUT0_BIT = {rx_data[10]};
    assign VAROUT1_GPIOOUT1_BIT = {rx_data[9]};
    assign VAROUT1_GPIOOUT2_BIT = {rx_data[8]};
    assign VAROUT1_GPIOOUT3_BIT = {rx_data[7]};
    assign VAROUT1_GPIOOUT4_BIT = {rx_data[6]};
    assign VAROUT1_GPIOOUT5_BIT = {rx_data[5]};
    assign VAROUT1_GPIOOUT6_BIT = {rx_data[4]};
    assign VAROUT1_GPIOOUT7_BIT = {rx_data[3]};
    assign VAROUT1_GPIOOUT8_BIT = {rx_data[2]};
    assign VAROUT1_GPIOOUT9_BIT = {rx_data[1]};
    // assign FILL = rx_data[0:0];

    // MASTER_FPGA -> PC IN (298 + FILL = 304)
    assign tx_data = {
        header_tx[7:0], header_tx[15:8], header_tx[23:16], header_tx[31:24],
        timestamp[7:0], timestamp[15:8], timestamp[23:16], timestamp[31:24],
        VARIN32_STEPDIR0_POSITION[7:0], VARIN32_STEPDIR0_POSITION[15:8], VARIN32_STEPDIR0_POSITION[23:16], VARIN32_STEPDIR0_POSITION[31:24],
        VARIN32_STEPDIR1_POSITION[7:0], VARIN32_STEPDIR1_POSITION[15:8], VARIN32_STEPDIR1_POSITION[23:16], VARIN32_STEPDIR1_POSITION[31:24],
        VARIN32_STEPDIR2_POSITION[7:0], VARIN32_STEPDIR2_POSITION[15:8], VARIN32_STEPDIR2_POSITION[23:16], VARIN32_STEPDIR2_POSITION[31:24],
        VARIN32_ENCODER0_POSITION[7:0], VARIN32_ENCODER0_POSITION[15:8], VARIN32_ENCODER0_POSITION[23:16], VARIN32_ENCODER0_POSITION[31:24],
        VARIN32_ENCODER1_POSITION[7:0], VARIN32_ENCODER1_POSITION[15:8], VARIN32_ENCODER1_POSITION[23:16], VARIN32_ENCODER1_POSITION[31:24],
        VARIN32_ENCODER2_POSITION[7:0], VARIN32_ENCODER2_POSITION[15:8], VARIN32_ENCODER2_POSITION[23:16], VARIN32_ENCODER2_POSITION[31:24],
        VARIN32_ENCODER3_POSITION[7:0], VARIN32_ENCODER3_POSITION[15:8], VARIN32_ENCODER3_POSITION[23:16], VARIN32_ENCODER3_POSITION[31:24],
        VARIN1_BITIN0_BIT,
        VARIN1_BITIN1_BIT,
        VARIN1_BITIN2_BIT,
        VARIN1_BITIN3_BIT,
        VARIN1_BITIN4_BIT,
        VARIN1_BITIN5_BIT,
        VARIN1_UARTSUB1_TIMEOUT,
        VARIN1_UARTSUB0_TIMEOUT,
        VARIN1_GPIOIN0_BIT,
        VARIN1_GPIOIN1_BIT,
        6'd0
    };




    // #################### ('satmcu1', 0) (sub0) ####################
    localparam SUB0_BUFFER_SIZE_RX = 16'd40; // 5 bytes
    localparam SUB0_BUFFER_SIZE_TX = 16'd40; // 5 bytes

    wire [SUB0_BUFFER_SIZE_RX-1:0] sub0_rx_data;
    wire [SUB0_BUFFER_SIZE_TX-1:0] sub0_tx_data;

    // SUB0_FPGA -> MASTER_FPGA / INPUTS (33 + FILL)
    // assign header_rx = {sub0_rx_data[15:8], sub0_rx_data[23:16], sub0_rx_data[31:24], sub0_rx_data[39:32]};
    assign VARIN1_GPIOIN1_BIT = {sub0_rx_data[7]};
    // assign FILL = sub0_rx_data[6:0];

    // MASTER_FPGA -> SUB0_FPGA / OUTPUTS (33 + FILL)
    assign sub0_tx_data = {
        32'h74697277,
        VAROUT1_GPIOOUT9_BIT,
        7'd0
    };

    // ###############################################


    // #################### ('satmcu0', 1) (sub1) ####################
    localparam SUB1_BUFFER_SIZE_RX = 16'd168; // 21 bytes
    localparam SUB1_BUFFER_SIZE_TX = 16'd48; // 6 bytes

    wire [SUB1_BUFFER_SIZE_RX-1:0] sub1_rx_data;
    wire [SUB1_BUFFER_SIZE_TX-1:0] sub1_tx_data;

    // SUB1_FPGA -> MASTER_FPGA / INPUTS (161 + FILL)
    // assign header_rx = {sub1_rx_data[143:136], sub1_rx_data[151:144], sub1_rx_data[159:152], sub1_rx_data[167:160]};
    assign VARIN32_ENCODER0_POSITION = {sub1_rx_data[111:104], sub1_rx_data[119:112], sub1_rx_data[127:120], sub1_rx_data[135:128]};
    assign VARIN32_ENCODER1_POSITION = {sub1_rx_data[79:72], sub1_rx_data[87:80], sub1_rx_data[95:88], sub1_rx_data[103:96]};
    assign VARIN32_ENCODER2_POSITION = {sub1_rx_data[47:40], sub1_rx_data[55:48], sub1_rx_data[63:56], sub1_rx_data[71:64]};
    assign VARIN32_ENCODER3_POSITION = {sub1_rx_data[15:8], sub1_rx_data[23:16], sub1_rx_data[31:24], sub1_rx_data[39:32]};
    assign VARIN1_GPIOIN0_BIT = {sub1_rx_data[7]};
    // assign FILL = sub1_rx_data[6:0];

    // MASTER_FPGA -> SUB1_FPGA / OUTPUTS (41 + FILL)
    assign sub1_tx_data = {
        32'h74697277,
        VAROUT1_GPIOOUT0_BIT,
        VAROUT1_GPIOOUT1_BIT,
        VAROUT1_GPIOOUT2_BIT,
        VAROUT1_GPIOOUT3_BIT,
        VAROUT1_GPIOOUT4_BIT,
        VAROUT1_GPIOOUT5_BIT,
        VAROUT1_GPIOOUT6_BIT,
        VAROUT1_GPIOOUT7_BIT,
        VAROUT1_GPIOOUT8_BIT,
        7'd0
    };

    // ###############################################

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
        .BUFFER_SIZE_RX(BUFFER_SIZE_RX),
        .BUFFER_SIZE_TX(BUFFER_SIZE_TX),
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
    wire PINOUT_STEPDIR0_EN_RAW;
    assign PINOUT_STEPDIR0_STEP = PINOUT_STEPDIR0_STEP_RAW;
    assign PINOUT_STEPDIR0_DIR = PINOUT_STEPDIR0_DIR_RAW;
    assign PINOUT_STEPDIR0_EN = PINOUT_STEPDIR0_EN_RAW;
    stepdir #(
        .PULSE_LEN(120),
        .DIR_DELAY(21)
    ) stepdir0 (
        .clk(sysclk),
        .step(PINOUT_STEPDIR0_STEP_RAW),
        .dir(PINOUT_STEPDIR0_DIR_RAW),
        .en(PINOUT_STEPDIR0_EN_RAW),
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

    // Name: bitin0 (bitin)
    assign VARIN1_BITIN0_BIT = PININ_BITIN0_BIT;

    // Name:  (stepdir)
    wire PINOUT_STEPDIR2_STEP_RAW;
    wire PINOUT_STEPDIR2_DIR_RAW;
    wire UNUSED_PIN_STEPDIR2_EN;
    assign PINOUT_STEPDIR2_STEP = PINOUT_STEPDIR2_STEP_RAW;
    assign PINOUT_STEPDIR2_DIR = PINOUT_STEPDIR2_DIR_RAW;
    stepdir #(
        .PULSE_LEN(120),
        .DIR_DELAY(21)
    ) stepdir2 (
        .clk(sysclk),
        .step(PINOUT_STEPDIR2_STEP_RAW),
        .dir(PINOUT_STEPDIR2_DIR_RAW),
        .en(UNUSED_PIN_STEPDIR2_EN),
        .velocity(VAROUT32_STEPDIR2_VELOCITY),
        .enable(VAROUT1_STEPDIR2_ENABLE & ~ERROR),
        .position(VARIN32_STEPDIR2_POSITION)
    );

    // Name: bitout0 (bitout)
    wire PINOUT_BITOUT0_BIT_RAW;
    assign PINOUT_BITOUT0_BIT = PINOUT_BITOUT0_BIT_RAW;
    assign PINOUT_BITOUT0_BIT_RAW = VAROUT1_BITOUT0_BIT;

    // Name: bitout1 (bitout)
    wire PINOUT_BITOUT1_BIT_RAW;
    assign PINOUT_BITOUT1_BIT = PINOUT_BITOUT1_BIT_RAW;
    assign PINOUT_BITOUT1_BIT_RAW = VAROUT1_BITOUT1_BIT;

    // Name: bitin1 (bitin)
    assign VARIN1_BITIN1_BIT = PININ_BITIN1_BIT;

    // Name: bitin2 (bitin)
    assign VARIN1_BITIN2_BIT = PININ_BITIN2_BIT;

    // Name: bitin3 (bitin)
    assign VARIN1_BITIN3_BIT = PININ_BITIN3_BIT;

    // Name:  (bitin)
    assign VARIN1_BITIN4_BIT = PININ_BITIN4_BIT;

    // Name:  (bitin)
    assign VARIN1_BITIN5_BIT = PININ_BITIN5_BIT;

    // Name:  (uartsub)
    wire PINOUT_UARTSUB1_TX_RAW;
    wire UNUSED_PIN_UARTSUB1_TX_ENABLE;
    assign PINOUT_UARTSUB1_TX = PINOUT_UARTSUB1_TX_RAW;
    uartsub #(
        .BUFFER_SIZE_RX(SUB0_BUFFER_SIZE_RX),
        .BUFFER_SIZE_TX(SUB0_BUFFER_SIZE_TX),
        .MSGID(32'h64617461),
        .ClkFrequency(30000000),
        .Baud(1000000),
        .Timeout(3000000),
        .CSUM(1)
    ) uartsub1 (
        .clk(sysclk),
        .rx(PININ_UARTSUB1_RX),
        .tx(PINOUT_UARTSUB1_TX_RAW),
        .tx_enable(UNUSED_PIN_UARTSUB1_TX_ENABLE),
        .timeout(VARIN1_UARTSUB1_TIMEOUT),
        .rx_data(sub0_rx_data),
        .tx_data(sub0_tx_data),
        .sync_in(INTERFACE_SYNC_RISINGEDGE)
    );

    // Name:  (uartsub)
    wire PINOUT_UARTSUB0_TX_RAW;
    wire UNUSED_PIN_UARTSUB0_TX_ENABLE;
    assign PINOUT_UARTSUB0_TX = PINOUT_UARTSUB0_TX_RAW;
    uartsub #(
        .BUFFER_SIZE_RX(SUB1_BUFFER_SIZE_RX),
        .BUFFER_SIZE_TX(SUB1_BUFFER_SIZE_TX),
        .MSGID(32'h64617461),
        .ClkFrequency(30000000),
        .Baud(1000000),
        .Timeout(3000000),
        .CSUM(1)
    ) uartsub0 (
        .clk(sysclk),
        .rx(PININ_UARTSUB0_RX),
        .tx(PINOUT_UARTSUB0_TX_RAW),
        .tx_enable(UNUSED_PIN_UARTSUB0_TX_ENABLE),
        .timeout(VARIN1_UARTSUB0_TIMEOUT),
        .rx_data(sub1_rx_data),
        .tx_data(sub1_tx_data),
        .sync_in(INTERFACE_SYNC_RISINGEDGE)
    );

endmodule
