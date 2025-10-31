# ethercat

<img align="right" width="320" src="image.png">


| :warning: EXPERIMENTAL |
|:-----------------------|

**experimental ethercat driver**

Keywords: stepper servo master

## Pins:
*FPGA-pins*
### in:

 * direction: input

### out:

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
 * default: False

### axis:
axis name (X,Y,Z,...)

 * type: select
 * default: None

### image:
hardware type

 * type: select
 * default: ethercatservo

### node_type:
Type

 * type: select
 * default: Servo/Stepper

### idx:
bus-index

 * type: int
 * min: -2
 * max: 255
 * default: -2


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
    "type": "ethercat",
    "pins": {
        "in": {
            "pin": "0"
        },
        "out": {
            "pin": "1"
        }
    }
}
```

## Full-Example:
```
{
    "type": "ethercat",
    "name": "",
    "is_joint": false,
    "axis": "",
    "image": "ethercatservo",
    "node_type": "Servo/Stepper",
    "idx": -2,
    "pins": {
        "in": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "debounce"
                }
            ]
        },
        "out": {
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
