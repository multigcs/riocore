# riosub

<img align="right" width="320" src="image.png">


| :warning: EXPERIMENTAL |
|:-----------------------|

**rio sub board**

to combine multible RIO boards via RS422

* the sub config must setup 'uart' as interface
* very limited !!!
* very buggy !!!
* some calculations will not work
* some plugins will not work
* only for testing

## Pins:
*FPGA-pins*
### tx:

 * direction: output

### rx:

 * direction: input


## Options:
*user-options*
### subconfig:
sub json-config file

 * type: str
 * default: 
 * unit: 

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


## Basic-Example:
```
{
    "type": "riosub",
    "pins": {
        "tx": {
            "pin": "0"
        },
        "rx": {
            "pin": "1"
        }
    }
}
```

## Full-Example:
```
{
    "type": "riosub",
    "subconfig": "",
    "baud": 1000000,
    "name": "",
    "pins": {
        "tx": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "rx": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "debounce"
                },
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
 * [uart_baud.v](uart_baud.v)
 * [uart_rx.v](uart_rx.v)
 * [uart_tx.v](uart_tx.v)
