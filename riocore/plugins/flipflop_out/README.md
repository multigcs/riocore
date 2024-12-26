# flipflop_out

<img align="right" width="320" src="image.png">

**flipflop output**

set and reset an output pin

Keywords: sr-flipflop

## Pins:
*FPGA-pins*
### bit:

 * direction: output


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
### set:

 * type: float
 * direction: output

### reset:

 * type: float
 * direction: output


## Interfaces:
*transport layer*
### set:

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
        "bit": {
            "pin": "0"
        }
    }
}
```

## Full-Example:
```
{
    "type": "flipflop_out",
    "default": 0,
    "name": "",
    "pins": {
        "bit": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {
        "set": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "set",
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
