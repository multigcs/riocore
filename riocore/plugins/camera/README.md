# camera

<img align="right" width="320" src="image.png">

**gui component to display an camera image**

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


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "camera",
    "pins": {}
}
```

## Full-Example:
```
{
    "type": "camera",
    "name": "",
    "device": "/dev/video0",
    "pins": {},
    "signals": {}
}
```
