from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "dis7seg"
        self.INFO = "7segment display with buttons"
        self.DESCRIPTION = "only usable for devboards with 7segment display / better using other 7seg plugins"
        self.KEYWORDS = "info display"
        self.ORIGIN = ""
        self.VERILOGS = ["dis7seg.v"]
        self.PINDEFAULTS = {
            "en1": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
            "en2": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
            "en3": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
            "en4": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
            "seg_a": {
                "direction": "output",
                "invert": False,
                "pull": None,
                "optional": True,
            },
            "seg_b": {
                "direction": "output",
                "invert": False,
                "pull": None,
                "optional": True,
            },
            "seg_c": {
                "direction": "output",
                "invert": False,
                "pull": None,
                "optional": True,
            },
            "seg_d": {
                "direction": "output",
                "invert": False,
                "pull": None,
                "optional": True,
            },
            "seg_e": {
                "direction": "output",
                "invert": False,
                "pull": None,
                "optional": True,
            },
            "seg_f": {
                "direction": "output",
                "invert": False,
                "pull": None,
                "optional": True,
            },
            "seg_g": {
                "direction": "output",
                "invert": False,
                "pull": None,
                "optional": True,
            },
        }
        self.INTERFACE = {
            "value": {
                "size": 16,
                "multiplexed": True,
                "direction": "output",
            },
        }
        self.SIGNALS = {
            "value": {
                "direction": "output",
                "min": 0,
                "max": 9999,
                "description": "number to display",
            },
        }
