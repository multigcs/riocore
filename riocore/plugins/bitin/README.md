# bitin
to read switches or other 1bit signals

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
 * pullup: True


## Options:
### name:
name of this plugin instance

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
