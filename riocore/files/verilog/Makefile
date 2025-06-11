
all: testb_toggle testb_oneshot

testb_toggle:
	iverilog -Wall -o testb_toggle.out testb_toggle.v toggle.v
	vvp testb_toggle.out
	test -e testb_toggle.gtkw && gtkwave testb_toggle.gtkw || gtkwave testb_toggle.vcd

testb_oneshot:
	iverilog -Wall -o testb_oneshot.out testb_oneshot.v oneshot.v
	vvp testb_oneshot.out
	test -e testb_oneshot.gtkw && gtkwave testb_oneshot.gtkw || gtkwave testb_oneshot.vcd

testb_debouncer:
	iverilog -Wall -o testb_debouncer.out testb_debouncer.v debouncer.v
	vvp testb_debouncer.out
	test -e testb_debouncer.gtkw && gtkwave testb_debouncer.gtkw || gtkwave testb_debouncer.vcd

clean:
	rm -rf *.out *.vcd
