# ethercat

<img align="right" width="320" src="image.png">


| :warning: EXPERIMENTAL |
|:-----------------------|

**experimental ethercat driver**

Keywords: stepper servo master

## Pins:
*FPGA-pins*
### out:

 * direction: all


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### node_type:
Type

 * type: select
 * default: Master

### idx:
bus-index

 * type: int
 * min: -2
 * max: 255
 * default: -2


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "ethercat",
    "pins": {
        "out": {
            "pin": "0"
        }
    }
}
```

## Full-Example:
```
{
    "type": "ethercat",
    "name": "",
    "node_type": "Master",
    "idx": -2,
    "pins": {
        "out": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {}
}
```
