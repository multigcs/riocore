from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "tlc549c"
        self.VERILOGS = ["tlc549c.v"]
        self.PINDEFAULTS = {
            "miso": {
                "direction": "input",
                "invert": False,
                "pullup": False,
            },
            "sclk": {
                "direction": "output",
                "invert": False,
                "pullup": False,
                "optional": True,
            },
            "sel": {
                "direction": "output",
                "invert": False,
                "pullup": False,
                "optional": True,
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
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()

        instance = instances[self.instances_name]
        instance_predefines = instance["predefines"]
        instance_parameter = instance["parameter"]
        instance_arguments = instance["arguments"]

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
