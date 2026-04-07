/*
    ######### Tangoboard #########


    Toolchain : gowin
    Family    : GW1N-9C
    Type      : GW1NR-LV9QN88PC6/I5
    Package   : 
    Clock     : 27.0 Mhz

    PININ_BITIN0_BIT <- 29 PULLUP
    PININ_BITIN1_BIT <- 53 PULLUP
    PININ_BITIN2_BIT <- 54 PULLUP
    PINOUT_STEPDIR0_STEP -> 63 
    PINOUT_STEPDIR0_DIR -> 86 
    PINOUT_STEPDIR0_EN -> 73 
    PINOUT_STEPDIR1_STEP -> 85 
    PINOUT_STEPDIR1_DIR -> 84 
    PINOUT_STEPDIR2_STEP -> 83 
    PINOUT_STEPDIR2_DIR -> 82 
    PINOUT_W55000_MOSI -> 48 
    PININ_W55000_MISO <- 49 
    PINOUT_W55000_SCLK -> 31 
    PINOUT_W55000_SEL -> 32 
    PININ_BITIN3_BIT <- 26 PULLUP
    PININ_BITIN4_BIT <- 27 PULLUP
    PININ_BITIN5_BIT <- 28 PULLUP
    PINOUT_PWMOUT0_PWM -> 76 
    PINOUT_BITOUT0_BIT -> 75 
    PINOUT_BITOUT1_BIT -> 74 
    PININ_BITIN6_BIT <- 55 PULLUP
    PININ_BITIN7_BIT <- 56 PULLUP
    PININ_SATUART0_RX <- 33 
    PINOUT_SATUART0_TX -> 40 

*/

/* verilator lint_off UNUSEDSIGNAL */

