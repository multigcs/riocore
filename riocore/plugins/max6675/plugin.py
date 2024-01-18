from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "max6675"
        self.VERILOGS = ["max6675.v"]
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
            },
            "sel": {
                "direction": "output",
                "invert": False,
                "pullup": False,
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
            },
        }

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
