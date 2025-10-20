# hy_vfd

<img align="right" width="320" src="image.png">

**non-realtime component for Huanyang VFDs**

This component connects the Huanyang VFD to the LinuxCNC HAL via a serial (RS-485) connection.

Keywords: jog usb

## Pins:
*FPGA-pins*


## Options:
*user-options*
### spindle:

 * type: int
 * min: 0
 * max: 4
 * default: 0

### device:

 * type: str
 * default: /dev/ttyUSB0

### baud:

 * type: str
 * default: 9600

### parity:

 * type: select
 * default: even

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
    "type": "hy_vfd",
    "pins": {}
}
```

## Full-Example:
```
{
    "type": "hy_vfd",
    "spindle": 0,
    "device": "/dev/ttyUSB0",
    "baud": "9600",
    "parity": "even",
    "name": "",
    "pins": {},
    "signals": {}
}
```
