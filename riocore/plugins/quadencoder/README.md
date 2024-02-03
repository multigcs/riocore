# quadencoder


quadencoder

## Basic-Example:
```
{
    "type": "quadencoder",
    "pins": {
        "a": {
            "pin": "0"
        },
        "b": {
            "pin": "1"
        }
    }
}
```

## Pins:
### a:

 * direction: input
 * pullup: True

### b:

 * direction: input
 * pullup: True


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
### position:
position feedback in steps

 * type: float
 * direction: input

### rps:
calculates revolutions per second

 * type: float
 * direction: input

### rpm:
calculates revolutions per minute

 * type: float
 * direction: input


## Interfaces:
### position:

 * size: 32 bit
 * direction: input


## Full-Example:
```
{
    "type": "quadencoder",
    "name": "",
    "net": "",
    "pins": {
        "a": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "debounce"
                }
            ]
        },
        "b": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {
        "position": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "position",
                "section": "inputs",
                "type": "meter"
            }
        },
        "rps": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "rps",
                "section": "inputs",
                "type": "meter"
            }
        },
        "rpm": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "rpm",
                "section": "inputs",
                "type": "meter"
            }
        }
    }
}
```

## Verilogs:
 * quadencoder.v
