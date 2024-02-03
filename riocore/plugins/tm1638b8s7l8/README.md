# tm1638b8s7l8


7segment display with buttons

## Basic-Example:
```
{
    "type": "tm1638b8s7l8",
    "pins": {
        "sel": {
            "pin": "0"
        },
        "sclk": {
            "pin": "1"
        },
        "data": {
            "pin": "2"
        }
    }
}
```

## Pins:
### sel:

 * direction: output
 * pullup: False

### sclk:

 * direction: output
 * pullup: False

### data:

 * direction: inout
 * pullup: False


## Options:
### name:
name of this plugin instance

 * type: str
 * default: None

### net:
target net in LinuxCNC

 * type: str
 * default: None


## Signals:
### sw0:

 * type: bit
 * direction: input

### sw1:

 * type: bit
 * direction: input

### sw2:

 * type: bit
 * direction: input

### sw3:

 * type: bit
 * direction: input

### sw4:

 * type: bit
 * direction: input

### sw5:

 * type: bit
 * direction: input

### sw6:

 * type: bit
 * direction: input

### sw7:

 * type: bit
 * direction: input

### led0:

 * type: bit
 * direction: output

### led1:

 * type: bit
 * direction: output

### led2:

 * type: bit
 * direction: output

### led3:

 * type: bit
 * direction: output

### led4:

 * type: bit
 * direction: output

### led5:

 * type: bit
 * direction: output

### led6:

 * type: bit
 * direction: output

### led7:

 * type: bit
 * direction: output

### number1:

 * type: float
 * direction: output
 * min: -65000
 * max: 65000

### number2:

 * type: float
 * direction: output
 * min: 0
 * max: 99


## Interfaces:
### sw0:

 * size: 1 bit
 * direction: input

### sw1:

 * size: 1 bit
 * direction: input

### sw2:

 * size: 1 bit
 * direction: input

### sw3:

 * size: 1 bit
 * direction: input

### sw4:

 * size: 1 bit
 * direction: input

### sw5:

 * size: 1 bit
 * direction: input

### sw6:

 * size: 1 bit
 * direction: input

### sw7:

 * size: 1 bit
 * direction: input

### led0:

 * size: 1 bit
 * direction: output

### led1:

 * size: 1 bit
 * direction: output

### led2:

 * size: 1 bit
 * direction: output

### led3:

 * size: 1 bit
 * direction: output

### led4:

 * size: 1 bit
 * direction: output

### led5:

 * size: 1 bit
 * direction: output

### led6:

 * size: 1 bit
 * direction: output

### led7:

 * size: 1 bit
 * direction: output

### number1:

 * size: 24 bit
 * direction: output

### number2:

 * size: 8 bit
 * direction: output


## Full-Example:
```
{
    "type": "tm1638b8s7l8",
    "name": "",
    "net": "",
    "pins": {
        "sel": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
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
        },
        "data": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {
        "sw0": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "sw0",
                "section": "inputs",
                "type": "led"
            }
        },
        "sw1": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "sw1",
                "section": "inputs",
                "type": "led"
            }
        },
        "sw2": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "sw2",
                "section": "inputs",
                "type": "led"
            }
        },
        "sw3": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "sw3",
                "section": "inputs",
                "type": "led"
            }
        },
        "sw4": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "sw4",
                "section": "inputs",
                "type": "led"
            }
        },
        "sw5": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "sw5",
                "section": "inputs",
                "type": "led"
            }
        },
        "sw6": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "sw6",
                "section": "inputs",
                "type": "led"
            }
        },
        "sw7": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "sw7",
                "section": "inputs",
                "type": "led"
            }
        },
        "led0": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "led0",
                "section": "outputs",
                "type": "checkbox"
            }
        },
        "led1": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "led1",
                "section": "outputs",
                "type": "checkbox"
            }
        },
        "led2": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "led2",
                "section": "outputs",
                "type": "checkbox"
            }
        },
        "led3": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "led3",
                "section": "outputs",
                "type": "checkbox"
            }
        },
        "led4": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "led4",
                "section": "outputs",
                "type": "checkbox"
            }
        },
        "led5": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "led5",
                "section": "outputs",
                "type": "checkbox"
            }
        },
        "led6": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "led6",
                "section": "outputs",
                "type": "checkbox"
            }
        },
        "led7": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "led7",
                "section": "outputs",
                "type": "checkbox"
            }
        },
        "number1": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "number1",
                "section": "outputs",
                "type": "scale"
            }
        },
        "number2": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "number2",
                "section": "outputs",
                "type": "scale"
            }
        }
    }
}
```

## Verilogs:
 * tm1638b8s7l8.v
