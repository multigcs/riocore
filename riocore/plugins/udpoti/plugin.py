from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "udpoti"
        self.VERILOGS = ["udpoti.v"]
        self.PINDEFAULTS = {
            "updown": {
                "direction": "output",
                "invert": False,
                "pullup": False,
            },
            "increment": {
                "direction": "output",
                "invert": False,
                "pullup": False,
            },
        }
        self.INTERFACE = {
            "value": {
                "size": 32,
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
        instance_parameter["RESOLUTION"] = self.plugin_setup.get("resolution", "100")
        frequency = int(self.plugin_setup.get("frequency", 100))
        divider = self.system_setup["speed"] // frequency
        instance_parameter["DIVIDER"] = divider
        return instances
