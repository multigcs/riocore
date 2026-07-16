# serv
**minimal risc-v softcore**

minimal risc-v cpu for testing

* Keywords: risc-v softcore cpu
* NEEDS: fpga

## Pins:
*FPGA-pins*
### gpio0:

 * direction: output

### gpio1:

 * direction: output

### gpio2:

 * direction: output


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### image:
hardware type

 * type: imgselect
 * default: generic

### ramsize:
memory size

 * type: int
 * min: 64
 * max: 2048
 * default: 64
 * unit: byte

### source:
source code (asm)

 * type: multiline
 * default: /*
* LED Blinker
* Assuming that GPIO_BASE is mapped to a GPIO core, which in turn is
* connected to LEDs, this will light the LEDs one at a time.
* Useful as smoke test to see that serv is running correctly
*/
#ifndef GPIO_BASE
#define GPIO_BASE 0x100
#endif

#ifndef DELAY
#define DELAY 0x20000 /* Loop 100000 times before inverting the LED */
#endif

	/*
	a0 = GPIO Base address
	t0 = Value
	t1 = Timer max value
	t2 = Current timer value

	*/

.globl _start
_start:
	/* Load GPIO base address to a0 */
	lui a0, %hi(GPIO_BASE)
	addi a0, a0, %lo(GPIO_BASE)

	/* Set timer value to control blink speed */
	li t1, DELAY

bl1:
	/* Write to LEDs */
	sb t0, 0(a0)

	/* invert LED */
	xori t0, t0, 1

	/* Reset timer */
	and t2, zero, zero

	/* Delay loop */
time1:
	addi t2, t2, 1
	bne t1, t2, time1
	j bl1



## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Verilogs:
 * [serv.v](serv.v)
 * [ram32.v](ram32.v)
 * [ser_add.v](ser_add.v)
 * [ser_lt.v](ser_lt.v)
 * [ser_shift.v](ser_shift.v)
 * [serv_alu.v](serv_alu.v)
 * [serv_bufreg.v](serv_bufreg.v)
 * [serv_csr.v](serv_csr.v)
 * [serv_ctrl.v](serv_ctrl.v)
 * [serv_decode.v](serv_decode.v)
 * [serv_mem_if.v](serv_mem_if.v)
 * [serv_rf_if.v](serv_rf_if.v)
 * [serv_rf_ram_if.v](serv_rf_ram_if.v)
 * [serv_rf_ram.v](serv_rf_ram.v)
 * [serv_rf_top.v](serv_rf_top.v)
 * [serv_state.v](serv_state.v)
 * [serv_top.v](serv_top.v)
 * [shift_reg.v](shift_reg.v)
