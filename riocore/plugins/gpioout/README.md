# gpioout

<img align="right" width="320" src="image.png">

**gpio output**

Keywords: output

## Pins:
*FPGA-pins*
### bit:

 * direction: output


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


## Signals:
*signals/pins in LinuxCNC*
### bit:

 * type: bit
 * direction: output


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "gpioout",
    "pins": {
        "bit": {
            "pin": "0"
        }
    }
}
```

## Full-Example:
```
{
    "type": "gpioout",
    "name": "",
    "image": "generic",
    "pins": {
        "bit": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {
        "bit": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "bit",
                "section": "outputs",
                "type": "checkbox"
            }
        }
    }
}
```
