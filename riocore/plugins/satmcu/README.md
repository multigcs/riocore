# satmcu

<img align="right" width="320" src="image.png">

**mcu based satellite**

mcu based satellite connected via RS422

## Pins:
*FPGA-pins*
### SAT:

 * direction: output
 * optional: True

### IO:2:

 * direction: all

### IO:3:

 * direction: all

### IO:4:

 * direction: all

### IO:5:

 * direction: all

### IO:6:

 * direction: all

### IO:7:

 * direction: all

### IO:8:

 * direction: all

### IO:9:

 * direction: all

### IO:10:

 * direction: all

### IO:11:

 * direction: all

### IO:12:

 * direction: all

### IO:13:

 * direction: all

### IO:14:

 * direction: all

### IO:15:

 * direction: all

### IO:28:

 * direction: all

### IO:27:

 * direction: all

### IO:26:

 * direction: all

### IO:22:

 * direction: all

### IO:21:

 * direction: all

### IO:20:

 * direction: all

### IO:19:

 * direction: all

### IO:18:

 * direction: all

### IO:17:

 * direction: all

### IO:16:

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
 * default: pico

### baud:
serial baud rate

 * type: int
 * min: 9600
 * max: 10000000
 * default: 1000000
 * unit: bit/s

### upload_port:
debug-port

 * type: str
 * default: /dev/ttyACM0


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "satmcu",
    "pins": {
        "SAT": {
            "pin": "0"
        },
        "IO:2": {
            "pin": "1"
        },
        "IO:3": {
            "pin": "2"
        },
        "IO:4": {
            "pin": "3"
        },
        "IO:5": {
            "pin": "4"
        },
        "IO:6": {
            "pin": "5"
        },
        "IO:7": {
            "pin": "6"
        },
        "IO:8": {
            "pin": "7"
        },
        "IO:9": {
            "pin": "8"
        },
        "IO:10": {
            "pin": "9"
        },
        "IO:11": {
            "pin": "10"
        },
        "IO:12": {
            "pin": "11"
        },
        "IO:13": {
            "pin": "12"
        },
        "IO:14": {
            "pin": "13"
        },
        "IO:15": {
            "pin": "14"
        },
        "IO:28": {
            "pin": "15"
        },
        "IO:27": {
            "pin": "16"
        },
        "IO:26": {
            "pin": "17"
        },
        "IO:22": {
            "pin": "18"
        },
        "IO:21": {
            "pin": "19"
        },
        "IO:20": {
            "pin": "20"
        },
        "IO:19": {
            "pin": "21"
        },
        "IO:18": {
            "pin": "22"
        },
        "IO:17": {
            "pin": "23"
        },
        "IO:16": {
            "pin": "24"
        }
    }
}
```

## Full-Example:
```
{
    "type": "satmcu",
    "name": "",
    "node_type": "pico",
    "baud": 1000000,
    "upload_port": "/dev/ttyACM0",
    "pins": {
        "SAT": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:2": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:3": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:4": {
            "pin": "3",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:5": {
            "pin": "4",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:6": {
            "pin": "5",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:7": {
            "pin": "6",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:8": {
            "pin": "7",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:9": {
            "pin": "8",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:10": {
            "pin": "9",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:11": {
            "pin": "10",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:12": {
            "pin": "11",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:13": {
            "pin": "12",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:14": {
            "pin": "13",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:15": {
            "pin": "14",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:28": {
            "pin": "15",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:27": {
            "pin": "16",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:26": {
            "pin": "17",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:22": {
            "pin": "18",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:21": {
            "pin": "19",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:20": {
            "pin": "20",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:19": {
            "pin": "21",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:18": {
            "pin": "22",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:17": {
            "pin": "23",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "IO:16": {
            "pin": "24",
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

## Verilogs:
 * [satmcu.v](satmcu.v)
 * [uart_baud.v](uart_baud.v)
 * [uart_rx.v](uart_rx.v)
 * [uart_tx.v](uart_tx.v)
