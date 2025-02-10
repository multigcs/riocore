# freqin

<img align="right" width="320" src="image.png">

**frequency input**

to messurement digital frequencies

Keywords: frequency

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

### freq_max:
maximum measured frequency (for filtering)

 * type: int
 * min: 10
 * max: 10000000
 * default: 1000000
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

## Full-Example:
```
{
    "type": "freqin",
    "freq_min": 10,
    "freq_max": 1000000,
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
