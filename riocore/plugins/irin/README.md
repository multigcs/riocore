# irin

<img align="right" width="320" src="image.png">

**IR-Remote input**

that was just a gimmick, not really useful

Keywords: remote control keyboard

## Pins:
*FPGA-pins*
### ir:

 * direction: input


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### code:

 * type: float
 * direction: input


## Interfaces:
*transport layer*
### code:

 * size: 8 bit
 * direction: input


## Basic-Example:
```
{
    "type": "irin",
    "pins": {
        "ir": {
            "pin": "0"
        }
    }
}
```

## Full-Example:
```
{
    "type": "irin",
    "name": "",
    "pins": {
        "ir": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "debounce"
                }
            ]
        }
    },
    "signals": {
        "code": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "code",
                "section": "inputs",
                "type": "meter"
            }
        }
    }
}
```

## Verilogs:
 * [irin.v](irin.v)
