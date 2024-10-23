# hx711
**digital weight sensor**

to measure weight's

Keywords: adc analog weight


![image.png](image.png)

## Basic-Example:
```
{
    "type": "hx711",
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
 * default: 0

### scale:
scale value

 * type: float
 * default: 1.0

### mode:
sensor mode

 * type: select
 * default: CHA_128

### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### weight:

 * type: float
 * direction: input
 * unit: Kg

### tare:

 * type: bit
 * direction: input

### toffset:

 * type: float
 * direction: output


## Interfaces:
*transport layer*
### weight:

 * size: 32 bit
 * direction: input
 * multiplexed: True


## Full-Example:
```
{
    "type": "hx711",
    "zero": 0,
    "scale": 1.0,
    "mode": "CHA_128",
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
        "weight": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "weight",
                "section": "inputs",
                "type": "meter"
            }
        },
        "tare": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "tare",
                "section": "inputs",
                "type": "led"
            }
        },
        "toffset": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "toffset",
                "section": "outputs",
                "type": "scale"
            }
        }
    }
}
```

## Verilogs:
 * [hx711.v](hx711.v)
