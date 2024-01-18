from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "as5600"
        self.VERILOGS = ["as5600.v"]
        self.PINDEFAULTS = {
            "sda": {
                "direction": "inout",
                "invert": False,
                "pullup": False,
            },
            "scl": {
                "direction": "output",
                "invert": False,
                "pullup": False,
            },
        }
        self.INTERFACE = {
            "position": {
                "size": 32,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "position": {
                "direction": "input",
            },
        }
