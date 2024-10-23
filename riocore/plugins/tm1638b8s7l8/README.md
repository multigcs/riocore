# tm1638b8s7l8
**7segment display with buttons**

with this plugin, you can use cheap TM1638 boards with LED's/Switches and 7segment displays as control interface for LinuxCNC (JOG/DRO)

Keywords: display info status keyboard buttons


![image.png](image.png)

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
*FPGA-pins*
### sel:
Select-Pin (STB)

 * direction: output

### sclk:
Clock-Pin (CLK)

 * direction: output

### data:
Data-Pin (DIO)

 * direction: inout


## Options:
*user-options*
### speed:
Data-clock

 * type: int
 * default: 1000000

### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
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
last 6 digits (-6500.0 -> 6500.0)

 * type: float
 * direction: output
 * min: -6500.0
 * max: 6500.0

### number2:
first 2 digits (0 -> 99)

 * type: float
 * direction: output
 * min: 0
 * max: 99


## Interfaces:
*transport layer*
### sw0:

 * size: 1 bit
 * direction: input
 * multiplexed: True

### sw1:

 * size: 1 bit
 * direction: input
 * multiplexed: True

### sw2:

 * size: 1 bit
 * direction: input
 * multiplexed: True

### sw3:

 * size: 1 bit
 * direction: input
 * multiplexed: True

### sw4:

 * size: 1 bit
 * direction: input
 * multiplexed: True

### sw5:

 * size: 1 bit
 * direction: input
 * multiplexed: True

### sw6:

 * size: 1 bit
 * direction: input
 * multiplexed: True

### sw7:

 * size: 1 bit
 * direction: input
 * multiplexed: True

### led0:

 * size: 1 bit
 * direction: output
 * multiplexed: True

### led1:

 * size: 1 bit
 * direction: output
 * multiplexed: True

### led2:

 * size: 1 bit
 * direction: output
 * multiplexed: True

### led3:

 * size: 1 bit
 * direction: output
 * multiplexed: True

### led4:

 * size: 1 bit
 * direction: output
 * multiplexed: True

### led5:

 * size: 1 bit
 * direction: output
 * multiplexed: True

### led6:

 * size: 1 bit
 * direction: output
 * multiplexed: True

### led7:

 * size: 1 bit
 * direction: output
 * multiplexed: True

### number1:

 * size: 24 bit
 * direction: output
 * multiplexed: True

### number2:

 * size: 8 bit
 * direction: output
 * multiplexed: True


## Full-Example:
```
{
    "type": "tm1638b8s7l8",
    "speed": 1000000,
    "name": "",
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
 * [tm1638b8s7l8.v](tm1638b8s7l8.v)
