
module prv32 (
        input wire  clk,
        input wire  uart_rx,
        output wire uart_tx,
        output wire led0,
        output wire led1,
        output wire led2,
        output wire led3,
        output wire led4,
        output wire led5,
        input  wire [31:0] val_out,
        output wire [31:0] val_in
    );

   parameter [0:0] BARREL_SHIFTER = 0;
   parameter [0:0] ENABLE_MUL = 0;
   parameter [0:0] ENABLE_DIV = 0;
   parameter [0:0] ENABLE_FAST_MUL = 0;
   parameter [0:0] ENABLE_COMPRESSED = 0;
   parameter [0:0] ENABLE_IRQ_QREGS = 0;

   parameter integer MEMBYTES = 8192; // This is not easy to change
   parameter [31:0] STACKADDR = (MEMBYTES); // Grows down. Software should set it.
   parameter [31:0] PROGADDR_RESET = 32'h0000_0000;
   parameter [31:0] PROGADDR_IRQ = 32'h0000_0000;

	wire [5:0] gpios;
	assign led0 = gpios[0];
	assign led1 = gpios[1];
	assign led2 = gpios[2];
	assign led3 = gpios[3];
	assign led4 = gpios[4];
	assign led5 = gpios[5];

	reg reset_button_n = 0;
	reg [15:0] counter = 10000;
	always @(posedge clk) begin
		if (counter == 0) begin
			reset_button_n <= 1;
		end else begin
			counter <= counter - 1;
        end
    end

    wire                       reset_n; 
    wire [31:0]                mem_addr;
    wire [31:0]                mem_wdata;
    wire [31:0]                mem_rdata;
    wire [3:0]                 mem_wstrb;
    wire                       mem_ready;
    wire                       mem_inst;
    wire                       gpios_sel;
    wire                       gpios_ready;
    wire [31:0]                gpios_data_o;
    wire                       sram_sel;
    wire                       sram_ready;
    wire [31:0]                sram_data_o;
    wire                       cdt_sel;
    wire                       cdt_ready;
    wire [31:0]                cdt_data_o;
    wire                       uart_sel;
    wire [31:0]                uart_data_o;
    wire                       uart_ready;

    wire                       vin_sel;
    wire                       vin_ready;
    wire [31:0]                vin_data_o;

    wire                       vout_sel;
    wire                       vout_ready;
    wire [31:0]                vout_data_o;

    assign val_in = vin_data_o;

   // Establish memory map for all slaves:
   //   SRAM 00000000 - 0001ffff
   //   LED  80000000
   //   UART 80000008 - 8000000f
   //   CDT  80000010 - 80000014
   //   VIN  80000020 - 80000024
   //   VOUT 80000030 - 80000034
   assign sram_sel = mem_valid && (mem_addr < 32'h00002000);
   assign gpios_sel = mem_valid && (mem_addr == 32'h80000000);
   assign uart_sel = mem_valid && ((mem_addr & 32'hfffffff8) == 32'h80000008);
   assign cdt_sel = mem_valid && (mem_addr == 32'h80000010);
   assign vin_sel = mem_valid && (mem_addr == 32'h80000020);
   assign vout_sel = mem_valid && (mem_addr == 32'h80000040);

   // Core can proceed regardless of *which* slave was targetted and is now ready.
   assign mem_ready = mem_valid & (sram_ready | gpios_ready | uart_ready | cdt_ready | vin_ready | vout_ready);


   // Select which slave's output data is to be fed to core.
   assign mem_rdata = sram_sel ? sram_data_o :
                      gpios_sel ? gpios_data_o :
                      uart_sel ? uart_data_o :
                      cdt_sel  ? cdt_data_o  :
                      vin_sel  ? vin_data_o  :
                      vout_sel ? vout_data_o :
                      32'h0;

   assign gpios = ~gpios_data_o[5:0]; // Connect to the gpios off the FPGA

   reset_control reset_controller
     (
      .clk(clk),
      .reset_button_n(reset_button_n),
      .reset_n(reset_n)
      );

   uart_wrap uart
     (
      .clk(clk),
      .reset_n(reset_n),
      .uart_tx(uart_tx),
      .uart_rx(uart_rx),
      .uart_sel(uart_sel),
      .addr(mem_addr[3:0]),
      .uart_wstrb(mem_wstrb),
      .uart_di(mem_wdata),
      .uart_do(uart_data_o),
      .uart_ready(uart_ready)
      );

   countdown_timer cdt
     (
      .clk(clk),
      .reset_n(reset_n),
      .cdt_sel(cdt_sel),
      .cdt_data_i(mem_wdata),
      .we(mem_wstrb),
      .cdt_ready(cdt_ready),
      .cdt_data_o(cdt_data_o)
      );

   sram #(.ADDRWIDTH(13)) memory
     (
      .clk(clk),
      .resetn(reset_n),
      .sram_sel(sram_sel),
      .wstrb(mem_wstrb),
      .addr(mem_addr[12:0]),
      .sram_data_i(mem_wdata),
      .sram_ready(sram_ready),
      .sram_data_o(sram_data_o)
      );
   
   gpio soc_gpios
     (
      .clk(clk),
      .reset_n(reset_n),
      .gpios_sel(gpios_sel),
      .gpios_data_i(mem_wdata[5:0]),
      .we(mem_wstrb[0]),
      .gpios_ready(gpios_ready),
      .gpios_data_o(gpios_data_o)
      );

   mvin soc_vin
     (
      .clk(clk),
      .reset_n(reset_n),
      .vin_sel(vin_sel),
      .vin_data_i(mem_wdata),
      .we(mem_wstrb[0]),
      .vin_ready(vin_ready),
      .vin_data_o(vin_data_o)
      );

   picorv32
     #(
       .STACKADDR(STACKADDR),
       .PROGADDR_RESET(PROGADDR_RESET),
       .PROGADDR_IRQ(PROGADDR_IRQ),
       .BARREL_SHIFTER(BARREL_SHIFTER),
       .COMPRESSED_ISA(ENABLE_COMPRESSED),
       .ENABLE_MUL(ENABLE_MUL),
       .ENABLE_DIV(ENABLE_DIV),
       .ENABLE_FAST_MUL(ENABLE_FAST_MUL),
       .ENABLE_IRQ(1),
       .ENABLE_IRQ_QREGS(ENABLE_IRQ_QREGS)
       ) cpu
       (
        .clk         (clk),
        .resetn      (reset_n),
        .mem_valid   (mem_valid),
        .mem_instr   (mem_instr),
        .mem_ready   (mem_ready),
        .mem_addr    (mem_addr),
        .mem_wdata   (mem_wdata),
        .mem_wstrb   (mem_wstrb),
        .mem_rdata   (mem_rdata),
        .irq         ('b0)
        );

endmodule // top


module mvin
  (
   input wire         clk,
   input wire         reset_n,
   input wire         vin_sel,
   input wire [31:0]   vin_data_i,
   input wire         we,
   output wire        vin_ready,
   output reg [31:0] vin_data_o
   );

   assign vin_ready = vin_sel;

   always @(posedge clk or negedge reset_n)
     if (!reset_n) 
       vin_data_o <= 'b0;
     else if (vin_sel)
       if (we) vin_data_o <= vin_data_i;

endmodule
