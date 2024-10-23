from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "tlc549c"
        self.INFO = "spi adc input"
        self.DESCRIPTION = "Analog input via tlc549 ADC"
        self.KEYWORDS = "analog adc"
        self.ORIGIN = ""
        self.VERILOGS = ["tlc549c.v"]
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
            "value": {
                "size": 8,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "value": {
                "direction": "input",
                "unit": "Volt",
                "description": "measured voltage",
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        divider = self.system_setup["speed"] // 1000000 // 2
        instance_parameter["DIVIDER"] = divider
        return instances

    def convert(self, signal_name, signal_setup, value):
        value = value * 3.3 / 255.0
        return value

    def convert_c(self, signal_name, signal_setup):
        return """
        value = value * 3.3 / 255.0;
        """
