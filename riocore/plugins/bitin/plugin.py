from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "bitin"
        self.INFO = "single input pin"
        self.DESCRIPTION = "to read switches or other 1bit signals"
        self.KEYWORDS = "switch limit estop keyboard"
        self.IMAGES = ["proximity", "estop", "probe", "switch", "opto", "smdbutton"]
        self.ORIGIN = ""
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
        instances = self.gateware_instances_base(direct=True)
        return instances
