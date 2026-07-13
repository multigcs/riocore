# mqtt

<img align="right" width="320" src="image.png">

**mqtt to hal**

reads mqtt values and writes to hal pins

* Keywords: mqtt

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

### server:

 * type: str
 * default: localhost

### port:

 * type: int
 * default: 1883

### config:

 * type: str
 * default: topic1:float:pin1,topic2:float:pin2


## Signals:
*signals/pins in LinuxCNC*
### pin1:

 * type: float
 * direction: input

### pin2:

 * type: float
 * direction: input


## Interfaces:
*transport layer*

