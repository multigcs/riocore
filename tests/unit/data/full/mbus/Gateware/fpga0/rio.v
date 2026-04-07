/*
    ######### Tangbob #########


    Toolchain : icestorm
    Family    : GW1N-9C
    Type      : GW1NR-LV9QN88PC6/I5
    Package   : 
    Clock     : 27.0 Mhz

    PINOUT_FPGA0_W5500_MOSI -> 32 
    PININ_FPGA0_W5500_MISO <- 48 
    PINOUT_FPGA0_W5500_SCLK -> 31 
    PINOUT_FPGA0_W5500_SEL -> 49 
    PINOUT_FPGA0_WLED_DATA -> 54 
    PINOUT_BLINK0_LED -> 16 
    PININOUT_I2CBUS0_SDA <> 56 
    PINOUT_I2CBUS0_SCL -> 55 
    PINOUT_STEPDIR0_STEP -> 41 
    PINOUT_STEPDIR0_DIR -> 40 
    PINOUT_STEPDIR1_STEP -> 33 
    PINOUT_STEPDIR1_DIR -> 29 
    PINOUT_STEPDIR2_STEP -> 28 
    PINOUT_STEPDIR2_DIR -> 27 
    PINOUT_STEPDIR2_EN -> 42 
    PININ_BITIN0_BIT <- 39 
    PININ_BITIN1_BIT <- 36 
    PININ_BITIN2_BIT <- 37 
    PININ_MBMASTER0_RX <- 69 
    PINOUT_MBMASTER0_TX -> 57 
    PINOUT_MBMASTER0_TX_ENABLE -> 68 

*/

/* verilator lint_off UNUSEDSIGNAL */

