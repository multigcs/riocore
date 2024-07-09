# ads1115
**4-channel adc via I2C**

to read analog signals with cheap ads1115 chips

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
*FPGA-pins*
### sda:

 * direction: inout
 * pullup: True

### scl:

 * direction: output
 * pullup: True


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: None


## Signals:
*signals/pins in LinuxCNC*
### adc0:

 * type: float
 * direction: input
 * unit: Volt

### adc1:

 * type: float
 * direction: input
 * unit: Volt

### adc2:

 * type: float
 * direction: input
 * unit: Volt

### adc3:

 * type: float
 * direction: input
 * unit: Volt


## Interfaces:
*transport layer*
### adc0:

 * size: 16 bit
 * direction: input
 * multiplexed: True

### adc1:

 * size: 16 bit
 * direction: input
 * multiplexed: True

### adc2:

 * size: 16 bit
 * direction: input
 * multiplexed: True

### adc3:

 * size: 16 bit
 * direction: input
 * multiplexed: True


## Full-Example:
```
{
    "type": "ads1115",
    "name": "",
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
 * [ads1115.v](ads1115.v)
