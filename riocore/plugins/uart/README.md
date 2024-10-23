# uart
**uart interface for host cominucation**

simple uart interface, not usable for realtime stuff in LinuxCNC / only for testing

Keywords: serial uart interface


![image.png](image.png)

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
        }
    }
}
```

## Pins:
*FPGA-pins*
### rx:

 * direction: input

### tx:

 * direction: output


## Options:
*user-options*
### baud:
serial baud rate

 * type: int
 * min: 9600
 * max: 10000000
 * default: 1000000
 * unit: bit/s

### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Full-Example:
```
{
    "type": "uart",
    "baud": 1000000,
    "name": "",
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
