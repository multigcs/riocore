# wled_bar


ws2812b interface for bar-displays

## Basic-Example:
```
{
    "type": "wled_bar",
    "pins": {
        "data": {
            "pin": "0"
        }
    }
}
```

## Pins:
### data:

 * direction: output
 * pullup: False


## Options:
### leds:
number of LED's

 * type: int
 * min: 0
 * max: 100
 * default: 12

### level:
LED brighness

 * type: int
 * min: 0
 * max: 255
 * default: 127

### name:
name of this plugin instance

 * type: str
 * default: None

### net:
target net in LinuxCNC

 * type: str
 * default: None


## Signals:
### value:

 * type: float
 * direction: output


## Interfaces:
### value:

 * size: 8 bit
 * direction: output


## Full-Example:
```
{
    "type": "wled_bar",
    "leds": 12,
    "level": 127,
    "name": "",
    "net": "",
    "pins": {
        "data": {
            "pin": "0",
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
 * ws2812.v
 * wled_bar.v