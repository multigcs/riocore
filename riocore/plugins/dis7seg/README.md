# dis7seg


7segment display with buttons

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
### en1:

 * direction: output
 * pullup: False

### en2:

 * direction: output
 * pullup: False

### en3:

 * direction: output
 * pullup: False

### en4:

 * direction: output
 * pullup: False

### seg_a:

 * direction: output
 * pullup: False

### seg_b:

 * direction: output
 * pullup: False

### seg_c:

 * direction: output
 * pullup: False

### seg_d:

 * direction: output
 * pullup: False

### seg_e:

 * direction: output
 * pullup: False

### seg_f:

 * direction: output
 * pullup: False

### seg_g:

 * direction: output
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
### value:
number to display

 * type: float
 * direction: output
 * min: 0
 * max: 9999


## Interfaces:
### value:

 * size: 16 bit
 * direction: output


## Full-Example:
```
{
    "type": "dis7seg",
    "name": "",
    "net": "",
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
 * dis7seg.v
