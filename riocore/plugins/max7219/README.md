# max7219
**7segment display based on max7219**

to display values from LinuxCNC on 7segment display's

Keywords: info display


![image.png](image.png)

## Basic-Example:
```
{
    "type": "max7219",
    "pins": {
        "mosi": {
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
### mosi:

 * direction: output

### sclk:

 * direction: output

### sel:

 * direction: output


## Options:
*user-options*
### brightness:
display brightness

 * type: int
 * min: 0
 * max: 15
 * default: 15

### frequency:
interface clock frequency

 * type: int
 * min: 100000
 * max: 10000000
 * default: 1000000

### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### value:

 * type: float
 * direction: output
 * min: -999999
 * max: 999999


## Interfaces:
*transport layer*
### value:

 * size: 24 bit
 * direction: output


## Full-Example:
```
{
    "type": "max7219",
    "brightness": 15,
    "frequency": 1000000,
    "name": "",
    "pins": {
        "mosi": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
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
                "section": "outputs",
                "type": "scale"
            }
        }
    }
}
```

## Verilogs:
 * [max7219.v](max7219.v)
