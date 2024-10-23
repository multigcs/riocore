# max6675
**SPI temperature sensor**

to messurement very high temperatures of up to 1250 degrees Celsius

Keywords: analog adc


![image.png](image.png)

## Basic-Example:
```
{
    "type": "max6675",
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
*FPGA-pins*
### miso:

 * direction: input

### sclk:

 * direction: output

### sel:

 * direction: output


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### temperature:

 * type: float
 * direction: input
 * unit: °C


## Interfaces:
*transport layer*
### temperature:

 * size: 16 bit
 * direction: input


## Full-Example:
```
{
    "type": "max6675",
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
        "temperature": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "temperature",
                "section": "inputs",
                "type": "meter"
            }
        }
    }
}
```

## Verilogs:
 * [max6675.v](max6675.v)
