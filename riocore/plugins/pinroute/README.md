# pinroute

<img align="right" width="320" src="image.png">

**routing one output pin to multiple inputs**

* NEEDS: fpga

## Pins:
*FPGA-pins*
### outA:

 * direction: output

### inA0:

 * direction: input

### inA1:

 * direction: input


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### inputs:
number of inputs

 * type: int
 * min: 2
 * max: 100
 * default: 2

### channels:
number of channels

 * type: int
 * min: 1
 * max: 16
 * default: 1


## Signals:
*signals/pins in LinuxCNC*
### input:
input selector

 * type: float
 * direction: output
 * min: 0
 * max: 1


## Interfaces:
*transport layer*
### input:

 * size: 8 bit
 * direction: output
 * multiplexed: True

