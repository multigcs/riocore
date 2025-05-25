# rioencoder
**serial abs-encoder**

abs-encoder over rs485 (rx-only)

Keywords: absolute ancoder angle bldc

## Pins:
*FPGA-pins*
### rx:

 * direction: input

### rw:

 * direction: output
 * optional: True


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### angle:

 * type: float
 * direction: input


## Interfaces:
*transport layer*
### angle:

 * size: 16 bit
 * direction: input


## Basic-Example:
```
{
    "type": "rioencoder",
    "pins": {
        "rx": {
            "pin": "0"
        },
        "rw": {
            "pin": "1"
        }
    }
}
```

## Full-Example:
```
{
    "type": "rioencoder",
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
        "rw": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {
        "angle": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "angle",
                "section": "inputs",
                "type": "meter"
            }
        }
    }
}
```

## Verilogs:
 * [rioencoder.v](rioencoder.v)
 * [uart_baud.v](uart_baud.v)
 * [uart_rx.v](uart_rx.v)
