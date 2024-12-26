# demux

<img align="right" width="320" src="image.png">

**binary demultiplexer**

decodes binary values

Keywords: binary demultiplexer

## Basic-Example:
```
{
    "type": "demux",
    "pins": {
        "pin0": {
            "pin": "0"
        },
        "pin1": {
            "pin": "1"
        }
    }
}
```

## Pins:
*FPGA-pins*
### pin0:

 * direction: input

### pin1:

 * direction: input


## Options:
*user-options*
### bits:
number of inputs

 * type: int
 * min: 1
 * max: 32
 * default: 2
 * unit: bits

### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### bit0:

 * type: bit
 * direction: input

### bit1:

 * type: bit
 * direction: input

### bit2:

 * type: bit
 * direction: input

### bit3:

 * type: bit
 * direction: input


## Interfaces:
*transport layer*
### bit0:

 * size: 1 bit
 * direction: input

### bit1:

 * size: 1 bit
 * direction: input

### bit2:

 * size: 1 bit
 * direction: input

### bit3:

 * size: 1 bit
 * direction: input


## Full-Example:
```
{
    "type": "demux",
    "bits": 2,
    "name": "",
    "pins": {
        "pin0": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "debounce"
                }
            ]
        },
        "pin1": {
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
        "bit0": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "bit0",
                "section": "inputs",
                "type": "led"
            }
        },
        "bit1": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "bit1",
                "section": "inputs",
                "type": "led"
            }
        },
        "bit2": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "bit2",
                "section": "inputs",
                "type": "led"
            }
        },
        "bit3": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "bit3",
                "section": "inputs",
                "type": "led"
            }
        }
    }
}
```
