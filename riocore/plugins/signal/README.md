# signal

<img align="right" width="320" src="image.png">

**virtual signal**

virtual signal

Keywords: virtual

## Pins:
*FPGA-pins*


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### dir:
signal direction

 * type: select
 * default: input

### vtype:
signal type

 * type: select
 * default: float


## Signals:
*signals/pins in LinuxCNC*
### value:

 * type: float
 * direction: input


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "signal",
    "pins": {}
}
```

## Full-Example:
```
{
    "type": "signal",
    "name": "",
    "dir": "input",
    "vtype": "float",
    "pins": {},
    "signals": {
        "value": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "value",
                "section": "inputs",
                "type": "meter"
            }
        }
    }
}
```
