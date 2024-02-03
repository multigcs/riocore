# quadencoderz


quadencoder with index pin

## Basic-Example:
```
{
    "type": "quadencoderz",
    "pins": {
        "a": {
            "pin": "0"
        },
        "b": {
            "pin": "1"
        },
        "z": {
            "pin": "2"
        }
    }
}
```

## Pins:
### a:

 * direction: input
 * pullup: False

### b:

 * direction: input
 * pullup: False

### z:
index pin

 * direction: input
 * pullup: False


## Options:
### quad_type:
encoder type

 * type: int
 * min: 1
 * max: 4
 * default: 2

### name:
name of this plugin instance

 * type: str
 * default: None

### net:
target net in LinuxCNC

 * type: str
 * default: None


## Signals:
### indexenable:

 * type: bit
 * direction: inout

### indexout:

 * type: bit
 * direction: input

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
### indexenable:

 * size: 1 bit
 * direction: output

### indexout:

 * size: 1 bit
 * direction: input

### position:

 * size: 32 bit
 * direction: input


## Full-Example:
```
{
    "type": "quadencoderz",
    "quad_type": 2,
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
        },
        "z": {
            "pin": "2",
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
        "indexenable": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "indexenable",
                "section": "status",
                "type": "meter"
            }
        },
        "indexout": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "indexout",
                "section": "inputs",
                "type": "led"
            }
        },
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
 * quadencoderz.v
