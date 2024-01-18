from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "shiftreg"
        self.VERILOGS = ["shiftreg.v"]
        self.PINDEFAULTS = {
            "out": {
                "direction": "output",
            },
            "in": {
                "direction": "input",
            },
            "sclk": {
                "direction": "output",
            },
            "load": {
                "direction": "output",
            },
        }
        self.TYPE = "expansion"
        self.INFO = "Expansion to add I/O's via shiftregister's"
        self.DESCRIPTION = """
do not use this for high frequency signals !!!

jitter measured with a EPM240 as 40bit Shiftreg:
```
@10Mhz clock and 5 byte data ~= 3.7us jitter
```

you can use this extra IO's in other plugins like this:
```
{
    "type": "dout_bit",
    "name": "LED0",
    "invert": "true",
    "pin": "EXPANSION0_OUTPUT[0]"
},
{
    "type": "dout_bit",
    "name": "LED1",
    "invert": "true",
    "pin": "EXPANSION0_OUTPUT[0]"
},
```

## Output-Expansion with 74HC595:

| EXP | 74HC595 | FUNC |
| --- | --- | --- |
| out | 14 | DS |
| in |  | |
| sclk | 11 | SH_CP / SRCLK |
| load | 12 | ST_CP / RCLK |

## Input-Expansion with 74HC165:

| EXP | 74HC165 | FUNC |
| --- | --- | --- |
| out |  | |
| in |  | SER |
| sclk | 2 | CLK |
| load |  | SH/LD |

### LinuxCNC-RIO with Unipolar Stepper's over Shiftreg to the FPGA
[![LinuxCNC-RIO with Unipolar Stepper's over Shiftreg to the FPGA](https://img.youtube.com/vi/NlLd5CRCOac/0.jpg)](https://www.youtube.com/shorts/NlLd5CRCOac "LinuxCNC-RIO with Unipolar Stepper's over Shiftreg to the FPGA")

        """

    def gateware_instances(self):
        instances = self.gateware_instances_base()

        instance = instances[self.instances_name]
        instance_predefines = instance["predefines"]
        instance_parameter = instance["parameter"]
        instance_arguments = instance["arguments"]

        speed = int(self.plugin_setup.get("speed", 10000000))
        bits = int(self.plugin_setup.get("bits", 8))
        divider = self.system_setup["speed"] // speed
        instance_parameter["DIVIDER"] = divider
        instance_parameter["WIDTH"] = bits

        return instances
