# pdmout
**pdm output**

to analog values via sigma-delta modulator

Keywords: joint dcservo acservo 10v 5v dac analog sigma-delta pdm


![image.png](image.png)

## Basic-Example:
```
{
    "type": "pdmout",
    "pins": {
        "pdm": {
            "pin": "0"
        },
        "en": {
            "pin": "1"
        }
    }
}
```

## Pins:
*FPGA-pins*
### pdm:

 * direction: output

### en:

 * direction: output
 * optional: True


## Options:
*user-options*
### resolution:
PDM Resolution

 * type: int
 * min: 8
 * max: 32
 * default: 16
 * unit: bit

### name:
name of this plugin instance

 * type: str
 * default: 

### axis:
axis name (X,Y,Z,...)

 * type: select
 * default: None

### is_joint:
configure as joint

 * type: bool
 * default: False


## Signals:
*signals/pins in LinuxCNC*
### value:

 * type: float
 * direction: output
 * min: 0
 * max: 100
 * unit: %

### enable:

 * type: bit
 * direction: output


## Interfaces:
*transport layer*
### value:

 * size: 16 bit
 * direction: output

### enable:

 * size: 1 bit
 * direction: output


## Full-Example:
```
{
    "type": "pdmout",
    "resolution": 16,
    "name": "",
    "axis": "",
    "is_joint": false,
    "pins": {
        "pdm": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "en": {
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
        },
        "enable": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "enable",
                "section": "outputs",
                "type": "checkbox"
            }
        }
    }
}
```

## Verilogs:
 * [pdmout.v](pdmout.v)
