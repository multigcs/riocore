# SLOTS

slots can be entered in the json board and config files,
which allow a kind of pin mapping to

1. assign plugins to a port more easily
2. assign modules to a slot to avoid specifying each pin individually

small example using the 'PMOD_1A' socket on the ICEBreakerV1.0e board's:

```
"slots": [
    {
        "name": "PMOD_1A",
        "comment": "PMOD 1A",
        "pins": {
            "P1": "4",
            "P2": "2",
            "P3": "47",
            "P4": "45",
            "P7": "3",
            "P8": "48",
            "P9": "46",
            "P10": "44"
        }
    }
]
```

In the config, the '44' can now be specified as follows ('SLOT_NAME:PIN_NAME'):
```
        {
            "type": "bitout",
            "name": "relais",
            "pins": {
                "bit": {
                    "pin": "PMOD_1A:P10"
                }
            }
        },
```

but it is even easier if several pins and plugins are used together,
e.g. if an existing 'module' is used....


# MODULES

with the help of 'modules' you can easily create recurring configurations
configurations as a kind of template.

Here is an example using the W5500 Ethernet module:

```
{
  "comment": "W5500-Ethernet",
  "plugins": [
        {
            "name": "w5500",
            "type": "w5500",
            "mac": "AA:AF:FA:CC:E3:1C",
            "ip": "192.168.10.195",
            "port": 2390,
            "pins": {
                "mosi": {
                    "pin": "P4"
                },
                "miso": {
                    "pin": "P3"
                },
                "sclk": {
                    "pin": "P2"
                },
                "sel": {
                    "pin": "P1"
                }
            }
        }
    ]
}
```

this gives you a module with predefined pin assignment and standardised connector,
in this case a PMOD connector (2x6pin pin header)

this module can now be very easily added to new configurations,
independent of the board:

```
    "modules": [
        {
            "slot": "PMOD_1A",
            "module": "w5500"
        }
    ],
```

all pins are mapped and all defaults are set
it is also possible to overwrite the defaults:

```
    "modules": [
        {
            "slot": "PMOD_1A",
            "module": "w5500",
            "setup": {
                "w5500": {
                    "ip": "192.168.1.220",
                }
            }
        }
    ],
```

the name 'w5500' under the 'setup' refers to the
refers to the 'name' of the plugin in the 'module' configuration



