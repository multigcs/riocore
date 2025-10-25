from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "shiftreg"
        self.INFO = "Expansion to add I/O's via shiftregister's"
        self.KEYWORDS = "expansion digital io"
        self.DESCRIPTION = """
do not use this for high frequency signals !!!

jitter measured with a EPM240 as 40bit Shiftreg:
```
@10Mhz clock and 5 byte data ~= 3.7us jitter
```

## Output-Expansion with 74HC595:

| Plugin | 74HC595 | FUNC | LABEL |
| --- | --- | --- | --- |
| out | 14 | DS | SER_IN |
| in | | | |
| sclk | 11 | SH_CP / SRCLK | Clock |
| load | 12 | ST_CP / RCLK | L_Clock |

## Input-Expansion with 74HC165:

| Plugin | 74HC165 | FUNC | LABEL |
| --- | --- | --- | --- |
| out | | | |
| in |  | SER | SER_OUT |
| sclk | 2 | CLK | CLK |
| load |  | SH/LD | SH/LD |

### LinuxCNC-RIO with Unipolar Stepper's over Shiftreg to the FPGA
[![LinuxCNC-RIO with Unipolar Stepper's over Shiftreg to the FPGA](https://img.youtube.com/vi/NlLd5CRCOac/0.jpg)](https://www.youtube.com/shorts/NlLd5CRCOac "LinuxCNC-RIO with Unipolar Stepper's over Shiftreg to the FPGA")

        """
        self.ORIGIN = ""
        self.VERILOGS = ["shiftreg.v"]
        self.PINDEFAULTS = {
            "out": {
                "direction": "output",
                "description": "output data (DS on 74HC595)",
                "optional": True,
            },
            "in": {
                "direction": "input",
                "description": "input data (SER_OUT on 74HC165)",
                "optional": True,
            },
            "sclk": {
                "direction": "output",
                "description": "input data (CLK on 74HC165/ CH_CP/SRCLK on 74HC595)",
            },
            "load": {
                "direction": "output",
                "description": "input data (SH/LD on 74HC165/ ST_CP/RCLK on 74HC595)",
            },
        }
        self.TYPE = "expansion"
        self.OPTIONS = {
            "speed": {
                "default": 1000000,
                "type": int,
                "min": 100000,
                "max": 10000000,
                "description": "interface clock",
            },
            "bits": {
                "default": 8,
                "type": int,
                "min": 8,
                "max": 1024,
                "description": "number of bits (IO's)",
            },
        }
        self.BITS_IN = 0
        self.BITS_OUT = 0
        if "in" in self.plugin_setup.get("pins", {}):
            self.BITS_IN = int(self.plugin_setup.get("bits", self.OPTIONS["bits"]["default"]))
        if "out" in self.plugin_setup.get("pins", {}):
            self.BITS_OUT = int(self.plugin_setup.get("bits", self.OPTIONS["bits"]["default"]))

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        instance_arguments = instance["arguments"]

        speed = int(self.plugin_setup.get("speed", self.OPTIONS["speed"]["default"]))
        bits = int(self.plugin_setup.get("bits", self.OPTIONS["bits"]["default"]))
        divider = int(self.system_setup["speed"] / speed / 3.3)
        instance_parameter["DIVIDER"] = divider
        instance_parameter["WIDTH"] = bits

        if "in" not in self.plugin_setup.get("pins", {}):
            del instance_arguments["data_in"]
        if "out" not in self.plugin_setup.get("pins", {}):
            del instance_arguments["data_out"]

        return instances
