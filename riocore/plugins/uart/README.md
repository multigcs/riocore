# uart


uart interface for host cominucation

## Basic-Example:
```
{
    "type": "uart",
    "pins": {
        "rx": {
            "pin": "0"
        },
        "tx": {
            "pin": "1"
        }
    }
}
```

## Pins:
### rx:

 * direction: input
 * pullup: False

### tx:

 * direction: output
 * pullup: False


## Options:
### baud:
serial baud rate

 * type: int
 * min: 9600
 * max: 10000000
 * default: 1000000
 * unit: bit/s

### name:
name of this plugin instance

 * type: str
 * default: None


## Signals:


## Interfaces:


## Full-Example:
```
{
    "type": "uart",
    "baud": 1000000,
    "name": "",
    "pins": {
        "rx": {
            "pin": "0",
            "modifiers": [
                {
                    "type": "debounce"
                }
            ]
        },
        "tx": {
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
 * uart.v
 * uart_baud.v
 * uart_rx.v
 * uart_tx.v
