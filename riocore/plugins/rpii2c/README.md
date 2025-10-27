# rpii2c

<img align="right" width="320" src="image.png">

**gpio support over i2c port**

gpio support over i2c port

Keywords: ii2c gpio

## Pins:
*FPGA-pins*
### IO:P7:

 * direction: all

### IO:P6:

 * direction: all

### IO:P5:

 * direction: all

### IO:P4:

 * direction: all

### IO:P3:

 * direction: all

### IO:P2:

 * direction: all

### IO:P1:

 * direction: all

### IO:P0:

 * direction: all


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### device:
i2c device

 * type: select
 * default: pcf8574

### address:
slave address

 * type: select
 * default: 0x20


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "rpii2c",
    "pins": {
        "IO:P7": {
            "pin": "0"
        },
        "IO:P6": {
            "pin": "1"
        },
        "IO:P5": {
            "pin": "2"
        },
        "IO:P4": {
            "pin": "3"
        },
        "IO:P3": {
            "pin": "4"
        },
        "IO:P2": {
            "pin": "5"
        },
        "IO:P1": {
            "pin": "6"
        },
        "IO:P0": {
            "pin": "7"
        }
    }
}
```

## Full-Example:
```
{
    "type": "rpii2c",
    "name": "",
    "device": "pcf8574",
    "address": "0x20",
    "pins": {
        "IO:P7": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:P6": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:P5": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:P4": {
            "pin": "3",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:P3": {
            "pin": "4",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:P2": {
            "pin": "5",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:P1": {
            "pin": "6",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:P0": {
            "pin": "7",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {}
}
```
