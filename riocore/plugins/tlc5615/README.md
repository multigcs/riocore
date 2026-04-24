# tlc5615

<img align="right" width="320" src="image.png">

**spi dac**

Analog-Output via spi dac

* Keywords: analog dac
* URL: https://www.ti.com/lit/ds/symlink/tlc5615.pdf?ts=1774302230717
* NEEDS: fpga

## Pins:
*FPGA-pins*
### mosi:

 * direction: output

### sclk:

 * direction: output

### sel:

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


## Signals:
*signals/pins in LinuxCNC*
### value:

 * type: float
 * direction: output
 * min: 0
 * max: 1023


## Interfaces:
*transport layer*
### value:

 * size: 16 bit
 * direction: output


## Verilogs:
 * [tlc5615.v](tlc5615.v)
