from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "pdmout"
        self.INFO = "pdm output"
        self.DESCRIPTION = "to analog values via sigma-delta modulator"
        self.KEYWORDS = "joint dcservo acservo 10v 5v dac analog sigma-delta pdm"
        self.ORIGIN = ""
        self.VERILOGS = ["pdmout.v"]
        self.TYPE = "joint"
        self.PINDEFAULTS = {
            "pdm": {
                "direction": "output",
            },
            "en": {
                "direction": "output",
                "optional": True,
            },
        }
        self.OPTIONS = {
            "resolution": {
                "default": 16,
                "type": int,
                "min": 8,
                "max": 32,
                "unit": "bit",
                "description": "PDM Resolution",
            },
        }
        self.INTERFACE = {
            "value": {
                "size": self.plugin_setup.get("resolution", self.OPTIONS["resolution"]["default"]),
                "direction": "output",
            },
            "enable": {
                "size": 1,
                "direction": "output",
                "on_error": False,
            },
        }
        self.SIGNALS = {
            "value": {
                "direction": "output",
                "min": 0,
                "max": 100,
                "unit": "%",
                "absolute": False,
                "setup": {
                    "min": {
                        "default": 0,
                        "type": int,
                        "min": -1000000,
                        "max": 1000000,
                        "unit": "",
                        "description": "minimum value (0%)",
                    },
                    "max": {
                        "default": 100,
                        "type": int,
                        "min": -1000000,
                        "max": 1000000,
                        "unit": "",
                        "description": "maximum value (100%)",
                    },
                },
            },
            "enable": {
                "direction": "output",
                "bool": True,
            },
        }
        if "dir" in self.plugin_setup.get("pins", {}):
            self.SIGNALS["value"]["min"] = -self.SIGNALS["value"]["max"]

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        resolution = int(self.plugin_setup.get("resolution", self.OPTIONS["resolution"]["default"]))
        instance_parameter["RESOLUTION"] = resolution
        return instances

