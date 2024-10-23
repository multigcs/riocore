# freqin
**frequency input**

to messurement digital frequencies

Keywords: frequency


![image.png](image.png)

## Basic-Example:
```
{
    "type": "freqin",
    "pins": {
        "freq": {
            "pin": "0"
        }
    }
}
```

## Pins:
*FPGA-pins*
### freq:

 * direction: input


## Options:
*user-options*
### freq_min:
minimum measured frequency (for faster updates)

 * type: int
 * min: 1
 * max: 10000
 * default: 10
 * unit: Hz

### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### frequency:

 * type: float
 * direction: input
 * unit: Hz

### valid:

 * type: bit
 * direction: input


## Interfaces:
*transport layer*
### frequency:

 * size: 32 bit
 * direction: input

### valid:

 * size: 1 bit
 * direction: input


## Full-Example:
```
{
    "type": "freqin",
    "freq_min": 10,
    "name": "",
    "pins": {
        "freq": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "debounce"
                }
            ]
        }
    },
    "signals": {
        "frequency": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "frequency",
                "section": "inputs",
                "type": "meter"
            }
        },
        "valid": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "valid",
                "section": "inputs",
                "type": "led"
            }
        }
    }
}
```

## Verilogs:
 * [freqin.v](freqin.v)
