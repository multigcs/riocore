# rpii2c

<img align="right" width="320" src="image.png">

**gpio support over i2c port**

gpio support over i2c port

Keywords: ii2c gpio

## Pins:
*FPGA-pins*


## Options:
*user-options*
### device:
i2c device

 * type: select
 * default: pcf8574

### address:
slave address

 * type: select
 * default: 0x20

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
    "type": "rpii2c",
    "pins": {}
}
```

## Full-Example:
```
{
    "type": "rpii2c",
    "device": "pcf8574",
    "address": "0x20",
    "name": "",
    "pins": {},
    "signals": {}
}
```
