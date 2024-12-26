# i2cbus
**I2C-Bus**

I2C-Bus - supports multiple busses with multiple devices per bus

sub-busses via multiplexer (pca9548) are also supported
        

Devices:
* [ads1115](devices/ads1115.py)
* [adxl345](devices/adxl345.py)
* [as5600](devices/as5600.py)
* [bmp180](devices/bmp180.py)
* [lm75](devices/lm75.py)
* [mlx90614](devices/mlx90614.py)
* [pca9685](devices/pca9685.py)
* [pcf8574](devices/pcf8574.py)

Keywords: adc temperatur voltage current


![image.png](image.png)

```mermaid
graph LR;
    FPGA-->Bus0;
    Bus0-->Device0-->Device1..;
    FPGA-->Bus1..;
    Bus1..-->Device2-->Device3..;
    Bus1..-->Multiplexer0-->Device4-->Device5..;
    Multiplexer0-->Device6-->Device7..;
```

## Basic-Example:
```
{
    "type": "i2cbus",
    "pins": {
        "sda": {
            "pin": "0"
        },
        "scl": {
            "pin": "1"
        }
    }
}
```

## Pins:
*FPGA-pins*
### sda:

 * direction: inout

### scl:

 * direction: output


## Options:
*user-options*
### speed:
I2C-Clockspeed

 * type: int
 * min: 100
 * max: 50000000
 * default: 100000
 * unit: Hz

### multiplexer:
Sub-Bus multiplexer address (pca9548)

 * type: select
 * default: 

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
    "type": "i2cbus",
    "speed": 100000,
    "multiplexer": "",
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
        }
    },
    "signals": {}
}
```

## Verilogs:
 * [i2c_master.v](i2c_master.v)
