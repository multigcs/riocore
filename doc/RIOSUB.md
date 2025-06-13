# RIOSUB

to combine multiple FPGA boards to one rio device

the FPGA's can be connected via RS422/RS485 or UART, depending on the distance

Warnings:
* Joint plug-ins can only be used on the master!
* all plug-ins of a slave are treated as one in the master

Riosub vs shiftreg expansion:
* !!! it is always better to have everything on one FPGA, each interface generates delays !!!
* shiftregs are faster for single bits and needs no extra FPGA
* shiftregs can only expand IO-Pins
* riosub can evaluate real-time data on the slave and only transmits the results
* shiftregs can create jitter on pwm/step signals
* riosub generates fast signals the slave FPGA

In the following example, the FPGA master is connected to the host via UDP, the FPGA slave via RS485 to the master.

First you need to configure your slave, because the master needs it's data to build

## Slave-Example (slave.json)
```
{
    "name": "Slave",
    "boardcfg": "Tangbob",
    "description": "Slave-FPGA",
    "protocol": "UDP",
    "plugins": [
        {
            "type": "uart",
            "pins": {
                "rx": {
                    "pin": "MODBUS:RX"
                },
                "tx": {
                    "pin": "MODBUS:TX"
                },
                "tx_enable": {
                    "pin": "MODBUS:TX_ENABLE"
                }
            },
            "uid": "uart0",
            "csum": true,
            "baud": 2500000
        },
        {
            "type": "wled",
            "pins": {
                "data": {
                    "pin": "WLED:DATA"
                }
            },
            "uid": "wled0"
        },
        {
            "type": "blink",
            "pins": {
                "led": {
                    "pin": "LED:L1",
                    "modifier": [
                        {
                            "type": "onerror",
                            "invert": true
                        }
                    ]
                }
            },
            "uid": "blink0"
        },
        {
            "type": "pwmout",
            "pins": {
                "pwm": {
                    "pin": "LED:L2",
                    "modifier": [
                        {
                            "type": "invert"
                        }
                    ]
                }
            },
            "uid": "pwmout1"
        },
        {
            "type": "quadencoder",
            "pins": {
                "a": {
                    "pin": "LEFT:P1"
                },
                "b": {
                    "pin": "LEFT:P2"
                }
            },
            "uid": "quadencoder0"
        },
        {
            "type": "quadencoder",
            "pins": {
                "a": {
                    "pin": "LEFT:P3"
                },
                "b": {
                    "pin": "LEFT:P4"
                }
            },
            "uid": "quadencoder1"
        }
    ]
}
```

## Master-Example (master.json)
```
{
    "name": "Master",
    "boardcfg": "Tangbob",
    "description": "Master-FPGA",
    "protocol": "UDP",
    "plugins": [
        {
            "type": "w5500",
            "pins": {
                "mosi": {
                    "pin": "SPI:MOSI"
                },
                "miso": {
                    "pin": "SPI:MISO"
                },
                "sclk": {
                    "pin": "SPI:SCLK"
                },
                "sel": {
                    "pin": "SPI:SEL"
                }
            },
            "uid": "w55000",
            "ip": "192.168.10.194",
            "gw": "192.168.10.1"
        },
        {
            "type": "riosub",
            "pins": {
                "tx": {
                    "pin": "MODBUS:TX"
                },
                "rx": {
                    "pin": "MODBUS:RX"
                },
                "tx_enable": {
                    "pin": "MODBUS:TX_ENABLE"
                }
            },
            "uid": "riosub0",
            "subconfig": "/usr/src/riocore/slave.json",
            "baud": 2500000
        },
        {
            "type": "wled",
            "pins": {
                "data": {
                    "pin": "WLED:DATA"
                }
            },
            "uid": "wled0"
        },
        {
            "type": "blink",
            "pins": {
                "led": {
                    "pin": "LED:L1",
                    "modifier": [
                        {
                            "type": "onerror",
                            "invert": true
                        }
                    ]
                }
            },
            "uid": "blink0"
        },
        {
            "type": "pwmout",
            "pins": {
                "pwm": {
                    "pin": "LED:L2",
                    "modifier": [
                        {
                            "type": "invert"
                        }
                    ]
                }
            },
            "uid": "pwmout1"
        },
        {
            "type": "stepdir",
            "pins": {
                "step": {
                    "pin": "LEFT:P1"
                },
                "dir": {
                    "pin": "LEFT:P2"
                }
            },
            "uid": "stepdir0",
            "is_joint": true
        }
    ]
}
```
