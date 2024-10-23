# w5500
**udp interface for host comunication**

w5500 driver for the interface communication over UDP

Keywords: ethernet network udp interface


![image.png](image.png)

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
        },
        "rst": {
            "pin": "4"
        },
        "intr": {
            "pin": "5"
        }
    }
}
```

## Pins:
*FPGA-pins*
### mosi:

 * direction: output

### miso:

 * direction: input

### sclk:

 * direction: output

### sel:

 * direction: output

### rst:

 * direction: output
 * optional: True

### intr:

 * direction: input
 * optional: True


## Options:
*user-options*
### mac:
MAC-Address

 * type: str
 * default: AA:AF:FA:CC:E3:1C

### ip:
IP-Address

 * type: str
 * default: 192.168.10.194

### mask:
Network-Mask

 * type: str
 * default: 255.255.255.0

### gw:
Gateway IP-Address

 * type: str
 * default: 192.168.10.1

### port:
UDP-Port

 * type: int
 * default: 2390

### speed:
SPI clock

 * type: int
 * default: 10000000

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
    "type": "w5500",
    "mac": "AA:AF:FA:CC:E3:1C",
    "ip": "192.168.10.194",
    "mask": "255.255.255.0",
    "gw": "192.168.10.1",
    "port": 2390,
    "speed": 10000000,
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
        },
        "rst": {
            "pin": "4",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "intr": {
            "pin": "5",
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
 * [w5500.v](w5500.v)
