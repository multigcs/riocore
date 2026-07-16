
module prv32 (
        input wire  clk,
        input wire  uart_rx,
        output wire uart_tx,
        output wire led0,
        output wire led1,
        output wire led2,
        output wire led3,
        output wire led4,
        output wire led5
    );

   parameter [0:0] BARREL_SHIFTER = 0;
   parameter [0:0] ENABLE_MUL = 0;
   parameter [0:0] ENABLE_DIV = 0;
   parameter [0:0] ENABLE_FAST_MUL = 0;
   parameter [0:0] ENABLE_COMPRESSED = 0;
   parameter [0:0] ENABLE_IRQ_QREGS = 0;

   parameter integer MEMBYTES = 8192; // This is not easy to change
   parameter [31:0] STACKADDR = (MEMBYTES); // Grows down.  Software should set it.
   parameter [31:0] PROGADDR_RESET = 32'h0000_0000;
   parameter [31:0] PROGADDR_IRQ = 32'h0000_0000;

	wire [5:0] leds;
	assign led0 = leds[0];
	assign led1 = leds[1];
	assign led2 = leds[2];
	assign led3 = leds[3];
	assign led4 = leds[4];
	assign led5 = leds[5];

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
   wire                       leds_sel;
   wire                       leds_ready;
   wire [31:0]                leds_data_o;
   wire                       sram_sel;
   wire                       sram_ready;
   wire [31:0]                sram_data_o;
   wire                       cdt_sel;
   wire                       cdt_ready;
   wire [31:0]                cdt_data_o;
   wire                       uart_sel;
   wire [31:0]                uart_data_o;
   wire                       uart_ready;

   // Establish memory map for all slaves:
   //   SRAM 00000000 - 0001ffff
   //   LED  80000000
   //   UART 80000008 - 8000000f
   //   CDT  80000010 - 80000014
   assign sram_sel = mem_valid && (mem_addr < 32'h00002000);
   assign leds_sel = mem_valid && (mem_addr == 32'h80000000);
   assign uart_sel = mem_valid && ((mem_addr & 32'hfffffff8) == 32'h80000008);
   assign cdt_sel = mem_valid && (mem_addr == 32'h80000010);

   // Core can proceed regardless of *which* slave was targetted and is now ready.
   assign mem_ready = mem_valid & (sram_ready | leds_ready | uart_ready | cdt_ready);


   // Select which slave's output data is to be fed to core.
   assign mem_rdata = sram_sel ? sram_data_o :
                      leds_sel ? leds_data_o :
                      uart_sel ? uart_data_o :
                      cdt_sel  ? cdt_data_o  : 32'h0;

   assign leds = ~leds_data_o[5:0]; // Connect to the LEDs off the FPGA

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
   
   tang_leds soc_leds
     (
      .clk(clk),
      .reset_n(reset_n),
      .leds_sel(leds_sel),
      .leds_data_i(mem_wdata[5:0]),
      .we(mem_wstrb[0]),
      .leds_ready(leds_ready),
      .leds_data_o(leds_data_o)
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
