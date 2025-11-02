# JSON-Config
```
{
    "name": "Ninja",
    "flow": {
        "view": {
            "scale": 1.2933049946865036,
            "pos": [
                351.1190223166843,
                -606.0
            ]
        },
        "board": {
            "pos": [
                540.0,
                1390.0
            ],
            "rotate": -90
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
            "type": "ninja",
            "node_type": "board",
            "pos": [
                670.0,
                -250.0
            ],
            "rotate": 90,
            "uid": "ninja0",
            "board": "w5500-evb-pico-parport"
        },
        {
            "type": "ninja",
            "node_type": "stepper",
            "pos": [
                1340.0,
                220.0
            ],
            "pins": {
                "step": {
                    "pin": "china-bob5x0:X:step"
                },
                "dir": {
                    "pin": "china-bob5x0:X:dir"
                }
            },
            "image": "servo42",
            "rotate": 180,
            "is_joint": true,
            "uid": "ninja1",
            "joint": {
                "scale": -800.0,
                "max_velocity": 25.0,
                "min_limit": 0.0,
                "max_limit": 230.0,
                "home": 0.0,
                "home_search_vel": -10.0,
                "home_final_vel": 20.0,
                "home_latch_vel": -1.0
            }
        },
        {
            "type": "ninja",
            "node_type": "stepper",
            "pos": [
                1340.0,
                20.0
            ],
            "pins": {
                "step": {
                    "pin": "china-bob5x0:Y:step"
                },
                "dir": {
                    "pin": "china-bob5x0:Y:dir"
                }
            },
            "image": "servo42",
            "rotate": 180,
            "name": "",
            "is_joint": true,
            "uid": "ninja2",
            "joint": {
                "scale": 800.0,
                "max_velocity": 25.0,
                "min_limit": 0.0,
                "max_limit": 160.0,
                "home": 0.0,
                "home_search_vel": -10.0,
                "home_final_vel": 20.0,
                "home_offset": 0.0,
                "home_latch_vel": -1.0
            }
        },
        {
            "type": "ninja",
            "node_type": "stepper",
            "pos": [
                1340.0,
                -180.0
            ],
            "pins": {
                "step": {
                    "pin": "china-bob5x0:Z:step"
                },
                "dir": {
                    "pin": "china-bob5x0:Z:dir"
                }
            },
            "rotate": 180,
            "name": "",
            "is_joint": true,
            "uid": "ninja3",
            "image": "servo42",
            "joint": {
                "scale": -1600.0,
                "max_velocity": 15.0,
                "min_limit": -32.0,
                "max_limit": 0.0,
                "home": 0.0,
                "home_search_vel": 10.0,
                "home_final_vel": 20.0,
                "home_latch_vel": 1.0
            }
        },
        {
            "type": "ninja",
            "node_type": "pwm",
            "pins": {
                "pwm": {
                    "pin": "china-bob5x0:PWM:analog"
                }
            },
            "uid": "ninjapwmgen0",
            "pos": [
                1010.0,
                -400.0
            ],
            "image": "spindle500w",
            "rotate": 0
        },
        {
            "type": "gpioin",
            "pins": {
                "bit": {
                    "pin": "china-bob5x0:OPTO:in0",
                    "modifier": [
                        {
                            "type": "invert",
                            "pos": [
                                880.0,
                                330.0
                            ]
                        }
                    ]
                }
            },
            "uid": "gpioin0",
            "pos": [
                1020.0,
                350.0
            ],
            "image": "proximity",
            "rotate": 0,
            "signals": {
                "bit": {
                    "net": "joint.0.home-sw-in"
                }
            },
            "name": "home-x"
        },
        {
            "type": "gpioin",
            "pins": {
                "bit": {
                    "pin": "china-bob5x0:OPTO:in1",
                    "modifier": [
                        {
                            "type": "invert",
                            "pos": [
                                880.0,
                                300.0
                            ]
                        }
                    ]
                }
            },
            "uid": "gpioin1",
            "pos": [
                1020.0,
                280.0
            ],
            "image": "proximity",
            "rotate": 0,
            "name": "home-y",
            "signals": {
                "bit": {
                    "net": "joint.1.home-sw-in"
                }
            }
        },
        {
            "type": "gpioin",
            "pins": {
                "bit": {
                    "pin": "china-bob5x0:OPTO:in2",
                    "modifier": [
                        {
                            "type": "invert",
                            "pos": [
                                880.0,
                                270.0
                            ]
                        }
                    ]
                }
            },
            "uid": "gpioin2",
            "pos": [
                1020.0,
                210.0
            ],
            "image": "proximity",
            "rotate": 0,
            "name": "home-z",
            "signals": {
                "bit": {
                    "net": "joint.2.home-sw-in"
                }
            }
        },
        {
            "type": "gpioout",
            "pins": {
                "bit": {
                    "pin": "china-bob5x0:RELAIS:out"
                }
            },
            "uid": "gpioout2",
            "pos": [
                760.0,
                -450.0
            ],
            "image": "relay",
            "rotate": 180,
            "name": "spindle-on",
            "signals": {
                "bit": {
                    "net": "spindle.0.on"
                }
            }
        },
        {
            "type": "gpioout",
            "pins": {
                "bit": {
                    "pin": "ninja0:IO:LED"
                }
            },
            "uid": "gpioout3",
            "pos": [
                740.0,
                140.0
            ],
            "image": "led",
            "rotate": 90,
            "name": "led"
        },
        {
            "type": "gpioout",
            "uid": "gpiooutgpioout",
            "pos": [
                1320.0,
                -260.0
            ],
            "pins": {
                "bit": {
                    "pin": "china-bob5x0:ALL:en"
                }
            },
            "name": "enable"
        },
        {
            "type": "halinput",
            "uid": "halinputhalinput",
            "pos": [
                530.0,
                220.0
            ]
        }
    ],
    "boardcfg": "",
    "breakouts": [
        {
            "breakout": "china-bob5x",
            "name": "china-bob5x0",
            "pos": [
                860.0,
                -270.0
            ],
            "rotate": 0,
            "slot": "ninja0:PAR"
        }
    ]
}
```
