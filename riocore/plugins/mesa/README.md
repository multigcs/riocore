# mesa

<img align="right" width="320" src="image.png">

**mesa**

mesa

Keywords: stepgen pwm mesa board hm2

URL: https://github.com/atrex66/stepper-mesa

## Pins:
*FPGA-pins*
### P1:P1:

 * direction: output

### P1:P14:

 * direction: all

### P1:P2:

 * direction: output

### P1:P15:

 * direction: all

### P1:P3:

 * direction: output

### P1:P16:

 * direction: all

### P1:P4:

 * direction: output

### P1:P17:

 * direction: all

### P1:P5:

 * direction: output

### P1:P6:

 * direction: output

### P1:P7:

 * direction: output

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

### P2:P1:

 * direction: all

### P2:P14:

 * direction: all

### P2:P2:

 * direction: all

### P2:P15:

 * direction: all

### P2:P3:

 * direction: all

### P2:P16:

 * direction: all

### P2:P4:

 * direction: all

### P2:P17:

 * direction: all

### P2:P5:

 * direction: all

### P2:P6:

 * direction: all

### P2:P7:

 * direction: all

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

### P7:P1:

 * direction: all

### P7:P14:

 * direction: all

### P7:P2:

 * direction: all

### P7:P15:

 * direction: all

### P7:P3:

 * direction: all

### P7:P16:

 * direction: all

### P7:P4:

 * direction: all

### P7:P17:

 * direction: all

### P7:P5:

 * direction: all

### P7:P6:

 * direction: all

### P7:P7:

 * direction: all

### P7:P8:

 * direction: all

### P7:P9:

 * direction: all

### P7:P10:

 * direction: all

### P7:P11:

 * direction: all

### P7:P12:

 * direction: all

### P7:P13:

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

### board:
card configuration

 * type: select
 * default: 7c81_5abobx3d

### spiclk_rate:
spiclk_rate

 * type: int
 * min: 10000
 * max: 1000000
 * default: 21250

### num_pwms:
number of pwm's

 * type: int
 * min: 0
 * max: 10
 * default: 1

### num_encoders:
number of encoder's

 * type: int
 * min: 0
 * max: 10
 * default: 0

### num_stepgens:
number of stepgen's

 * type: int
 * min: 0
 * max: 10
 * default: 3

### num_serials:
number of serial's

 * type: int
 * min: 0
 * max: 10
 * default: 0


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "mesa",
    "pins": {
        "P1:P1": {
            "pin": "0"
        },
        "P1:P14": {
            "pin": "1"
        },
        "P1:P2": {
            "pin": "2"
        },
        "P1:P15": {
            "pin": "3"
        },
        "P1:P3": {
            "pin": "4"
        },
        "P1:P16": {
            "pin": "5"
        },
        "P1:P4": {
            "pin": "6"
        },
        "P1:P17": {
            "pin": "7"
        },
        "P1:P5": {
            "pin": "8"
        },
        "P1:P6": {
            "pin": "9"
        },
        "P1:P7": {
            "pin": "10"
        },
        "P1:P8": {
            "pin": "11"
        },
        "P1:P9": {
            "pin": "12"
        },
        "P1:P10": {
            "pin": "13"
        },
        "P1:P11": {
            "pin": "14"
        },
        "P1:P12": {
            "pin": "15"
        },
        "P1:P13": {
            "pin": "16"
        },
        "P2:P1": {
            "pin": "17"
        },
        "P2:P14": {
            "pin": "18"
        },
        "P2:P2": {
            "pin": "19"
        },
        "P2:P15": {
            "pin": "20"
        },
        "P2:P3": {
            "pin": "21"
        },
        "P2:P16": {
            "pin": "22"
        },
        "P2:P4": {
            "pin": "23"
        },
        "P2:P17": {
            "pin": "24"
        },
        "P2:P5": {
            "pin": "25"
        },
        "P2:P6": {
            "pin": "26"
        },
        "P2:P7": {
            "pin": "27"
        },
        "P2:P8": {
            "pin": "28"
        },
        "P2:P9": {
            "pin": "29"
        },
        "P2:P10": {
            "pin": "30"
        },
        "P2:P11": {
            "pin": "31"
        },
        "P2:P12": {
            "pin": "32"
        },
        "P2:P13": {
            "pin": "33"
        },
        "P7:P1": {
            "pin": "34"
        },
        "P7:P14": {
            "pin": "35"
        },
        "P7:P2": {
            "pin": "36"
        },
        "P7:P15": {
            "pin": "37"
        },
        "P7:P3": {
            "pin": "38"
        },
        "P7:P16": {
            "pin": "39"
        },
        "P7:P4": {
            "pin": "40"
        },
        "P7:P17": {
            "pin": "41"
        },
        "P7:P5": {
            "pin": "42"
        },
        "P7:P6": {
            "pin": "43"
        },
        "P7:P7": {
            "pin": "44"
        },
        "P7:P8": {
            "pin": "45"
        },
        "P7:P9": {
            "pin": "46"
        },
        "P7:P10": {
            "pin": "47"
        },
        "P7:P11": {
            "pin": "48"
        },
        "P7:P12": {
            "pin": "49"
        },
        "P7:P13": {
            "pin": "50"
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
    "board": "7c81_5abobx3d",
    "spiclk_rate": 21250,
    "num_pwms": 1,
    "num_encoders": 0,
    "num_stepgens": 3,
    "num_serials": 0,
    "pins": {
        "P1:P1": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P14": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P2": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P15": {
            "pin": "3",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P3": {
            "pin": "4",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P16": {
            "pin": "5",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P4": {
            "pin": "6",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P17": {
            "pin": "7",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P5": {
            "pin": "8",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P6": {
            "pin": "9",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P7": {
            "pin": "10",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P8": {
            "pin": "11",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P9": {
            "pin": "12",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P10": {
            "pin": "13",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P11": {
            "pin": "14",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P12": {
            "pin": "15",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P13": {
            "pin": "16",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P1": {
            "pin": "17",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P14": {
            "pin": "18",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P2": {
            "pin": "19",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P15": {
            "pin": "20",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P3": {
            "pin": "21",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P16": {
            "pin": "22",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P4": {
            "pin": "23",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P17": {
            "pin": "24",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P5": {
            "pin": "25",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P6": {
            "pin": "26",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P7": {
            "pin": "27",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P8": {
            "pin": "28",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P9": {
            "pin": "29",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P10": {
            "pin": "30",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P11": {
            "pin": "31",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P12": {
            "pin": "32",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P13": {
            "pin": "33",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P1": {
            "pin": "34",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P14": {
            "pin": "35",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P2": {
            "pin": "36",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P15": {
            "pin": "37",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P3": {
            "pin": "38",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P16": {
            "pin": "39",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P4": {
            "pin": "40",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P17": {
            "pin": "41",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P5": {
            "pin": "42",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P6": {
            "pin": "43",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P7": {
            "pin": "44",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P8": {
            "pin": "45",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P9": {
            "pin": "46",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P10": {
            "pin": "47",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P11": {
            "pin": "48",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P12": {
            "pin": "49",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P13": {
            "pin": "50",
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
