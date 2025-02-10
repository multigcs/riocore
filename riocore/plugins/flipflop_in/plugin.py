from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "flipflop_in"
        self.INFO = "flipflop input"
        self.DESCRIPTION = "set and reset an input bit"
        self.KEYWORDS = "sr-flipflop"
        self.ORIGIN = ""
        self.VERILOGS = ["flipflop_in.v"]
        self.PINDEFAULTS = {
            "set": {
                "direction": "input",
            },
            "reset": {
                "direction": "input",
            },
        }
        self.INTERFACE = {
            "bit": {
                "size": 1,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "bit": {
                "direction": "input",
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
