# uartsub

<img align="right" width="320" src="image.png">

**uartsub interface for host cominucation**

simple uartsub interface, not usable for realtime stuff in LinuxCNC / only for testing

Keywords: serial uartsub interface

## Pins:
*FPGA-pins*
### rx:

 * direction: input

### tx:

 * direction: output

### tx_enable:

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

### baud:
serial baud rate

 * type: int
 * min: 9600
 * max: 10000000
 * default: 2500000
 * unit: bit/s

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


## Basic-Example:
```
{
    "type": "uartsub",
    "pins": {
        "rx": {
            "pin": "0"
        },
        "tx": {
            "pin": "1"
        },
        "tx_enable": {
            "pin": "2"
        },
        "SAT:OUT": {
            "pin": "3"
        }
    }
}
```

## Full-Example:
```
{
    "type": "uartsub",
    "name": "",
    "baud": 2500000,
    "timeout": 100,
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
        },
        "SAT:OUT": {
            "pin": "3",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {
        "timeout": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "timeout",
                "section": "inputs",
                "type": "led"
            }
        }
    }
}
```

## Verilogs:
 * [uartsub.v](uartsub.v)
 * [uart_baud.v](uart_baud.v)
 * [uart_rx.v](uart_rx.v)
 * [uart_tx.v](uart_tx.v)
