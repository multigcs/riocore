from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "as5600"
        self.INFO = "magnetic absolute encoder"
        self.DESCRIPTION = "for position feedbacks"
        self.KEYWORDS = "encoder scale feedback absolute"
        self.ORIGIN = "https://learn.lushaylabs.com/i2c-adc-micro-procedures/#the-i2c-protocol"
        self.VERILOGS = ["as5600.v"]
        self.PINDEFAULTS = {
            "sda": {
                "direction": "inout",
                "invert": False,
                "pull": None,
            },
            "scl": {
                "direction": "output",
                "invert": False,
                "pull": None,
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
