# wled_bar

<img align="right" width="320" src="image.png">

**ws2812b interface for bar-displays**

simple ws2812b driver with variable input to build led-bars

* Keywords: led rgb status info
* NEEDS: fpga

## Pins:
*FPGA-pins*
### data:

 * direction: output


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### leds:
number of LED's

 * type: int
 * min: 0
 * max: 100
 * default: 12

### level:
LED brighness

 * type: int
 * min: 0
 * max: 255
 * default: 127


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


## Verilogs:
 * [ws2812.v](ws2812.v)
 * [wled_bar.v](wled_bar.v)
