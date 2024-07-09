# spi
spi interface for host comunication

for direct connections to Raspberry-PI or over UDB2SPI-Bridges

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
### mosi:

 * direction: input
 * pullup: False

### miso:

 * direction: output
 * pullup: False

### sclk:

 * direction: input
 * pullup: False

### sel:

 * direction: input
 * pullup: False


## Options:
### name:
name of this plugin instance

 * type: str
 * default: None


## Signals:


## Interfaces:


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
 * spi.v
