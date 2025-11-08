from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "shiftreg"
        self.COMPONENT = "shiftreg"
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
                "pos": (185, 260),
            },
            "in": {
                "direction": "input",
                "description": "input data (SER_OUT on 74HC165)",
                "optional": True,
                "pos": (159, 260),
            },
            "sclk": {
                "direction": "output",
                "description": "input data (CLK on 74HC165/ CH_CP/SRCLK on 74HC595)",
                "pos": (114, 260),
            },
            "load": {
                "direction": "output",
                "description": "input data (SH/LD on 74HC165/ ST_CP/RCLK on 74HC595)",
                "pos": (137, 260),
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

        self.IMAGE_SHOW = True
        self.IMAGE = "inout8.png"

        self.BITS_IN = 0
        self.BITS_OUT = 0
        if "in" in self.plugin_setup.get("pins", {}):
            self.BITS_IN = int(self.plugin_setup.get("bits", self.OPTIONS["bits"]["default"]))
            if self.BITS_IN > 8:
                self.IMAGE_SHOW = False
            px = 12
            py = 54
            for bit in range(self.BITS_IN):
                self.PINDEFAULTS[f"INPUT:{bit}"] = {"direction": "input", "type": ["FPGA"], "edge": "source", "pos": (px, py)}
                py += 23
        if "out" in self.plugin_setup.get("pins", {}):
            self.BITS_OUT = int(self.plugin_setup.get("bits", self.OPTIONS["bits"]["default"]))
            if self.BITS_OUT > 8:
                self.IMAGE_SHOW = False
            px = 367
            py = 54 + 7 * 23
            for bit in range(self.BITS_OUT):
                self.PINDEFAULTS[f"OUTPUT:{bit}"] = {"direction": "output", "type": ["FPGA"], "edge": "source", "pos": (px, py)}
                py -= 23

    def update_prefixes(cls, parent, instances):
        fnum = 0
        for instance in instances:
            for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=instance.instances_name):
                instance.hal_prefix = instance.instances_name
                plugin_instance = connected_pin["instance"]
                # plugin_instance.PREFIX = f"{instance.master}.{instance.hal_prefix}.{plugin_instance.instances_name}"
                plugin_instance.PREFIX = f"{instance.master}.{plugin_instance.instances_name}"
                fnum += 1

    def update_pins(self, parent):
        for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=self.instances_name):
            psetup = connected_pin["setup"]
            pin = connected_pin["pin"]
            if pin in self.PINDEFAULTS:
                direction, bit = pin.split(":")
                psetup["pin"] = f"{self.instances_name.upper()}_{direction}[{bit}]"
            connected_pin["instance"].master = self.master

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
