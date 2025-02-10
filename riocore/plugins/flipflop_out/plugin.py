from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "flipflop_out"
        self.INFO = "flipflop output"
        self.DESCRIPTION = "set and reset an output pin"
        self.KEYWORDS = "sr-flipflop"
        self.ORIGIN = ""
        self.VERILOGS = ["flipflop_out.v"]
        self.PINDEFAULTS = {
            "bit": {
                "direction": "output",
            },
        }
        self.INTERFACE = {
            "set": {
                "size": 1,
                "direction": "output",
            },
            "reset": {
                "size": 1,
                "direction": "output",
            },
        }
        self.SIGNALS = {
            "set": {
                "direction": "output",
            },
            "reset": {
                "direction": "output",
            },
        }
        self.OPTIONS = {
            "default": {
                "default": 0,
                "type": bool,
                "unit": "",
                "description": "default value after startup",
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        default = self.plugin_setup.get("default", self.OPTIONS["default"]["default"])
        instance_parameter["DEFAULT"] = default
        return instances
