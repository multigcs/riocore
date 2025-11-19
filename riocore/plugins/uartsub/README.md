# uart

<img align="right" width="320" src="image.png">

**uart interface for host cominucation**

simple uart interface, not usable for realtime stuff in LinuxCNC / only for testing

Keywords: serial uart interface

## Pins:
*FPGA-pins*
### rx:

 * direction: input

### tx:

 * direction: output

### tx_enable:

 * direction: output
 * optional: True


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### baud:
serial baud rate

 * type: int
 * min: 9600
 * max: 10000000
 * default: 1000000
 * unit: bit/s

### csum:
activate checksums

 * type: bool
 * default: False


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "uart",
    "pins": {
        "rx": {
            "pin": "0"
        },
        "tx": {
            "pin": "1"
        },
        "tx_enable": {
            "pin": "2"
        }
    }
}
```

## Full-Example:
```
{
    "type": "uart",
    "name": "",
    "baud": 1000000,
    "csum": false,
    "pins": {
        "rx": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "debounce"
                }
            ]
        },
        "tx": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "tx_enable": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {}
}
```

## Verilogs:
 * [uart.v](uart.v)
 * [uart_baud.v](uart_baud.v)
 * [uart_rx.v](uart_rx.v)
 * [uart_tx.v](uart_tx.v)
