from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "max6675"
        self.VERILOGS = ["max6675.v"]
        self.PINDEFAULTS = {
            "miso": {
                "direction": "input",
                "invert": False,
                "pull": None,
            },
            "sclk": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
            "sel": {
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
        self.INFO = "SPI temperature sensor"
        self.DESCRIPTION = "to messurement very high temperatures of up to 1250 degrees Celsius"

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_predefines = instance["predefines"]
        instance_parameter = instance["parameter"]
        instance_arguments = instance["arguments"]
        # example
        # frequency = int(self.plugin_setup.get("frequency", 100))
        # divider = self.system_setup["speed"] // frequency
        # instance_parameter["DIVIDER"] = divider
        # instance_parameter["DIVIDER"] = self.plugin_setup.get("divider", "1000")
        return instances

    def convert(self, signal_name, signal_setup, value):
        value = value * 0.25
        return value

    def convert_c(self, signal_name, signal_setup):
        return """
        value = value * 0.25;
        """
