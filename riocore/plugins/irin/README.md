# irin
**IR-Remote input**

that was just a gimmick, not really useful

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

## Pins:
### ir:

 * direction: input
 * pullup: False


## Options:
### name:
name of this plugin instance

 * type: str
 * default: None


## Signals:
### code:

 * type: float
 * direction: input


## Interfaces:
### code:

 * size: 8 bit
 * direction: input


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
