# flipflop_out

<img align="right" width="320" src="image.png">

**flipflop output**

set and reset an output pin

Keywords: sr-flipflop

## Pins:
*FPGA-pins*
### outbit:

 * direction: output


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### default:
default value after startup

 * type: bool
 * default: 0
 * unit: 


## Signals:
*signals/pins in LinuxCNC*
### setbit:

 * type: float
 * direction: output

### reset:

 * type: float
 * direction: output


## Interfaces:
*transport layer*
### setbit:

 * size: 1 bit
 * direction: output

### reset:

 * size: 1 bit
 * direction: output


## Basic-Example:
```
{
    "type": "flipflop_out",
    "pins": {
        "outbit": {
            "pin": "0"
        }
    }
}
```

## Full-Example:
```
{
    "type": "flipflop_out",
    "name": "",
    "default": 0,
    "pins": {
        "outbit": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {
        "setbit": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "setbit",
                "section": "outputs",
                "type": "scale"
            }
        },
        "reset": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "reset",
                "section": "outputs",
                "type": "scale"
            }
        }
    }
}
```

## Verilogs:
 * [flipflop_out.v](flipflop_out.v)
