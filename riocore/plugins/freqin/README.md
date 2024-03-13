# freqin
to messurement digital frequencies

frequency input

## Basic-Example:
```
{
    "type": "freqin",
    "pins": {
        "freq": {
            "pin": "0"
        }
    }
}
```

## Pins:
### freq:

 * direction: input
 * pullup: False


## Options:
### freq_min:
minimum measured frequency (for faster updates)

 * type: int
 * min: 1
 * max: 10000
 * default: 10
 * unit: Hz

### name:
name of this plugin instance

 * type: str
 * default: None


## Signals:
### frequency:

 * type: float
 * direction: input

### valid:

 * type: bit
 * direction: input


## Interfaces:
### frequency:

 * size: 32 bit
 * direction: input

### valid:

 * size: 1 bit
 * direction: input


## Full-Example:
```
{
    "type": "freqin",
    "freq_min": 10,
    "name": "",
    "pins": {
        "freq": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "debounce"
                }
            ]
        }
    },
    "signals": {
        "frequency": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "frequency",
                "section": "inputs",
                "type": "meter"
            }
        },
        "valid": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "valid",
                "section": "inputs",
                "type": "led"
            }
        }
    }
}
```

## Verilogs:
 * freqin.v
