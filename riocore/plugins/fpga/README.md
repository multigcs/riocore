# fpga
**fpga board**

fpga

Keywords: fpga board

## Pins:
*FPGA-pins*


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### node_type:
board type

 * type: select
 * default: Tangbob

### simulation:
simulation mode

 * type: bool
 * default: False


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "fpga",
    "pins": {}
}
```

## Full-Example:
```
{
    "type": "fpga",
    "name": "",
    "node_type": "Tangbob",
    "simulation": false,
    "pins": {},
    "signals": {}
}
```
