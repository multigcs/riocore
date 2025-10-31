# mesapwmgen

<img align="right" width="320" src="image.png">

**mesa pwm pulse generation**

Keywords: pwm

## Pins:
*FPGA-pins*
### pwm:

 * direction: output


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### image:
hardware type

 * type: select
 * default: spindle500w

### scale:
max pwm value

 * type: float
 * min: 0.1
 * max: 100000
 * default: 100


## Signals:
*signals/pins in LinuxCNC*
### value:

 * type: float
 * direction: output
 * min: 0.0
 * max: 100

### enable:

 * type: bit
 * direction: output


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "mesapwmgen",
    "pins": {
        "pwm": {
            "pin": "0"
        }
    }
}
```

## Full-Example:
```
{
    "type": "mesapwmgen",
    "name": "",
    "image": "spindle500w",
    "scale": 100,
    "pins": {
        "pwm": {
            "pin": "0",
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
