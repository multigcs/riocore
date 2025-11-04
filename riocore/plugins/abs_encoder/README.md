# panasonic_abs

<img align="right" width="320" src="image.png">


| :warning: EXPERIMENTAL |
|:-----------------------|

**serial abs-encoder**

abs-encoder over rs485

TODO: csum, pos/revs, cleanup

for Panasonic and some Bosch/Rexroth Servos with
mfe0017 encoder

FG      Shield      
VCC-    GND     Black
VCC+    5V      White
VB-     GND     Orange
VB+     3.3V    RED
SD+     RS485-A Blue
SD-     RS485-B Brown

Connector:
V+  V-
B-  SD+
B+  SD-  FG

Keywords: absolute angle bldc panasonic bosch rexroth mfe0017 minas

## Pins:
*FPGA-pins*
### rx:

 * direction: input

### tx:

 * direction: output

### tx_enable:

 * direction: output

### debug_bit:

 * direction: output
 * optional: True


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### delay:
clock delay for next manchester bit

 * type: int
 * min: 1
 * max: 100
 * default: 3
 * unit: clocks

### delay_next:
clock delay for center of the next manchester bit

 * type: int
 * min: 1
 * max: 100
 * default: 4
 * unit: clocks


## Signals:
*signals/pins in LinuxCNC*
### tmp1:

 * type: float
 * direction: input

### tmp2:

 * type: float
 * direction: input

### angle:

 * type: float
 * direction: input

### position:

 * type: float
 * direction: input

### revs:

 * type: float
 * direction: input

### csum:

 * type: float
 * direction: input

### debug_data:

 * type: float
 * direction: input

### cmd:

 * type: float
 * direction: output


## Interfaces:
*transport layer*
### tmp1:

 * size: 8 bit
 * direction: input

### tmp2:

 * size: 8 bit
 * direction: input

### angle:

 * size: 16 bit
 * direction: input

### position:

 * size: 32 bit
 * direction: input

### csum:

 * size: 8 bit
 * direction: input

### debug_data:

 * size: 32 bit
 * direction: input

### cmd:

 * size: 8 bit
 * direction: output


## Basic-Example:
```
{
    "type": "panasonic_abs",
    "pins": {
        "rx": {
            "pin": "0"
        },
        "tx": {
            "pin": "1"
        },
        "tx_enable": {
            "pin": "2"
        },
        "debug_bit": {
            "pin": "3"
        }
    }
}
```

## Full-Example:
```
{
    "type": "panasonic_abs",
    "name": "",
    "delay": 3,
    "delay_next": 4,
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
        },
        "debug_bit": {
            "pin": "3",
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
        "csum": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "csum",
                "section": "inputs",
                "type": "meter"
            }
        },
        "debug_data": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "debug_data",
                "section": "inputs",
                "type": "meter"
            }
        },
        "cmd": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "cmd",
                "section": "outputs",
                "type": "scale"
            }
        }
    }
}
```

## Verilogs:
 * [panasonic_abs.v](panasonic_abs.v)
 * [uart_baud.v](uart_baud.v)
 * [uart_rx.v](uart_rx.v)
 * [uart_tx.v](uart_tx.v)
