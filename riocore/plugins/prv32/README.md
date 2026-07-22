# prv32
**picorv32 based risc-v softcore**

picorv32 risc-v cpu for testing
i using this riscv-toolchain: https://github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases/tag/v15.2.0-1

* Keywords: risc-v softcore cpu
* NEEDS: fpga

## Pins:
*FPGA-pins*


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

### ENABLE_MUL:

 * type: bool
 * default: True

### ENABLE_DIV:

 * type: bool
 * default: True

### ENABLE_COMPRESSED:

 * type: bool
 * default: False

### ramsize:
size of ram in byte

 * type: int
 * min: 512
 * max: 8192
 * default: 8192


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
