
module i2cbus_i2cbus0
    #(parameter MAX_BITS = 64, parameter MAX_DIN = 64)
    (
        input clk,
        output reg [15:0] lm75_0_temp = 0,
        output reg lm75_0_valid = 0,
        inout sda,
        output scl
    );
    localparam RW_WRITE = 0;
    localparam RW_READ = 1;

    // device lm75_0 (100000Hz)
    localparam DEVICE_LM75_0 = 0;
    localparam DEVICE_LM75_0_ADDR = 7'h48;
    localparam DEVICE_LM75_0_DIVIDER = 45;

    reg [7:0] device_lm75_0_step = 0;

    reg [31:0] divider = 100;
    reg [7:0] mpx_last = 255;
    reg [15:0] temp = 0;
    reg do_init = 1;
    reg stop = 1;
    reg [7:0] device_n = 0;
    reg [6:0] addr = 0;
    reg rw = RW_WRITE;
    reg [4:0] bytes = 0;
    reg [MAX_BITS-1:0] data_out = 0;
    wire [MAX_DIN-1:0] data_in;
    reg start = 0;
    reg wakeup = 0;
    wire busy;
    wire error;
    always @(posedge clk) begin

        if (wakeup == 1 && busy == 1) begin
            wakeup <= 0;
        end else if (start == 1 && busy == 1) begin
            start <= 0;
        end else if (start == 0 && busy == 0) begin

            if (device_n == DEVICE_LM75_0) begin
                divider <= DEVICE_LM75_0_DIVIDER;

                if (do_init) begin
                    // init steps for lm75_0
                    case (device_lm75_0_step)
                        default: begin
                            device_lm75_0_step <= 0;
                            device_n <= device_n + 7'd1;
                            lm75_0_valid <= ~error;
                        end
                    endcase

                end else begin
                    // loop steps for lm75_0
                    case (device_lm75_0_step)
                        // lm75_0: read
                        0: begin
                            // lm75_0: read: request the data
                            device_lm75_0_step <= device_lm75_0_step + 7'd1;
                            addr <= DEVICE_LM75_0_ADDR;
                            rw <= RW_READ;
                            bytes <= 2;
                            stop <= 1;
                            start <= 1;
                        end
                        1: begin
                            device_lm75_0_step <= device_lm75_0_step + 7'd1;
                            // lm75_0: read: check for error / return variable
                            if (error == 0) begin
                                lm75_0_temp <= data_in[15:0];
                            end
                        end

                        default: begin
                            device_lm75_0_step <= 0;
                            device_n <= device_n + 7'd1;
                            lm75_0_valid <= ~error;
                        end
                    endcase

                end

            end else begin
                do_init <= 0;
                device_n <= 0;
            end
        end
    end

    i2c_master #(.MAX_BITS(MAX_BITS), .MAX_DIN(MAX_DIN)) i2cinst0 (
        .clk(clk),
        .sda(sda),
        .scl(scl),
        .start(start),
        .wakeup(wakeup),
        .busy(busy),
        .error(error),
        .set_divider(divider),
        .set_addr(addr),
        .set_rw(rw),
        .stop(stop),
        .set_bytes(bytes),
        .set_data_out(data_out),
        .data_in(data_in)
    );
endmodule