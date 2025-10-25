# bitinsel
**input selector / demultiplexer**

input selector / demultiplexer with data pin

## Pins:
*FPGA-pins*
### bit_in:

 * direction: input

### addr0:

 * direction: output

### addr1:

 * direction: output

### addr2:

 * direction: output

### addr3:

 * direction: output


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### speed:
interface clock

 * type: int
 * min: 100000
 * max: 10000000
 * default: 1000000

### bits:
number of selector bits

 * type: int
 * min: 1
 * max: 32
 * default: 4
 * unit: bits


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Basic-Example:
```
{
    "type": "bitinsel",
    "pins": {
        "bit_in": {
            "pin": "0"
        },
        "addr0": {
            "pin": "1"
        },
        "addr1": {
            "pin": "2"
        },
        "addr2": {
            "pin": "3"
        },
        "addr3": {
            "pin": "4"
        }
    }
}
```

## Full-Example:
```
{
    "type": "bitinsel",
    "name": "",
    "speed": 1000000,
    "bits": 4,
    "pins": {
        "bit_in": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "debounce"
                }
            ]
        },
        "addr0": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "addr1": {
            "pin": "2",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "addr2": {
            "pin": "3",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "addr3": {
            "pin": "4",
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
 * [bitinsel.v](bitinsel.v)
