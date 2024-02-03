# bitin


single input pin

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
### bit:

 * direction: input
 * pullup: False


## Options:
### name:
name of this plugin instance

 * type: str
 * default: None

### net:
target net in LinuxCNC

 * type: str
 * default: None


## Signals:
### bit:

 * type: bit
 * direction: input


## Interfaces:
### bit:

 * size: 1 bit
 * direction: input


## Full-Example:
```
{
    "type": "bitin",
    "name": "",
    "net": "",
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
