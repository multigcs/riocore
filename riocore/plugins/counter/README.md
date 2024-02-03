# counter


pulse counter input

## Basic-Example:
```
{
    "type": "counter",
    "pins": {
        "up": {
            "pin": "0"
        },
        "down": {
            "pin": "1"
        },
        "reset": {
            "pin": "2"
        }
    }
}
```

## Pins:
### up:
increment pin

 * direction: input
 * pullup: False

### down:
decrement pin

 * direction: input
 * pullup: False

### reset:
reset to zero pin

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
### counter:

 * type: float
 * direction: input


## Interfaces:
### counter:

 * size: 32 bit
 * direction: input


## Full-Example:
```
{
    "type": "counter",
    "name": "",
    "net": "",
    "pins": {
        "up": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "debounce"
                }
            ]
        },
        "down": {
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
        "reset": {
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
        "counter": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "counter",
                "section": "inputs",
                "type": "meter"
            }
        }
    }
}
```

## Verilogs:
 * counter.v
