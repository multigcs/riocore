module uart_wrap
  (
   input wire         clk,
   input wire         reset_n,
   input wire         uart_rx,
   output wire        uart_tx,
   input wire         uart_sel,
   input wire [3:0]   addr, // Choose div or dat
   input wire [3:0]   uart_wstrb,
   input wire [31:0]  uart_di,
   output wire [31:0] uart_do,
   output wire        uart_ready
   );

   wire               div_sel;
   wire               dat_sel;
   wire [31:0]        div_do;
   wire [31:0]        dat_do;
   wire               dat_wait;
            
   assign div_sel = uart_sel && (addr == 4'h8);
   assign dat_sel = uart_sel && (addr == 4'hc);
   assign uart_do = div_sel ? div_do :
                    dat_sel ? dat_do : 32'h0;
   assign uart_ready = div_sel | (dat_sel && !dat_wait);
   
   simpleuart uart
     (
      .clk(clk),
      .resetn(reset_n),
      .ser_tx(uart_tx),
      .ser_rx(uart_rx),
      .reg_div_we(div_sel ? uart_wstrb : 4'b0000),
      .reg_div_di(uart_di),
      .reg_div_do(div_do),
      .reg_dat_we(dat_sel ? uart_wstrb[0] : 1'b0),
      .reg_dat_re(dat_sel && !uart_wstrb),
      .reg_dat_di(uart_di),
      .reg_dat_do(dat_do),
      .reg_dat_wait(dat_wait)
      );

endmodule
