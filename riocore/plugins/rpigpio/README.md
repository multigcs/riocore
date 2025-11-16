# rpigpio

<img align="right" width="320" src="image.png">

**gpio support**

gpio support for Raspberry PI4/5 and maybe other boards

gpio modes:
* rpi5: hal_gpio: gpioinfo shows GPIO7 for GPIO7
* rpi4: hal_gpio: gpioinfo shows SPI_CE1_N for GPIO7
* pi_gpio: hal_pi_gpio: no invert support, not for rpi5

Keywords: rpi gpio raspberry rpi4 rpi5

## Pins:
*FPGA-pins*
### GPIO:P3:

 * direction: all

### GPIO:P5:

 * direction: all

### GPIO:P7:

 * direction: all

### GPIO:P8:

 * direction: all

### GPIO:P10:

 * direction: all

### GPIO:P11:

 * direction: all

### GPIO:P12:

 * direction: all

### GPIO:P13:

 * direction: all

### GPIO:P15:

 * direction: all

### GPIO:P16:

 * direction: all

### GPIO:P18:

 * direction: all

### GPIO:P19:

 * direction: all

### GPIO:P21:

 * direction: all

### GPIO:P22:

 * direction: all

### GPIO:P23:

 * direction: all

### GPIO:P24:

 * direction: all

### GPIO:P26:

 * direction: all

### GPIO:P29:

 * direction: all

### GPIO:P31:

 * direction: all

### GPIO:P32:

 * direction: all

### GPIO:P33:

 * direction: all

### GPIO:P35:

 * direction: all

### GPIO:P36:

 * direction: all

### GPIO:P37:

 * direction: all

### GPIO:P38:

 * direction: all

### GPIO:P40:

 * direction: all


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### mode:
gpio mode (rpi5: gpioinfo shows GPIO7 / rpi4: gpioinfo shows SPI_CE1_N for GPIO7)

 * type: select
 * default: rpi5


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "rpigpio",
    "pins": {
        "GPIO:P3": {
            "pin": "0"
        },
        "GPIO:P5": {
            "pin": "1"
        },
        "GPIO:P7": {
            "pin": "2"
        },
        "GPIO:P8": {
            "pin": "3"
        },
        "GPIO:P10": {
            "pin": "4"
        },
        "GPIO:P11": {
            "pin": "5"
        },
        "GPIO:P12": {
            "pin": "6"
        },
        "GPIO:P13": {
            "pin": "7"
        },
        "GPIO:P15": {
            "pin": "8"
        },
        "GPIO:P16": {
            "pin": "9"
        },
        "GPIO:P18": {
            "pin": "10"
        },
        "GPIO:P19": {
            "pin": "11"
        },
        "GPIO:P21": {
            "pin": "12"
        },
        "GPIO:P22": {
            "pin": "13"
        },
        "GPIO:P23": {
            "pin": "14"
        },
        "GPIO:P24": {
            "pin": "15"
        },
        "GPIO:P26": {
            "pin": "16"
        },
        "GPIO:P29": {
            "pin": "17"
        },
        "GPIO:P31": {
            "pin": "18"
        },
        "GPIO:P32": {
            "pin": "19"
        },
        "GPIO:P33": {
            "pin": "20"
        },
        "GPIO:P35": {
            "pin": "21"
        },
        "GPIO:P36": {
            "pin": "22"
        },
        "GPIO:P37": {
            "pin": "23"
        },
        "GPIO:P38": {
            "pin": "24"
        },
        "GPIO:P40": {
            "pin": "25"
        }
    }
}
```

## Full-Example:
```
{
    "type": "rpigpio",
    "name": "",
    "mode": "rpi5",
    "pins": {
        "GPIO:P3": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P5": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P7": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P8": {
            "pin": "3",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P10": {
            "pin": "4",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P11": {
            "pin": "5",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P12": {
            "pin": "6",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P13": {
            "pin": "7",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P15": {
            "pin": "8",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P16": {
            "pin": "9",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P18": {
            "pin": "10",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P19": {
            "pin": "11",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P21": {
            "pin": "12",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P22": {
            "pin": "13",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P23": {
            "pin": "14",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P24": {
            "pin": "15",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P26": {
            "pin": "16",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P29": {
            "pin": "17",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P31": {
            "pin": "18",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P32": {
            "pin": "19",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P33": {
            "pin": "20",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P35": {
            "pin": "21",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P36": {
            "pin": "22",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P37": {
            "pin": "23",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P38": {
            "pin": "24",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "GPIO:P40": {
            "pin": "25",
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
