# prv32

<img align="right" width="320" src="image.png">


| :warning: EXPERIMENTAL |
|:-----------------------|

**picorv32 based risc-v softcore**

picorv32 risc-v cpu for testing
i using this riscv-toolchain: https://github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases/tag/v15.2.0-1

* Keywords: risc-v softcore cpu
* NEEDS: fpga

## Pins:
*FPGA-pins*
### LED0:

 * direction: inout
 * optional: True


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

### BARREL_SHIFTER:

 * type: bool
 * default: False

### ENABLE_MUL:

 * type: bool
 * default: True

### ENABLE_DIV:

 * type: bool
 * default: True

### ENABLE_FAST_MUL:

 * type: bool
 * default: False

### ENABLE_COMPRESSED:

 * type: bool
 * default: False

### ENABLE_IRQ_QREGS:

 * type: bool
 * default: False

### uarts:
number of uarts

 * type: int
 * min: 0
 * max: 1
 * default: 0

### pwms:
number of pwms

 * type: int
 * min: 0
 * max: 1
 * default: 0

### ramsize:
size of ram in bytes

 * type: select
 * default: 1024
 * options: 512, 768, 1024, 2048, 4096, 8192


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Verilogs:
 * [prv32_timer.v](prv32_timer.v)
 * [prv32_reset.v](prv32_reset.v)
 * [prv32_gpio.v](prv32_gpio.v)
 * [prv32_rio.v](prv32_rio.v)
 * [prv32_uart_wrap.v](prv32_uart_wrap.v)
 * [prv32_simpleuart.v](prv32_simpleuart.v)
 * [picorv32.v](picorv32.v)
