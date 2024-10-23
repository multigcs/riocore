# rcservo
**rc-servo output**

to control rc-servos, usable as joint or as variable/analog output in LinuxCNC

Keywords: joint rcservo


![image.png](image.png)

## Basic-Example:
```
{
    "type": "rcservo",
    "pins": {
        "pwm": {
            "pin": "0"
        }
    }
}
```

## Pins:
*FPGA-pins*
### pwm:

 * direction: output


## Options:
*user-options*
### frequency:
update frequency

 * type: int
 * min: 20
 * max: 150
 * default: 100

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
### position:
absolute position (-100 = 1ms / 100 = 2ms)

 * type: float
 * direction: output
 * min: -100.0
 * max: 100.0

### enable:

 * type: bit
 * direction: output


## Interfaces:
*transport layer*
### position:

 * size: 32 bit
 * direction: output

### enable:

 * size: 1 bit
 * direction: output


## Full-Example:
```
{
    "type": "rcservo",
    "frequency": 100,
    "name": "",
    "axis": "",
    "is_joint": false,
    "pins": {
        "pwm": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {
        "position": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "position",
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
 * [rcservo.v](rcservo.v)
