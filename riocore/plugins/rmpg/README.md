# camjog

<img align="right" width="320" src="image.png">

**gui component to jog via camera image**

Keywords: jog gui robot

## Pins:
*FPGA-pins*


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### device:

 * type: str
 * default: /dev/video0

### width:

 * type: int
 * default: 640

### height:

 * type: int
 * default: 480

### scale:

 * type: float
 * default: 1.0

### tabname:

 * type: str
 * default: camjog


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "camjog",
    "pins": {}
}
```

## Full-Example:
```
{
    "type": "camjog",
    "name": "",
    "device": "/dev/video0",
    "width": 640,
    "height": 480,
    "scale": 1.0,
    "tabname": "camjog",
    "pins": {},
    "signals": {}
}
```
