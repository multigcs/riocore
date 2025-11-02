# JSON-Config
```
{
    "name": "ICEBreakerV1.0e",
    "flow": {
        "view": {
            "scale": 1.48,
            "pos": [
                882,
                -61
            ]
        },
        "board": {
            "pos": [
                1160.0,
                350.0
            ],
            "rotate": 0
        },
        "hal": {
            "misc": [
                1640.0,
                310.0
            ],
            "joint.0": [
                1640.0,
                400.0
            ],
            "joint.1": [
                1640.0,
                180.0
            ],
            "joint.2": [
                1640.0,
                50.0
            ],
            "spindle.0": [
                1640.0,
                -40.0
            ]
        }
    },
    "plugins": [
        {
            "type": "w5500",
            "pins": {
                "miso": {
                    "pin": "SPI:MISO"
                },
                "sel": {
                    "pin": "SPI:SEL"
                },
                "sclk": {
                    "pin": "SPI:SCLK"
                },
                "mosi": {
                    "pin": "SPI:MOSI"
                }
            },
            "uid": "w55000",
            "pos": [
                850.0,
                400.0
            ],
            "image": "w5500mini",
            "gw": "192.168.11.1",
            "ip": "192.168.11.194",
            "rotate": 90
        },
        {
            "type": "stepdir",
            "pins": {
                "step": {
                    "pin": "PMOD1A:P4"
                },
                "dir": {
                    "pin": "PMOD1A:P10"
                },
                "en": {
                    "pin": "PMOD1A:P1"
                }
            },
            "uid": "stepdir0",
            "pos": [
                1280.0,
                -10.0
            ],
            "image": "stepper",
            "is_joint": true,
            "joint": {
                "min_ferror": 10.0,
                "ferror": 22.0,
                "max_acceleration": 100.0
            },
            "rotate": -90
        },
        {
            "type": "stepdir",
            "pins": {
                "step": {
                    "pin": "PMOD1A:P3"
                },
                "dir": {
                    "pin": "PMOD1A:P9"
                }
            },
            "uid": "stepdir1",
            "pos": [
                1020.0,
                -10.0
            ],
            "name": "",
            "image": "stepper",
            "is_joint": true,
            "joint": {
                "ferror": 20.0,
                "min_ferror": 10.0,
                "max_acceleration": 110.0
            },
            "rotate": -90
        },
        {
            "type": "blink",
            "pins": {
                "led": {
                    "pin": "LED:R"
                }
            },
            "uid": "blink0",
            "pos": [
                1080.0,
                370.0
            ],
            "image": "led",
            "rotate": 180
        },
        {
            "type": "bitin",
            "pins": {
                "bit": {
                    "pin": "BUTTON:1"
                }
            },
            "uid": "bitin0",
            "pos": [
                890.0,
                270.0
            ],
            "image": "switch",
            "rotate": 180
        },
        {
            "type": "stepdir",
            "pins": {
                "step": {
                    "pin": "PMOD1A:P2"
                },
                "dir": {
                    "pin": "PMOD1A:P8"
                }
            },
            "uid": "stepdir2",
            "pos": [
                760.0,
                -10.0
            ],
            "name": "",
            "image": "stepper",
            "is_joint": true,
            "joint": {
                "ferror": 20.0,
                "min_ferror": 10.0,
                "max_acceleration": 110.0
            },
            "rotate": -90
        },
        {
            "type": "bitout",
            "uid": "bitout0",
            "image": "relay",
            "pos": [
                1410.0,
                320.0
            ],
            "pins": {
                "bit": {
                    "pin": "PMOD1B:P1"
                }
            }
        },
        {
            "type": "bitout",
            "uid": "bitout1",
            "image": "relay",
            "pos": [
                1410.0,
                470.0
            ],
            "pins": {
                "bit": {
                    "pin": "PMOD1B:P7"
                }
            }
        },
        {
            "type": "bitin",
            "uid": "bitin1",
            "image": "proximity",
            "pos": [
                1060.0,
                600.0
            ],
            "pins": {
                "bit": {
                    "pin": "PMOD1B:P4"
                }
            },
            "rotate": 90
        },
        {
            "type": "bitin",
            "uid": "bitin2",
            "image": "proximity",
            "pos": [
                1200.0,
                600.0
            ],
            "pins": {
                "bit": {
                    "pin": "PMOD1B:P2"
                }
            },
            "rotate": 90
        },
        {
            "type": "bitin",
            "uid": "bitin3",
            "image": "proximity",
            "pos": [
                1130.0,
                600.0
            ],
            "pins": {
                "bit": {
                    "pin": "PMOD1B:P3"
                }
            },
            "rotate": 90
        },
        {
            "type": "bitin",
            "uid": "bitin4",
            "image": "proximity",
            "pos": [
                1270.0,
                600.0
            ],
            "pins": {
                "bit": {
                    "pin": "PMOD1B:P10"
                }
            },
            "name": "",
            "rotate": 90
        },
        {
            "type": "bitin",
            "uid": "bitin5",
            "image": "proximity",
            "pos": [
                1340.0,
                600.0
            ],
            "pins": {
                "bit": {
                    "pin": "PMOD1B:P9"
                }
            },
            "name": "",
            "rotate": 90
        }
    ],
    "linuxcnc": {
        "ini": {
            "DISPLAY": {
                "DEFAULT_LINEAR_VELOCITY": 20.0
            },
            "EMCMOT": {
                "SERVO_PERIOD": 1500000
            }
        }
    },
    "boardcfg": "ICEBreakerV1.0e",
    "protocol": "UDP",
    "toolchain": "icestorm"
}

```
