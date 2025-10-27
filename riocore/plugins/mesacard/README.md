# mesacard

<img align="right" width="320" src="image.png">

**mesacard**

mesacard

Keywords: mesacard gpio

## Pins:
*FPGA-pins*
### P1:P1:

 * direction: output

### P1:P2:

 * direction: all

### P1:P3:

 * direction: output

### P1:P4:

 * direction: all

### P1:P5:

 * direction: output

### P1:P6:

 * direction: all

### P1:P7:

 * direction: output

### P1:P8:

 * direction: all

### P1:P9:

 * direction: output

### P1:P10:

 * direction: output

### P1:P11:

 * direction: output

### P1:P12:

 * direction: output

### P1:P13:

 * direction: output

### P1:P14:

 * direction: all

### P1:P15:

 * direction: input

### P1:P16:

 * direction: input

### P1:P17:

 * direction: input

### P2:P1:

 * direction: output

### P2:P2:

 * direction: all

### P2:P3:

 * direction: output

### P2:P4:

 * direction: all

### P2:P5:

 * direction: output

### P2:P6:

 * direction: all

### P2:P7:

 * direction: output

### P2:P8:

 * direction: all

### P2:P9:

 * direction: output

### P2:P10:

 * direction: output

### P2:P11:

 * direction: output

### P2:P12:

 * direction: output

### P2:P13:

 * direction: output

### P2:P14:

 * direction: all

### P2:P15:

 * direction: input

### P2:P16:

 * direction: input

### P2:P17:

 * direction: input

### P7:P1:

 * direction: output

### P7:P2:

 * direction: all

### P7:P3:

 * direction: output

### P7:P4:

 * direction: all

### P7:P5:

 * direction: output

### P7:P6:

 * direction: all

### P7:P7:

 * direction: output

### P7:P8:

 * direction: all

### P7:P9:

 * direction: output

### P7:P10:

 * direction: output

### P7:P11:

 * direction: output

### P7:P12:

 * direction: output

### P7:P13:

 * direction: output

### P7:P14:

 * direction: all

### P7:P15:

 * direction: input

### P7:P16:

 * direction: input

### P7:P17:

 * direction: input


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### cardtype:
card configuration

 * type: select
 * default: 7c81_5abobx3d


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "mesacard",
    "pins": {
        "P1:P1": {
            "pin": "0"
        },
        "P1:P2": {
            "pin": "1"
        },
        "P1:P3": {
            "pin": "2"
        },
        "P1:P4": {
            "pin": "3"
        },
        "P1:P5": {
            "pin": "4"
        },
        "P1:P6": {
            "pin": "5"
        },
        "P1:P7": {
            "pin": "6"
        },
        "P1:P8": {
            "pin": "7"
        },
        "P1:P9": {
            "pin": "8"
        },
        "P1:P10": {
            "pin": "9"
        },
        "P1:P11": {
            "pin": "10"
        },
        "P1:P12": {
            "pin": "11"
        },
        "P1:P13": {
            "pin": "12"
        },
        "P1:P14": {
            "pin": "13"
        },
        "P1:P15": {
            "pin": "14"
        },
        "P1:P16": {
            "pin": "15"
        },
        "P1:P17": {
            "pin": "16"
        },
        "P2:P1": {
            "pin": "17"
        },
        "P2:P2": {
            "pin": "18"
        },
        "P2:P3": {
            "pin": "19"
        },
        "P2:P4": {
            "pin": "20"
        },
        "P2:P5": {
            "pin": "21"
        },
        "P2:P6": {
            "pin": "22"
        },
        "P2:P7": {
            "pin": "23"
        },
        "P2:P8": {
            "pin": "24"
        },
        "P2:P9": {
            "pin": "25"
        },
        "P2:P10": {
            "pin": "26"
        },
        "P2:P11": {
            "pin": "27"
        },
        "P2:P12": {
            "pin": "28"
        },
        "P2:P13": {
            "pin": "29"
        },
        "P2:P14": {
            "pin": "30"
        },
        "P2:P15": {
            "pin": "31"
        },
        "P2:P16": {
            "pin": "32"
        },
        "P2:P17": {
            "pin": "33"
        },
        "P7:P1": {
            "pin": "34"
        },
        "P7:P2": {
            "pin": "35"
        },
        "P7:P3": {
            "pin": "36"
        },
        "P7:P4": {
            "pin": "37"
        },
        "P7:P5": {
            "pin": "38"
        },
        "P7:P6": {
            "pin": "39"
        },
        "P7:P7": {
            "pin": "40"
        },
        "P7:P8": {
            "pin": "41"
        },
        "P7:P9": {
            "pin": "42"
        },
        "P7:P10": {
            "pin": "43"
        },
        "P7:P11": {
            "pin": "44"
        },
        "P7:P12": {
            "pin": "45"
        },
        "P7:P13": {
            "pin": "46"
        },
        "P7:P14": {
            "pin": "47"
        },
        "P7:P15": {
            "pin": "48"
        },
        "P7:P16": {
            "pin": "49"
        },
        "P7:P17": {
            "pin": "50"
        }
    }
}
```

## Full-Example:
```
{
    "type": "mesacard",
    "name": "",
    "cardtype": "7c81_5abobx3d",
    "pins": {
        "P1:P1": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P2": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P3": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P4": {
            "pin": "3",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P5": {
            "pin": "4",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P6": {
            "pin": "5",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P7": {
            "pin": "6",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P8": {
            "pin": "7",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P9": {
            "pin": "8",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P10": {
            "pin": "9",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P11": {
            "pin": "10",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P12": {
            "pin": "11",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P13": {
            "pin": "12",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P14": {
            "pin": "13",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P15": {
            "pin": "14",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P16": {
            "pin": "15",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "P1:P17": {
            "pin": "16",
            "modifiers": [
                {
                    "type": "debounce"
                },
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
        "P2:P2": {
            "pin": "18",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P3": {
            "pin": "19",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P4": {
            "pin": "20",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P5": {
            "pin": "21",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P6": {
            "pin": "22",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P7": {
            "pin": "23",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P8": {
            "pin": "24",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P9": {
            "pin": "25",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P10": {
            "pin": "26",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P11": {
            "pin": "27",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P12": {
            "pin": "28",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P13": {
            "pin": "29",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P14": {
            "pin": "30",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P15": {
            "pin": "31",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P16": {
            "pin": "32",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "P2:P17": {
            "pin": "33",
            "modifiers": [
                {
                    "type": "debounce"
                },
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
        "P7:P2": {
            "pin": "35",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P3": {
            "pin": "36",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P4": {
            "pin": "37",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P5": {
            "pin": "38",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P6": {
            "pin": "39",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P7": {
            "pin": "40",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P8": {
            "pin": "41",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P9": {
            "pin": "42",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P10": {
            "pin": "43",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P11": {
            "pin": "44",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P12": {
            "pin": "45",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P13": {
            "pin": "46",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P14": {
            "pin": "47",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P15": {
            "pin": "48",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P16": {
            "pin": "49",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "P7:P17": {
            "pin": "50",
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
    "signals": {}
}
```
