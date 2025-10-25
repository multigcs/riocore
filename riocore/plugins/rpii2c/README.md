# rpii2c

<img align="right" width="320" src="image.png">

**gpio support over i2c port**

gpio support over i2c port

Keywords: ii2c gpio

## Pins:
*FPGA-pins*


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### device:
i2c device

 * type: select
 * default: pcf8574

### address:
slave address

 * type: select
 * default: 0x20


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
    "name": "",
    "device": "pcf8574",
    "address": "0x20",
    "pins": {},
    "signals": {}
}
```
