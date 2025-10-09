# gpioin

<img align="right" width="320" src="image.png">

**gpio input**

Keywords: input

## Pins:
*FPGA-pins*
### bit:

 * direction: input


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### bit:

 * type: bit
 * direction: input


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "gpioin",
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
    "type": "gpioin",
    "name": "",
    "pins": {
        "bit": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "debounce"
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
                "section": "inputs",
                "type": "led"
            }
        }
    }
}
```
