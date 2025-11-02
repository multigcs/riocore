# JSON-Config
```
{
    "name": "Mix1",
    "_syncto": "cnc@192.168.10.86:/home/cnc/MesaTest/",
    "flow": {
        "view": {
            "scale": 1.09,
            "pos": [
                -100,
                -366
            ]
        },
        "board": {
            "pos": [
                850.0,
                410.0
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
            "type": "mesacard",
            "uid": "mesacard0",
            "pos": [
                650.0,
                -140.0
            ],
            "rotate": -90
        },
        {
            "type": "mesastepgen",
            "uid": "mesastepgen0",
            "pos": [
                -70.0,
                350.0
            ],
            "image": "stepper",
            "is_joint": true,
            "rotate": 180,
            "pins": {
                "step": {
                    "pin": "china-bob5x0:Z:step"
                },
                "dir": {
                    "pin": "china-bob5x0:Z:dir"
                }
            }
        },
        {
            "type": "mesastepgen",
            "uid": "mesastepgen1",
            "pos": [
                -70.0,
                80.0
            ],
            "image": "stepper",
            "is_joint": true,
            "pins": {
                "step": {
                    "pin": "china-bob5x0:Y:step"
                },
                "dir": {
                    "pin": "china-bob5x0:Y:dir"
                }
            },
            "rotate": 180,
            "name": ""
        },
        {
            "type": "mesastepgen",
            "uid": "mesastepgen2",
            "pos": [
                -70.0,
                -190.0
            ],
            "image": "stepper",
            "is_joint": true,
            "pins": {
                "step": {
                    "pin": "china-bob5x0:X:step"
                },
                "dir": {
                    "pin": "china-bob5x0:X:dir"
                }
            },
            "rotate": 180,
            "name": ""
        },
        {
            "type": "gpioin",
            "uid": "gpioin0",
            "pos": [
                310.0,
                -280.0
            ],
            "image": "proximity",
            "rotate": -90,
            "pins": {
                "bit": {
                    "pin": "china-bob5x0:OPTO:in2"
                }
            }
        },
        {
            "type": "gpioout",
            "pins": {
                "bit": {
                    "pin": "china-bob5x0:RELAIS:out",
                    "modifier": [
                        {
                            "type": "invert",
                            "pos": [
                                430.0,
                                450.0
                            ]
                        }
                    ]
                }
            },
            "uid": "gpioout0",
            "pos": [
                420.0,
                520.0
            ],
            "image": "relay",
            "rotate": 90
        },
        {
            "type": "gpioin",
            "uid": "gpioin1",
            "pos": [
                380.0,
                -280.0
            ],
            "image": "proximity",
            "name": "",
            "rotate": -90,
            "pins": {
                "bit": {
                    "pin": "china-bob5x0:OPTO:in1"
                }
            }
        },
        {
            "type": "gpioin",
            "uid": "gpioin2",
            "pos": [
                450.0,
                -280.0
            ],
            "image": "proximity",
            "name": "",
            "rotate": -90,
            "pins": {
                "bit": {
                    "pin": "china-bob5x0:OPTO:in0",
                    "modifier": [
                        {
                            "type": "invert",
                            "pos": [
                                460.0,
                                -60.0
                            ]
                        }
                    ]
                }
            }
        },
        {
            "type": "mesapwmgen",
            "pins": {
                "pwm": {
                    "pin": "china-bob5x0:PWM:analog"
                }
            },
            "uid": "mesapwmgen0",
            "pos": [
                260.0,
                470.0
            ],
            "image": "spindle500w",
            "rotate": 90,
            "scale": 20000.0
        },
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
                690.0,
                440.0
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
                }
            },
            "uid": "stepdir0",
            "pos": [
                1090.0,
                510.0
            ],
            "image": "stepper",
            "is_joint": true,
            "joint": {
                "min_ferror": 10.0,
                "ferror": 22.0,
                "max_acceleration": 100.0
            }
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
                1090.0,
                250.0
            ],
            "name": "",
            "image": "stepper",
            "is_joint": true,
            "joint": {
                "ferror": 20.0,
                "min_ferror": 10.0,
                "max_acceleration": 110.0
            }
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
                770.0,
                390.0
            ],
            "image": "led",
            "rotate": 180
        },
        {
            "type": "ethercat",
            "uid": "ethercat0",
            "pos": [
                1220.0,
                -170.0
            ],
            "node_type": "Master",
            "idx": -1
        },
        {
            "type": "ethercat",
            "uid": "ethercat1",
            "pos": [
                1460.0,
                -250.0
            ],
            "image": "ethercatservo",
            "is_joint": true,
            "joint": {
                "scale": 20000.0
            },
            "idx": 0,
            "node_type": "Servo/Stepper"
        },
        {
            "type": "halinput",
            "uid": "halinput0",
            "pos": [
                1340.0,
                340.0
            ],
            "b": "abs-z",
            "z": "",
            "a": "-abs-rz"
        },
        {
            "type": "bitout",
            "pins": {
                "bit": {
                    "pin": "PMOD1A:P1"
                }
            },
            "uid": "bitout0",
            "pos": [
                940.0,
                300.0
            ]
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
                660.0,
                290.0
            ],
            "image": "switch",
            "rotate": 180
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
    "breakouts": [
        {
            "slot": "mesacard0:P1",
            "breakout": "china-bob5x",
            "name": "china-bob5x0",
            "pos": [
                270.0,
                -10.0
            ],
            "rotate": 180
        }
    ],
    "boardcfg": "ICEBreakerV1.0e",
    "protocol": "UDP",
    "toolchain": "icestorm"
}

```
