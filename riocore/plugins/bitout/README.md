# bitout

<img align="right" width="320" src="image.png">

**singe bit output pin**

to control relais, leds, valves, ....

Keywords: led relais valve lamp motor magnet

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


## Signals:
*signals/pins in LinuxCNC*
### bit:

 * type: bit
 * direction: output


## Interfaces:
*transport layer*
### bit:

 * size: 1 bit
 * direction: output


## Basic-Example:
```
{
    "type": "bitout",
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
    "type": "bitout",
    "name": "",
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
