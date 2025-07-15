
all: testb

testb:
	cat interval.v | sed 's| clog2(| $$clog2(|g' > interval-test.v
	iverilog -Wall -o testb.out testb.v interval-test.v
	rm -rf interval-test.v
	vvp testb.out
	test -e testb.gtkw && gtkwave testb.gtkw || gtkwave testb.vcd

clean:
	rm -rf testb.out testb.vcd
