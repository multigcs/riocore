# bitout
**singe bit output pin**

to control relais, leds, valves, ....

Keywords: led relais valve lamp motor magnet


![image.png](image.png)

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
