
all: testb

testb:
	iverilog -Wall -o testb.out testb.v tlc5615.v
	vvp testb.out
	test -e testb.gtkw && gtkwave testb.gtkw || gtkwave testb.vcd

clean:
	rm -rf testb.out testb.vcd
