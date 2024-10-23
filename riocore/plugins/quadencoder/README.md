# quadencoder
**quadencoder**

usable as position feedback for closed-loop configuration or as variable input to control LinuxCNC overwrites

Keywords: feedback encoder rotary linear glassscale


![image.png](image.png)

## Basic-Example:
```
{
    "type": "quadencoder",
    "pins": {
        "a": {
            "pin": "0"
        },
        "b": {
            "pin": "1"
        }
    }
}
```

## Pins:
*FPGA-pins*
### a:

 * direction: input
 * pull: up

### b:

 * direction: input
 * pull: up


## Options:
*user-options*
### quad_type:
encoder type

 * type: int
 * min: 0
 * max: 4
 * default: 2

### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### position:
position feedback in steps

 * type: float
 * direction: input

### rps:
calculates revolutions per second

 * type: float
 * direction: input

### rpm:
calculates revolutions per minute

 * type: float
 * direction: input


## Interfaces:
*transport layer*
### position:

 * size: 32 bit
 * direction: input


## Full-Example:
```
{
    "type": "quadencoder",
    "quad_type": 2,
    "name": "",
    "pins": {
        "a": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "debounce"
                }
            ]
        },
        "b": {
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
        "position": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "position",
                "section": "inputs",
                "type": "meter"
            }
        },
        "rps": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "rps",
                "section": "inputs",
                "type": "meter"
            }
        },
        "rpm": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "rpm",
                "section": "inputs",
                "type": "meter"
            }
        }
    }
}
```

## Verilogs:
 * [quadencoder.v](quadencoder.v)
