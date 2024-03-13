from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "bitout"
        self.PINDEFAULTS = {
            "bit": {
                "direction": "output",
                "invert": False,
                "pullup": False,
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
        self.INFO = "singe bit output pin"
        self.DESCRIPTION = "to control relais, leds, valves, ...."

    def gateware_instances(self):
        instances = self.gateware_instances_base(direct=True)
        return instances
