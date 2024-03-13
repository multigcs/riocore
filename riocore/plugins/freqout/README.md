# freqout
to output variable frequency signals

frequency output

## Basic-Example:
```
{
    "type": "freqout",
    "pins": {
        "freq": {
            "pin": "0"
        }
    }
}
```

## Pins:
### freq:

 * direction: output
 * pullup: False


## Options:
### name:
name of this plugin instance

 * type: str
 * default: None


## Signals:
### frequency:
output frequency

 * type: float
 * direction: output
 * min: 0
 * max: 1000000


## Interfaces:
### frequency:

 * size: 32 bit
 * direction: output


## Full-Example:
```
{
    "type": "freqout",
    "name": "",
    "pins": {
        "freq": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
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
                "section": "outputs",
                "type": "scale"
            }
        }
    }
}
```

## Verilogs:
 * freqout.v
