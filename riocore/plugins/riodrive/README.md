# riodrive

<img align="right" width="320" src="image.png">

**to control a riodrive via can-bus**

riodrive is a fork of odrive (v3.6)

Keywords: canbus odrive bldc brushless servo

URL: https://github.com/multigcs/riodrive

## Pins:
*FPGA-pins*
### tx:

 * direction: output

### rx:

 * direction: input


## Options:
*user-options*
### baud:
can-bus baud rate

 * type: int
 * min: 300
 * max: 10000000
 * default: 500000
 * unit: bit/s

### interval:
update interval / normaly it should be 1khz, but with sync=true, this is a good default

 * type: int
 * min: 100
 * max: 10000
 * default: 400
 * unit: Hz

### sync:
in sync with interface (eg UDP)

 * type: bool
 * default: True

### error:
trigger error on connection/drive problems

 * type: bool
 * default: True

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
### power:

 * type: float
 * direction: input
 * unit: W

### temp:

 * type: float
 * direction: input
 * unit: °C

### state:

 * type: float
 * direction: input
 * unit: 

### traj:

 * type: bit
 * direction: input
 * unit: 

### mot:

 * type: bit
 * direction: input
 * unit: 

### enc:

 * type: bit
 * direction: input
 * unit: 

### ctrl:

 * type: bit
 * direction: input
 * unit: 

### position:

 * type: float
 * direction: input
 * unit: 

### velocity:

 * type: float
 * direction: output
 * min: -100
 * max: 100
 * unit: 

### enable:

 * type: bit
 * direction: output

### error:

 * type: bit
 * direction: input


## Interfaces:
*transport layer*
### power:

 * size: 16 bit
 * direction: input

### temp:

 * size: 8 bit
 * direction: input

### state:

 * size: 4 bit
 * direction: input

### traj:

 * size: 1 bit
 * direction: input

### mot:

 * size: 1 bit
 * direction: input

### enc:

 * size: 1 bit
 * direction: input

### ctrl:

 * size: 1 bit
 * direction: input

### position:

 * size: 32 bit
 * direction: input

### velocity:

 * size: 32 bit
 * direction: output

### enable:

 * size: 1 bit
 * direction: output

### error:

 * size: 1 bit
 * direction: input


## Basic-Example:
```
{
    "type": "riodrive",
    "pins": {
        "tx": {
            "pin": "0"
        },
        "rx": {
            "pin": "1"
        }
    }
}
```

## Full-Example:
```
{
    "type": "riodrive",
    "baud": 500000,
    "interval": 400,
    "sync": true,
    "error": true,
    "name": "",
    "axis": "",
    "is_joint": false,
    "pins": {
        "tx": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "rx": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {
        "power": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "power",
                "section": "inputs",
                "type": "meter"
            }
        },
        "temp": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "temp",
                "section": "inputs",
                "type": "meter"
            }
        },
        "state": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "state",
                "section": "inputs",
                "type": "meter"
            }
        },
        "traj": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "traj",
                "section": "inputs",
                "type": "led"
            }
        },
        "mot": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "mot",
                "section": "inputs",
                "type": "led"
            }
        },
        "enc": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "enc",
                "section": "inputs",
                "type": "led"
            }
        },
        "ctrl": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "ctrl",
                "section": "inputs",
                "type": "led"
            }
        },
        "position": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "position",
                "section": "inputs",
                "type": "meter"
            }
        },
        "velocity": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "velocity",
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
        },
        "error": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "display": {
                "title": "error",
                "section": "inputs",
                "type": "led"
            }
        }
    }
}
```

## Verilogs:
 * [riodrive.v](riodrive.v)
 * [canbus_tx.v](canbus_tx.v)
 * [canbus_rx.v](canbus_rx.v)
