# demux
**binary demultiplexer**

decodes binary values
```mermaid
graph LR;
    FPGA-Pin0-->Bin2Dec;
    FPGA-Pin1-->Bin2Dec;
    Bin2Dec-->Dec==0-->Hal-Bit0;
    Bin2Dec-->Dec==1-->Hal-Bit1;
    Bin2Dec-->Dec==2-->Hal-Bit2;
    Bin2Dec-->Dec==3-->Hal-Bit3;
```
        

Keywords: binary demultiplexer


![image.png](image.png)

## Basic-Example:
```
{
    "type": "demux",
    "pins": {
        "pin0": {
            "pin": "0"
        },
        "pin1": {
            "pin": "1"
        }
    }
}
```

## Pins:
*FPGA-pins*
### pin0:

 * direction: input

### pin1:

 * direction: input


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

 * type: float
 * direction: input

### bit1:

 * type: float
 * direction: input

### bit2:

 * type: float
 * direction: input

### bit3:

 * type: float
 * direction: input


## Interfaces:
*transport layer*
### bit0:

 * size: 1 bit
 * direction: input

### bit1:

 * size: 1 bit
 * direction: input

### bit2:

 * size: 1 bit
 * direction: input

### bit3:

 * size: 1 bit
 * direction: input


## Full-Example:
```
{
    "type": "demux",
    "bits": 2,
    "name": "",
    "pins": {
        "pin0": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "debounce"
                }
            ]
        },
        "pin1": {
            "pin": "1",
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
        "bit0": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "bit0",
                "section": "inputs",
                "type": "meter"
            }
        },
        "bit1": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "bit1",
                "section": "inputs",
                "type": "meter"
            }
        },
        "bit2": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "bit2",
                "section": "inputs",
                "type": "meter"
            }
        },
        "bit3": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "bit3",
                "section": "inputs",
                "type": "meter"
            }
        }
    }
}
```
