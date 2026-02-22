from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "gpioin"
        self.COMPONENT = "gpioin"
        self.INFO = "gpio input"
        self.DESCRIPTION = ""
        self.KEYWORDS = "input"
        self.IMAGES = ["proximity", "estop", "probe", "switch", "opto", "smdbutton", "touchprobe", "toggleswitch"]
        self.TYPE = "io"
        self.PLUGIN_TYPE = "gpio"
        self.NEEDS = ["gpio", "fpga"]
        self.SIGNALS = {
            "bit": {
                "direction": "input",
                "bool": True,
            },
        }
        self.PINDEFAULTS = {
            "bit": {
                "direction": "input",
                "edge": "target",
                "type": ["GPIO", "FPGA"],
            },
        }
        self.INTERFACE = {
            "bit": {
                "size": 1,
                "direction": "input",
            },
        }

    def gateware_instances(self):
        return self.gateware_instances_base(direct=True)

    def firmware_defines(self, variable_name):
        pin = self.plugin_setup["pins"]["bit"]["pin"]
        return f"#define {variable_name}_PIN_BIT {pin}"

    def firmware_setup(self, variable_name):
        return f"    pinMode({variable_name}_PIN_BIT, INPUT_PULLUP);"

    def firmware_loop(self, variable_name):
        return f"    {variable_name} = digitalRead({variable_name}_PIN_BIT);"
