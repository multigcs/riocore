# blink

<img align="right" width="320" src="image.png">

**blinking output pin**

outputs a fixed frequency / was used to indicate that the FPGA is runing / no control signals

Keywords: led blinking

## Pins:
*FPGA-pins*
### led:

 * direction: output


## Options:
*user-options*
### frequency:
blink frequency in Hz

 * type: float
 * default: 1.0
 * unit: Hz

### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "blink",
    "pins": {
        "led": {
            "pin": "0"
        }
    }
}
```

## Full-Example:
```
{
    "type": "blink",
    "frequency": 1.0,
    "name": "",
    "pins": {
        "led": {
            "pin": "0",
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
 * [blink.v](blink.v)
