# spipoti
**spi digital poti**

Analog-Outout via spi digital poti

Keywords: analog poti dac


![image.png](image.png)

## Basic-Example:
```
{
    "type": "spipoti",
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
### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### value:

 * type: float
 * direction: output


## Interfaces:
*transport layer*
### value:

 * size: 8 bit
 * direction: output


## Full-Example:
```
{
    "type": "spipoti",
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
 * [spipoti.v](spipoti.v)
