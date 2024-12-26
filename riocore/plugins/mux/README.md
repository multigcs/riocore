# mux

<img align="right" width="320" src="image.png">

**binary multiplexer**

encodes binary values

Keywords: binary multiplexer

## Basic-Example:
```
{
    "type": "mux",
    "pins": {
        "pin0": {
            "pin": "0"
        },
        "pin1": {
            "pin": "1"
        },
        "pin2": {
            "pin": "2"
        },
        "pin3": {
            "pin": "3"
        }
    }
}
```

## Pins:
*FPGA-pins*
### pin0:

 * direction: output

### pin1:

 * direction: output

### pin2:

 * direction: output

### pin3:

 * direction: output


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
 * direction: output

### bit1:

 * type: bit
 * direction: output


## Interfaces:
*transport layer*
### bit0:

 * size: 1 bit
 * direction: output

### bit1:

 * size: 1 bit
 * direction: output


## Full-Example:
```
{
    "type": "mux",
    "bits": 2,
    "name": "",
    "pins": {
        "pin0": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "pin1": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "pin2": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "pin3": {
            "pin": "3",
            "modifiers": [
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
                "section": "outputs",
                "type": "checkbox"
            }
        },
        "bit1": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "bit1",
                "section": "outputs",
                "type": "checkbox"
            }
        }
    }
}
```
