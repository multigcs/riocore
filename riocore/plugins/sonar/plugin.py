from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "sonar"
        self.VERILOGS = ["sonar.v"]
        self.PINDEFAULTS = {
            "trigger": {
                "direction": "output",
                "invert": False,
                "pullup": False,
            },
            "echo": {
                "direction": "input",
                "invert": False,
                "pullup": False,
            },
        }
        self.INTERFACE = {
            "distance": {
                "size": 32,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "distance": {
                "direction": "input",
                "format": "0.2f",
                "unit": "cm",
            },
        }

    def convert(self, signal_name, signal_setup, value):
        if value != 0:
            value = 1000 / self.system_setup["speed"] / 20 * value * 343.2
        return value

    def convert_c(self, signal_name, signal_setup):
        return f"""
        value = 1000 / OSC_CLOCK / 20 * value * 343.2;
        """
