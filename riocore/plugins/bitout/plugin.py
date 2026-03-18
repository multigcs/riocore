from riocore import PluginImages
from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "bitout"
        self.INFO = "singe bit output pin"
        self.DESCRIPTION = "to control relay, leds, valves, ...."
        self.KEYWORDS = "led relais relay valve lamp motor magnet"
        self.IMAGES = PluginImages.bitout
        self.NEEDS = ["fpga"]
        self.ORIGIN = ""
        self.PLUGIN_CONFIGS = {"Wizard": "config.py"}
        self.PINDEFAULTS = {
            "bit": {
                "direction": "output",
            },
        }
        self.INTERFACE = {
            "bit": {
                "size": 1,
                "direction": "output",
            },
        }
        self.SIGNALS = {
            "bit": {
                "direction": "output",
                "bool": True,
            },
        }

    def gateware_instances(self):
        return self.gateware_instances_base(direct=True)
