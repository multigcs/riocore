# stepgen

<img align="right" width="320" src="image.png">

**software step pulse generation**

stepgen is used to control stepper motors.
The maximum step rate depends on the CPU and other factors,
and is usually in the range of 5 kHz to 25 kHz.
If higher rates are needed, a hardware step generator is a better choice.

Keywords: stepper

## Pins:
*FPGA-pins*
### step:

 * direction: output

### dir:

 * direction: output


## Options:
*user-options*
### mode:
Modus

 * type: select
 * default: 0

### name:
name of this plugin instance

 * type: str
 * default: 

### axis:
axis name (X,Y,Z,...)

 * type: select
 * default: None

### is_joint:
configure as joint

 * type: bool
 * default: False


## Signals:
*signals/pins in LinuxCNC*
### position-cmd:
set position

 * type: float
 * direction: output

### position-fb:
position feedback

 * type: float
 * direction: input
 * unit: steps

### position-scale:
steps / unit

 * type: float
 * direction: output


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "stepgen",
    "pins": {
        "step": {
            "pin": "0"
        },
        "dir": {
            "pin": "1"
        }
    }
}
```

## Full-Example:
```
{
    "type": "stepgen",
    "mode": "0",
    "name": "",
    "axis": "",
    "is_joint": false,
    "pins": {
        "step": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "dir": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {
        "position-cmd": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "position-cmd",
                "section": "outputs",
                "type": "scale"
            }
        },
        "position-fb": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "position-fb",
                "section": "inputs",
                "type": "meter"
            }
        },
        "position-scale": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "position-scale",
                "section": "outputs",
                "type": "scale"
            }
        }
    }
}
```
