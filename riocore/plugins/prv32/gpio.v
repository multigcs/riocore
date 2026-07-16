/* Copyright 2024 Grug Huhler.  License SPDX BSD-2-Clause. */

// tang_leds is a toy peripheral that allows software on the
// core to write to a register that controls the LEDs on the
// Tang Nano 9K board.  It can also read this register,

module gpio
  (
   input wire         clk,
   input wire         reset_n,
   input wire         gpios_sel,
   input wire [5:0]   gpios_data_i,
   input wire         we,
   output wire        gpios_ready,
   output wire [31:0] gpios_data_o
   );

   reg [5:0]          gpios = 'b0;

   assign gpios_data_o = {26'b00000000000000000000000000, gpios};
   assign gpios_ready = gpios_sel;

   always @(posedge clk or negedge reset_n)
     if (!reset_n) 
       gpios <= 'b0;
     else if (gpios_sel)
       if (we) gpios <= gpios_data_i;

endmodule
