from riocore import PluginImages
from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "bitin"
        self.INFO = "single input pin"
        self.DESCRIPTION = "to read switches or other 1bit signals"
        self.KEYWORDS = "switch limit estop keyboard"
        self.IMAGES = PluginImages.bitin
        self.NEEDS = ["fpga"]
        self.ORIGIN = ""
        self.PLUGIN_CONFIGS = {"Wizard": "config.py"}
        self.PINDEFAULTS = {
            "bit": {
                "direction": "input",
            },
        }
        self.INTERFACE = {
            "bit": {
                "size": 1,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "bit": {
                "direction": "input",
                "bool": True,
            },
        }

    def gateware_instances(self):
        return self.gateware_instances_base(direct=True)
