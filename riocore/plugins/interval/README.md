# interval

<img align="right" width="320" src="image.png">


| :warning: EXPERIMENTAL |
|:-----------------------|

**interval timer**

to control things like lubric pumps

* NEEDS: fpga

## Pins:
*FPGA-pins*
### out:

 * direction: output


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### enable:

 * type: bit
 * direction: output

### ontime:

 * type: float
 * direction: output
 * min: 0
 * unit: seconds

### interval:

 * type: float
 * direction: output
 * min: 0
 * unit: seconds


## Interfaces:
*transport layer*
### enable:

 * size: 1 bit
 * direction: output
 * multiplexed: True

### ontime:

 * size: 24 bit
 * direction: output
 * multiplexed: True

### interval:

 * size: 24 bit
 * direction: output
 * multiplexed: True


## Verilogs:
 * [interval.v](interval.v)
