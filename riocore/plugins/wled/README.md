# wled


ws2812b interface

## Basic-Example:
```
{
    "type": "wled",
    "pins": {
        "data": {
            "pin": "0"
        }
    }
}
```

## Pins:
### data:

 * direction: output
 * pullup: False


## Options:
### leds:
number of LED's

 * type: int
 * min: 0
 * max: 100
 * default: 1

### level:
LED brighness

 * type: int
 * min: 0
 * max: 255
 * default: 127

### name:
name of this plugin instance

 * type: str
 * default: None

### net:
target net in LinuxCNC

 * type: str
 * default: None


## Signals:
### 0_green:

 * type: bit
 * direction: output

### 0_blue:

 * type: bit
 * direction: output

### 0_red:

 * type: bit
 * direction: output


## Interfaces:
### 0_green:

 * size: 1 bit
 * direction: output

### 0_blue:

 * size: 1 bit
 * direction: output

### 0_red:

 * size: 1 bit
 * direction: output


## Full-Example:
```
{
    "type": "wled",
    "leds": 1,
    "level": 127,
    "name": "",
    "net": "",
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
        "0_green": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "0_green",
                "section": "outputs",
                "type": "checkbox"
            }
        },
        "0_blue": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "0_blue",
                "section": "outputs",
                "type": "checkbox"
            }
        },
        "0_red": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "0_red",
                "section": "outputs",
                "type": "checkbox"
            }
        }
    }
}
```

## Verilogs:
 * ws2812.v
 * wled.v
