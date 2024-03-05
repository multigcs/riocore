# uartbridge


uart bridge

## Basic-Example:
```
{
    "type": "uartbridge",
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
 * default: 24
 * unit: bits

### tx_buffersize:
max tx buffer size

 * type: int
 * min: 32
 * max: 255
 * default: 16
 * unit: bits

### tx_frame:
tx frame format

 * type: str
 * default: 

### rx_frame:
rx frame format

 * type: str
 * default: 

### name:
name of this plugin instance

 * type: str
 * default: None


## Signals:
the signals of this plugin are user configurable


## Interfaces:
### rxdata:

 * size: 24 bit
 * direction: input

### txdata:

 * size: 16 bit
 * direction: output


## Full-Example:
```
{
    "type": "uartbridge",
    "baud": 9600,
    "rx_buffersize": 24,
    "tx_buffersize": 16,
    "tx_frame": "",
    "rx_frame": "",
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
    "signals": {}
}
```

## Verilogs:
 * uartbridge.v
 * uart_baud.v
 * uart_rx.v
 * uart_tx.v
