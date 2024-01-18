from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "irin"
        self.VERILOGS = ["irin.v"]
        self.PINDEFAULTS = {
            "ir": {
                "direction": "input",
                "invert": False,
                "pullup": False,
            },
        }
        self.INTERFACE = {
            "code": {
                "size": 8,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "code": {
                "direction": "input",
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
        return value
