/*
    ######### TangPrimer25K #########


    Toolchain : gowin
    Family    : GW5A-25A
    Type      : GW5A-LV25MG121NC1/I0
    Package   : PG256
    Clock     : 50.0 Mhz

    PINOUT_BLINK0_LED -> E8 
    PINOUT_BITOUT0_BIT -> D7 
    PININ_BITIN0_BIT <- H11 PULLDOWN
    PININ_BITIN1_BIT <- H10 PULLDOWN
    PINOUT_STEPDIR0_STEP -> L5 
    PINOUT_STEPDIR0_DIR -> K5 
    PINOUT_STEPDIR0_EN -> A11 
    PINOUT_STEPDIR1_STEP -> K11 
    PINOUT_STEPDIR1_DIR -> L11 
    PINOUT_STEPDIR2_STEP -> E11 
    PINOUT_STEPDIR2_DIR -> E10 
    PINOUT_W55000_MOSI -> B11 
    PININ_W55000_MISO <- C11 
    PINOUT_W55000_SCLK -> G11 
    PINOUT_W55000_SEL -> D11 

*/

/* verilator lint_off UNUSEDSIGNAL */

module rio (
        // RIO
        input sysclk_in,
        output PINOUT_BLINK0_LED,
        output PINOUT_BITOUT0_BIT,
        input PININ_BITIN0_BIT,
        input PININ_BITIN1_BIT,
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
        output PINOUT_W55000_SEL
    );

    localparam BUFFER_SIZE_TX = 16'd168; // 21 bytes
    localparam BUFFER_SIZE_RX = 16'd136; // 17 bytes

    reg INTERFACE_TIMEOUT = 0;
    wire INTERFACE_SYNC;
    wire ERROR;
    assign ERROR = (INTERFACE_TIMEOUT);

    wire sysclk;
    assign sysclk = sysclk_in;

    reg[2:0] INTERFACE_SYNCr;  always @(posedge sysclk) INTERFACE_SYNCr <= {INTERFACE_SYNCr[1:0], INTERFACE_SYNC};
    wire INTERFACE_SYNC_RISINGEDGE = (INTERFACE_SYNCr[2:1]==2'b01);

    parameter TIMEOUT = 5000000;
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

    wire VAROUT1_BITOUT0_BIT;
    wire VARIN1_BITIN0_BIT;
    wire VARIN1_BITIN1_BIT;
    wire [31:0] VAROUT32_STEPDIR0_VELOCITY;
    wire VAROUT1_STEPDIR0_ENABLE;
    wire [31:0] VARIN32_STEPDIR0_POSITION;
    wire [31:0] VAROUT32_STEPDIR1_VELOCITY;
    wire VAROUT1_STEPDIR1_ENABLE;
    wire [31:0] VARIN32_STEPDIR1_POSITION;
    wire [31:0] VAROUT32_STEPDIR2_VELOCITY;
    wire VAROUT1_STEPDIR2_ENABLE;
    wire [31:0] VARIN32_STEPDIR2_POSITION;

    // PC -> MASTER_FPGA / OUT (132 + FILL = 136)
    // assign header_rx = {rx_data[111:104], rx_data[119:112], rx_data[127:120], rx_data[135:128]};
    assign VAROUT32_STEPDIR0_VELOCITY = {rx_data[79:72], rx_data[87:80], rx_data[95:88], rx_data[103:96]};
    assign VAROUT32_STEPDIR1_VELOCITY = {rx_data[47:40], rx_data[55:48], rx_data[63:56], rx_data[71:64]};
    assign VAROUT32_STEPDIR2_VELOCITY = {rx_data[15:8], rx_data[23:16], rx_data[31:24], rx_data[39:32]};
    assign VAROUT1_BITOUT0_BIT = {rx_data[7]};
    assign VAROUT1_STEPDIR0_ENABLE = {rx_data[6]};
    assign VAROUT1_STEPDIR1_ENABLE = {rx_data[5]};
    assign VAROUT1_STEPDIR2_ENABLE = {rx_data[4]};
    // assign FILL = rx_data[3:0];

    // MASTER_FPGA -> PC IN (162 + FILL = 168)
    assign tx_data = {
        HEADER_TX[7:0], HEADER_TX[15:8], HEADER_TX[23:16], HEADER_TX[31:24],
        timestamp[7:0], timestamp[15:8], timestamp[23:16], timestamp[31:24],
        VARIN32_STEPDIR0_POSITION[7:0], VARIN32_STEPDIR0_POSITION[15:8], VARIN32_STEPDIR0_POSITION[23:16], VARIN32_STEPDIR0_POSITION[31:24],
        VARIN32_STEPDIR1_POSITION[7:0], VARIN32_STEPDIR1_POSITION[15:8], VARIN32_STEPDIR1_POSITION[23:16], VARIN32_STEPDIR1_POSITION[31:24],
        VARIN32_STEPDIR2_POSITION[7:0], VARIN32_STEPDIR2_POSITION[15:8], VARIN32_STEPDIR2_POSITION[23:16], VARIN32_STEPDIR2_POSITION[31:24],
        VARIN1_BITIN0_BIT,
        VARIN1_BITIN1_BIT,
        6'd0
    };



    // Name: status (blink)
    wire PINOUT_BLINK0_LED_RAW_ONERROR;
    wire PINOUT_BLINK0_LED_RAW;
    assign PINOUT_BLINK0_LED_RAW_ONERROR = PINOUT_BLINK0_LED_RAW & ERROR;
    assign PINOUT_BLINK0_LED = PINOUT_BLINK0_LED_RAW_ONERROR;
    blink #(
        .DIVIDER(25000000)
    ) blink0 (
        .clk(sysclk),
        .led(PINOUT_BLINK0_LED_RAW)
    );

    // Name: LED (bitout)
    wire PINOUT_BITOUT0_BIT_RAW;
    assign PINOUT_BITOUT0_BIT = PINOUT_BITOUT0_BIT_RAW;
    assign PINOUT_BITOUT0_BIT_RAW = VAROUT1_BITOUT0_BIT;

    // Name: SW1 (bitin)
    assign VARIN1_BITIN0_BIT = PININ_BITIN0_BIT;

    // Name: SW2 (bitin)
    assign VARIN1_BITIN1_BIT = PININ_BITIN1_BIT;

    // Name: stepdir0 (stepdir)
    wire PINOUT_STEPDIR0_STEP_RAW;
    wire PINOUT_STEPDIR0_DIR_RAW;
    wire PINOUT_STEPDIR0_EN_RAW;
    assign PINOUT_STEPDIR0_STEP = PINOUT_STEPDIR0_STEP_RAW;
    assign PINOUT_STEPDIR0_DIR = PINOUT_STEPDIR0_DIR_RAW;
    assign PINOUT_STEPDIR0_EN = PINOUT_STEPDIR0_EN_RAW;
    stepdir #(
        .PULSE_LEN(200),
        .DIR_DELAY(35)
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
        .PULSE_LEN(200),
        .DIR_DELAY(35)
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
        .PULSE_LEN(200),
        .DIR_DELAY(35)
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
        .IP_ADDR({8'd192, 8'd168, 8'd11, 8'd194}),
        .NET_MASK({8'd255, 8'd255, 8'd255, 8'd0}),
        .GW_ADDR({8'd192, 8'd168, 8'd11, 8'd1}),
        .PORT(2390),
        .BUFFER_SIZE_RX(BUFFER_SIZE_RX),
        .BUFFER_SIZE_TX(BUFFER_SIZE_TX),
        .MSGID(32'h74697277),
        .DIVIDER(1)
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

endmodule
