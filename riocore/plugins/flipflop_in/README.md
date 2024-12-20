# flipflop_in
**flipflop input**

set and reset an input bit

Keywords: sr-flipflop


![image.png](image.png)

## Basic-Example:
```
{
    "type": "flipflop_in",
    "pins": {
        "set": {
            "pin": "0"
        },
        "reset": {
            "pin": "1"
        }
    }
}
```

## Pins:
*FPGA-pins*
### set:

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
### bit:

 * type: float
 * direction: input


## Interfaces:
*transport layer*
### bit:

 * size: 1 bit
 * direction: input


## Full-Example:
```
{
    "type": "flipflop_in",
    "default": 0,
    "name": "",
    "pins": {
        "set": {
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
        "bit": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "bit",
                "section": "inputs",
                "type": "meter"
            }
        }
    }
}
```

## Verilogs:
 * [flipflop_in.v](flipflop_in.v)
