# bitout
to control relais, leds, valves, ....

singe bit output pin

## Basic-Example:
```
{
    "type": "bitout",
    "pins": {
        "bit": {
            "pin": "0"
        }
    }
}
```

## Pins:
### bit:

 * direction: output
 * pullup: False


## Options:
### name:
name of this plugin instance

 * type: str
 * default: None


## Signals:
### bit:

 * type: bit
 * direction: output


## Interfaces:
### bit:

 * size: 1 bit
 * direction: output


## Full-Example:
```
{
    "type": "bitout",
    "name": "",
    "pins": {
        "bit": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
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
                "section": "outputs",
                "type": "checkbox"
            }
        }
    }
}
```
