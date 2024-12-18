
all: testb_toggle testb_oneshot

testb_toggle:
	iverilog -Wall -o testb_toggle.out testb_toggle.v toggle.v
	vvp testb_toggle.out
	test -e testb_toggle.gtkw && gtkwave testb_toggle.gtkw || gtkwave testb_toggle.vcd

testb_oneshot:
	iverilog -Wall -o testb_oneshot.out testb_oneshot.v oneshot.v
	vvp testb_oneshot.out
	test -e testb_oneshot.gtkw && gtkwave testb_oneshot.gtkw || gtkwave testb_oneshot.vcd

clean:
	rm -rf *.out *.vcd
