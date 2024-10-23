# wled_bar
**ws2812b interface for bar-displays**

simple ws2812b driver with variable input to build led-bars

Keywords: led rgb status info


![image.png](image.png)

## Basic-Example:
```
{
    "type": "wled_bar",
    "pins": {
        "data": {
            "pin": "0"
        }
    }
}
```

## Pins:
*FPGA-pins*
### data:

 * direction: output


## Options:
*user-options*
### leds:
number of LED's

 * type: int
 * min: 0
 * max: 100
 * default: 12

### level:
LED brighness

 * type: int
 * min: 0
 * max: 255
 * default: 127

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
    "type": "wled_bar",
    "leds": 12,
    "level": 127,
    "name": "",
    "pins": {
        "data": {
            "pin": "0",
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
 * [ws2812.v](ws2812.v)
 * [wled_bar.v](wled_bar.v)
