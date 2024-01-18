from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "ads1115"
        self.VERILOGS = ["ads1115.v"]
        self.PINDEFAULTS = {
            "sda": {
                "direction": "inout",
                "invert": False,
                "pullup": True,
            },
            "scl": {
                "direction": "output",
                "invert": False,
                "pullup": True,
            },
        }
        self.INTERFACE = {
            "adc0": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            "adc1": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            "adc2": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
            "adc3": {
                "size": 16,
                "direction": "input",
                "multiplexed": True,
            },
        }
        self.SIGNALS = {
            "adc0": {
                "direction": "input",
                "format": "0.3f",
                "unit": "Volt",
            },
            "adc1": {
                "direction": "input",
                "format": "0.3f",
                "unit": "Volt",
            },
            "adc2": {
                "direction": "input",
                "format": "0.3f",
                "unit": "Volt",
            },
            "adc3": {
                "direction": "input",
                "format": "0.3f",
                "unit": "Volt",
            },
        }

    def convert(self, signal_name, signal_setup, value):
        value /= 1000.0
        if signal_setup.get("sensor") == "NTC":
            Rt = 10.0 * value / (3.3 - value)
            tempK = 1.0 / (math.log(Rt / 10.0) / 3950.0 + 1.0 / (273.15 + 25.0))
            tempC = tempK - 273.15
            value = tempC
        return value
