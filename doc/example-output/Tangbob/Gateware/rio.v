/*
    ######### Tangbob #########


    Toolchain : gowin
    Family    : GW1N-9C
    Type      : GW1NR-LV9QN88PC6/I5
    Package   : 
    Clock     : 27.0 Mhz

    PINOUT_W55000_MOSI -> SPI:MOSI 
    PININ_W55000_MISO <- SPI:MISO 
    PINOUT_W55000_SCLK -> SPI:SCLK 
    PINOUT_W55000_SEL -> SPI:SEL 
    PINOUT_WLED0_DATA -> WLED:DATA 
    PINOUT_MODBUS0_TX -> MODBUS:TX 
    PININ_MODBUS0_RX <- MODBUS:RX 
    PINOUT_MODBUS0_TX_ENABLE -> MODBUS:TX_ENABLE 
    PINOUT_BLINK0_LED -> 10 
    PININOUT_I2CBUS0_SDA <> I2C:sda 
    PINOUT_I2CBUS0_SCL -> I2C:scl 
    PINOUT_BITOUT0_BIT -> 42 
    PININ_BITIN0_BIT <- 37 PULLUP
    PININ_BITIN1_BIT <- 38 PULLUP
    PININ_BITIN2_BIT <- 35 PULLUP
    PINOUT_BITOUT1_BIT -> 30 
    PINOUT_PWMOUT0_PWM -> 53 
    PININ_BITIN3_BIT <- 39 PULLUP
    PININ_BITIN4_BIT <- 36 PULLUP
    PINOUT_STEPDIR0_STEP -> 41 
    PINOUT_STEPDIR0_DIR -> 40 
    PINOUT_STEPDIR1_STEP -> 33 
    PINOUT_STEPDIR1_DIR -> 29 
    PINOUT_STEPDIR2_STEP -> 28 
    PINOUT_STEPDIR2_DIR -> 27 
    PINOUT_STEPDIR3_STEP -> 26 
    PINOUT_STEPDIR3_DIR -> 25 

*/

/* verilator lint_off UNUSEDSIGNAL */

