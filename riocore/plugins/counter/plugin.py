from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "counter"
        self.INFO = "pulse counter input"
        self.DESCRIPTION = "to counting digital pulses, supporting up,down and reset signals"
        self.KEYWORDS = "counter pulse"
        self.ORIGIN = ""
        self.VERILOGS = ["counter.v"]
        self.PINDEFAULTS = {
            "up": {
                "direction": "input",
                "invert": False,
                "pull": None,
                "optional": True,
                "description": "increment pin",
            },
            "down": {
                "direction": "input",
                "invert": False,
                "pull": None,
                "optional": True,
                "description": "decrement pin",
            },
            "reset": {
                "direction": "input",
                "invert": False,
                "pull": None,
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
