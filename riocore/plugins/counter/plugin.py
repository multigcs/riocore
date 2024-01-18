from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "counter"
        self.VERILOGS = ["counter.v"]
        self.PINDEFAULTS = {
            "up": {
                "direction": "input",
                "invert": False,
                "pullup": False,
                "optional": True,
            },
            "down": {
                "direction": "input",
                "invert": False,
                "pullup": False,
                "optional": True,
            },
            "reset": {
                "direction": "input",
                "invert": False,
                "pullup": False,
                "optional": True,
            },
        }
        self.INTERFACE = {
            "counter": {
                "size": 32,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "counter": {
                "direction": "input",
            },
        }
