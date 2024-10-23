from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "lm75"
        self.INFO = "I2C Temperature-Sensor"
        self.DESCRIPTION = "simple temperature sensor"
        self.KEYWORDS = "analog adc temperature"
        self.ORIGIN = "https://learn.lushaylabs.com/i2c-adc-micro-procedures/#the-i2c-protocol"
        self.VERILOGS = ["lm75.v"]
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
            "temperature": {
                "size": 16,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "temperature": {
                "direction": "input",
                "unit": "°C",
            },
        }
