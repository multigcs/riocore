/* Copyright 2024 Grug Huhler.  License SPDX BSD-2-Clause.

Timer that can be written and read and always counts
down, stopping at zero.  The implementation is intentionally
overcomplicated.  It meets unnecessary goals:

  * Operate as a litte-endian register accessable with any
    aligned access as a byte, half-word, or 32-bit word.
  * Let individual bytes of half-words be written without
    changing other bits in the register.
  * Use a state machine for cdt_ready that adds more delay
    than is needed.  It should work just to assert READY
    as soon as SEL is seen.
*/

module countdown_timer
  (
   input wire         clk,
   input wire         reset_n,
   input wire         cdt_sel,
   input wire [31:0]  cdt_data_i,
   input wire [3:0]   we,
   output wire        cdt_ready,
   output wire [31:0] cdt_data_o
   );

   reg [1:0]          delay_state = 'b0;
   reg [31:0]         counter = 'b0;

   assign cdt_data_o = counter;
   assign cdt_ready = (delay_state == 2'b10);

   always @(posedge clk or negedge reset_n)
     if (!reset_n)
       delay_state <= 'b0;
     else
       case (delay_state)
         2'b00: begin // Await SEL
            if (cdt_sel)
              delay_state <= 2'b01;
            else
              delay_state <= 2'b00;
         end
         2'b01: begin // Working (for one cycle)
            if (cdt_sel)
              delay_state <= 2'b10;
            else
              delay_state <= 2'b00;
         end
         2'b10: begin // Finished
            if (cdt_sel)
              delay_state <= 2'b11;
            else
              delay_state <= 2'b00;
         end
         2'b11: begin // Await !cdt_sel
            if (cdt_sel)
              delay_state <= 2'b11;
            else
              delay_state <= 2'b00;
         end
       endcase

   always @(posedge clk or negedge reset_n)
     if (!reset_n) begin
        counter <= 'b0;
     end
     else if (cdt_sel) begin
        if (we) begin
           if (we[3]) counter[31:24] <= cdt_data_i[31:24];
           if (we[2]) counter[23:16] <= cdt_data_i[23:16];
           if (we[1]) counter[15:8] <= cdt_data_i[15:8];
           if (we[0]) counter[7:0] <= cdt_data_i[7:0];
        end
        else
          if (counter != 'b0) counter <= counter - 1;
     end
     else begin
        if (counter != 'b0) counter <= counter - 1;
     end

endmodule // countdown_timer
