# tlc549c
Analog input via tlc549 ADC

spi adc input

## Basic-Example:
```
{
    "type": "tlc549c",
    "pins": {
        "miso": {
            "pin": "0"
        },
        "sclk": {
            "pin": "1"
        },
        "sel": {
            "pin": "2"
        }
    }
}
```

## Pins:
### miso:

 * direction: input
 * pullup: False

### sclk:

 * direction: output
 * pullup: False

### sel:

 * direction: output
 * pullup: False


## Options:
### name:
name of this plugin instance

 * type: str
 * default: None


## Signals:
### value:
measured voltage

 * type: float
 * direction: input


## Interfaces:
### value:

 * size: 8 bit
 * direction: input


## Full-Example:
```
{
    "type": "tlc549c",
    "name": "",
    "pins": {
        "miso": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "debounce"
                }
            ]
        },
        "sclk": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "sel": {
            "pin": "2",
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
                "section": "inputs",
                "type": "meter"
            }
        }
    }
}
```

## Verilogs:
 * tlc549c.v
