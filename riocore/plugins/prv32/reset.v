/* Copyright 2024 Grug Huhler.  License SPDX BSD-2-Clause. */

module reset_control
(
 input wire  clk,
 input wire  reset_button_n,
 output wire reset_n
);

   reg [5:0] reset_count = 0;

   // picorv32 must see a reset_n rising edge so hold it active
   // until a count completes.
   assign reset_n = &reset_count;

   always @(posedge clk)
     if (reset_button_n)
       reset_count <= reset_count + !reset_n;
     else
       reset_count <= 'b0;

endmodule
