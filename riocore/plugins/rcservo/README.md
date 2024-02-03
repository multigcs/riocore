# rcservo


rc-servo output

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
### pwm:

 * direction: output
 * pullup: False


## Options:
### frequency:
update frequency

 * type: int
 * min: 20
 * max: 150
 * default: 100

### name:
name of this plugin instance

 * type: str
 * default: None

### net:
target net in LinuxCNC

 * type: str
 * default: None

### axis:
axis name (X,Y,Z,...)

 * type: select
 * default: None

### is_joint:
configure as joint

 * type: bool
 * default: True


## Signals:
### position:
absolute position (-100 = 1ms / 100 = 2ms)

 * type: float
 * direction: output
 * min: -100
 * max: 100

### enable:

 * type: bit
 * direction: output


## Interfaces:
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
    "net": "",
    "axis": "",
    "is_joint": true,
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
 * rcservo.v
