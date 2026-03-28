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

### POWER:5V_1:

 * direction: none
 * optional: True

### POWER:5V_2:

 * direction: none
 * optional: True

### POWER:GND:

 * direction: none
 * optional: True

### POWER:F_GND_1:

 * direction: none
 * optional: True

### POWER:F_GND_2:

 * direction: none
 * optional: True

### POWER:F_24V:

 * direction: none
 * optional: True

### POWER:F_GND_3:

 * direction: none
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
        "POWER:5V_1": {
            "pin": "23"
        },
        "POWER:5V_2": {
            "pin": "24"
        },
        "POWER:GND": {
            "pin": "25"
        },
        "POWER:F_GND_1": {
            "pin": "26"
        },
        "POWER:F_GND_2": {
            "pin": "27"
        },
        "POWER:F_24V": {
            "pin": "28"
        },
        "POWER:F_GND_3": {
            "pin": "29"
        },
        "PWM:analog": {
            "pin": "30"
        },
        "PWM:digital": {
            "pin": "31"
        },
        "B:dir": {
            "pin": "32"
        },
        "B:step": {
            "pin": "33"
        },
        "ALL:en": {
            "pin": "34"
        },
        "A:dir": {
            "pin": "35"
        },
        "A:step": {
            "pin": "36"
        },
        "Z:dir": {
            "pin": "37"
        },
        "Z:step": {
            "pin": "38"
        },
        "Y:dir": {
            "pin": "39"
        },
        "Y:step": {
            "pin": "40"
        },
        "X:dir": {
            "pin": "41"
        },
        "X:step": {
            "pin": "42"
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
        "POWER:5V_1": {
            "pin": "23",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "POWER:5V_2": {
            "pin": "24",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "POWER:GND": {
            "pin": "25",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "POWER:F_GND_1": {
            "pin": "26",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "POWER:F_GND_2": {
            "pin": "27",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "POWER:F_24V": {
            "pin": "28",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "POWER:F_GND_3": {
            "pin": "29",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PWM:analog": {
            "pin": "30",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PWM:digital": {
            "pin": "31",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "B:dir": {
            "pin": "32",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "B:step": {
            "pin": "33",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "ALL:en": {
            "pin": "34",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "A:dir": {
            "pin": "35",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "A:step": {
            "pin": "36",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "Z:dir": {
            "pin": "37",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "Z:step": {
            "pin": "38",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "Y:dir": {
            "pin": "39",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "Y:step": {
            "pin": "40",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "X:dir": {
            "pin": "41",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "X:step": {
            "pin": "42",
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
