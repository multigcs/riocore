# mesastepgen

<img align="right" width="320" src="image.png">

**masa step pulse generation**

Keywords: stepper

## Pins:
*FPGA-pins*
### step:

 * direction: output

### dir:

 * direction: output


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### is_joint:
configure as joint

 * type: bool
 * default: True

### axis:
axis name (X,Y,Z,...)

 * type: select
 * default: None

### image:
hardware type

 * type: select
 * default: generic


## Signals:
*signals/pins in LinuxCNC*
### velocity:
set position

 * type: float
 * direction: output

### position:
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
    "type": "mesastepgen",
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
    "type": "mesastepgen",
    "name": "",
    "is_joint": true,
    "axis": "",
    "image": "generic",
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
        "velocity": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "velocity",
                "section": "outputs",
                "type": "scale"
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
