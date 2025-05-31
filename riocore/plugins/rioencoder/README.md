# rioencoder

| :warning: EXPERIMENTAL |
|:-----------------------|

**serial abs-encoder**

abs-encoder over rs485 (rx-only)

Keywords: absolute angle bldc

## Pins:
*FPGA-pins*
### rx:

 * direction: input

### rw:

 * direction: output
 * optional: True


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### revs:

 * type: float
 * direction: input

### angle:

 * type: float
 * direction: input

### temperature:

 * type: float
 * direction: input
 * unit: °C

### position:

 * type: float
 * direction: input

### rps:

 * type: float
 * direction: input

### rpm:

 * type: float
 * direction: input


## Interfaces:
*transport layer*
### revs:

 * size: 32 bit
 * direction: input

### angle:

 * size: 16 bit
 * direction: input

### temperature:

 * size: 16 bit
 * direction: input


## Basic-Example:
```
{
    "type": "rioencoder",
    "pins": {
        "rx": {
            "pin": "0"
        },
        "rw": {
            "pin": "1"
        }
    }
}
```

## Full-Example:
```
{
    "type": "rioencoder",
    "name": "",
    "pins": {
        "rx": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "debounce"
                }
            ]
        },
        "rw": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {
        "revs": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "revs",
                "section": "inputs",
                "type": "meter"
            }
        },
        "angle": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "angle",
                "section": "inputs",
                "type": "meter"
            }
        },
        "temperature": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "temperature",
                "section": "inputs",
                "type": "meter"
            }
        },
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
 * [rioencoder.v](rioencoder.v)
 * [uart_baud.v](uart_baud.v)
 * [uart_rx.v](uart_rx.v)
