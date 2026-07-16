
module serv (
	input wire clk,
	output wire gpio0,
	output wire gpio1,
	output wire gpio2
);
	parameter RAM_SIZE = 64;
    parameter INITIAL_FILE = "prog.hex";

	reg resetn = 0;
	reg [1:0] counter = 1;
	always @(posedge clk) begin
		if (counter == 0) begin
			resetn <= 1;
		end else begin
			counter <= counter - 1;
        end
    end

	wire [2:0] gpio;
	assign gpio0 = gpio[0];
	assign gpio1 = gpio[1];
	assign gpio2 = gpio[2];

	wire i_rst;
	wire i_timer_irq;
	wire [31:0] o_ibus_adr;
	wire o_ibus_cyc;
	wire [31:0] i_ibus_rdt;
	reg i_ibus_ack;
	wire [31:0] o_dbus_adr;
	wire [31:0] o_dbus_dat;
	wire [3:0] o_dbus_sel;
	wire o_dbus_we;
	wire o_dbus_cyc;
	wire [31:0] i_dbus_rdt;
	reg i_dbus_ack;
	wire o_rf_rreq;
	wire o_rf_wreq;
	wire i_rf_ready;
	wire [5:0] o_wreg0;
	wire [5:0] o_wreg1;
	wire o_wen0;
	wire o_wen1;
	wire o_wdata0;
	wire o_wdata1;
	wire [5:0] o_rreg0;
	wire [5:0] o_rreg1;
	wire i_rdata0;
	wire i_rdata1;

	serv_top serv_top_inst(
		.clk(clk),
		.i_rst(i_rst),
		.i_timer_irq(i_timer_irq),
		.o_ibus_adr(o_ibus_adr),
		.o_ibus_cyc(o_ibus_cyc),
		.i_ibus_rdt(i_ibus_rdt),
		.i_ibus_ack(i_ibus_ack),
		.o_dbus_adr(o_dbus_adr),
		.o_dbus_dat(o_dbus_dat),
		.o_dbus_sel(o_dbus_sel),
		.o_dbus_we(o_dbus_we),
		.o_dbus_cyc(o_dbus_cyc),
		.i_dbus_rdt(i_dbus_rdt),
		.i_dbus_ack(i_dbus_ack),
		.o_rf_rreq(o_rf_rreq),
		.o_rf_wreq(o_rf_wreq),
		.i_rf_ready(i_rf_ready),
		.o_wreg0(o_wreg0),
		.o_wreg1(o_wreg1),
		.o_wen0(o_wen0),
		.o_wen1(o_wen1),
		.o_wdata0(o_wdata0),
		.o_wdata1(o_wdata1),
		.o_rreg0(o_rreg0),
		.o_rreg1(o_rreg1),
		.i_rdata0(i_rdata0),
		.i_rdata1(i_rdata1)
	);

	assign i_rst = !resetn;
	assign i_timer_irq = 0;
	reg [31:0] gpio_out;
	assign gpio = ~gpio_out[2:0];
	wire [7:0] rf_waddr;
	wire rf_wen;
	wire [7:0] rf_wdata;
	wire [7:0] rf_raddr;
	reg [7:0] rf_rdata;

	serv_rf_ram_if rf_ram_if(
		.i_clk(clk),
		.i_rst(!resetn),
		.i_wreq(o_rf_wreq),
		.i_rreq(o_rf_rreq),
		.o_ready(i_rf_ready),
		.i_wreg0(o_wreg0),
		.i_wreg1(o_wreg1),
		.i_wen0(o_wen0),
		.i_wen1(o_wen1),
		.i_wdata0(o_wdata0),
		.i_wdata1(o_wdata1),
		.i_rreg0(o_rreg0),
		.i_rreg1(o_rreg1),
		.o_rdata0(i_rdata0),
		.o_rdata1(i_rdata1),
		.o_waddr(rf_waddr),
		.o_wen(rf_wen),
		.o_wdata(rf_wdata),
		.o_raddr(rf_raddr),
		.i_rdata(rf_rdata)
	);

	reg [7:0] rf_mem [0:255];
	always @(posedge clk) begin
		if (rf_wen) begin
			rf_mem[rf_waddr] <= rf_wdata;
        end
		rf_rdata <= rf_mem[rf_raddr];
	end

	ram32 #(
		.INITIAL_FILE(INITIAL_FILE),
		.RAM_SIZE(RAM_SIZE)
	) iram(
		.clk(clk),
		.resetn(resetn),
		.addr(o_ibus_adr[9:2]),
		.ce(o_ibus_cyc),
		.we(0),
		.data_in(0),
		.data_out(i_ibus_rdt)
	);

	always @(posedge clk) begin
        i_ibus_ack <= (!resetn ? 0 : o_ibus_cyc && !i_ibus_ack);
    end
	always @(posedge clk) begin
        i_dbus_ack <= (!resetn ? 0 : o_dbus_cyc && !i_dbus_ack);
    end
	always @(posedge clk) begin
		if ((o_dbus_cyc && o_dbus_we) && o_dbus_adr[8]) begin
			gpio_out <= o_dbus_dat;
        end
    end
endmodule
