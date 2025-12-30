# fpga
**TangNano20K - GW2AR-18 devboard**

Keywords: TangNano20K board fpga gateware

## Pins:
*FPGA-pins*
### PIN:76:

 * direction: all
 * optional: True

### PIN:80:

 * direction: all
 * optional: True

### PIN:42:

 * direction: all
 * optional: True

### PIN:41:

 * direction: all
 * optional: True

### PIN:56:

 * direction: all
 * optional: True

### PIN:54:

 * direction: all
 * optional: True

### PIN:51:

 * direction: all
 * optional: True

### PIN:48:

 * direction: all
 * optional: True

### PIN:55:

 * direction: all
 * optional: True

### PIN:49:

 * direction: all
 * optional: True

### PIN:86:

 * direction: all
 * optional: True

### PIN:79:

 * direction: all
 * optional: True

### PIN:72:

 * direction: all
 * optional: True

### PIN:71:

 * direction: all
 * optional: True

### PIN:53:

 * direction: all
 * optional: True

### PIN:52:

 * direction: all
 * optional: True

### PIN:73:

 * direction: all
 * optional: True

### PIN:74:

 * direction: all
 * optional: True

### PIN:75:

 * direction: all
 * optional: True

### PIN:85:

 * direction: all
 * optional: True

### PIN:77:

 * direction: all
 * optional: True

### PIN:15:

 * direction: all
 * optional: True

### PIN:16:

 * direction: all
 * optional: True

### PIN:27:

 * direction: all
 * optional: True

### PIN:28:

 * direction: all
 * optional: True

### PIN:25:

 * direction: all
 * optional: True

### PIN:26:

 * direction: all
 * optional: True

### PIN:29:

 * direction: all
 * optional: True

### PIN:30:

 * direction: all
 * optional: True

### PIN:31:

 * direction: all
 * optional: True

### PIN:17:

 * direction: all
 * optional: True

### PIN:20:

 * direction: all
 * optional: True

### PIN:19:

 * direction: all
 * optional: True

### PIN:18:

 * direction: all
 * optional: True

### LED:L0:

 * direction: all
 * optional: True

### LED:L1:

 * direction: all
 * optional: True

### LED:L2:

 * direction: all
 * optional: True

### LED:L3:

 * direction: all
 * optional: True

### LED:L4:

 * direction: all
 * optional: True

### LED:L5:

 * direction: all
 * optional: True

### SW:S1:

 * direction: input
 * optional: True

### SW:S2:

 * direction: input
 * optional: True

### UART:RX:

 * direction: input
 * optional: True

### UART:TX:

 * direction: output
 * optional: True

### WLED:DATA:

 * direction: all
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
 * default: TangNano20K

### protocol:
communication protocol

 * type: select
 * default: SPI

### simulation:
simulation mode

 * type: bool
 * default: False

### toolchain:
used toolchain

 * type: select
 * default: gowin

### speed:
FPGA clock speed

 * type: int
 * min: 1000000
 * max: 500000000
 * default: 27000000
 * unit: Hz


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "fpga",
    "pins": {
        "PIN:76": {
            "pin": "0"
        },
        "PIN:80": {
            "pin": "1"
        },
        "PIN:42": {
            "pin": "2"
        },
        "PIN:41": {
            "pin": "3"
        },
        "PIN:56": {
            "pin": "4"
        },
        "PIN:54": {
            "pin": "5"
        },
        "PIN:51": {
            "pin": "6"
        },
        "PIN:48": {
            "pin": "7"
        },
        "PIN:55": {
            "pin": "8"
        },
        "PIN:49": {
            "pin": "9"
        },
        "PIN:86": {
            "pin": "10"
        },
        "PIN:79": {
            "pin": "11"
        },
        "PIN:72": {
            "pin": "12"
        },
        "PIN:71": {
            "pin": "13"
        },
        "PIN:53": {
            "pin": "14"
        },
        "PIN:52": {
            "pin": "15"
        },
        "PIN:73": {
            "pin": "16"
        },
        "PIN:74": {
            "pin": "17"
        },
        "PIN:75": {
            "pin": "18"
        },
        "PIN:85": {
            "pin": "19"
        },
        "PIN:77": {
            "pin": "20"
        },
        "PIN:15": {
            "pin": "21"
        },
        "PIN:16": {
            "pin": "22"
        },
        "PIN:27": {
            "pin": "23"
        },
        "PIN:28": {
            "pin": "24"
        },
        "PIN:25": {
            "pin": "25"
        },
        "PIN:26": {
            "pin": "26"
        },
        "PIN:29": {
            "pin": "27"
        },
        "PIN:30": {
            "pin": "28"
        },
        "PIN:31": {
            "pin": "29"
        },
        "PIN:17": {
            "pin": "30"
        },
        "PIN:20": {
            "pin": "31"
        },
        "PIN:19": {
            "pin": "32"
        },
        "PIN:18": {
            "pin": "33"
        },
        "LED:L0": {
            "pin": "34"
        },
        "LED:L1": {
            "pin": "35"
        },
        "LED:L2": {
            "pin": "36"
        },
        "LED:L3": {
            "pin": "37"
        },
        "LED:L4": {
            "pin": "38"
        },
        "LED:L5": {
            "pin": "39"
        },
        "SW:S1": {
            "pin": "40"
        },
        "SW:S2": {
            "pin": "41"
        },
        "UART:RX": {
            "pin": "42"
        },
        "UART:TX": {
            "pin": "43"
        },
        "WLED:DATA": {
            "pin": "44"
        }
    }
}
```

## Full-Example:
```
{
    "type": "fpga",
    "name": "",
    "node_type": "TangNano20K",
    "protocol": "SPI",
    "simulation": false,
    "toolchain": "gowin",
    "speed": 27000000,
    "pins": {
        "PIN:76": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:80": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:42": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:41": {
            "pin": "3",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:56": {
            "pin": "4",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:54": {
            "pin": "5",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:51": {
            "pin": "6",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:48": {
            "pin": "7",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:55": {
            "pin": "8",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:49": {
            "pin": "9",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:86": {
            "pin": "10",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:79": {
            "pin": "11",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:72": {
            "pin": "12",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:71": {
            "pin": "13",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:53": {
            "pin": "14",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:52": {
            "pin": "15",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:73": {
            "pin": "16",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:74": {
            "pin": "17",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:75": {
            "pin": "18",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:85": {
            "pin": "19",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:77": {
            "pin": "20",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:15": {
            "pin": "21",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:16": {
            "pin": "22",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:27": {
            "pin": "23",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:28": {
            "pin": "24",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:25": {
            "pin": "25",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:26": {
            "pin": "26",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:29": {
            "pin": "27",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:30": {
            "pin": "28",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:31": {
            "pin": "29",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:17": {
            "pin": "30",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:20": {
            "pin": "31",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:19": {
            "pin": "32",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "PIN:18": {
            "pin": "33",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "LED:L0": {
            "pin": "34",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "LED:L1": {
            "pin": "35",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "LED:L2": {
            "pin": "36",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "LED:L3": {
            "pin": "37",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "LED:L4": {
            "pin": "38",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "LED:L5": {
            "pin": "39",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "SW:S1": {
            "pin": "40",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "SW:S2": {
            "pin": "41",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "UART:RX": {
            "pin": "42",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "UART:TX": {
            "pin": "43",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "WLED:DATA": {
            "pin": "44",
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
