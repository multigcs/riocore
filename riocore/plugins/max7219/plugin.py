from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "max7219"
        self.VERILOGS = ["max7219.v"]
        self.PINDEFAULTS = {
            "mosi": {
                "direction": "output",
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
            "value": {
                "size": 8,
                "direction": "output",
            },
        }
        self.SIGNALS = {
            "value": {
                "direction": "output",
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_predefines = instance["predefines"]
        instance_parameter = instance["parameter"]
        instance_arguments = instance["arguments"]
        # instance_parameter["WIDTH"] = self.plugin_setup.get("width", "8")
        # example
        # frequency = int(self.plugin_setup.get("frequency", 100))
        # divider = self.system_setup["speed"] // frequency
        # instance_parameter["DIVIDER"] = divider
        # instance_parameter["DIVIDER"] = self.plugin_setup.get("divider", "100000")
        return instances
