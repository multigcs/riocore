# stepperonline_abs

<img align="right" width="320" src="image.png">


| :warning: EXPERIMENTAL |
|:-----------------------|

**serial abs-encoder stepperonline A6**

abs-encoder over rs485

17bit Absolute

Firewire-Connector:
* 1 5V
* 2 GND
* 3 NC
* 4 NC
* 5 PS+
* 6 PS-

Keywords: absolute angle bldc stepperonline A6

## Pins:
*FPGA-pins*
### rx:

 * direction: input

### tx:

 * direction: output

### tx_enable:

 * direction: output


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### tmp1:

 * type: float
 * direction: input

### tmp2:

 * type: float
 * direction: input

### revs:

 * type: float
 * direction: input

### angle16:

 * type: float
 * direction: input

### angle:

 * type: float
 * direction: input

### position:

 * type: float
 * direction: input


## Interfaces:
*transport layer*
### tmp1:

 * size: 8 bit
 * direction: input

### tmp2:

 * size: 8 bit
 * direction: input

### revs:

 * size: 32 bit
 * direction: input

### angle16:

 * size: 16 bit
 * direction: input

### angle:

 * size: 32 bit
 * direction: input


## Basic-Example:
```
{
    "type": "stepperonline_abs",
    "pins": {
        "rx": {
            "pin": "0"
        },
        "tx": {
            "pin": "1"
        },
        "tx_enable": {
            "pin": "2"
        }
    }
}
```

## Full-Example:
```
{
    "type": "stepperonline_abs",
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
        "tx": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "tx_enable": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {
        "tmp1": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "tmp1",
                "section": "inputs",
                "type": "meter"
            }
        },
        "tmp2": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "tmp2",
                "section": "inputs",
                "type": "meter"
            }
        },
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
        "angle16": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "angle16",
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
        }
    }
}
```

## Verilogs:
 * [stepperonline_abs.v](stepperonline_abs.v)
 * [uart_baud.v](uart_baud.v)
 * [uart_rx.v](uart_rx.v)
 * [uart_tx.v](uart_tx.v)
