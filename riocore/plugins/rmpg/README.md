# rmpg

<img align="right" width="320" src="image.png">

**remote mpg server**

see riocore/plugins/rmpg/clients/ for clients

Keywords: jog cam remote

## Pins:
*FPGA-pins*


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### port:

 * type: int
 * default: 10000


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "rmpg",
    "pins": {}
}
```

## Full-Example:
```
{
    "type": "rmpg",
    "name": "",
    "port": 10000,
    "pins": {},
    "signals": {}
}
```