module rio (
        // RIO
        input sysclk_in,
        input PININ_BITIN0_BIT,
        input PININ_BITIN1_BIT,
        input PININ_BITIN2_BIT,
        output PINOUT_STEPDIR0_STEP,
        output PINOUT_STEPDIR0_DIR,
        output PINOUT_STEPDIR0_EN,
        output PINOUT_STEPDIR1_STEP,
        output PINOUT_STEPDIR1_DIR,
        output PINOUT_STEPDIR2_STEP,
        output PINOUT_STEPDIR2_DIR,
        output PINOUT_W55000_MOSI,
        input PININ_W55000_MISO,
        output PINOUT_W55000_SCLK,
        output PINOUT_W55000_SEL,
        input PININ_BITIN3_BIT,
        input PININ_BITIN4_BIT,
        input PININ_BITIN5_BIT,
        output PINOUT_PWMOUT0_PWM,
        output PINOUT_BITOUT0_BIT,
        output PINOUT_BITOUT1_BIT,
        input PININ_BITIN6_BIT,
        input PININ_BITIN7_BIT,
        input PININ_SATUART0_RX,
        output PINOUT_SATUART0_TX
    );

    localparam BUFFER_SIZE_TX = 16'd224; // 28 bytes
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

    reg [31:0] MULTIPLEXED_INPUT_VALUE = 0;
    reg [7:0] MULTIPLEXED_INPUT_ID = 0;
    wire VARIN1_BITIN0_BIT;
    wire VARIN1_BITIN1_BIT;
    wire VARIN1_BITIN2_BIT;
    wire [31:0] VAROUT32_STEPDIR0_VELOCITY;
    wire VAROUT1_STEPDIR0_ENABLE;
    wire [31:0] VARIN32_STEPDIR0_POSITION;
    wire [31:0] VAROUT32_STEPDIR1_VELOCITY;
    wire VAROUT1_STEPDIR1_ENABLE;
    wire [31:0] VARIN32_STEPDIR1_POSITION;
    wire [31:0] VAROUT32_STEPDIR2_VELOCITY;
    wire VAROUT1_STEPDIR2_ENABLE;
    wire [31:0] VARIN32_STEPDIR2_POSITION;
    wire VARIN1_BITIN3_BIT;
    wire VARIN1_BITIN4_BIT;
    wire VARIN1_BITIN5_BIT;
    wire [15:0] VAROUT16_PWMOUT0_DTY;
    wire VAROUT1_PWMOUT0_ENABLE;
    wire VAROUT1_BITOUT0_BIT;
    wire VAROUT1_BITOUT1_BIT;
    wire VARIN1_BITIN6_BIT;
    wire VARIN1_BITIN7_BIT;
    wire [31:0] VARIN32_FEED_POSITION;
    wire VARIN1_SATUART0_TIMEOUT;
    wire [31:0] VARIN32_SPINDLE_POSITION;
    wire [31:0] VARIN32_RAPID_POSITION;
    wire [31:0] VARIN32_JOGWHEEL_POSITION;
    wire VARIN1_MPGESTOP_BIT;
    wire VARIN1_SCALE0_BIT;
    wire VAROUT1_LEDSCALE0_BIT;
    wire VARIN1_SCALE1_BIT;
    wire VARIN1_SCALE2_BIT;
    wire VARIN1_SELECTX_BIT;
    wire VARIN1_SELECTY_BIT;
    wire VAROUT1_LEDSCALE1_BIT;
    wire VAROUT1_LEDSCALE2_BIT;
    wire VAROUT1_SELECTEDX_BIT;
    wire VAROUT1_SELECTEDY_BIT;
    wire VAROUT1_SELECTEDZ_BIT;
    wire VARIN1_SELECTZ_BIT;
    wire VARIN1_LBUTTON_BIT;
    wire VARIN1_CBUTTON_BIT;
    wire VARIN1_RBUTTON_BIT;

    // PC -> MASTER_FPGA / OUT (156 + FILL = 160)
    // assign header_rx = {rx_data[135:128], rx_data[143:136], rx_data[151:144], rx_data[159:152]};
    assign VAROUT32_STEPDIR0_VELOCITY = {rx_data[103:96], rx_data[111:104], rx_data[119:112], rx_data[127:120]};
    assign VAROUT32_STEPDIR1_VELOCITY = {rx_data[71:64], rx_data[79:72], rx_data[87:80], rx_data[95:88]};
    assign VAROUT32_STEPDIR2_VELOCITY = {rx_data[39:32], rx_data[47:40], rx_data[55:48], rx_data[63:56]};
    assign VAROUT16_PWMOUT0_DTY = {rx_data[23:16], rx_data[31:24]};
    assign VAROUT1_STEPDIR0_ENABLE = {rx_data[15]};
    assign VAROUT1_STEPDIR1_ENABLE = {rx_data[14]};
    assign VAROUT1_STEPDIR2_ENABLE = {rx_data[13]};
    assign VAROUT1_PWMOUT0_ENABLE = {rx_data[12]};
    assign VAROUT1_BITOUT0_BIT = {rx_data[11]};
    assign VAROUT1_BITOUT1_BIT = {rx_data[10]};
    assign VAROUT1_LEDSCALE0_BIT = {rx_data[9]};
    assign VAROUT1_LEDSCALE1_BIT = {rx_data[8]};
    assign VAROUT1_LEDSCALE2_BIT = {rx_data[7]};
    assign VAROUT1_SELECTEDX_BIT = {rx_data[6]};
    assign VAROUT1_SELECTEDY_BIT = {rx_data[5]};
    assign VAROUT1_SELECTEDZ_BIT = {rx_data[4]};
    // assign FILL = rx_data[3:0];

    // MASTER_FPGA -> PC IN (219 + FILL = 224)
    assign tx_data = {
        HEADER_TX[7:0], HEADER_TX[15:8], HEADER_TX[23:16], HEADER_TX[31:24],
        timestamp[7:0], timestamp[15:8], timestamp[23:16], timestamp[31:24],
        MULTIPLEXED_INPUT_VALUE[7:0], MULTIPLEXED_INPUT_VALUE[15:8], MULTIPLEXED_INPUT_VALUE[23:16], MULTIPLEXED_INPUT_VALUE[31:24],
        MULTIPLEXED_INPUT_ID[7:0],
        VARIN32_STEPDIR0_POSITION[7:0], VARIN32_STEPDIR0_POSITION[15:8], VARIN32_STEPDIR0_POSITION[23:16], VARIN32_STEPDIR0_POSITION[31:24],
        VARIN32_STEPDIR1_POSITION[7:0], VARIN32_STEPDIR1_POSITION[15:8], VARIN32_STEPDIR1_POSITION[23:16], VARIN32_STEPDIR1_POSITION[31:24],
        VARIN32_STEPDIR2_POSITION[7:0], VARIN32_STEPDIR2_POSITION[15:8], VARIN32_STEPDIR2_POSITION[23:16], VARIN32_STEPDIR2_POSITION[31:24],
        VARIN1_BITIN0_BIT,
        VARIN1_BITIN1_BIT,
        VARIN1_BITIN2_BIT,
        VARIN1_BITIN3_BIT,
        VARIN1_BITIN4_BIT,
        VARIN1_BITIN5_BIT,
        VARIN1_BITIN6_BIT,
        VARIN1_BITIN7_BIT,
        VARIN1_SATUART0_TIMEOUT,
        VARIN1_MPGESTOP_BIT,
        VARIN1_SCALE0_BIT,
        VARIN1_SCALE1_BIT,
        VARIN1_SCALE2_BIT,
        VARIN1_SELECTX_BIT,
        VARIN1_SELECTY_BIT,
        VARIN1_SELECTZ_BIT,
        VARIN1_LBUTTON_BIT,
        VARIN1_CBUTTON_BIT,
        VARIN1_RBUTTON_BIT,
        5'd0
    };


    always @(posedge sysclk) begin
        if (INTERFACE_SYNC_RISINGEDGE == 1) begin
            if (MULTIPLEXED_INPUT_ID < 3) begin
                MULTIPLEXED_INPUT_ID = MULTIPLEXED_INPUT_ID + 1'd1;
            end else begin
                MULTIPLEXED_INPUT_ID = 0;
            end
            if (MULTIPLEXED_INPUT_ID == 0) begin
                MULTIPLEXED_INPUT_VALUE <= VARIN32_FEED_POSITION[31:0];
            end
            if (MULTIPLEXED_INPUT_ID == 1) begin
                MULTIPLEXED_INPUT_VALUE <= VARIN32_SPINDLE_POSITION[31:0];
            end
            if (MULTIPLEXED_INPUT_ID == 2) begin
                MULTIPLEXED_INPUT_VALUE <= VARIN32_RAPID_POSITION[31:0];
            end
            if (MULTIPLEXED_INPUT_ID == 3) begin
                MULTIPLEXED_INPUT_VALUE <= VARIN32_JOGWHEEL_POSITION[31:0];
            end
        end
    end


    // #################### ('satmcu0', 0) (sub0) ####################
    localparam SUB0_BUFFER_SIZE_RX = 16'd176; // 22 bytes
    localparam SUB0_BUFFER_SIZE_TX = 16'd40; // 5 bytes

    wire [SUB0_BUFFER_SIZE_RX-1:0] sub0_rx_data;
    wire [SUB0_BUFFER_SIZE_TX-1:0] sub0_tx_data;

    // SUB0_FPGA -> MASTER_FPGA / INPUTS (170 + FILL)
    // assign header_rx = {sub0_rx_data[151:144], sub0_rx_data[159:152], sub0_rx_data[167:160], sub0_rx_data[175:168]};
    assign VARIN32_FEED_POSITION = {sub0_rx_data[119:112], sub0_rx_data[127:120], sub0_rx_data[135:128], sub0_rx_data[143:136]};
    assign VARIN32_SPINDLE_POSITION = {sub0_rx_data[87:80], sub0_rx_data[95:88], sub0_rx_data[103:96], sub0_rx_data[111:104]};
    assign VARIN32_RAPID_POSITION = {sub0_rx_data[55:48], sub0_rx_data[63:56], sub0_rx_data[71:64], sub0_rx_data[79:72]};
    assign VARIN32_JOGWHEEL_POSITION = {sub0_rx_data[23:16], sub0_rx_data[31:24], sub0_rx_data[39:32], sub0_rx_data[47:40]};
    assign VARIN1_MPGESTOP_BIT = {sub0_rx_data[15]};
    assign VARIN1_SCALE0_BIT = {sub0_rx_data[14]};
    assign VARIN1_SCALE1_BIT = {sub0_rx_data[13]};
    assign VARIN1_SCALE2_BIT = {sub0_rx_data[12]};
    assign VARIN1_SELECTX_BIT = {sub0_rx_data[11]};
    assign VARIN1_SELECTY_BIT = {sub0_rx_data[10]};
    assign VARIN1_SELECTZ_BIT = {sub0_rx_data[9]};
    assign VARIN1_LBUTTON_BIT = {sub0_rx_data[8]};
    assign VARIN1_CBUTTON_BIT = {sub0_rx_data[7]};
    assign VARIN1_RBUTTON_BIT = {sub0_rx_data[6]};
    // assign FILL = sub0_rx_data[5:0];

    // MASTER_FPGA -> SUB0_FPGA / OUTPUTS (38 + FILL)
    assign sub0_tx_data = {
        32'h74697277,
        VAROUT1_LEDSCALE0_BIT,
        VAROUT1_LEDSCALE1_BIT,
        VAROUT1_LEDSCALE2_BIT,
        VAROUT1_SELECTEDX_BIT,
        VAROUT1_SELECTEDY_BIT,
        VAROUT1_SELECTEDZ_BIT,
        2'd0
    };

    // ###############################################

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

    // Name: stepdir0 (stepdir)
    wire PINOUT_STEPDIR0_STEP_RAW;
    wire PINOUT_STEPDIR0_DIR_RAW;
    wire PINOUT_STEPDIR0_EN_RAW;
    assign PINOUT_STEPDIR0_STEP = PINOUT_STEPDIR0_STEP_RAW;
    assign PINOUT_STEPDIR0_DIR = PINOUT_STEPDIR0_DIR_RAW;
    assign PINOUT_STEPDIR0_EN = PINOUT_STEPDIR0_EN_RAW;
    stepdir #(
        .PULSE_LEN(27),
        .DIR_DELAY(18)
    ) stepdir0 (
        .clk(sysclk),
        .step(PINOUT_STEPDIR0_STEP_RAW),
        .dir(PINOUT_STEPDIR0_DIR_RAW),
        .en(PINOUT_STEPDIR0_EN_RAW),
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
        .PULSE_LEN(27),
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
    wire UNUSED_PIN_STEPDIR2_EN;
    assign PINOUT_STEPDIR2_STEP = PINOUT_STEPDIR2_STEP_RAW;
    assign PINOUT_STEPDIR2_DIR = PINOUT_STEPDIR2_DIR_RAW;
    stepdir #(
        .PULSE_LEN(27),
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
        .IP_ADDR({8'd192, 8'd168, 8'd11, 8'd201}),
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

    // Name: alarm_x (bitin)
    assign VARIN1_BITIN3_BIT = PININ_BITIN3_BIT;

    // Name: alarm_y (bitin)
    assign VARIN1_BITIN4_BIT = PININ_BITIN4_BIT;

    // Name: alarm_z (bitin)
    assign VARIN1_BITIN5_BIT = PININ_BITIN5_BIT;

    // Name: pwmout0 (pwmout)
    wire PINOUT_PWMOUT0_PWM_RAW;
    wire UNUSED_PIN_PWMOUT0_DIR;
    wire UNUSED_PIN_PWMOUT0_EN;
    assign PINOUT_PWMOUT0_PWM = PINOUT_PWMOUT0_PWM_RAW;
    // PWM-Resolution: >= 14bit
    pwmout #(
        .DIVIDER(27000),
        .BITWIDTH(16)
    ) pwmout0 (
        .clk(sysclk),
        .pwm(PINOUT_PWMOUT0_PWM_RAW),
        .dir(UNUSED_PIN_PWMOUT0_DIR),
        .en(UNUSED_PIN_PWMOUT0_EN),
        .dty(VAROUT16_PWMOUT0_DTY),
        .enable(VAROUT1_PWMOUT0_ENABLE & ~ERROR)
    );

    // Name: forward (bitout)
    wire PINOUT_BITOUT0_BIT_RAW;
    assign PINOUT_BITOUT0_BIT = PINOUT_BITOUT0_BIT_RAW;
    assign PINOUT_BITOUT0_BIT_RAW = VAROUT1_BITOUT0_BIT;

    // Name: bitout1 (bitout)
    wire PINOUT_BITOUT1_BIT_RAW;
    assign PINOUT_BITOUT1_BIT = PINOUT_BITOUT1_BIT_RAW;
    assign PINOUT_BITOUT1_BIT_RAW = VAROUT1_BITOUT1_BIT;

    // Name: touch (bitin)
    wire PININ_BITIN6_BIT_INVERTED;
    assign PININ_BITIN6_BIT_INVERTED = ~PININ_BITIN6_BIT;
    assign VARIN1_BITIN6_BIT = PININ_BITIN6_BIT_INVERTED;

    // Name: estop-sw (bitin)
    wire PININ_BITIN7_BIT_INVERTED;
    assign PININ_BITIN7_BIT_INVERTED = ~PININ_BITIN7_BIT;
    assign VARIN1_BITIN7_BIT = PININ_BITIN7_BIT_INVERTED;

    // Name: satuart0 (satuart)
    wire PINOUT_SATUART0_TX_RAW;
    wire UNUSED_PIN_SATUART0_TX_ENABLE;
    assign PINOUT_SATUART0_TX = PINOUT_SATUART0_TX_RAW;
    satuart #(
        .BUFFER_SIZE_RX(SUB0_BUFFER_SIZE_RX),
        .BUFFER_SIZE_TX(SUB0_BUFFER_SIZE_TX),
        .MSGID(32'h61746164),
        .ClkFrequency(27000000),
        .Baud(1000000),
        .Timeout(2700000),
        .CSUM(1)
    ) satuart0 (
        .clk(sysclk),
        .rx(PININ_SATUART0_RX),
        .tx(PINOUT_SATUART0_TX_RAW),
        .tx_enable(UNUSED_PIN_SATUART0_TX_ENABLE),
        .timeout(VARIN1_SATUART0_TIMEOUT),
        .rx_data(sub0_rx_data),
        .tx_data(sub0_tx_data),
        .sync_in(INTERFACE_SYNC_RISINGEDGE)
    );

endmodule
