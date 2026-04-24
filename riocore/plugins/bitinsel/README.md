# bitinsel
**input selector / demultiplexer**

input selector / demultiplexer with data pin

* NEEDS: fpga

## Pins:
*FPGA-pins*
### bit_in:

 * direction: input

### addr0:

 * direction: output

### addr1:

 * direction: output

### addr2:

 * direction: output

### addr3:

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

### speed:
interface clock

 * type: int
 * min: 100000
 * max: 10000000
 * default: 1000000

### bits:
number of selector bits

 * type: int
 * min: 1
 * max: 32
 * default: 4
 * unit: bits


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Verilogs:
 * [bitinsel.v](bitinsel.v)
