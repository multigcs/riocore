# tlc549c
**spi adc input**

Analog input via tlc549 ADC

Keywords: analog adc


![image.png](image.png)

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
### value:
measured voltage

 * type: float
 * direction: input
 * unit: Volt


## Interfaces:
*transport layer*
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
 * [tlc549c.v](tlc549c.v)
