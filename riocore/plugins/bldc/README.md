# bldc

<img align="right" width="320" src="image.png">


| :warning: EXPERIMENTAL |
|:-----------------------|

**BLDC FOC**

to control BLDC Motors

Motor-Setup:
* set motor poles and encoder resolution in the options
* start rio-test gui
* set mode to calibration (2)
* set enable
* set velocity to ~30% (warning: motor will start to spin !)
* adjust the offset until the motor stop's (should between -15<->15)
* add the offset value to your json config
```
    "signals": {
        "offset": {
            "setp": "-11"
        }
    }
```

Keywords: joint brushless

## Pins:
*FPGA-pins*
### u_p:

 * direction: output

### v_p:

 * direction: output

### w_p:

 * direction: output

### u_n:

 * direction: output
 * optional: True

### v_n:

 * direction: output
 * optional: True

### w_n:

 * direction: output
 * optional: True

### en:

 * direction: output
 * optional: True


## Options:
*user-options*
### frequency:
PWM frequency

 * type: int
 * min: 10
 * max: 200000
 * default: 50000
 * unit: Hz

### pwmmode:
PWM mode

 * type: select
 * default: 0
 * unit: 

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

### table_len:
sinus table lenght in bits

 * type: int
 * min: 4
 * max: 12
 * default: 6
 * unit: bits

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

### enable:

 * type: bit
 * direction: output

### mode:

 * type: float
 * direction: output
 * min: 0
 * max: 2


## Interfaces:
*transport layer*
### velocity:

 * size: 16 bit
 * direction: output

### offset:

 * size: 16 bit
 * direction: output
 * multiplexed: True

### enable:

 * size: 1 bit
 * direction: output

### mode:

 * size: 8 bit
 * direction: output
 * multiplexed: True


## Basic-Example:
```
{
    "type": "bldc",
    "pins": {
        "u_p": {
            "pin": "0"
        },
        "v_p": {
            "pin": "1"
        },
        "w_p": {
            "pin": "2"
        },
        "u_n": {
            "pin": "3"
        },
        "v_n": {
            "pin": "4"
        },
        "w_n": {
            "pin": "5"
        },
        "en": {
            "pin": "6"
        }
    }
}
```

## Full-Example:
```
{
    "type": "bldc",
    "frequency": 50000,
    "pwmmode": 0,
    "halsensor": "",
    "poles": 4,
    "table_len": 6,
    "feedback_res": 4096,
    "name": "",
    "axis": "",
    "is_joint": false,
    "pins": {
        "u_p": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "v_p": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "w_p": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "u_n": {
            "pin": "3",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "v_n": {
            "pin": "4",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "w_n": {
            "pin": "5",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "en": {
            "pin": "6",
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
        "enable": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "enable",
                "section": "outputs",
                "type": "checkbox"
            }
        },
        "mode": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "mode",
                "section": "outputs",
                "type": "scale"
            }
        }
    }
}
```

## Verilogs:
 * [bldc.v](bldc.v)
