# udpoti
**digital-poti with up/down+dir interface**

controling digital poti for analog outputs

Keywords: analog dac poti


![image.png](image.png)

## Basic-Example:
```
{
    "type": "udpoti",
    "pins": {
        "updown": {
            "pin": "0"
        },
        "increment": {
            "pin": "1"
        }
    }
}
```

## Pins:
*FPGA-pins*
### updown:

 * direction: output

### increment:

 * direction: output


## Options:
*user-options*
### resolution:
number of steps from min to maximum value

 * type: int
 * min: 0
 * max: 255
 * default: 100

### frequency:
interface frequency

 * type: int
 * min: 0
 * max: 100000
 * default: 100
 * unit: Hz

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

 * size: 32 bit
 * direction: output


## Full-Example:
```
{
    "type": "udpoti",
    "resolution": 100,
    "frequency": 100,
    "name": "",
    "pins": {
        "updown": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "increment": {
            "pin": "1",
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
 * [udpoti.v](udpoti.v)
