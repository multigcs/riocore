# parport

<img align="right" width="320" src="image.png">

**gpio support over parallel port**

PC parallel port used as gpio

Keywords: parport gpio

## Pins:
*FPGA-pins*


## Options:
*user-options*
### portaddr:
parport address

 * type: select
 * default: 0

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
    "type": "parport",
    "pins": {}
}
```

## Full-Example:
```
{
    "type": "parport",
    "portaddr": "0",
    "name": "",
    "pins": {},
    "signals": {}
}
```
