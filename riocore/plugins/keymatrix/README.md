# keymatrix

<img align="right" width="320" src="image.png">

**Matix-Keyboard**

input for matrix keyboards

* Keywords: keyboard keys
* NEEDS: fpga

## Pins:
*FPGA-pins*
### col0:

 * direction: output

### col1:

 * direction: output

### col2:

 * direction: output

### col3:

 * direction: output

### row0:

 * direction: input
 * pull: up

### row1:

 * direction: input
 * pull: up

### row2:

 * direction: input
 * pull: up

### row3:

 * direction: input
 * pull: up


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### cols:
number cols

 * type: int
 * min: 0
 * max: 8
 * default: 4

### rows:
number rows

 * type: int
 * min: 0
 * max: 8
 * default: 4

### sendkeys:
using sendkeys hal-component

 * type: bool
 * default: False

### mapping:
keycodes

 * type: str
 * default: 2, 5, 8, 27, 3, 6, 9, 11, 4, 7, 10, 43, 30, 48, 46, 32


## Signals:
*signals/pins in LinuxCNC*
### value:

 * type: float
 * direction: input

### scancode:

 * type: float
 * direction: input


## Interfaces:
*transport layer*
### value:

 * size: 8 bit
 * direction: input


## Verilogs:
 * [keymatrix.v](keymatrix.v)
