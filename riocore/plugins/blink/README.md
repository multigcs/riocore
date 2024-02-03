# blink


blinking output pin

## Basic-Example:
```
{
    "type": "blink",
    "pins": {
        "led": {
            "pin": "0"
        }
    }
}
```

## Pins:
### led:

 * direction: output
 * pullup: False


## Options:
### frequency:
blink frequency in Hz

 * type: float
 * default: 1.0
 * unit: Hz

### name:
name of this plugin instance

 * type: str
 * default: None


## Signals:


## Interfaces:


## Full-Example:
```
{
    "type": "blink",
    "frequency": 1.0,
    "name": "",
    "pins": {
        "led": {
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
 * blink.v
