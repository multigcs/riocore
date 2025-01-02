# pinroute

<img align="right" width="320" src="image.png">

**routing one output pin to multiple inputs**

```mermaid
graph LR;
    In0-->Routing;
    In1-->Routing;
    Routing-->Out;
```

## Pins:
*FPGA-pins*
### outA:

 * direction: output

### inA0:

 * direction: input

### inA1:

 * direction: input


## Options:
*user-options*
### inputs:
number of inputs

 * type: int
 * min: 2
 * max: 100
 * default: 2

### channels:
number of channels

 * type: int
 * min: 1
 * max: 16
 * default: 1

### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### input:
input selector

 * type: float
 * direction: output
 * min: 0
 * max: 1


## Interfaces:
*transport layer*
### input:

 * size: 8 bit
 * direction: output
 * multiplexed: True


## Basic-Example:
```
{
    "type": "pinroute",
    "pins": {
        "outA": {
            "pin": "0"
        },
        "inA0": {
            "pin": "1"
        },
        "inA1": {
            "pin": "2"
        }
    }
}
```

## Full-Example:
```
{
    "type": "pinroute",
    "inputs": 2,
    "channels": 1,
    "name": "",
    "pins": {
        "outA": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "inA0": {
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
        "inA1": {
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
        "input": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "input",
                "section": "outputs",
                "type": "scale"
            }
        }
    }
}
```
