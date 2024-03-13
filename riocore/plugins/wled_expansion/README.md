# wled
simple ws2812b led driver / same as the wled plugin but integrated as an expansion to combinate with other plugins

ws2812b interface acting as an expansion port

## Basic-Example:
```
{
    "type": "wled",
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
 * default: 1

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


## Signals:


## Interfaces:


## Full-Example:
```
{
    "type": "wled",
    "leds": 1,
    "level": 127,
    "name": "",
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
    "signals": {}
}
```

## Verilogs:
 * ws2812.v
 * wled.v
