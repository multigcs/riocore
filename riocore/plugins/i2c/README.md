# i2c

<img align="right" width="320" src="image.png">

**i2c plugin**

to read and write values (analog/digital) via modbus, also supports hy_vfd spindles

Keywords: modbus rtu vfd spindle expansion analog digital

URL: https://www.modbustools.com/modbus.html#function16

## Pins:
*FPGA-pins*
### sda:

 * direction: inout

### scl:

 * direction: output

### BUS:IO:

 * direction: output


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


## Basic-Example:
```
{
    "type": "i2c",
    "pins": {
        "sda": {
            "pin": "0"
        },
        "scl": {
            "pin": "1"
        },
        "BUS:IO": {
            "pin": "2"
        }
    }
}
```

## Full-Example:
```
{
    "type": "i2c",
    "name": "",
    "pins": {
        "sda": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "scl": {
            "pin": "1",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "BUS:IO": {
            "pin": "2",
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
 * [i2c_master.v](i2c_master.v)
