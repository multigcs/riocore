# yaskawa_abs

| :warning: EXPERIMENTAL |
|:-----------------------|

**serial abs-encoder**

abs-encoder over rs485

angle scale: 16bit (65536)
position scale: 17bit (131072)

protocol in short:
    * RS485
    * manchester code
    * stuffing bit (after 5x1)
    * 16bit checksum

very time critical
on TangNano9k:
 "speed": "32400000",
 parameter DELAY=3, parameter DELAY_NEXT=4

Keywords: absolute angle bldc

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

### rx_synced:

 * direction: output
 * optional: True


## Options:
*user-options*
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

### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### batt_error:

 * type: bit
 * direction: input

### temp:

 * type: float
 * direction: input

### angle:

 * type: float
 * direction: input

### position:

 * type: float
 * direction: input

### csum:

 * type: float
 * direction: input

### debug_data:

 * type: float
 * direction: input


## Interfaces:
*transport layer*
### batt_error:

 * size: 1 bit
 * direction: input

### temp:

 * size: 8 bit
 * direction: input

### angle:

 * size: 16 bit
 * direction: input

### position:

 * size: 32 bit
 * direction: input

### csum:

 * size: 16 bit
 * direction: input

### debug_data:

 * size: 32 bit
 * direction: input


## Basic-Example:
```
{
    "type": "yaskawa_abs",
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
        },
        "rx_synced": {
            "pin": "4"
        }
    }
}
```

## Full-Example:
```
{
    "type": "yaskawa_abs",
    "delay": 3,
    "delay_next": 4,
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
        },
        "debug_bit": {
            "pin": "3",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "rx_synced": {
            "pin": "4",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {
        "batt_error": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "batt_error",
                "section": "inputs",
                "type": "led"
            }
        },
        "temp": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "temp",
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
        }
    }
}
```

## Verilogs:
 * [yaskawa_abs.v](yaskawa_abs.v)
