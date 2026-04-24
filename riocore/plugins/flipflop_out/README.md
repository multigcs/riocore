# flipflop_out

<img align="right" width="320" src="image.png">

**flipflop output**

set and reset an output pin

* Keywords: sr-flipflop
* NEEDS: fpga

## Pins:
*FPGA-pins*
### outbit:

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

### default:
default value after startup

 * type: bool
 * default: 0
 * unit: 


## Signals:
*signals/pins in LinuxCNC*
### setbit:

 * type: float
 * direction: output

### reset:

 * type: float
 * direction: output


## Interfaces:
*transport layer*
### setbit:

 * size: 1 bit
 * direction: output

### reset:

 * size: 1 bit
 * direction: output


## Verilogs:
 * [flipflop_out.v](flipflop_out.v)
