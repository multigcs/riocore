# remora

<img align="right" width="320" src="image.png">

**remora**

remora

Keywords: stepgen pwm remora board pico w5500

URL: https://github.com/scottalford75/Remora-RP2040-W5500

## Pins:
*FPGA-pins*
### IO:GP15:

 * direction: all

### IO:GP14:

 * direction: all

### IO:GP13:

 * direction: all

### IO:GP12:

 * direction: all

### IO:GP11:

 * direction: all

### IO:GP10:

 * direction: all

### IO:GP9:

 * direction: all

### IO:GP8:

 * direction: all

### IO:GP7:

 * direction: all

### IO:GP6:

 * direction: all

### IO:GP5:

 * direction: all

### IO:GP4:

 * direction: all

### IO:GP3:

 * direction: all

### IO:GP2:

 * direction: all

### IO:GP1:

 * direction: all

### IO:GP0:

 * direction: all

### IO:GP22:

 * direction: all

### IO:GP26:

 * direction: all

### IO:GP27:

 * direction: all

### IO:GP28:

 * direction: all


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### node_type:
board type

 * type: select
 * default: board

### board:
board type

 * type: select
 * default: W5500-EVB-Pico

### mac:
MAC-Address

 * type: str
 * default: 00:08:DC:12:34:56

### ip:
IP-Address

 * type: str
 * default: 192.168.0.177

### mask:
Network-Mask

 * type: str
 * default: 255.255.255.0

### gw:
Gateway IP-Address

 * type: str
 * default: 192.168.10.1

### port:
UDP-Port

 * type: int
 * default: 8888


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "remora",
    "pins": {
        "IO:GP15": {
            "pin": "0"
        },
        "IO:GP14": {
            "pin": "1"
        },
        "IO:GP13": {
            "pin": "2"
        },
        "IO:GP12": {
            "pin": "3"
        },
        "IO:GP11": {
            "pin": "4"
        },
        "IO:GP10": {
            "pin": "5"
        },
        "IO:GP9": {
            "pin": "6"
        },
        "IO:GP8": {
            "pin": "7"
        },
        "IO:GP7": {
            "pin": "8"
        },
        "IO:GP6": {
            "pin": "9"
        },
        "IO:GP5": {
            "pin": "10"
        },
        "IO:GP4": {
            "pin": "11"
        },
        "IO:GP3": {
            "pin": "12"
        },
        "IO:GP2": {
            "pin": "13"
        },
        "IO:GP1": {
            "pin": "14"
        },
        "IO:GP0": {
            "pin": "15"
        },
        "IO:GP22": {
            "pin": "16"
        },
        "IO:GP26": {
            "pin": "17"
        },
        "IO:GP27": {
            "pin": "18"
        },
        "IO:GP28": {
            "pin": "19"
        }
    }
}
```

## Full-Example:
```
{
    "type": "remora",
    "name": "",
    "node_type": "board",
    "board": "W5500-EVB-Pico",
    "mac": "00:08:DC:12:34:56",
    "ip": "192.168.0.177",
    "mask": "255.255.255.0",
    "gw": "192.168.10.1",
    "port": 8888,
    "pins": {
        "IO:GP15": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:GP14": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:GP13": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:GP12": {
            "pin": "3",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:GP11": {
            "pin": "4",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:GP10": {
            "pin": "5",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:GP9": {
            "pin": "6",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:GP8": {
            "pin": "7",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:GP7": {
            "pin": "8",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:GP6": {
            "pin": "9",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:GP5": {
            "pin": "10",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:GP4": {
            "pin": "11",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:GP3": {
            "pin": "12",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:GP2": {
            "pin": "13",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:GP1": {
            "pin": "14",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:GP0": {
            "pin": "15",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:GP22": {
            "pin": "16",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:GP26": {
            "pin": "17",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:GP27": {
            "pin": "18",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:GP28": {
            "pin": "19",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {}
}
```
