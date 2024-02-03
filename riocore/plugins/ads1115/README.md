# ads1115


4-chanel adc via I2C

## Basic-Example:
```
{
    "type": "ads1115",
    "pins": {
        "sda": {
            "pin": "0"
        },
        "scl": {
            "pin": "1"
        }
    }
}
```

## Pins:
### sda:

 * direction: inout
 * pullup: True

### scl:

 * direction: output
 * pullup: True


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
### adc0:

 * type: float
 * direction: input

### adc1:

 * type: float
 * direction: input

### adc2:

 * type: float
 * direction: input

### adc3:

 * type: float
 * direction: input


## Interfaces:
### adc0:

 * size: 16 bit
 * direction: input

### adc1:

 * size: 16 bit
 * direction: input

### adc2:

 * size: 16 bit
 * direction: input

### adc3:

 * size: 16 bit
 * direction: input


## Full-Example:
```
{
    "type": "ads1115",
    "name": "",
    "net": "",
    "pins": {
        "sda": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "scl": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {
        "adc0": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "adc0",
                "section": "inputs",
                "type": "meter"
            }
        },
        "adc1": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "adc1",
                "section": "inputs",
                "type": "meter"
            }
        },
        "adc2": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "adc2",
                "section": "inputs",
                "type": "meter"
            }
        },
        "adc3": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "adc3",
                "section": "inputs",
                "type": "meter"
            }
        }
    }
}
```

## Verilogs:
 * ads1115.v
