# parport

<img align="right" width="320" src="image.png">

**gpio support over parallel port**

PC parallel port used as gpio

Keywords: parport gpio

## Pins:
*FPGA-pins*


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### portaddr:
parport address

 * type: select
 * default: 0


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
    "name": "",
    "portaddr": "0",
    "pins": {},
    "signals": {}
}
```
