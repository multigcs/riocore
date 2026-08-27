# udp2axi

<img align="right" width="320" src="image.png">


| :warning: EXPERIMENTAL |
|:-----------------------|

**udp2axi interface for armcore comunication**

udp2axi driver for the interface communication to an embedded arm-core

* Keywords: zynq xilinx interface
* NEEDS: axi

## Pins:
*FPGA-pins*
### AXI:

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

### ip:
IP-Address

 * type: str
 * default: 192.168.10.119

### mask:
Network-Mask

 * type: str
 * default: 255.255.255.0

### gw:
Gateway IP-Address

 * type: str
 * default: 192.168.10.1

### port:
UDP-Port

 * type: int
 * default: 2390


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*

