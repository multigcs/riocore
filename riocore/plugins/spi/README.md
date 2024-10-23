# spi
**spi interface for host comunication**

for direct connections to Raspberry-PI or over UDB2SPI-Bridges

Keywords: interface spi raspberry rpi


![image.png](image.png)

## Basic-Example:
```
{
    "type": "spi",
    "pins": {
        "mosi": {
            "pin": "0"
        },
        "miso": {
            "pin": "1"
        },
        "sclk": {
            "pin": "2"
        },
        "sel": {
            "pin": "3"
        }
    }
}
```

## Pins:
*FPGA-pins*
### mosi:

 * direction: input

### miso:

 * direction: output

### sclk:

 * direction: input

### sel:

 * direction: input


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Full-Example:
```
{
    "type": "spi",
    "name": "",
    "pins": {
        "mosi": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "debounce"
                }
            ]
        },
        "miso": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "sclk": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "sel": {
            "pin": "3",
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

## Verilogs:
 * [spi.v](spi.v)
