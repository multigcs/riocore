# modbus


generic modbus plugin

## Basic-Example:
```
{
    "type": "modbus",
    "pins": {
        "tx": {
            "pin": "0"
        },
        "rx": {
            "pin": "1"
        },
        "tx_enable": {
            "pin": "2"
        }
    }
}
```

## Pins:
### tx:

 * direction: output
 * pullup: False

### rx:

 * direction: input
 * pullup: False

### tx_enable:

 * direction: output
 * pullup: False


## Options:
### baud:
serial baud rate

 * type: int
 * min: 300
 * max: 10000000
 * default: 9600
 * unit: bit/s

### rx_buffersize:
max rx buffer size

 * type: int
 * min: 32
 * max: 255
 * default: 128
 * unit: bits

### tx_buffersize:
max tx buffer size

 * type: int
 * min: 32
 * max: 255
 * default: 128
 * unit: bits

### name:
name of this plugin instance

 * type: str
 * default: None


## Signals:
the signals of this plugin are user configurable


## Interfaces:
### rxdata:

 * size: 128 bit
 * direction: input

### txdata:

 * size: 128 bit
 * direction: output


## Full-Example:
```
{
    "type": "modbus",
    "baud": 9600,
    "rx_buffersize": 128,
    "tx_buffersize": 128,
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
        },
        "tx_enable": {
            "pin": "2",
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
 * modbus.v
 * uart_baud.v
 * uart_rx.v
 * uart_tx.v
