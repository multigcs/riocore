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
                "description": "increment pin",
            },
            "down": {
                "direction": "input",
                "invert": False,
                "pullup": False,
                "optional": True,
                "description": "decrement pin",
            },
            "reset": {
                "direction": "input",
                "invert": False,
                "pullup": False,
                "optional": True,
                "description": "reset to zero pin",
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
        self.INFO = "pulse counter input"
        self.DESCRIPTION = ""
