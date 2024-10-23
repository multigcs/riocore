# icewerxadc
**4-channel adc of the iceWerx-board**

to read analog signals from the iceWerx-board

Range: 0-3.3V -> 0-1024

https://eu.robotshop.com/de/products/devantech-icewerx-ice40-hx8k-fpga

should work also with the iceFUN board

        

Keywords: analog adc voltage ampere


![image.png](image.png)

## Limitations
* boards: iceWerx-iCE40-HX8K, OctoBot

## Basic-Example:
```
{
    "type": "icewerxadc",
    "pins": {
        "tx": {
            "pin": "0"
        },
        "rx": {
            "pin": "1"
        }
    }
}
```

## Pins:
*FPGA-pins*
### tx:

 * direction: output

### rx:

 * direction: input


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 


## Signals:
*signals/pins in LinuxCNC*
### adc1:

 * type: float
 * direction: input
 * unit: Volt

### adc2:

 * type: float
 * direction: input
 * unit: Volt

### adc3:

 * type: float
 * direction: input
 * unit: Volt

### adc4:

 * type: float
 * direction: input
 * unit: Volt


## Interfaces:
*transport layer*
### adc1:
1. ADC channel

 * size: 10 bit
 * direction: input
 * multiplexed: True

### adc2:
2. ADC channel

 * size: 10 bit
 * direction: input
 * multiplexed: True

### adc3:
3. ADC channel

 * size: 10 bit
 * direction: input
 * multiplexed: True

### adc4:
4. ADC channel

 * size: 10 bit
 * direction: input
 * multiplexed: True


## Full-Example:
```
{
    "type": "icewerxadc",
    "name": "",
    "pins": {
        "tx": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "invert"
                }
            ]
        },
        "rx": {
            "pin": "1",
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
    "signals": {
        "adc1": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "adc1",
                "section": "inputs",
                "type": "meter"
            }
        },
        "adc2": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "adc2",
                "section": "inputs",
                "type": "meter"
            }
        },
        "adc3": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "adc3",
                "section": "inputs",
                "type": "meter"
            }
        },
        "adc4": {
            "net": "xxx.yyy.zzz",
            "function": "rio.xxx",
            "scale": 100.0,
            "offset": 0.0,
            "display": {
                "title": "adc4",
                "section": "inputs",
                "type": "meter"
            }
        }
    }
}
```

## Verilogs:
 * [icewerxadc.v](icewerxadc.v)
 * [uart_baud.v](uart_baud.v)
 * [uart_rx.v](uart_rx.v)
 * [uart_tx.v](uart_tx.v)
