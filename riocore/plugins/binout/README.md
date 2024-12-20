# binout
**decimal to binary output**

outputs binary values

Keywords: binary


![image.png](image.png)

## Basic-Example:
```
{
    "type": "binout",
    "pins": {
        "bit0": {
            "pin": "0"
        },
        "bit1": {
            "pin": "1"
        },
        "bit2": {
            "pin": "2"
        },
        "bit3": {
            "pin": "3"
        }
    }
}
```

## Pins:
*FPGA-pins*
### bit0:

 * direction: output

### bit1:

 * direction: output

### bit2:

 * direction: output

### bit3:

 * direction: output


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
 * direction: output


## Interfaces:
*transport layer*
### value:

 * size: 8 bit
 * direction: output


## Full-Example:
```
{
    "type": "binout",
    "bits": 4,
    "name": "",
    "pins": {
        "bit0": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "bit1": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "bit2": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "bit3": {
            "pin": "3",
            "modifiers": [
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
                "section": "outputs",
                "type": "scale"
            }
        }
    }
}
```
