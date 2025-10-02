# flipflop_in

<img align="right" width="320" src="image.png">

**flipflop input**

set and reset an input bit

Keywords: sr-flipflop

## Pins:
*FPGA-pins*
### setbit:

 * direction: input

### reset:

 * direction: input


## Options:
*user-options*
### default:
default value after startup

 * type: bool
 * default: 0
 * unit: 

### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### outbit:

 * type: float
 * direction: input


## Interfaces:
*transport layer*
### outbit:

 * size: 1 bit
 * direction: input


## Basic-Example:
```
{
    "type": "flipflop_in",
    "pins": {
        "setbit": {
            "pin": "0"
        },
        "reset": {
            "pin": "1"
        }
    }
}
```

## Full-Example:
```
{
    "type": "flipflop_in",
    "default": 0,
    "name": "",
    "pins": {
        "setbit": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "debounce"
                }
            ]
        },
        "reset": {
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
    "signals": {
        "outbit": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "outbit",
                "section": "inputs",
                "type": "meter"
            }
        }
    }
}
```

## Verilogs:
 * [flipflop_in.v](flipflop_in.v)
