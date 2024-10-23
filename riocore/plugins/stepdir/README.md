# stepdir
**step/dir output for stepper drivers**

to control motor drivers via step/dir pin's and an optional enable pin

Keywords: stepper servo joint


![image.png](image.png)

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
*FPGA-pins*
### step:

 * direction: output

### dir:

 * direction: output

### en:

 * direction: output
 * optional: True


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### axis:
axis name (X,Y,Z,...)

 * type: select
 * default: None

### is_joint:
configure as joint

 * type: bool
 * default: False


## Signals:
*signals/pins in LinuxCNC*
### velocity:
speed in steps per second

 * type: float
 * direction: output
 * min: -100000
 * max: 100000
 * unit: Hz

### position:
position feedback

 * type: float
 * direction: input
 * unit: steps

### enable:

 * type: bit
 * direction: output


## Interfaces:
*transport layer*
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
 * [stepdir.v](stepdir.v)
