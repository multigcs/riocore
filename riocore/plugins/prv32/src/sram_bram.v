
module prv32_sram #(parameter ADDRWIDTH=13, parameter MEMBYTES=2048) (
        input wire                 clk,
        input wire                 resetn,
        input wire                 sram_sel,
        input wire [3:0]           wstrb,
        input wire [ADDRWIDTH-1:0] addr,
        input wire [31:0]          sram_data_i,
        output wire                sram_ready,
        output wire [31:0]         sram_data_o
    );
 
    reg ready = 1'b0;
    assign sram_ready = ready;

    always @(posedge clk) begin
        if (sram_sel) begin
            ready <= 1'b1;
        end else begin
            ready <= 1'b0;
        end
    end

    reg [31:0] mem [0:MEMBYTES/4-1];

    assign sram_data_o = mem[addr[ADDRWIDTH-1:2]];

    always @(posedge clk) begin
        if (sram_sel && |wstrb) begin
	    if (wstrb[0]) mem[addr][ 7: 0] <= sram_data_i[ 7: 0];
	    if (wstrb[1]) mem[addr][15: 8] <= sram_data_i[15: 8];
	    if (wstrb[2]) mem[addr][23:16] <= sram_data_i[23:16];
	    if (wstrb[3]) mem[addr][31:24] <= sram_data_i[31:24];
	end
    end

    initial $readmemh("src/prog.hex", mem);
   
endmodule

