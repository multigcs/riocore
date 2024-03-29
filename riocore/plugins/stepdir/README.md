# stepdir
to control motor drivers via step/dir pin's and an optional enable pin

step/dir output for stepper drivers

## Basic-Example:
```
{
    "type": "stepdir",
    "pins": {
        "step": {
            "pin": "0"
        },
        "dir": {
            "pin": "1"
        },
        "en": {
            "pin": "2"
        }
    }
}
```

## Pins:
### step:

 * direction: output
 * pullup: False

### dir:

 * direction: output
 * pullup: False

### en:

 * direction: output
 * pullup: False


## Options:
### name:
name of this plugin instance

 * type: str
 * default: None

### axis:
axis name (X,Y,Z,...)

 * type: select
 * default: None

### is_joint:
configure as joint

 * type: bool
 * default: False


## Signals:
### velocity:
speed in steps per second

 * type: float
 * direction: output
 * min: -1000000
 * max: 1000000

### position:
position feedback

 * type: float
 * direction: input

### enable:

 * type: bit
 * direction: output


## Interfaces:
### velocity:

 * size: 32 bit
 * direction: output

### enable:

 * size: 1 bit
 * direction: output

### position:

 * size: 32 bit
 * direction: input


## Full-Example:
```
{
    "type": "stepdir",
    "name": "",
    "axis": "",
    "is_joint": false,
    "pins": {
        "step": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "dir": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "en": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {
        "velocity": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "velocity",
                "section": "outputs",
                "type": "scale"
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
        "enable": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "enable",
                "section": "outputs",
                "type": "checkbox"
            }
        }
    }
}
```

## Verilogs:
 * stepdir.v
