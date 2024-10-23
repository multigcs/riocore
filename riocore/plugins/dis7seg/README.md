# dis7seg
**7segment display with buttons**

only usable for devboards with 7segment display / better using other 7seg plugins

Keywords: info display


![image.png](image.png)

## Basic-Example:
```
{
    "type": "dis7seg",
    "pins": {
        "en1": {
            "pin": "0"
        },
        "en2": {
            "pin": "1"
        },
        "en3": {
            "pin": "2"
        },
        "en4": {
            "pin": "3"
        },
        "seg_a": {
            "pin": "4"
        },
        "seg_b": {
            "pin": "5"
        },
        "seg_c": {
            "pin": "6"
        },
        "seg_d": {
            "pin": "7"
        },
        "seg_e": {
            "pin": "8"
        },
        "seg_f": {
            "pin": "9"
        },
        "seg_g": {
            "pin": "10"
        }
    }
}
```

## Pins:
*FPGA-pins*
### en1:

 * direction: output

### en2:

 * direction: output

### en3:

 * direction: output

### en4:

 * direction: output

### seg_a:

 * direction: output
 * optional: True

### seg_b:

 * direction: output
 * optional: True

### seg_c:

 * direction: output
 * optional: True

### seg_d:

 * direction: output
 * optional: True

### seg_e:

 * direction: output
 * optional: True

### seg_f:

 * direction: output
 * optional: True

### seg_g:

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
### value:
number to display

 * type: float
 * direction: output
 * min: 0
 * max: 9999


## Interfaces:
*transport layer*
### value:

 * size: 16 bit
 * direction: output
 * multiplexed: True


## Full-Example:
```
{
    "type": "dis7seg",
    "name": "",
    "pins": {
        "en1": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "en2": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "en3": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "en4": {
            "pin": "3",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "seg_a": {
            "pin": "4",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "seg_b": {
            "pin": "5",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "seg_c": {
            "pin": "6",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "seg_d": {
            "pin": "7",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "seg_e": {
            "pin": "8",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "seg_f": {
            "pin": "9",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "seg_g": {
            "pin": "10",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {
        "value": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "value",
                "section": "outputs",
                "type": "scale"
            }
        }
    }
}
```

## Verilogs:
 * [dis7seg.v](dis7seg.v)
