# max10adc
**MAX10 ADC inputs**

only usable for the max10 fpga boards

Keywords: analog adc voltage ampere


![image.png](image.png)

## Limitations
* family: MAX 10
* toolchains: quartus

## Basic-Example:
```
{
    "type": "max10adc",
    "pins": {}
}
```

## Pins:
*FPGA-pins*


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### adc0:

 * type: float
 * direction: input

### adc1:

 * type: float
 * direction: input

### adc2:

 * type: float
 * direction: input

### adc3:

 * type: float
 * direction: input

### adc4:

 * type: float
 * direction: input

### adc5:

 * type: float
 * direction: input

### adc6:

 * type: float
 * direction: input

### adc7:

 * type: float
 * direction: input


## Interfaces:
*transport layer*
### adc0:

 * size: 16 bit
 * direction: input

### adc1:

 * size: 16 bit
 * direction: input

### adc2:

 * size: 16 bit
 * direction: input

### adc3:

 * size: 16 bit
 * direction: input

### adc4:

 * size: 16 bit
 * direction: input

### adc5:

 * size: 16 bit
 * direction: input

### adc6:

 * size: 16 bit
 * direction: input

### adc7:

 * size: 16 bit
 * direction: input


## Full-Example:
```
{
    "type": "max10adc",
    "name": "",
    "pins": {},
    "signals": {
        "adc0": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "adc0",
                "section": "inputs",
                "type": "meter"
            }
        },
        "adc1": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "adc1",
                "section": "inputs",
                "type": "meter"
            }
        },
        "adc2": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "adc2",
                "section": "inputs",
                "type": "meter"
            }
        },
        "adc3": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "adc3",
                "section": "inputs",
                "type": "meter"
            }
        },
        "adc4": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "adc4",
                "section": "inputs",
                "type": "meter"
            }
        },
        "adc5": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "adc5",
                "section": "inputs",
                "type": "meter"
            }
        },
        "adc6": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "adc6",
                "section": "inputs",
                "type": "meter"
            }
        },
        "adc7": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "adc7",
                "section": "inputs",
                "type": "meter"
            }
        }
    }
}
```

## Verilogs:
 * [max10adc.v](max10adc.v)
