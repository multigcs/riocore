# bldc

<img align="right" width="320" src="image.png">

**BLDC FOC**

to control BLDC Motors - experimental

Motor-Setup:
* set motor poles and encoder resolution in the options
* start rio-test gui
* set enable
* leave torque at zero
* set velocity to ~30% (warning: motor will start to spin !)
* adjust the offset until the motor stop's (should between -15<->15)
* add the offset value to your json config and set a torque value (0-16)
```
    "signals": {
        "offset": {
            "setp": "-11"
        },
        "torque": {
            "setp": "16"
        }
    }
```

Keywords: joint brushless

## Pins:
*FPGA-pins*
### u:

 * direction: output

### v:

 * direction: output

### w:

 * direction: output

### en:

 * direction: output


## Options:
*user-options*
### frequency:
PWM frequency

 * type: int
 * min: 10
 * max: 1000000
 * default: 10000
 * unit: Hz

### halsensor:
encoder instance

 * type: str
 * default: 
 * unit: 

### poles:
motor poles

 * type: int
 * min: 2
 * max: 100
 * default: 4
 * unit: 

### feedback_res:
encoder resolution

 * type: int
 * min: 10
 * max: 100000
 * default: 4096
 * unit: 

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

 * type: float
 * direction: output
 * min: -100
 * max: 100
 * unit: %

### offset:

 * type: float
 * direction: output
 * min: -64
 * max: 64
 * unit: 

### torque:

 * type: float
 * direction: output
 * min: 0
 * max: 16.0
 * unit: 

### enable:

 * type: bit
 * direction: output

### testmode:

 * type: bit
 * direction: output


## Interfaces:
*transport layer*
### velocity:

 * size: 16 bit
 * direction: output

### offset:

 * size: 8 bit
 * direction: output

### torque:

 * size: 8 bit
 * direction: output

### enable:

 * size: 1 bit
 * direction: output

### testmode:

 * size: 1 bit
 * direction: output


## Basic-Example:
```
{
    "type": "bldc",
    "pins": {
        "u": {
            "pin": "0"
        },
        "v": {
            "pin": "1"
        },
        "w": {
            "pin": "2"
        },
        "en": {
            "pin": "3"
        }
    }
}
```

## Full-Example:
```
{
    "type": "bldc",
    "frequency": 10000,
    "halsensor": "",
    "poles": 4,
    "feedback_res": 4096,
    "name": "",
    "axis": "",
    "is_joint": false,
    "pins": {
        "u": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "v": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "w": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "en": {
            "pin": "3",
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
        "offset": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "offset",
                "section": "outputs",
                "type": "scale"
            }
        },
        "torque": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "torque",
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
        },
        "testmode": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "testmode",
                "section": "outputs",
                "type": "checkbox"
            }
        }
    }
}
```

## Verilogs:
 * [bldc.v](bldc.v)
