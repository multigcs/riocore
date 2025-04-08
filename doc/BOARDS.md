# add new boards
* these examples refer to a ULX3S

to create a new board config, you need to create a directory like this:
```
mkdir -p riocore/boards/ULX3S
```

then create a new board.json file in this directory like this:

cat riocore/boards/ULX3S/board.json
```
{
    "name": "ULX3S",
    "description": "A powerful ECP5 board for open source FPGA development ",
    "comment": "",
    "url": "https://radiona.org/ulx3s/",
    "toolchain": "icestorm",
    "family": "ecp5",
    "type": "25k",
    "package": "CABGA381",
    "clock": {
        "speed": "25000000",
        "pin": "P3"
    }
}
```

* the name must be the same as the directory name,
* description, comment and url are optional
* for the toolchain, you can look at: riocore/generator/toolchains/ to see the available options
* clock/speed is the used Crystal/Oscillator speed in Hz and
* clock/pin the Input-Pin of this Crystal/Oscillator.

that's all you need for a basic configuration

## Advanced

for more advanced configurations, you can add an image of the board and some pinout informations

### Board-Image
filename:
```
riocore/boards/ULX3S/board.png
```

* the size should be approximately ~800x600
* format and suffix: png
* from above and preferably without edges (only you need some space later for the pin-labels)
* should be without copyrights

### Pinout informations

you can also add informations about the pins and connectors(slots) on the board (or LEDs/Switches/..),
this is usefull for a simpler configuration.

LED example:
```
"slots": [
    {
        "name": "LED",
        "comment": "onboard LEDs",
        "pins": {
            "L0": {"pin": "B2", "direction": "output"},
            "L1": {"pin": "C2"},
            "L2": {"pin": "C1"},
            "L3": {"pin": "D2"},
            "L4": {"pin": "D1"},
            "L5": {"pin": "E2"},
            "L6": {"pin": "E1"},
            "L7": {
                "pin": "H3",
                "pos": [
                    85,
                    290
                ]
            }
        }
    },
]
```
* slots: connector / button-group / led-group
* pins/pin: the FPGA pinname ()
* pins/direction: optional, is used by the plugin filter (output / input / all)
* pins/pos: optional, with this info, you can see the pin in rio-setup on the right location and click it to setup ([X, Y] position on the boardimage)

this allows you to use eg "LED:L0" in you later plugin setup without searching for the read FPGA-Pin name in the schematics







