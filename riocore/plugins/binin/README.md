# binin
**binary to decimal input**

reads binary values

Keywords: binary


![image.png](image.png)

## Basic-Example:
```
{
    "type": "binin",
    "pins": {
        "bin0": {
            "pin": "0"
        },
        "bin1": {
            "pin": "1"
        },
        "bin2": {
            "pin": "2"
        },
        "bin3": {
            "pin": "3"
        }
    }
}
```

## Pins:
*FPGA-pins*
### bin0:

 * direction: input

### bin1:

 * direction: input

### bin2:

 * direction: input

### bin3:

 * direction: input


## Options:
*user-options*
### bits:
number of inputs

 * type: int
 * min: 1
 * max: 32
 * default: 4
 * unit: bits

### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### value:

 * type: float
 * direction: input


## Interfaces:
*transport layer*
### value:

 * size: 8 bit
 * direction: input


## Full-Example:
```
{
    "type": "binin",
    "bits": 4,
    "name": "",
    "pins": {
        "bin0": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "debounce"
                }
            ]
        },
        "bin1": {
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
        "bin2": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "bin3": {
            "pin": "3",
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
        "value": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "value",
                "section": "inputs",
                "type": "meter"
            }
        }
    }
}
```
