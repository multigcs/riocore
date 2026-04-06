# satuart

<img align="right" width="320" src="image.png">

**uart interface for satellite cominucation**

simple uart interface to connect satellite mcu/fpga

* Keywords: serial satuart interface rs422
* NEEDS: fpga

## Pins:
*FPGA-pins*
### rx:

 * direction: input

### tx:

 * direction: output

### tx_enable:
for RS485 mode

 * direction: output
 * optional: True

### SAT:OUT:

 * direction: output


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### timeout:
timeout in ms

 * type: int
 * min: 1
 * max: 10000
 * default: 100
 * unit: ms


## Signals:
*signals/pins in LinuxCNC*
### timeout:

 * type: bit
 * direction: input


## Interfaces:
*transport layer*
### timeout:

 * size: 1 bit
 * direction: input


## Verilogs:
 * [satuart.v](satuart.v)
 * [uart_baud.v](uart_baud.v)
 * [uart_rx.v](uart_rx.v)
 * [uart_tx.v](uart_tx.v)
