# binout

<img align="right" width="320" src="image.png">

**decimal to binary output**

outputs binary values

Keywords: binary dec2bin r2r-dac

```mermaid
graph LR;
    Hal-Value-->Dec2Bin;
    Dec2Bin-->FPGA-Pin0;
    Dec2Bin-->FPGA-Pin1;
```

## Basic-Example:
```
{
    "type": "binout",
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

 * direction: output

### bin1:

 * direction: output

### bin2:

 * direction: output

### bin3:

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
        "bin0": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "bin1": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "bin2": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "bin3": {
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
