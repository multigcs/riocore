from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "gpioout"
        self.COMPONENT = "gpioout"
        self.INFO = "gpio output"
        self.DESCRIPTION = ""
        self.KEYWORDS = "output"
        self.IMAGES = ["relay", "ssr", "ssr2a", "led", "smdled", "spindle500w", "compressor", "vacuum", "valve", "dinrailplug", "motor"]
        self.TYPE = "io"
        self.PLUGIN_TYPE = "gpio"
        self.NEEDS = ["gpio", "fpga"]
        self.SIGNALS = {
            "bit": {
                "direction": "output",
                "bool": True,
            },
        }
        self.PINDEFAULTS = {
            "bit": {
                "direction": "output",
                "edge": "target",
                "type": ["GPIO", "FPGA"],
            },
        }
        self.INTERFACE = {
            "bit": {
                "size": 1,
                "direction": "output",
            },
        }

    def gateware_instances(self):
        return self.gateware_instances_base(direct=True)

    def firmware_defines(self, variable_name):
        pin = self.plugin_setup["pins"]["bit"]["pin"]
        return f"#define {variable_name}_PIN_BIT {pin}"

    def firmware_setup(self, variable_name):
        return f"    pinMode({variable_name}_PIN_BIT, OUTPUT);"

    def firmware_loop(self, variable_name):
        return f"    digitalWrite({variable_name}_PIN_BIT, {variable_name});"
