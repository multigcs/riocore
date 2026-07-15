module ram32 (
	clk,
	resetn,
	addr,
	ce,
	we,
	data_in,
	data_out
);
	parameter RAM_SIZE = 1024;
	parameter INITIAL_FILE = "";
	localparam RAM_ADDR_BITS = $clog2(RAM_SIZE / 4);
	input wire clk;
	input wire resetn;
	input wire [RAM_ADDR_BITS - 1:0] addr;
	input wire ce;
	input wire we;
	input wire [31:0] data_in;
	output reg [31:0] data_out;
	reg [31:0] mem [0:(RAM_SIZE / 4) - 1];
	always @(posedge clk)
		if (!resetn)
			data_out <= 0;
		else if (ce)
			data_out <= (we ? data_in : mem[addr]);
	always @(posedge clk)
		if (we)
			mem[addr] <= data_in;
	initial if (|INITIAL_FILE)
		$readmemh(INITIAL_FILE, mem);
endmodule
