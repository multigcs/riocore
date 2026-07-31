# gowin_empu
**TangNano4K ARM core**

Cortex M3 ARM core inside TangNano4K

* Keywords: arm hardcore cpu
* NEEDS: fpga, gowin_empu

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

### uarts:
number of uarts

 * type: int
 * min: 0
 * max: 1
 * default: 0


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Verilogs:
 * [gowin_empu_top.v](gowin_empu_top.v)
