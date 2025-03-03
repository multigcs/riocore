from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "sonar"
        self.INFO = "sonar sensor for distance measurement"
        self.DESCRIPTION = "to messure distance via cheap ultra-sonic sensors (like filling level of bigger water tanks)"
        self.KEYWORDS = "distance ultrasonic level oil water"
        self.ORIGIN = ""
        self.VERILOGS = ["sonar.v"]
        self.PINDEFAULTS = {
            "trigger": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
            "echo": {
                "direction": "input",
                "invert": False,
                "pull": None,
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
                "description": "distance between sensor and object",
            },
        }

    def convert(self, signal_name, signal_setup, value):
        if value != 0:
            value = 1000 / self.system_setup["speed"] / 20 * value * 343.2
        return value

    def convert_c(self, signal_name, signal_setup):
        return """
        value = 1000 / OSC_CLOCK / 20 * value * 343.2;
        """
