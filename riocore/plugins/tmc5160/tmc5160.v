
module tmc5160 #(
    parameter integer SPI_DIVIDER   = 25,
    parameter integer STARTUP_CYCLES = 2500000,

    parameter [31:0] GCONF          = 32'h00000004,
    parameter [31:0] GLOBAL_SCALER  = 32'h00000000,
    parameter [31:0] IHOLD_IRUN     = 32'h00080F05,
    parameter [31:0] TPOWERDOWN     = 32'h0000000A,
    parameter [31:0] TPWMTHRS       = 32'h00000000,
    parameter [31:0] TCOOLTHRS      = 32'h00000000,
    parameter [31:0] THIGH          = 32'h00000000,
    parameter [31:0] CHOPCONF       = 32'h000100C3,
    parameter [31:0] COOLCONF       = 32'h00000000,
    parameter [31:0] PWMCONF        = 32'hC40C001E,

    parameter [31:0] VSTART         = 32'h00000001,
    parameter [31:0] A1             = 32'h000003E8,
    parameter [31:0] V1             = 32'h00000000,
    parameter [31:0] AMAX           = 32'h000003E8,
    parameter [31:0] DMAX           = 32'h000003E8,
    parameter [31:0] D1             = 32'h000003E8,
    parameter [31:0] VSTOP          = 32'h0000000A,
    parameter [31:0] TZEROWAIT      = 32'h00000000,
    parameter [31:0] SW_MODE        = 32'h00000000,
    parameter [31:0] XACTUAL_INIT   = 32'h00000000
) (
    input  wire                    clk,
    input  wire signed [31:0]      velocity,
    input  wire                    enable,
    output reg  signed [31:0]      position = 'd0,
    output wire [9:0]  sg_result,
    output wire [4:0]  cs_actual,

    output wire stat_swr,
    output wire stat_swl,
    output wire stat_standstill,
    output wire stat_sg2,
    output wire stat_driver_error,
    output wire stat_reset,

    output wire stat_olb,
    output wire stat_ola,
    output wire stat_2gb,
    output wire stat_2ga,
    output wire stat_otpw,
    output wire stat_ot,
    output wire stat_fsactive,
    output wire stat_stealth,
    output wire stat_s2vsb,
    output wire stat_s2vsa,
    output wire fault,

    output reg  sck = 'd0,
    output reg  mosi = 'd0,
    input  wire miso,
    output reg  cs_n = 'd0,
    output wire enable_n
);

    /*
     * TMC5160 register addresses
     */
    localparam [6:0] REG_GCONF         = 7'h00;
    localparam [6:0] REG_GSTAT         = 7'h01;
    localparam [6:0] REG_GLOBAL_SCALER = 7'h0B;
    localparam [6:0] REG_IHOLD_IRUN    = 7'h10;
    localparam [6:0] REG_TPOWERDOWN    = 7'h11;
    localparam [6:0] REG_TPWMTHRS      = 7'h13;
    localparam [6:0] REG_TCOOLTHRS     = 7'h14;
    localparam [6:0] REG_THIGH         = 7'h15;

    localparam [6:0] REG_RAMPMODE      = 7'h20;
    localparam [6:0] REG_XACTUAL       = 7'h21;
    localparam [6:0] REG_VSTART        = 7'h23;
    localparam [6:0] REG_A1            = 7'h24;
    localparam [6:0] REG_V1            = 7'h25;
    localparam [6:0] REG_AMAX          = 7'h26;
    localparam [6:0] REG_VMAX          = 7'h27;
    localparam [6:0] REG_DMAX          = 7'h28;
    localparam [6:0] REG_D1            = 7'h2A;
    localparam [6:0] REG_VSTOP         = 7'h2B;
    localparam [6:0] REG_TZEROWAIT     = 7'h2C;
    localparam [6:0] REG_XTARGET       = 7'h2D;

    localparam [6:0] REG_SW_MODE       = 7'h34;
    localparam [6:0] REG_CHOPCONF      = 7'h6C;
    localparam [6:0] REG_COOLCONF      = 7'h6D;
    localparam [6:0] REG_DRV_STATUS    = 7'h6F;
    localparam [6:0] REG_PWMCONF       = 7'h70;

    localparam [31:0] RAMPMODE_POSITION = 32'd0;
    localparam [31:0] RAMPMODE_VEL_POS  = 32'd1;
    localparam [31:0] RAMPMODE_VEL_NEG  = 32'd2;

    localparam integer SAFE_SPI_DIVIDER =
        (SPI_DIVIDER < 1) ? 1 : SPI_DIVIDER;

    /*
     * SPI engine
     *
     * TMC5160 uses SPI mode 3:
     *   - SCK idle high
     *   - MOSI changes on falling edges
     *   - MISO sampled on rising edges
     */
    reg         spi_start;
    reg [39:0]  spi_tx_data;
    reg [39:0]  spi_rx_data;
    reg         spi_done;

    reg [1:0]   spi_state;
    reg         spi_phase;
    reg [5:0]   spi_bit_count;
    reg [31:0]  spi_div_count;
    reg [39:0]  spi_tx_shift;
    reg [39:0]  spi_rx_shift;

    wire spi_busy = (spi_state != 2'd0);

    always @(posedge clk) begin
        spi_done <= 1'b0;

        case (spi_state)
            2'd0: begin
                sck  <= 1'b1;
                cs_n <= 1'b1;
                mosi <= 1'b0;

                if (spi_start) begin
                    spi_tx_shift  <= spi_tx_data;
                    spi_rx_shift  <= 40'd0;
                    spi_bit_count <= 6'd40;
                    spi_div_count <= SAFE_SPI_DIVIDER - 1;
                    spi_phase     <= 1'b0;
                    cs_n          <= 1'b0;
                    spi_state     <= 2'd1;
                end
            end

            2'd1: begin
                if (spi_div_count != 0) begin
                    spi_div_count <= spi_div_count - 1;
                end else begin
                    spi_div_count <= SAFE_SPI_DIVIDER - 1;

                    if (!spi_phase) begin
                        /*
                         * Falling edge: present the next output bit.
                         */
                        sck       <= 1'b0;
                        mosi      <= spi_tx_shift[39];
                        spi_phase <= 1'b1;
                    end else begin
                        /*
                         * Rising edge: sample one input bit.
                         */
                        sck          <= 1'b1;
                        spi_rx_shift <= {
                            spi_rx_shift[38:0],
                            miso
                        };
                        spi_tx_shift <= {
                            spi_tx_shift[38:0],
                            1'b0
                        };
                        spi_phase <= 1'b0;

                        if (spi_bit_count == 1) begin
                            spi_rx_data <= {
                                spi_rx_shift[38:0],
                                miso
                            };
                            spi_div_count <= SAFE_SPI_DIVIDER - 1;
                            spi_state <= 2'd2;
                        end else begin
                            spi_bit_count <= spi_bit_count - 1;
                        end
                    end
                end
            end

            2'd2: begin
                /*
                 * Keep chip select low for one additional half clock after
                 * the final rising edge.
                 */
                if (spi_div_count != 0) begin
                    spi_div_count <= spi_div_count - 1;
                end else begin
                    cs_n      <= 1'b1;
                    sck       <= 1'b1;
                    mosi      <= 1'b0;
                    spi_done  <= 1'b1;
                    spi_state <= 2'd0;
                end
            end

            default: begin
                spi_state <= 2'd0;
                cs_n      <= 1'b1;
                sck       <= 1'b1;
                mosi      <= 1'b0;
            end
        endcase
    end

    /*
     * Initialization datagrams.
     *
     * TMC write datagram:
     *   bit 39    = 1
     *   bits 38:32 = register address
     *   bits 31:0 = data
     */
    function [39:0] init_datagram;
        input [4:0] index;
        begin
            case (index)
                5'd0:
                    init_datagram = {1'b1, REG_GCONF, GCONF};

                5'd1:
                    /* Clear reset and error flags. */
                    init_datagram = {1'b1, REG_GSTAT, 32'h00000007};

                5'd2:
                    init_datagram = {
                        1'b1, REG_GLOBAL_SCALER, GLOBAL_SCALER
                    };

                5'd3:
                    init_datagram = {
                        1'b1, REG_IHOLD_IRUN, IHOLD_IRUN
                    };

                5'd4:
                    init_datagram = {
                        1'b1, REG_TPOWERDOWN, TPOWERDOWN
                    };

                5'd5:
                    init_datagram = {
                        1'b1, REG_TPWMTHRS, TPWMTHRS
                    };

                5'd6:
                    init_datagram = {
                        1'b1, REG_TCOOLTHRS, TCOOLTHRS
                    };

                5'd7:
                    init_datagram = {
                        1'b1, REG_THIGH, THIGH
                    };

                5'd8:
                    init_datagram = {
                        1'b1, REG_CHOPCONF, CHOPCONF
                    };

                5'd9:
                    init_datagram = {
                        1'b1, REG_COOLCONF, COOLCONF
                    };

                5'd10:
                    init_datagram = {
                        1'b1, REG_PWMCONF, PWMCONF
                    };

                5'd11:
                    init_datagram = {
                        1'b1, REG_VSTART, VSTART
                    };

                5'd12:
                    init_datagram = {
                        1'b1, REG_A1, A1
                    };

                5'd13:
                    init_datagram = {
                        1'b1, REG_V1, V1
                    };

                5'd14:
                    init_datagram = {
                        1'b1, REG_AMAX, AMAX
                    };

                5'd15:
                    init_datagram = {
                        1'b1, REG_DMAX, DMAX
                    };

                5'd16:
                    init_datagram = {
                        1'b1, REG_D1, D1
                    };

                5'd17:
                    init_datagram = {
                        1'b1, REG_VSTOP, VSTOP
                    };

                5'd18:
                    init_datagram = {
                        1'b1, REG_TZEROWAIT, TZEROWAIT
                    };

                5'd19:
                    init_datagram = {
                        1'b1, REG_SW_MODE, SW_MODE
                    };

                5'd20:
                    init_datagram = {
                        1'b1, REG_XACTUAL, XACTUAL_INIT
                    };

                5'd21:
                    init_datagram = {
                        1'b1, REG_XTARGET, XACTUAL_INIT
                    };

                5'd22:
                    init_datagram = {
                        1'b1, REG_RAMPMODE, RAMPMODE_VEL_NEG
                    };

                5'd23:
                    init_datagram = {
                        1'b1, REG_VMAX, 32'd0
                    };

                default:
                    init_datagram = {
                        1'b1, REG_VMAX, 32'd0
                    };
            endcase
        end
    endfunction

    localparam [4:0] INIT_LAST = 5'd23;

    reg [31:0] startup_counter;
    reg        startup_done;
    reg [4:0]  init_index;
    reg        init_done;

    /*
     * Read responses are pipelined by the TMC5160. The payload returned by
     * the current transaction belongs to the preceding read request.
     */
    reg        launched_read;
    reg [6:0]  launched_address;
    reg        pending_read;
    reg [6:0]  pending_address;

    reg [31:0] sent_vmax;
    reg [1:0]  sent_mode;
    reg        poll_drv_status;
    reg [1:0]  writes_since_poll;

    wire [31:0] velocity_magnitude =
        velocity[31] ? (~velocity + 32'd1) : velocity;

    /*
     * VMAX is a 23-bit value.
     */
    wire velocity_overflow = |velocity_magnitude[31:23];

    wire [31:0] requested_vmax =
        (!enable) ? 32'd0 :
        velocity_overflow ? 32'h007FFFFF :
        velocity_magnitude;

    wire [1:0] requested_mode =
        velocity[31] ? 2'd2 : 2'd1;

    /*
     * enable_n remains inactive until initialization has completed.
     */
    assign enable_n = ~(enable && init_done);
    reg [7:0]  tmc_status = 'd0;
    reg [31:0] drv_status = 32'd0;
    /*
     * Critical fault indication:
     *   tmc_status[1]  driver_error
     *   DRV_STATUS[12] s2vsa
     *   DRV_STATUS[13] s2vsb
     *   DRV_STATUS[25] overtemperature
     *   DRV_STATUS[27] s2ga
     *   DRV_STATUS[28] s2gb
     */
    assign fault =
        tmc_status[1]  |
        drv_status[12] |
        drv_status[13] |
        drv_status[25] |
        drv_status[27] |
        drv_status[28];

    assign stat_swr = tmc_status[7];
    assign stat_swl = tmc_status[6];
    assign stat_standstill = tmc_status[3];
    assign stat_sg2 = tmc_status[2];
    assign stat_driver_error = tmc_status[1];
    assign stat_reset = tmc_status[0];

    assign stat_olb = drv_status[30];
    assign stat_ola = drv_status[29];
    assign stat_2gb = drv_status[28];
    assign stat_2ga = drv_status[27];
    assign stat_otpw = drv_status[26];
    assign stat_ot = drv_status[25];
    assign cs_actual = drv_status[20:16];
    assign stat_fsactive = drv_status[15];
    assign stat_stealth = drv_status[14];
    assign stat_s2vsb = drv_status[13];
    assign stat_s2vsa = drv_status[12];
    assign sg_result = drv_status[9:0];

    initial begin
        sck               = 1'b1;
        mosi              = 1'b0;
        cs_n              = 1'b1;

        spi_start         = 1'b0;
        spi_tx_data       = 40'd0;
        spi_rx_data       = 40'd0;
        spi_done          = 1'b0;
        spi_state         = 2'd0;
        spi_phase         = 1'b0;
        spi_bit_count     = 6'd0;
        spi_div_count     = 32'd0;
        spi_tx_shift      = 40'd0;
        spi_rx_shift      = 40'd0;

        startup_counter   = 32'd0;
        startup_done      = (STARTUP_CYCLES == 0);
        init_index        = 5'd0;
        init_done         = 1'b0;

        launched_read     = 1'b0;
        launched_address  = 7'd0;
        pending_read      = 1'b0;
        pending_address   = 7'd0;

        sent_vmax         = 32'd0;
        sent_mode         = 2'd1;
        poll_drv_status   = 1'b0;
        writes_since_poll = 2'd0;

        position          = 32'sd0;
        drv_status        = 32'd0;
        tmc_status        = 8'd0;
    end

    always @(posedge clk) begin
        /*
         * spi_start is a one-cycle request.
         */
        spi_start <= 1'b0;

        if (!startup_done) begin
            if ((STARTUP_CYCLES == 0) ||
                (startup_counter >= STARTUP_CYCLES - 1)) begin
                startup_done <= 1'b1;
            end else begin
                startup_counter <= startup_counter + 1;
            end
        end

        /*
         * Handle a completed SPI transaction.
         */
        if (spi_done) begin
            tmc_status <= spi_rx_data[39:32];

            if (pending_read) begin
                case (pending_address)
                    REG_XACTUAL:
                        position <= spi_rx_data[31:0];

                    REG_DRV_STATUS:
                        drv_status <= spi_rx_data[31:0];

                    default: begin
                    end
                endcase
            end

            /*
             * The next returned payload belongs to the transaction which
             * just completed.
             */
            pending_read    <= launched_read;
            pending_address <= launched_address;

            if (!init_done) begin
                if (init_index == INIT_LAST) begin
                    init_done <= 1'b1;
                end else begin
                    init_index <= init_index + 1;
                end
            end
        end

        /*
         * Queue another transaction when the SPI engine is idle.
         *
         * Do not launch during spi_done so that initialization indices and
         * pending-read bookkeeping settle before the next transaction.
         */
        if (!spi_busy && !spi_start && !spi_done && startup_done) begin
            if (!init_done) begin
                spi_tx_data      <= init_datagram(init_index);
                launched_read    <= 1'b0;
                launched_address <= 7'd0;
                spi_start        <= 1'b1;
            end else begin
                /*
                 * Guarantee periodic status polling even when velocity is
                 * changing continuously.
                 */
                if (writes_since_poll >= 2) begin
                    if (poll_drv_status) begin
                        spi_tx_data <= {
                            1'b0, REG_DRV_STATUS, 32'd0
                        };
                        launched_address <= REG_DRV_STATUS;
                    end else begin
                        spi_tx_data <= {
                            1'b0, REG_XACTUAL, 32'd0
                        };
                        launched_address <= REG_XACTUAL;
                    end

                    launched_read     <= 1'b1;
                    poll_drv_status   <= ~poll_drv_status;
                    writes_since_poll <= 2'd0;
                    spi_start         <= 1'b1;
                end else if ((!enable || requested_vmax == 0) &&
                             sent_vmax != 0) begin
                    /*
                     * Stop before disabling or for a zero command.
                     */
                    spi_tx_data <= {
                        1'b1, REG_VMAX, 32'd0
                    };
                    launched_read     <= 1'b0;
                    launched_address  <= REG_VMAX;
                    sent_vmax         <= 32'd0;
                    writes_since_poll <= writes_since_poll + 1;
                    spi_start         <= 1'b1;
                end else if (enable &&
                             requested_vmax != 0 &&
                             requested_mode != sent_mode) begin
                    /*
                     * On reversal, command zero velocity before changing
                     * RAMPMODE.
                     */
                    if (sent_vmax != 0) begin
                        spi_tx_data <= {
                            1'b1, REG_VMAX, 32'd0
                        };
                        launched_address <= REG_VMAX;
                        sent_vmax <= 32'd0;
                    end else begin
                        spi_tx_data <= {
                            1'b1,
                            REG_RAMPMODE,
                            30'd0,
                            requested_mode
                        };
                        launched_address <= REG_RAMPMODE;
                        sent_mode <= requested_mode;
                    end

                    launched_read     <= 1'b0;
                    writes_since_poll <= writes_since_poll + 1;
                    spi_start         <= 1'b1;
                end else if (enable &&
                             requested_vmax != sent_vmax) begin
                    spi_tx_data <= {
                        1'b1, REG_VMAX, requested_vmax
                    };
                    launched_read     <= 1'b0;
                    launched_address  <= REG_VMAX;
                    sent_vmax         <= requested_vmax;
                    writes_since_poll <= writes_since_poll + 1;
                    spi_start         <= 1'b1;
                end else begin
                    /*
                     * No command update is pending: poll XACTUAL and
                     * DRV_STATUS alternately.
                     */
                    if (poll_drv_status) begin
                        spi_tx_data <= {
                            1'b0, REG_DRV_STATUS, 32'd0
                        };
                        launched_address <= REG_DRV_STATUS;
                    end else begin
                        spi_tx_data <= {
                            1'b0, REG_XACTUAL, 32'd0
                        };
                        launched_address <= REG_XACTUAL;
                    end

                    launched_read     <= 1'b1;
                    poll_drv_status   <= ~poll_drv_status;
                    writes_since_poll <= 2'd0;
                    spi_start         <= 1'b1;
                end
            end
        end
    end

endmodule
