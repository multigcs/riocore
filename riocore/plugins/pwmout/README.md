# pwmout

<img align="right" width="320" src="image.png">

**pwm output**

to control AC/DC-Motors or for analog outputs

Keywords: joint dcservo acservo 10v 5v dac analog

## Pins:
*FPGA-pins*
### pwm:

 * direction: output

### dir:

 * direction: output
 * optional: True

### en:

 * direction: output
 * optional: True


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### is_joint:
configure as joint

 * type: bool
 * default: False

### axis:
axis name (X,Y,Z,...)

 * type: select
 * default: None

### image:
hardware type

 * type: select
 * default: spindle500w

### frequency:
PWM frequency

 * type: int
 * min: 10
 * max: 1000000
 * default: 10000
 * unit: Hz


## Signals:
*signals/pins in LinuxCNC*
### dty:

 * type: float
 * direction: output
 * min: 0
 * max: 100
 * unit: %

### enable:

 * type: bit
 * direction: output


## Interfaces:
*transport layer*
### dty:

 * size: 32 bit
 * direction: output

### enable:

 * size: 1 bit
 * direction: output


## Basic-Example:
```
{
    "type": "pwmout",
    "pins": {
        "pwm": {
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

## Full-Example:
```
{
    "type": "pwmout",
    "name": "",
    "is_joint": false,
    "axis": "",
    "image": "spindle500w",
    "frequency": 10000,
    "pins": {
        "pwm": {
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
        "dty": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "dty",
                "section": "outputs",
                "type": "scale"
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
 * [pwmout.v](pwmout.v)
