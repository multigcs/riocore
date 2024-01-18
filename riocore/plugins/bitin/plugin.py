from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "bitin"
        self.PINDEFAULTS = {
            "bit": {
                "direction": "input",
                "invert": False,
                "pullup": False,
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
