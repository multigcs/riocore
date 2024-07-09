# icewerxadc
to read analog signals from the iceWerx-board

4-channel adc of the iceWerx-board

## Basic-Example:
```
{
    "type": "icewerxadc",
    "pins": {
        "tx": {
            "pin": "0"
        },
        "rx": {
            "pin": "1"
        }
    }
}
```

## Pins:
### tx:

 * direction: output
 * pullup: False

### rx:

 * direction: input
 * pullup: False


## Options:
### name:
name of this plugin instance

 * type: str
 * default: None


## Signals:
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


## Interfaces:
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


## Full-Example:
```
{
    "type": "icewerxadc",
    "name": "",
    "pins": {
        "tx": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "rx": {
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
        }
    }
}
```

## Verilogs:
 * icewerxadc.v
 * uart_baud.v
 * uart_rx.v
 * uart_tx.v
