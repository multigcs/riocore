
all: testb

testb:
	iverilog -Wall -o testb.out testb.v flipflop_out.v
	vvp testb.out
	#gtkwave testb.vcd
	gtkwave testb.gtkw

clean:
	rm -rf testb.out testb.vcd