module rio (
        input sysclk_in,
        output PINOUT_W55000_MOSI,
        input PININ_W55000_MISO,
        output PINOUT_W55000_SCLK,
        output PINOUT_W55000_SEL,
        output PINOUT_WLED0_DATA,
        output PINOUT_MODBUS0_TX,
        input PININ_MODBUS0_RX,
        output PINOUT_MODBUS0_TX_ENABLE,
        output PINOUT_BLINK0_LED,
        inout PININOUT_I2CBUS0_SDA,
        output PINOUT_I2CBUS0_SCL,
        output PINOUT_BITOUT0_BIT,
        input PININ_BITIN0_BIT,
        input PININ_BITIN1_BIT,
        input PININ_BITIN2_BIT,
        output PINOUT_BITOUT1_BIT,
        output PINOUT_PWMOUT0_PWM,
        input PININ_BITIN3_BIT,
        input PININ_BITIN4_BIT,
        output PINOUT_STEPDIR0_STEP,
        output PINOUT_STEPDIR0_DIR,
        output PINOUT_STEPDIR1_STEP,
        output PINOUT_STEPDIR1_DIR,
        output PINOUT_STEPDIR2_STEP,
        output PINOUT_STEPDIR2_DIR,
        output PINOUT_STEPDIR3_STEP,
        output PINOUT_STEPDIR3_DIR
    );

    parameter BUFFER_SIZE = 16'd352; // 44 bytes

    reg INTERFACE_TIMEOUT = 0;
    wire INTERFACE_SYNC;
    parameter ESTOP = 0;
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

    wire[351:0] rx_data;
    wire[351:0] tx_data;

    reg [31:0] timestamp = 0;
    reg signed [31:0] header_tx = 0;
    always @(posedge sysclk) begin
        timestamp <= timestamp + 1'd1;
        if (ESTOP) begin
            header_tx <= 32'h65737470;
        end else begin
            header_tx <= 32'h64617461;
        end
    end

    reg [15:0] MULTIPLEXED_INPUT_VALUE = 0;
    reg [7:0] MULTIPLEXED_INPUT_ID = 0;
    wire VAROUT1_WLED0_0_GREEN;
    wire VAROUT1_WLED0_0_BLUE;
    wire VAROUT1_WLED0_0_RED;
    wire [127:0] VARIN128_MODBUS0_RXDATA;
    wire [127:0] VAROUT128_MODBUS0_TXDATA;
    wire [15:0] VARIN16_I2CBUS0_LM75_0_TEMP;
    wire VARIN1_I2CBUS0_LM75_0_VALID;
    wire VAROUT1_BITOUT0_BIT;
    wire VARIN1_BITIN0_BIT;
    wire VARIN1_BITIN1_BIT;
    wire VARIN1_BITIN2_BIT;
    wire VAROUT1_BITOUT1_BIT;
    wire [31:0] VAROUT32_PWMOUT0_DTY;
    wire VAROUT1_PWMOUT0_ENABLE;
    wire VARIN1_BITIN3_BIT;
    wire VARIN1_BITIN4_BIT;
    wire [31:0] VAROUT32_STEPDIR0_VELOCITY;
    wire VAROUT1_STEPDIR0_ENABLE;
    wire [31:0] VARIN32_STEPDIR0_POSITION;
    wire [31:0] VAROUT32_STEPDIR1_VELOCITY;
    wire VAROUT1_STEPDIR1_ENABLE;
    wire [31:0] VARIN32_STEPDIR1_POSITION;
    wire [31:0] VAROUT32_STEPDIR2_VELOCITY;
    wire VAROUT1_STEPDIR2_ENABLE;
    wire [31:0] VARIN32_STEPDIR2_POSITION;
    wire [31:0] VAROUT32_STEPDIR3_VELOCITY;
    wire VAROUT1_STEPDIR3_ENABLE;
    wire [31:0] VARIN32_STEPDIR3_POSITION;

    // PC -> FPGA (330 + FILL)
    // assign header_rx = {rx_data[327:320], rx_data[335:328], rx_data[343:336], rx_data[351:344]};
    assign VAROUT128_MODBUS0_TXDATA = {rx_data[199:192], rx_data[207:200], rx_data[215:208], rx_data[223:216], rx_data[231:224], rx_data[239:232], rx_data[247:240], rx_data[255:248], rx_data[263:256], rx_data[271:264], rx_data[279:272], rx_data[287:280], rx_data[295:288], rx_data[303:296], rx_data[311:304], rx_data[319:312]};
    assign VAROUT32_PWMOUT0_DTY = {rx_data[167:160], rx_data[175:168], rx_data[183:176], rx_data[191:184]};
    assign VAROUT32_STEPDIR0_VELOCITY = {rx_data[135:128], rx_data[143:136], rx_data[151:144], rx_data[159:152]};
    assign VAROUT32_STEPDIR1_VELOCITY = {rx_data[103:96], rx_data[111:104], rx_data[119:112], rx_data[127:120]};
    assign VAROUT32_STEPDIR2_VELOCITY = {rx_data[71:64], rx_data[79:72], rx_data[87:80], rx_data[95:88]};
    assign VAROUT32_STEPDIR3_VELOCITY = {rx_data[39:32], rx_data[47:40], rx_data[55:48], rx_data[63:56]};
    assign VAROUT1_WLED0_0_GREEN = {rx_data[31]};
    assign VAROUT1_WLED0_0_BLUE = {rx_data[30]};
    assign VAROUT1_WLED0_0_RED = {rx_data[29]};
    assign VAROUT1_BITOUT0_BIT = {rx_data[28]};
    assign VAROUT1_BITOUT1_BIT = {rx_data[27]};
    assign VAROUT1_PWMOUT0_ENABLE = {rx_data[26]};
    assign VAROUT1_STEPDIR0_ENABLE = {rx_data[25]};
    assign VAROUT1_STEPDIR1_ENABLE = {rx_data[24]};
    assign VAROUT1_STEPDIR2_ENABLE = {rx_data[23]};
    assign VAROUT1_STEPDIR3_ENABLE = {rx_data[22]};
    // assign FILL = rx_data[21:0];

    // FPGA -> PC (349 + FILL)
    assign tx_data = {
        header_tx[7:0], header_tx[15:8], header_tx[23:16], header_tx[31:24],
        timestamp[7:0], timestamp[15:8], timestamp[23:16], timestamp[31:24],
        MULTIPLEXED_INPUT_VALUE[7:0], MULTIPLEXED_INPUT_VALUE[15:8],
        MULTIPLEXED_INPUT_ID[7:0],
        VARIN128_MODBUS0_RXDATA[7:0], VARIN128_MODBUS0_RXDATA[15:8], VARIN128_MODBUS0_RXDATA[23:16], VARIN128_MODBUS0_RXDATA[31:24], VARIN128_MODBUS0_RXDATA[39:32], VARIN128_MODBUS0_RXDATA[47:40], VARIN128_MODBUS0_RXDATA[55:48], VARIN128_MODBUS0_RXDATA[63:56], VARIN128_MODBUS0_RXDATA[71:64], VARIN128_MODBUS0_RXDATA[79:72], VARIN128_MODBUS0_RXDATA[87:80], VARIN128_MODBUS0_RXDATA[95:88], VARIN128_MODBUS0_RXDATA[103:96], VARIN128_MODBUS0_RXDATA[111:104], VARIN128_MODBUS0_RXDATA[119:112], VARIN128_MODBUS0_RXDATA[127:120],
        VARIN32_STEPDIR0_POSITION[7:0], VARIN32_STEPDIR0_POSITION[15:8], VARIN32_STEPDIR0_POSITION[23:16], VARIN32_STEPDIR0_POSITION[31:24],
        VARIN32_STEPDIR1_POSITION[7:0], VARIN32_STEPDIR1_POSITION[15:8], VARIN32_STEPDIR1_POSITION[23:16], VARIN32_STEPDIR1_POSITION[31:24],
        VARIN32_STEPDIR2_POSITION[7:0], VARIN32_STEPDIR2_POSITION[15:8], VARIN32_STEPDIR2_POSITION[23:16], VARIN32_STEPDIR2_POSITION[31:24],
        VARIN32_STEPDIR3_POSITION[7:0], VARIN32_STEPDIR3_POSITION[15:8], VARIN32_STEPDIR3_POSITION[23:16], VARIN32_STEPDIR3_POSITION[31:24],
        VARIN1_BITIN0_BIT,
        VARIN1_BITIN1_BIT,
        VARIN1_BITIN2_BIT,
        VARIN1_BITIN3_BIT,
        VARIN1_BITIN4_BIT,
        3'd0
    };


    // update expansion output pins
    always @(posedge sysclk) begin
    end
    always @(posedge sysclk) begin
        if (INTERFACE_SYNC_RISINGEDGE == 1) begin
            if (MULTIPLEXED_INPUT_ID < 1) begin
                MULTIPLEXED_INPUT_ID = MULTIPLEXED_INPUT_ID + 1'd1;
            end else begin
                MULTIPLEXED_INPUT_ID = 0;
            end
            if (MULTIPLEXED_INPUT_ID == 0) begin
                MULTIPLEXED_INPUT_VALUE <= VARIN16_I2CBUS0_LM75_0_TEMP[15:0];
            end
            if (MULTIPLEXED_INPUT_ID == 1) begin
                MULTIPLEXED_INPUT_VALUE <= VARIN1_I2CBUS0_LM75_0_VALID;
            end
        end
    end

    // Name: w55000 (w5500)
    assign PINOUT_W55000_MOSI = PINOUT_W55000_MOSI_RAW;
    assign PINOUT_W55000_SCLK = PINOUT_W55000_SCLK_RAW;
    assign PINOUT_W55000_SEL = PINOUT_W55000_SEL_RAW;
    wire PINOUT_W55000_MOSI_RAW;
    wire PINOUT_W55000_SCLK_RAW;
    wire PINOUT_W55000_SEL_RAW;
    w5500 #(
        .MAC_ADDR({8'hAA, 8'hAF, 8'hFA, 8'hCC, 8'hE3, 8'h1C}),
        .IP_ADDR({8'd192, 8'd168, 8'd10, 8'd194}),
        .NET_MASK({8'd255, 8'd255, 8'd255, 8'd0}),
        .GW_ADDR({8'd192, 8'd168, 8'd10, 8'd1}),
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
        .intr(1'd0),
        .rx_data(rx_data),
        .tx_data(tx_data),
        .sync(INTERFACE_SYNC)
    );

    // Name: wled0 (wled)
    assign PINOUT_WLED0_DATA = PINOUT_WLED0_DATA_RAW;
    wire PINOUT_WLED0_DATA_RAW;
    wire [0:0] WLED0_GREEN;
    wire [0:0] WLED0_BLUE;
    wire [0:0] WLED0_RED;
    assign WLED0_GREEN[0] = VAROUT1_WLED0_0_GREEN;
    assign WLED0_BLUE[0] = VAROUT1_WLED0_0_BLUE;
    assign WLED0_RED[0] = VAROUT1_WLED0_0_RED;
    wled #(
        .NUM_LEDS(1),
        .LEVEL(127),
        .CLK_MHZ(27)
    ) wled0 (
        .clk(sysclk),
        .data(PINOUT_WLED0_DATA_RAW),
        .green(WLED0_GREEN),
        .blue(WLED0_BLUE),
        .red(WLED0_RED)
    );

    // Name: modbus0 (modbus)
    assign PINOUT_MODBUS0_TX = PINOUT_MODBUS0_TX_RAW;
    assign PINOUT_MODBUS0_TX_ENABLE = PINOUT_MODBUS0_TX_ENABLE_RAW;
    wire PINOUT_MODBUS0_TX_RAW;
    wire PINOUT_MODBUS0_TX_ENABLE_RAW;
    reg [127:0] VAROUT128_MODBUS0_TXDATA_TMP;
    reg [7:0] modbus0_cmd_num = 0;
    reg [7:0] modbus0_frame_counter = 0;
    reg [31:0] modbus0_cmd_counter = 0;
    always @(posedge sysclk) begin
        if (ERROR) begin
            if (modbus0_cmd_counter < 5400000) begin
                modbus0_cmd_counter <= modbus0_cmd_counter + 32'd1;
            end else begin
                modbus0_cmd_counter <= 0;
                modbus0_frame_counter <= modbus0_frame_counter + 8'd1;
                case (modbus0_cmd_num)
                endcase
            end
        end else begin
            VAROUT128_MODBUS0_TXDATA_TMP <= VAROUT128_MODBUS0_TXDATA;
        end
    end
    modbus #(
        .RX_BUFFERSIZE(128),
        .TX_BUFFERSIZE(128),
        .ClkFrequency(27000000),
        .Baud(9600)
    ) modbus0 (
        .clk(sysclk),
        .tx(PINOUT_MODBUS0_TX_RAW),
        .rx(PININ_MODBUS0_RX),
        .tx_enable(PINOUT_MODBUS0_TX_ENABLE_RAW),
        .rxdata(VARIN128_MODBUS0_RXDATA),
        .txdata(VAROUT128_MODBUS0_TXDATA_TMP)
    );

    // Name: blink0 (blink)
    assign PINOUT_BLINK0_LED = PINOUT_BLINK0_LED_RAW;
    wire PINOUT_BLINK0_LED_RAW;
    blink #(
        .DIVIDER(13500000)
    ) blink0 (
        .clk(sysclk),
        .led(PINOUT_BLINK0_LED_RAW)
    );

    // Name: i2cbus0 (i2cbus)
    assign PINOUT_I2CBUS0_SCL = PINOUT_I2CBUS0_SCL_RAW;
    wire PINOUT_I2CBUS0_SCL_RAW;
    i2cbus_i2cbus0 #(
        .MAX_BITS(16),
        .MAX_DIN(48)
    ) i2cbus0 (
        .clk(sysclk),
        .sda(PININOUT_I2CBUS0_SDA),
        .scl(PINOUT_I2CBUS0_SCL_RAW),
        .lm75_0_temp(VARIN16_I2CBUS0_LM75_0_TEMP),
        .lm75_0_valid(VARIN1_I2CBUS0_LM75_0_VALID)
    );

    // Name: enable (bitout)
    wire PINOUT_BITOUT0_BIT_RAW_INVERTED;
    assign PINOUT_BITOUT0_BIT_RAW_INVERTED = ~PINOUT_BITOUT0_BIT_RAW;
    wire PINOUT_BITOUT0_BIT_RAW_INVERTED_ONERROR;
    assign PINOUT_BITOUT0_BIT_RAW_INVERTED_ONERROR = PINOUT_BITOUT0_BIT_RAW_INVERTED & ~ERROR;
    wire PINOUT_BITOUT0_BIT_RAW_INVERTED_ONERROR_INVERTED;
    assign PINOUT_BITOUT0_BIT_RAW_INVERTED_ONERROR_INVERTED = ~PINOUT_BITOUT0_BIT_RAW_INVERTED_ONERROR;
    assign PINOUT_BITOUT0_BIT = PINOUT_BITOUT0_BIT_RAW_INVERTED_ONERROR_INVERTED;
    wire PINOUT_BITOUT0_BIT_RAW;
    assign PINOUT_BITOUT0_BIT_RAW = VAROUT1_BITOUT0_BIT;

    // Name: home-x (bitin)
    assign VARIN1_BITIN0_BIT = PININ_BITIN0_BIT;

    // Name: home-y (bitin)
    assign VARIN1_BITIN1_BIT = PININ_BITIN1_BIT;

    // Name: home-z (bitin)
    assign VARIN1_BITIN2_BIT = PININ_BITIN2_BIT;

    // Name: spindle-enable (bitout)
    wire PINOUT_BITOUT1_BIT_RAW_INVERTED;
    assign PINOUT_BITOUT1_BIT_RAW_INVERTED = ~PINOUT_BITOUT1_BIT_RAW;
    assign PINOUT_BITOUT1_BIT = PINOUT_BITOUT1_BIT_RAW_INVERTED;
    wire PINOUT_BITOUT1_BIT_RAW;
    assign PINOUT_BITOUT1_BIT_RAW = VAROUT1_BITOUT1_BIT;

    // Name: pwm (pwmout)
    wire PINOUT_PWMOUT0_PWM_RAW_INVERTED;
    assign PINOUT_PWMOUT0_PWM_RAW_INVERTED = ~PINOUT_PWMOUT0_PWM_RAW;
    assign PINOUT_PWMOUT0_PWM = PINOUT_PWMOUT0_PWM_RAW_INVERTED;
    wire PINOUT_PWMOUT0_PWM_RAW;
    pwmout #(
        .DIVIDER(2700)
    ) pwmout0 (
        .clk(sysclk),
        .pwm(PINOUT_PWMOUT0_PWM_RAW),
        .dty(VAROUT32_PWMOUT0_DTY),
        .enable(VAROUT1_PWMOUT0_ENABLE & ~ERROR)
    );

    // Name: e-stop (bitin)
    assign VARIN1_BITIN3_BIT = PININ_BITIN3_BIT;

    // Name: probe (bitin)
    assign VARIN1_BITIN4_BIT = PININ_BITIN4_BIT;

    // Name: joint-0 (stepdir)
    assign PINOUT_STEPDIR0_STEP = PINOUT_STEPDIR0_STEP_RAW;
    assign PINOUT_STEPDIR0_DIR = PINOUT_STEPDIR0_DIR_RAW;
    wire PINOUT_STEPDIR0_STEP_RAW;
    wire PINOUT_STEPDIR0_DIR_RAW;
    stepdir #(
        .PULSE_LEN(108),
        .DIR_DELAY(18)
    ) stepdir0 (
        .clk(sysclk),
        .step(PINOUT_STEPDIR0_STEP_RAW),
        .dir(PINOUT_STEPDIR0_DIR_RAW),
        .velocity(VAROUT32_STEPDIR0_VELOCITY),
        .enable(VAROUT1_STEPDIR0_ENABLE & ~ERROR),
        .position(VARIN32_STEPDIR0_POSITION)
    );

    // Name: joint-1 (stepdir)
    assign PINOUT_STEPDIR1_STEP = PINOUT_STEPDIR1_STEP_RAW;
    assign PINOUT_STEPDIR1_DIR = PINOUT_STEPDIR1_DIR_RAW;
    wire PINOUT_STEPDIR1_STEP_RAW;
    wire PINOUT_STEPDIR1_DIR_RAW;
    stepdir #(
        .PULSE_LEN(108),
        .DIR_DELAY(18)
    ) stepdir1 (
        .clk(sysclk),
        .step(PINOUT_STEPDIR1_STEP_RAW),
        .dir(PINOUT_STEPDIR1_DIR_RAW),
        .velocity(VAROUT32_STEPDIR1_VELOCITY),
        .enable(VAROUT1_STEPDIR1_ENABLE & ~ERROR),
        .position(VARIN32_STEPDIR1_POSITION)
    );

    // Name: joint-2 (stepdir)
    assign PINOUT_STEPDIR2_STEP = PINOUT_STEPDIR2_STEP_RAW;
    assign PINOUT_STEPDIR2_DIR = PINOUT_STEPDIR2_DIR_RAW;
    wire PINOUT_STEPDIR2_STEP_RAW;
    wire PINOUT_STEPDIR2_DIR_RAW;
    stepdir #(
        .PULSE_LEN(108),
        .DIR_DELAY(18)
    ) stepdir2 (
        .clk(sysclk),
        .step(PINOUT_STEPDIR2_STEP_RAW),
        .dir(PINOUT_STEPDIR2_DIR_RAW),
        .velocity(VAROUT32_STEPDIR2_VELOCITY),
        .enable(VAROUT1_STEPDIR2_ENABLE & ~ERROR),
        .position(VARIN32_STEPDIR2_POSITION)
    );

    // Name: joint-3 (stepdir)
    assign PINOUT_STEPDIR3_STEP = PINOUT_STEPDIR3_STEP_RAW;
    assign PINOUT_STEPDIR3_DIR = PINOUT_STEPDIR3_DIR_RAW;
    wire PINOUT_STEPDIR3_STEP_RAW;
    wire PINOUT_STEPDIR3_DIR_RAW;
    stepdir #(
        .PULSE_LEN(108),
        .DIR_DELAY(18)
    ) stepdir3 (
        .clk(sysclk),
        .step(PINOUT_STEPDIR3_STEP_RAW),
        .dir(PINOUT_STEPDIR3_DIR_RAW),
        .velocity(VAROUT32_STEPDIR3_VELOCITY),
        .enable(VAROUT1_STEPDIR3_ENABLE & ~ERROR),
        .position(VARIN32_STEPDIR3_POSITION)
    );

endmodule
