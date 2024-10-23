# bitin
**single input pin**

to read switches or other 1bit signals

Keywords: switch limit estop keyboard


![image.png](image.png)

## Basic-Example:
```
{
    "type": "bitin",
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
### bit:

 * size: 1 bit
 * direction: input


## Full-Example:
```
{
    "type": "bitin",
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
