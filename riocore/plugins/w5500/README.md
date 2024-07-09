# w5500
**udp interface for host comunication - experimental**

w5500 driver for the interface communication over UDP

## Basic-Example:
```
{
    "type": "w5500",
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

 * direction: output
 * pullup: False

### miso:

 * direction: input
 * pullup: False

### sclk:

 * direction: output
 * pullup: False

### sel:

 * direction: output
 * pullup: False


## Options:
### mac:
MAC-Address

 * type: str
 * default: AA:AF:FA:CC:E3:1C

### ip:
IP-Address

 * type: str
 * default: 192.168.10.194

### port:
UDP-Port

 * type: int
 * default: 2390

### name:
name of this plugin instance

 * type: str
 * default: None


## Signals:


## Interfaces:


## Full-Example:
```
{
    "type": "w5500",
    "mac": "AA:AF:FA:CC:E3:1C",
    "ip": "192.168.10.194",
    "port": 2390,
    "name": "",
    "pins": {
        "mosi": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "miso": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "debounce"
                },
                {
                    "type": "invert"
                }
            ]
        },
        "sclk": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "sel": {
            "pin": "3",
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
 * w5500.v
