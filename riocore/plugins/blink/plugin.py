from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "blink"
        self.VERILOGS = ["blink.v"]
        self.PINDEFAULTS = {
            "led": {
                "direction": "output",
                "invert": False,
                "pullup": False,
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_predefines = instance["predefines"]
        instance_parameter = instance["parameter"]
        instance_arguments = instance["arguments"]
        freq = int(self.plugin_setup.get("frequency", 1))
        divider = self.system_setup["speed"] // freq // 2
        instance_parameter["DIVIDER"] = divider
        return instances
