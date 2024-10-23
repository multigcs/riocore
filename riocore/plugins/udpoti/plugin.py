from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "udpoti"
        self.INFO = "digital-poti with up/down+dir interface"
        self.DESCRIPTION = "controling digital poti for analog outputs"
        self.KEYWORDS = "analog dac poti"
        self.ORIGIN = ""
        self.VERILOGS = ["udpoti.v"]
        self.PINDEFAULTS = {
            "updown": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
            "increment": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
        }
        self.OPTIONS = {
            "resolution": {
                "default": 100,
                "type": int,
                "min": 0,
                "max": 255,
                "description": "number of steps from min to maximum value",
            },
            "frequency": {
                "default": 100,
                "type": int,
                "min": 0,
                "max": 100000,
                "unit": "Hz",
                "description": "interface frequency",
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
        instance["predefines"]
        instance_parameter = instance["parameter"]
        instance["arguments"]
        instance_parameter["RESOLUTION"] = self.plugin_setup.get("resolution", self.OPTIONS["resolution"]["default"])
        frequency = int(self.plugin_setup.get("frequency", self.OPTIONS["frequency"]["default"]))
        divider = self.system_setup["speed"] // frequency
        instance_parameter["DIVIDER"] = divider
        return instances
