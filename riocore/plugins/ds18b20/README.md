# ds18b20

<img align="right" width="320" src="image.png">

**1Wire Temperature sensor**

for cheap 1wire temperature sensor's, only one per pin is supported at the moment

Keywords: adc analog temperature

## Basic-Example:
```
{
    "type": "ds18b20",
    "pins": {
        "one_wire": {
            "pin": "0"
        }
    }
}
```

## Pins:
*FPGA-pins*
### one_wire:

 * direction: inout


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### temperature:

 * type: float
 * direction: input
 * unit: Hz


## Interfaces:
*transport layer*
### temperature:

 * size: 16 bit
 * direction: input


## Full-Example:
```
{
    "type": "ds18b20",
    "name": "",
    "pins": {
        "one_wire": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        }
    },
    "signals": {
        "temperature": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "temperature",
                "section": "inputs",
                "type": "meter"
            }
        }
    }
}
```

## Verilogs:
 * [ds18b20.v](ds18b20.v)
