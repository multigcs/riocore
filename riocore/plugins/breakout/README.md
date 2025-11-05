# breakout

<img align="right" width="320" src="image.png">

**5Axis China-BOB**

## Pins:
*FPGA-pins*
### SLOT:P1:

 * direction: all
 * optional: True

### SLOT:P2:

 * direction: all
 * optional: True

### SLOT:P3:

 * direction: all
 * optional: True

### SLOT:P4:

 * direction: all
 * optional: True

### SLOT:P5:

 * direction: all
 * optional: True

### SLOT:P6:

 * direction: all
 * optional: True

### SLOT:P7:

 * direction: all
 * optional: True

### SLOT:P8:

 * direction: all
 * optional: True

### SLOT:P9:

 * direction: all
 * optional: True

### SLOT:P10:

 * direction: all
 * optional: True

### SLOT:P11:

 * direction: all
 * optional: True

### SLOT:P12:

 * direction: all
 * optional: True

### SLOT:P13:

 * direction: all
 * optional: True

### SLOT:P14:

 * direction: all
 * optional: True

### SLOT:P15:

 * direction: all
 * optional: True

### SLOT:P16:

 * direction: all
 * optional: True

### SLOT:P17:

 * direction: all
 * optional: True

### OPTO:in0:

 * direction: input
 * optional: True

### OPTO:in1:

 * direction: input
 * optional: True

### OPTO:in2:

 * direction: input
 * optional: True

### OPTO:in3:

 * direction: input
 * optional: True

### OPTO:in4:

 * direction: input
 * optional: True

### RELAIS:out:

 * direction: output
 * optional: True

### PWM:analog:

 * direction: output
 * optional: True

### PWM:digital:

 * direction: output
 * optional: True

### B:dir:

 * direction: output
 * optional: True

### B:step:

 * direction: output
 * optional: True

### ALL:en:

 * direction: output
 * optional: True

### A:dir:

 * direction: output
 * optional: True

### A:step:

 * direction: output
 * optional: True

### Z:dir:

 * direction: output
 * optional: True

### Z:step:

 * direction: output
 * optional: True

### Y:dir:

 * direction: output
 * optional: True

### Y:step:

 * direction: output
 * optional: True

### X:dir:

 * direction: output
 * optional: True

### X:step:

 * direction: output
 * optional: True


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### node_type:
board type

 * type: select
 * default: china-bob5x


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "breakout",
    "pins": {
        "SLOT:P1": {
            "pin": "0"
        },
        "SLOT:P2": {
            "pin": "1"
        },
        "SLOT:P3": {
            "pin": "2"
        },
        "SLOT:P4": {
            "pin": "3"
        },
        "SLOT:P5": {
            "pin": "4"
        },
        "SLOT:P6": {
            "pin": "5"
        },
        "SLOT:P7": {
            "pin": "6"
        },
        "SLOT:P8": {
            "pin": "7"
        },
        "SLOT:P9": {
            "pin": "8"
        },
        "SLOT:P10": {
            "pin": "9"
        },
        "SLOT:P11": {
            "pin": "10"
        },
        "SLOT:P12": {
            "pin": "11"
        },
        "SLOT:P13": {
            "pin": "12"
        },
        "SLOT:P14": {
            "pin": "13"
        },
        "SLOT:P15": {
            "pin": "14"
        },
        "SLOT:P16": {
            "pin": "15"
        },
        "SLOT:P17": {
            "pin": "16"
        },
        "OPTO:in0": {
            "pin": "17"
        },
        "OPTO:in1": {
            "pin": "18"
        },
        "OPTO:in2": {
            "pin": "19"
        },
        "OPTO:in3": {
            "pin": "20"
        },
        "OPTO:in4": {
            "pin": "21"
        },
        "RELAIS:out": {
            "pin": "22"
        },
        "PWM:analog": {
            "pin": "23"
        },
        "PWM:digital": {
            "pin": "24"
        },
        "B:dir": {
            "pin": "25"
        },
        "B:step": {
            "pin": "26"
        },
        "ALL:en": {
            "pin": "27"
        },
        "A:dir": {
            "pin": "28"
        },
        "A:step": {
            "pin": "29"
        },
        "Z:dir": {
            "pin": "30"
        },
        "Z:step": {
            "pin": "31"
        },
        "Y:dir": {
            "pin": "32"
        },
        "Y:step": {
            "pin": "33"
        },
        "X:dir": {
            "pin": "34"
        },
        "X:step": {
            "pin": "35"
        }
    }
}
```

## Full-Example:
```
{
    "type": "breakout",
    "name": "",
    "node_type": "china-bob5x",
    "pins": {
        "SLOT:P1": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "SLOT:P2": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "SLOT:P3": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "SLOT:P4": {
            "pin": "3",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "SLOT:P5": {
            "pin": "4",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "SLOT:P6": {
            "pin": "5",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "SLOT:P7": {
            "pin": "6",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "SLOT:P8": {
            "pin": "7",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "SLOT:P9": {
            "pin": "8",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "SLOT:P10": {
            "pin": "9",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "SLOT:P11": {
            "pin": "10",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "SLOT:P12": {
            "pin": "11",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "SLOT:P13": {
            "pin": "12",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "SLOT:P14": {
            "pin": "13",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "SLOT:P15": {
            "pin": "14",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "SLOT:P16": {
            "pin": "15",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "SLOT:P17": {
            "pin": "16",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "OPTO:in0": {
            "pin": "17",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "OPTO:in1": {
            "pin": "18",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "OPTO:in2": {
            "pin": "19",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "OPTO:in3": {
            "pin": "20",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "OPTO:in4": {
            "pin": "21",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "RELAIS:out": {
            "pin": "22",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PWM:analog": {
            "pin": "23",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PWM:digital": {
            "pin": "24",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "B:dir": {
            "pin": "25",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "B:step": {
            "pin": "26",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "ALL:en": {
            "pin": "27",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "A:dir": {
            "pin": "28",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "A:step": {
            "pin": "29",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "Z:dir": {
            "pin": "30",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "Z:step": {
            "pin": "31",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "Y:dir": {
            "pin": "32",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "Y:step": {
            "pin": "33",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "X:dir": {
            "pin": "34",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "X:step": {
            "pin": "35",
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
