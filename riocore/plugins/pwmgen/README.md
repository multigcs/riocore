# pwmgen

<img align="right" width="320" src="image.png">

**software PWM/PDM generation**

pwmgen is used to generate PWM (pulse width modulation) or PDM (pulse density modulation) signals.
The maximum PWM frequency and the resolution is quite limited compared to hardware-based approaches,
but in many cases software PWM can be very useful. If better performance is needed,
a hardware PWM generator is a better choice.

Keywords: pwm

## Pins:
*FPGA-pins*
### pwm:

 * direction: output

### dir:

 * direction: output
 * optional: True


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### image:
hardware type

 * type: select
 * default: generic

### mode:
modus

 * type: select
 * default: 1

### pwm-freq:
pwm frequency

 * type: float
 * min: 1
 * max: 100000
 * default: 100
 * unit: Hz

### scale:
scale

 * type: float
 * min: -10000.0
 * max: 10000.0
 * default: 100.0
 * unit: 

### offset:
offset

 * type: float
 * min: 0.0
 * max: 10000.0
 * default: 0.0
 * unit: 

### min-dc:
minimum duty cycle

 * type: float
 * min: 0.0
 * max: 100.0
 * default: 0.0
 * unit: 

### max-dc:
maximum duty cycle

 * type: float
 * min: 0.0
 * max: 1.0
 * default: 1.0
 * unit: 

### dither-pwm:
dither-pwm

 * type: bool
 * default: False


## Signals:
*signals/pins in LinuxCNC*
### value:

 * type: float
 * direction: output
 * min: -100.0
 * max: 100.0

### enable:

 * type: bit
 * direction: output


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "pwmgen",
    "pins": {
        "pwm": {
            "pin": "0"
        },
        "dir": {
            "pin": "1"
        }
    }
}
```

## Full-Example:
```
{
    "type": "pwmgen",
    "name": "",
    "image": "generic",
    "mode": "1",
    "pwm-freq": 100,
    "scale": 100.0,
    "offset": 0.0,
    "min-dc": 0.0,
    "max-dc": 1.0,
    "dither-pwm": false,
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
