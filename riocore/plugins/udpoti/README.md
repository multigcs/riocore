# udpoti
digital-poti with up/down+dir interface

controling digital poti for analog outputs

## Basic-Example:
```
{
    "type": "udpoti",
    "pins": {
        "updown": {
            "pin": "0"
        },
        "increment": {
            "pin": "1"
        }
    }
}
```

## Pins:
### updown:

 * direction: output
 * pullup: False

### increment:

 * direction: output
 * pullup: False


## Options:
### resolution:
number of steps from min to maximum value

 * type: int
 * min: 0
 * max: 255
 * default: 100

### frequency:
interface frequency

 * type: int
 * min: 0
 * max: 100000
 * default: 100
 * unit: Hz

### name:
name of this plugin instance

 * type: str
 * default: None


## Signals:
### value:

 * type: float
 * direction: output


## Interfaces:
### value:

 * size: 32 bit
 * direction: output


## Full-Example:
```
{
    "type": "udpoti",
    "resolution": 100,
    "frequency": 100,
    "name": "",
    "pins": {
        "updown": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "increment": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {
        "value": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "value",
                "section": "outputs",
                "type": "scale"
            }
        }
    }
}
```

## Verilogs:
 * udpoti.v
