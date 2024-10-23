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
        self.ORIGIN = ""
        self.VERILOGS = ["shiftreg.v"]
        self.PINDEFAULTS = {
            "out": {
                "direction": "output",
                "description": "output data (DS on 74HC595)",
            },
            "in": {
                "direction": "input",
                "description": "input data (SER_OUT on 74HC165)",
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

    def gateware_instances(self):
        instances = self.gateware_instances_base()

        instance = instances[self.instances_name]
        instance["predefines"]
        instance_parameter = instance["parameter"]
        instance["arguments"]

        speed = int(self.plugin_setup.get("speed", self.OPTIONS["speed"]["default"]))
        bits = int(self.plugin_setup.get("bits", self.OPTIONS["bits"]["default"]))
        divider = self.system_setup["speed"] // speed
        instance_parameter["DIVIDER"] = divider
        instance_parameter["WIDTH"] = bits

        return instances
