# mesa

<img align="right" width="320" src="image.png">

**support for mesa-cards with hm2 firmware**

## flashing 7i92
mesaflash --device 7i92 --addr 10.10.10.10  --write /mnt/data2/src/riocore/MI^C/mesact_firmware/7i92/7i92_G540x2D.bit

Keywords: stepgen pwm mesa board hm2

## Pins:
*FPGA-pins*
### P2:P1:

 * direction: output

### P2:P14:

 * direction: all

### P2:P2:

 * direction: output

### P2:P15:

 * direction: all

### P2:P3:

 * direction: output

### P2:P16:

 * direction: all

### P2:P4:

 * direction: output

### P2:P17:

 * direction: all

### P2:P5:

 * direction: output

### P2:P6:

 * direction: output

### P2:P7:

 * direction: output

### P2:P8:

 * direction: all

### P2:P9:

 * direction: all

### P2:P10:

 * direction: all

### P2:P11:

 * direction: all

### P2:P12:

 * direction: all

### P2:P13:

 * direction: all

### P1:P1:

 * direction: all

### P1:P14:

 * direction: all

### P1:P2:

 * direction: all

### P1:P15:

 * direction: all

### P1:P3:

 * direction: all

### P1:P16:

 * direction: all

### P1:P4:

 * direction: all

### P1:P17:

 * direction: all

### P1:P5:

 * direction: all

### P1:P6:

 * direction: all

### P1:P7:

 * direction: all

### P1:P8:

 * direction: all

### P1:P9:

 * direction: all

### P1:P10:

 * direction: all

### P1:P11:

 * direction: all

### P1:P12:

 * direction: all

### P1:P13:

 * direction: all


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### node_type:
instance type

 * type: select
 * default: board

### boardname:
card configuration

 * type: select
 * default: 7i92

### firmware:
firmware

 * type: select
 * default: DMMBOB1x2D

### num_pwms:
number of pwm's

 * type: int
 * min: 0
 * max: 2
 * default: 1

### num_encoders:
number of encoder's

 * type: int
 * min: 0
 * max: 2
 * default: 0

### num_stepgens:
number of stepgen's

 * type: int
 * min: 0
 * max: 8
 * default: 3

### num_serials:
number of serial's

 * type: int
 * min: 0
 * max: 0
 * default: 0

### ip_address:
ip address

 * type: str
 * default: 10.10.10.10


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "mesa",
    "pins": {
        "P2:P1": {
            "pin": "0"
        },
        "P2:P14": {
            "pin": "1"
        },
        "P2:P2": {
            "pin": "2"
        },
        "P2:P15": {
            "pin": "3"
        },
        "P2:P3": {
            "pin": "4"
        },
        "P2:P16": {
            "pin": "5"
        },
        "P2:P4": {
            "pin": "6"
        },
        "P2:P17": {
            "pin": "7"
        },
        "P2:P5": {
            "pin": "8"
        },
        "P2:P6": {
            "pin": "9"
        },
        "P2:P7": {
            "pin": "10"
        },
        "P2:P8": {
            "pin": "11"
        },
        "P2:P9": {
            "pin": "12"
        },
        "P2:P10": {
            "pin": "13"
        },
        "P2:P11": {
            "pin": "14"
        },
        "P2:P12": {
            "pin": "15"
        },
        "P2:P13": {
            "pin": "16"
        },
        "P1:P1": {
            "pin": "17"
        },
        "P1:P14": {
            "pin": "18"
        },
        "P1:P2": {
            "pin": "19"
        },
        "P1:P15": {
            "pin": "20"
        },
        "P1:P3": {
            "pin": "21"
        },
        "P1:P16": {
            "pin": "22"
        },
        "P1:P4": {
            "pin": "23"
        },
        "P1:P17": {
            "pin": "24"
        },
        "P1:P5": {
            "pin": "25"
        },
        "P1:P6": {
            "pin": "26"
        },
        "P1:P7": {
            "pin": "27"
        },
        "P1:P8": {
            "pin": "28"
        },
        "P1:P9": {
            "pin": "29"
        },
        "P1:P10": {
            "pin": "30"
        },
        "P1:P11": {
            "pin": "31"
        },
        "P1:P12": {
            "pin": "32"
        },
        "P1:P13": {
            "pin": "33"
        }
    }
}
```

## Full-Example:
```
{
    "type": "mesa",
    "name": "",
    "node_type": "board",
    "boardname": "7i92",
    "firmware": "DMMBOB1x2D",
    "num_pwms": 1,
    "num_encoders": 0,
    "num_stepgens": 3,
    "num_serials": 0,
    "ip_address": "10.10.10.10",
    "pins": {
        "P2:P1": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P14": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P2": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P15": {
            "pin": "3",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P3": {
            "pin": "4",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P16": {
            "pin": "5",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P4": {
            "pin": "6",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P17": {
            "pin": "7",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P5": {
            "pin": "8",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P6": {
            "pin": "9",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P7": {
            "pin": "10",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P8": {
            "pin": "11",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P9": {
            "pin": "12",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P10": {
            "pin": "13",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P11": {
            "pin": "14",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P12": {
            "pin": "15",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P13": {
            "pin": "16",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P1": {
            "pin": "17",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P14": {
            "pin": "18",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P2": {
            "pin": "19",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P15": {
            "pin": "20",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P3": {
            "pin": "21",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P16": {
            "pin": "22",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P4": {
            "pin": "23",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P17": {
            "pin": "24",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P5": {
            "pin": "25",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P6": {
            "pin": "26",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P7": {
            "pin": "27",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P8": {
            "pin": "28",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P9": {
            "pin": "29",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P10": {
            "pin": "30",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P11": {
            "pin": "31",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P12": {
            "pin": "32",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P13": {
            "pin": "33",
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
