# binout

<img align="right" width="320" src="image.png">

**decimal to binary output**

outputs binary values

* Keywords: binary dec2bin r2r-dac
* NEEDS: fpga

## Pins:
*FPGA-pins*
### bin0:

 * direction: output

### bin1:

 * direction: output

### bin2:

 * direction: output

### bin3:

 * direction: output


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
 * default: 4
 * unit: bits


## Signals:
*signals/pins in LinuxCNC*
### value:

 * type: float
 * direction: output


## Interfaces:
*transport layer*
### value:

 * size: 8 bit
 * direction: output

