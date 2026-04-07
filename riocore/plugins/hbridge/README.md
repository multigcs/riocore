# hbridge

<img align="right" width="320" src="image.png">

**hbridge output**

to control DC-Motors

* Keywords: joint dcservo
* NEEDS: fpga

## Pins:
*FPGA-pins*
### out1:

 * direction: output

### out2:

 * direction: output

### en:

 * direction: output
 * optional: True


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### is_joint:
configure as joint

 * type: bool
 * default: True

### axis:
axis name (X,Y,Z,...)

 * type: select
 * default: None
 * options: X, Y, Z, A, B, C, U, V, W

### frequency:
PWM frequency

 * type: int
 * min: 10
 * max: 1000000
 * default: 10000
 * unit: Hz


## Signals:
*signals/pins in LinuxCNC*
### dty:

 * type: float
 * direction: output
 * min: -100
 * max: 100
 * unit: %

### enable:

 * type: bit
 * direction: output


## Interfaces:
*transport layer*
### dty:

 * size: 32 bit
 * direction: output

### enable:

 * size: 1 bit
 * direction: output


## Verilogs:
 * [hbridge.v](hbridge.v)
