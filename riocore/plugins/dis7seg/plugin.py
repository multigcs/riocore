from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "dis7seg"
        self.VERILOGS = ["dis7seg.v"]
        self.PINDEFAULTS = {
            "en1": {
                "direction": "output",
                "invert": False,
                "pullup": False,
            },
            "en2": {
                "direction": "output",
                "invert": False,
                "pullup": False,
            },
            "en3": {
                "direction": "output",
                "invert": False,
                "pullup": False,
            },
            "en4": {
                "direction": "output",
                "invert": False,
                "pullup": False,
            },
            "seg_a": {
                "direction": "output",
                "invert": False,
                "pullup": False,
                "optional": True,
            },
            "seg_b": {
                "direction": "output",
                "invert": False,
                "pullup": False,
                "optional": True,
            },
            "seg_c": {
                "direction": "output",
                "invert": False,
                "pullup": False,
                "optional": True,
            },
            "seg_d": {
                "direction": "output",
                "invert": False,
                "pullup": False,
                "optional": True,
            },
            "seg_e": {
                "direction": "output",
                "invert": False,
                "pullup": False,
                "optional": True,
            },
            "seg_f": {
                "direction": "output",
                "invert": False,
                "pullup": False,
                "optional": True,
            },
            "seg_g": {
                "direction": "output",
                "invert": False,
                "pullup": False,
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
            },
        }
