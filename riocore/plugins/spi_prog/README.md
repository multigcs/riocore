# spi_prog

<img align="right" width="320" src="image.png">

**spi interface for host comunication and flash programming**

for direct connections to Raspberry-PI - supporting flash programming - spartan6 only at the moment

* Keywords: interface spi raspberry rpi flash mesa
* NEEDS: mesa

## Pins:
*FPGA-pins*
### mosi:

 * direction: input

### miso:

 * direction: output

### sclk:

 * direction: input

### sel:

 * direction: input

### prog:

 * direction: input
 * pull: down

### reboot:

 * direction: output
 * pull: down

### eeprom_mosi:

 * direction: output

### eeprom_miso:

 * direction: input

### eeprom_sclk:

 * direction: output

### eeprom_sel:

 * direction: output


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### spitype:
SPI-Type

 * type: select
 * default: rpi4
 * options: rpi4, rpi5, generic

### cs:
Chip-Select pin on the Host-Side CS0/CS1

 * type: int
 * min: 0
 * max: 1
 * default: 0


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Verilogs:
 * [spi_prog.v](spi_prog.v)
