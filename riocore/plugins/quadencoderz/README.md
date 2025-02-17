# quadencoderz

<img align="right" width="320" src="image.png">

**quadencoder with index pin**

usable as spindle-encoder for rigid tapping and thread cutting.  It is critical that your position-scale and QUAD_TYPE match, see the details in the description for QUAD_TYPE

Keywords: feedback encoder rotary linear glassscale  index

## Pins:
*FPGA-pins*
### a:

 * direction: input

### b:

 * direction: input

### z:
index pin

 * direction: input


## Options:
*user-options*
### quad_type:
The count from the encoder will be bitshifted by the value of QUAD_TYPE.  Use 0 for 4x mode.  The position-scale should match.  For examle if you have a 600 CPR encoder 4x mode will give you 2400 PPR and your scale should be set to 2400.

 * type: int
 * min: 0
 * max: 4
 * default: 2

### rps_sum:
number of collected values before calculate the rps value

 * type: int
 * min: 0
 * max: 100
 * default: 10

### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### indexenable:

 * type: bit
 * direction: inout

### indexout:

 * type: bit
 * direction: input

### position:
position feedback in steps

 * type: float
 * direction: input

### rps:
calculates revolutions per second

 * type: float
 * direction: input

### rpm:
calculates revolutions per minute

 * type: float
 * direction: input


## Interfaces:
*transport layer*
### indexenable:

 * size: 1 bit
 * direction: output

### indexout:

 * size: 1 bit
 * direction: input

### position:

 * size: 32 bit
 * direction: input


## Basic-Example:
```
{
    "type": "quadencoderz",
    "pins": {
        "a": {
            "pin": "0"
        },
        "b": {
            "pin": "1"
        },
        "z": {
            "pin": "2"
        }
    }
}
```

## Full-Example:
```
{
    "type": "quadencoderz",
    "quad_type": 2,
    "rps_sum": 10,
    "name": "",
    "pins": {
        "a": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "debounce"
                }
            ]
        },
        "b": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "z": {
            "pin": "2",
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
        "indexenable": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "indexenable",
                "section": "status",
                "type": "meter"
            }
        },
        "indexout": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "indexout",
                "section": "inputs",
                "type": "led"
            }
        },
        "position": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "position",
                "section": "inputs",
                "type": "meter"
            }
        },
        "rps": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "rps",
                "section": "inputs",
                "type": "meter"
            }
        },
        "rpm": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "rpm",
                "section": "inputs",
                "type": "meter"
            }
        }
    }
}
```

## Verilogs:
 * [quadencoderz.v](quadencoderz.v)
