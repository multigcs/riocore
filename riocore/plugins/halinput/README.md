# halinput

<img align="right" width="320" src="image.png">

**joypad support**

halinput joypad support

Keywords: jog joypad usb

## Pins:
*FPGA-pins*


## Options:
*user-options*
### joypad_name:

 * type: str
 * default: Joystick

### slow:

 * type: str
 * default: btn-top2

### medium:

 * type: str
 * default: btn-base

### fast:

 * type: str
 * default: btn-pinkie

### x:

 * type: float
 * default: abs-x

### y:

 * type: float
 * default: -abs-y

### z:

 * type: float
 * default: -abs-rz

### a:

 * type: float
 * default: 

### b:

 * type: float
 * default: 

### c:

 * type: float
 * default: 

### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "halinput",
    "pins": {}
}
```

## Full-Example:
```
{
    "type": "halinput",
    "joypad_name": "Joystick",
    "slow": "btn-top2",
    "medium": "btn-base",
    "fast": "btn-pinkie",
    "x": "abs-x",
    "y": "-abs-y",
    "z": "-abs-rz",
    "a": "",
    "b": "",
    "c": "",
    "name": "",
    "pins": {},
    "signals": {}
}
```
