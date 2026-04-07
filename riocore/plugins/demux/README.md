# demux

<img align="right" width="320" src="image.png">

**binary demultiplexer**

decodes binary values

* Keywords: binary demultiplexer
* NEEDS: fpga

## Pins:
*FPGA-pins*
### pin0:

 * direction: input

### pin1:

 * direction: input


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### bits:
number of inputs

 * type: int
 * min: 1
 * max: 32
 * default: 2
 * unit: bits


## Signals:
*signals/pins in LinuxCNC*
### bit0:

 * type: bit
 * direction: input

### bit1:

 * type: bit
 * direction: input

### bit2:

 * type: bit
 * direction: input

### bit3:

 * type: bit
 * direction: input


## Interfaces:
*transport layer*
### bit0:

 * size: 1 bit
 * direction: input

### bit1:

 * size: 1 bit
 * direction: input

### bit2:

 * size: 1 bit
 * direction: input

### bit3:

 * size: 1 bit
 * direction: input