module rio (
        // RIO
        input sysclk_in,
        output PINOUT_FPGA0_W5500_MOSI,
        input PININ_FPGA0_W5500_MISO,
        output PINOUT_FPGA0_W5500_SCLK,
        output PINOUT_FPGA0_W5500_SEL,
        output PINOUT_FPGA0_WLED_DATA,
        output PINOUT_BLINK0_LED,
        inout PININOUT_I2CBUS0_SDA,
        output PINOUT_I2CBUS0_SCL,
        output PINOUT_STEPDIR0_STEP,
        output PINOUT_STEPDIR0_DIR,
        output PINOUT_STEPDIR1_STEP,
        output PINOUT_STEPDIR1_DIR,
        output PINOUT_STEPDIR2_STEP,
        output PINOUT_STEPDIR2_DIR,
        output PINOUT_STEPDIR2_EN,
        input PININ_BITIN0_BIT,
        input PININ_BITIN1_BIT,
        input PININ_BITIN2_BIT,
        input PININ_MBMASTER0_RX,
        output PINOUT_MBMASTER0_TX,
        output PINOUT_MBMASTER0_TX_ENABLE
    );

    localparam BUFFER_SIZE_TX = 16'd320; // 40 bytes
    localparam BUFFER_SIZE_RX = 16'd272; // 34 bytes

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
    reg [TIMEOUT_BITS-1:0] timeout_counter = 0;

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

    localparam HEADER_TX = 32'h64617461;

    reg [31:0] timestamp = 32'd0;
    always @(posedge sysclk) begin
        timestamp <= timestamp + 32'd1;
    end

    reg [15:0] MULTIPLEXED_INPUT_VALUE = 0;
    reg [7:0] MULTIPLEXED_INPUT_ID = 0;
    wire VAROUT1_FPGA0_WLED_0_GREEN;
    wire VAROUT1_FPGA0_WLED_0_BLUE;
    wire VAROUT1_FPGA0_WLED_0_RED;
    wire VAROUT1_FPGA0_WLED_1_GREEN;
    wire VAROUT1_FPGA0_WLED_1_BLUE;
    wire VAROUT1_FPGA0_WLED_1_RED;
    wire VAROUT1_FPGA0_WLED_2_GREEN;
    wire VAROUT1_FPGA0_WLED_2_BLUE;
    wire VAROUT1_FPGA0_WLED_2_RED;
    wire [31:0] VAROUT32_STEPDIR0_VELOCITY;
    wire VAROUT1_STEPDIR0_ENABLE;
    wire [31:0] VARIN32_STEPDIR0_POSITION;
    wire [31:0] VAROUT32_STEPDIR1_VELOCITY;
    wire VAROUT1_STEPDIR1_ENABLE;
    wire [31:0] VARIN32_STEPDIR1_POSITION;
    wire [31:0] VAROUT32_STEPDIR2_VELOCITY;
    wire VAROUT1_STEPDIR2_ENABLE;
    wire [31:0] VARIN32_STEPDIR2_POSITION;
    wire VARIN1_BITIN0_BIT;
    wire VARIN1_BITIN1_BIT;
    wire VARIN1_BITIN2_BIT;
    wire [127:0] VARIN128_MBMASTER0_RXDATA;
    wire [127:0] VAROUT128_MBMASTER0_TXDATA;
    wire [15:0] VARIN16_I2C_LM75_0_I2C_LM75_0_TEMP;
    wire VARIN1_I2C_LM75_0_I2C_LM75_0_VALID;

    // PC -> MASTER_FPGA / OUT (268 + FILL = 272)
    // assign header_rx = {rx_data[247:240], rx_data[255:248], rx_data[263:256], rx_data[271:264]};
    assign VAROUT128_MBMASTER0_TXDATA = {rx_data[119:112], rx_data[127:120], rx_data[135:128], rx_data[143:136], rx_data[151:144], rx_data[159:152], rx_data[167:160], rx_data[175:168], rx_data[183:176], rx_data[191:184], rx_data[199:192], rx_data[207:200], rx_data[215:208], rx_data[223:216], rx_data[231:224], rx_data[239:232]};
    assign VAROUT32_STEPDIR0_VELOCITY = {rx_data[87:80], rx_data[95:88], rx_data[103:96], rx_data[111:104]};
    assign VAROUT32_STEPDIR1_VELOCITY = {rx_data[55:48], rx_data[63:56], rx_data[71:64], rx_data[79:72]};
    assign VAROUT32_STEPDIR2_VELOCITY = {rx_data[23:16], rx_data[31:24], rx_data[39:32], rx_data[47:40]};
    assign VAROUT1_FPGA0_WLED_0_GREEN = {rx_data[15]};
    assign VAROUT1_FPGA0_WLED_0_BLUE = {rx_data[14]};
    assign VAROUT1_FPGA0_WLED_0_RED = {rx_data[13]};
    assign VAROUT1_FPGA0_WLED_1_GREEN = {rx_data[12]};
    assign VAROUT1_FPGA0_WLED_1_BLUE = {rx_data[11]};
    assign VAROUT1_FPGA0_WLED_1_RED = {rx_data[10]};
    assign VAROUT1_FPGA0_WLED_2_GREEN = {rx_data[9]};
    assign VAROUT1_FPGA0_WLED_2_BLUE = {rx_data[8]};
    assign VAROUT1_FPGA0_WLED_2_RED = {rx_data[7]};
    assign VAROUT1_STEPDIR0_ENABLE = {rx_data[6]};
    assign VAROUT1_STEPDIR1_ENABLE = {rx_data[5]};
    assign VAROUT1_STEPDIR2_ENABLE = {rx_data[4]};
    // assign FILL = rx_data[3:0];

    // MASTER_FPGA -> PC IN (315 + FILL = 320)
    assign tx_data = {
        HEADER_TX[7:0], HEADER_TX[15:8], HEADER_TX[23:16], HEADER_TX[31:24],
        timestamp[7:0], timestamp[15:8], timestamp[23:16], timestamp[31:24],
        MULTIPLEXED_INPUT_VALUE[7:0], MULTIPLEXED_INPUT_VALUE[15:8],
        MULTIPLEXED_INPUT_ID[7:0],
        VARIN128_MBMASTER0_RXDATA[7:0], VARIN128_MBMASTER0_RXDATA[15:8], VARIN128_MBMASTER0_RXDATA[23:16], VARIN128_MBMASTER0_RXDATA[31:24], VARIN128_MBMASTER0_RXDATA[39:32], VARIN128_MBMASTER0_RXDATA[47:40], VARIN128_MBMASTER0_RXDATA[55:48], VARIN128_MBMASTER0_RXDATA[63:56], VARIN128_MBMASTER0_RXDATA[71:64], VARIN128_MBMASTER0_RXDATA[79:72], VARIN128_MBMASTER0_RXDATA[87:80], VARIN128_MBMASTER0_RXDATA[95:88], VARIN128_MBMASTER0_RXDATA[103:96], VARIN128_MBMASTER0_RXDATA[111:104], VARIN128_MBMASTER0_RXDATA[119:112], VARIN128_MBMASTER0_RXDATA[127:120],
        VARIN32_STEPDIR0_POSITION[7:0], VARIN32_STEPDIR0_POSITION[15:8], VARIN32_STEPDIR0_POSITION[23:16], VARIN32_STEPDIR0_POSITION[31:24],
        VARIN32_STEPDIR1_POSITION[7:0], VARIN32_STEPDIR1_POSITION[15:8], VARIN32_STEPDIR1_POSITION[23:16], VARIN32_STEPDIR1_POSITION[31:24],
        VARIN32_STEPDIR2_POSITION[7:0], VARIN32_STEPDIR2_POSITION[15:8], VARIN32_STEPDIR2_POSITION[23:16], VARIN32_STEPDIR2_POSITION[31:24],
        VARIN1_BITIN0_BIT,
        VARIN1_BITIN1_BIT,
        VARIN1_BITIN2_BIT,
        5'd0
    };


    always @(posedge sysclk) begin
        if (INTERFACE_SYNC_RISINGEDGE == 1) begin
            if (MULTIPLEXED_INPUT_ID < 1) begin
                MULTIPLEXED_INPUT_ID = MULTIPLEXED_INPUT_ID + 1'd1;
            end else begin
                MULTIPLEXED_INPUT_ID = 0;
            end
            if (MULTIPLEXED_INPUT_ID == 0) begin
                MULTIPLEXED_INPUT_VALUE <= VARIN16_I2C_LM75_0_I2C_LM75_0_TEMP[15:0];
            end
            if (MULTIPLEXED_INPUT_ID == 1) begin
                MULTIPLEXED_INPUT_VALUE <= VARIN1_I2C_LM75_0_I2C_LM75_0_VALID;
            end
        end
    end

    // Name: fpga0_w5500 (w5500)
    wire PINOUT_FPGA0_W5500_MOSI_RAW;
    wire PINOUT_FPGA0_W5500_SCLK_RAW;
    wire PINOUT_FPGA0_W5500_SEL_RAW;
    wire UNUSED_PIN_FPGA0_W5500_RST;
    assign PINOUT_FPGA0_W5500_MOSI = PINOUT_FPGA0_W5500_MOSI_RAW;
    assign PINOUT_FPGA0_W5500_SCLK = PINOUT_FPGA0_W5500_SCLK_RAW;
    assign PINOUT_FPGA0_W5500_SEL = PINOUT_FPGA0_W5500_SEL_RAW;
    w5500 #(
        .MAC_ADDR({8'hAA, 8'hAF, 8'hFA, 8'hCC, 8'hE3, 8'h1C}),
        .IP_ADDR({8'd192, 8'd168, 8'd10, 8'd191}),
        .NET_MASK({8'd255, 8'd255, 8'd255, 8'd0}),
        .GW_ADDR({8'd192, 8'd168, 8'd10, 8'd1}),
        .PORT(2390),
        .BUFFER_SIZE_RX(BUFFER_SIZE_RX),
        .BUFFER_SIZE_TX(BUFFER_SIZE_TX),
        .MSGID(32'h74697277),
        .DIVIDER(0)
    ) fpga0_w5500 (
        .clk(sysclk),
        .mosi(PINOUT_FPGA0_W5500_MOSI_RAW),
        .miso(PININ_FPGA0_W5500_MISO),
        .sclk(PINOUT_FPGA0_W5500_SCLK_RAW),
        .sel(PINOUT_FPGA0_W5500_SEL_RAW),
        .rst(UNUSED_PIN_FPGA0_W5500_RST),
        .intr(1'd0),
        .rx_data(rx_data),
        .tx_data(tx_data),
        .sync(INTERFACE_SYNC)
    );

    // Name: fpga0_wled (wled)
    wire PINOUT_FPGA0_WLED_DATA_RAW;
    wire [2:0] FPGA0_WLED_GREEN;
    wire [2:0] FPGA0_WLED_BLUE;
    wire [2:0] FPGA0_WLED_RED;
    assign PINOUT_FPGA0_WLED_DATA = PINOUT_FPGA0_WLED_DATA_RAW;
    assign FPGA0_WLED_GREEN[2] = VAROUT1_FPGA0_WLED_0_GREEN;
    assign FPGA0_WLED_BLUE[2] = VAROUT1_FPGA0_WLED_0_BLUE;
    assign FPGA0_WLED_RED[2] = VAROUT1_FPGA0_WLED_0_RED;
    assign FPGA0_WLED_GREEN[1] = VAROUT1_FPGA0_WLED_1_GREEN;
    assign FPGA0_WLED_BLUE[1] = VAROUT1_FPGA0_WLED_1_BLUE;
    assign FPGA0_WLED_RED[1] = VAROUT1_FPGA0_WLED_1_RED;
    assign FPGA0_WLED_GREEN[0] = VAROUT1_FPGA0_WLED_2_GREEN;
    assign FPGA0_WLED_BLUE[0] = VAROUT1_FPGA0_WLED_2_BLUE;
    assign FPGA0_WLED_RED[0] = VAROUT1_FPGA0_WLED_2_RED;
    wled #(
        .NUM_LEDS(3),
        .LEVEL(127),
        .CLK_MHZ(27)
    ) fpga0_wled (
        .clk(sysclk),
        .data(PINOUT_FPGA0_WLED_DATA_RAW),
        .green(FPGA0_WLED_GREEN),
        .blue(FPGA0_WLED_BLUE),
        .red(FPGA0_WLED_RED)
    );

    // Name: blink0 (blink)
    wire PINOUT_BLINK0_LED_RAW;
    assign PINOUT_BLINK0_LED = PINOUT_BLINK0_LED_RAW;
    blink #(
        .DIVIDER(13500000)
    ) blink0 (
        .clk(sysclk),
        .led(PINOUT_BLINK0_LED_RAW)
    );

    // Name: i2cbus0 (i2c)
    wire PINOUT_I2CBUS0_SCL_RAW;
    assign PINOUT_I2CBUS0_SCL = PINOUT_I2CBUS0_SCL_RAW;
    i2cbus_i2cbus0 #(
        .MAX_BITS(16),
        .MAX_DIN(48)
    ) i2cbus0 (
        .clk(sysclk),
        .sda(PININOUT_I2CBUS0_SDA),
        .scl(PINOUT_I2CBUS0_SCL_RAW),
        .i2c_lm75_0_temp(VARIN16_I2C_LM75_0_I2C_LM75_0_TEMP),
        .i2c_lm75_0_valid(VARIN1_I2C_LM75_0_I2C_LM75_0_VALID)
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

    // Name: stepdir1 (stepdir)
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

    // Name: stepdir2 (stepdir)
    wire PINOUT_STEPDIR2_STEP_RAW;
    wire PINOUT_STEPDIR2_DIR_RAW;
    wire PINOUT_STEPDIR2_EN_RAW;
    assign PINOUT_STEPDIR2_STEP = PINOUT_STEPDIR2_STEP_RAW;
    assign PINOUT_STEPDIR2_DIR = PINOUT_STEPDIR2_DIR_RAW;
    assign PINOUT_STEPDIR2_EN = PINOUT_STEPDIR2_EN_RAW;
    stepdir #(
        .PULSE_LEN(108),
        .DIR_DELAY(18)
    ) stepdir2 (
        .clk(sysclk),
        .step(PINOUT_STEPDIR2_STEP_RAW),
        .dir(PINOUT_STEPDIR2_DIR_RAW),
        .en(PINOUT_STEPDIR2_EN_RAW),
        .velocity(VAROUT32_STEPDIR2_VELOCITY),
        .enable(VAROUT1_STEPDIR2_ENABLE & ~ERROR),
        .position(VARIN32_STEPDIR2_POSITION)
    );

    // Name: home-x (bitin)
    wire PININ_BITIN0_BIT_INVERTED;
    assign PININ_BITIN0_BIT_INVERTED = ~PININ_BITIN0_BIT;
    assign VARIN1_BITIN0_BIT = PININ_BITIN0_BIT_INVERTED;

    // Name: home-y (bitin)
    wire PININ_BITIN1_BIT_INVERTED;
    assign PININ_BITIN1_BIT_INVERTED = ~PININ_BITIN1_BIT;
    assign VARIN1_BITIN1_BIT = PININ_BITIN1_BIT_INVERTED;

    // Name: home-z (bitin)
    wire PININ_BITIN2_BIT_INVERTED;
    assign PININ_BITIN2_BIT_INVERTED = ~PININ_BITIN2_BIT;
    assign VARIN1_BITIN2_BIT = PININ_BITIN2_BIT_INVERTED;

    // Name: mbmaster0 (mbus)
    wire PINOUT_MBMASTER0_TX_RAW;
    wire PINOUT_MBMASTER0_TX_ENABLE_RAW;
    assign PINOUT_MBMASTER0_TX = PINOUT_MBMASTER0_TX_RAW;
    assign PINOUT_MBMASTER0_TX_ENABLE = PINOUT_MBMASTER0_TX_ENABLE_RAW;
    reg [127:0] VAROUT128_MBMASTER0_TXDATA_TMP;
    reg [7:0] mbmaster0_cmd_num = 0;
    reg [7:0] mbmaster0_frame_counter = 0;
    reg [31:0] mbmaster0_cmd_counter = 0;
    always @(posedge sysclk) begin
        if (INTERFACE_TIMEOUT) begin
            if (mbmaster0_cmd_counter < 5400000) begin
                mbmaster0_cmd_counter <= mbmaster0_cmd_counter + 32'd1;
            end else begin
                mbmaster0_cmd_counter <= 0;
                mbmaster0_frame_counter <= mbmaster0_frame_counter + 8'd1;
            end
        end else begin
            VAROUT128_MBMASTER0_TXDATA_TMP <= VAROUT128_MBMASTER0_TXDATA;
        end
    end
    mbus #(
        .RX_BUFFERSIZE(128),
        .TX_BUFFERSIZE(128),
        .ClkFrequency(27000000),
        .Baud(9600)
    ) mbmaster0 (
        .clk(sysclk),
        .rx(PININ_MBMASTER0_RX),
        .tx(PINOUT_MBMASTER0_TX_RAW),
        .tx_enable(PINOUT_MBMASTER0_TX_ENABLE_RAW),
        .rxdata(VARIN128_MBMASTER0_RXDATA),
        .txdata(VAROUT128_MBMASTER0_TXDATA_TMP)
    );

endmodule
