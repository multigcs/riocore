# hx710

<img align="right" width="320" src="image.png">

**24bit adc**

24bit adc (HX710B)

Keywords: adc analog

## Pins:
*FPGA-pins*
### miso:

 * direction: input

### sclk:

 * direction: output


## Options:
*user-options*
### zero:
zero value

 * type: int
 * default: 1379496

### scale:
scale value

 * type: float
 * default: 1e-05

### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### pressure:

 * type: float
 * direction: input
 * unit: ?


## Interfaces:
*transport layer*
### pressure:

 * size: 32 bit
 * direction: input
 * multiplexed: True


## Basic-Example:
```
{
    "type": "hx710",
    "pins": {
        "miso": {
            "pin": "0"
        },
        "sclk": {
            "pin": "1"
        }
    }
}
```

## Full-Example:
```
{
    "type": "hx710",
    "zero": 1379496,
    "scale": 1e-05,
    "name": "",
    "pins": {
        "miso": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "debounce"
                }
            ]
        },
        "sclk": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {
        "pressure": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "pressure",
                "section": "inputs",
                "type": "meter"
            }
        }
    }
}
```

## Verilogs:
 * [hx710.v](hx710.v)
