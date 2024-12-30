from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "hbridge"
        self.INFO = "hbridge output"
        self.DESCRIPTION = "to control DC-Motors"
        self.KEYWORDS = "joint dcservo"
        self.ORIGIN = ""
        self.VERILOGS = ["hbridge.v"]
        self.TYPE = "joint"
        self.PINDEFAULTS = {
            "out1": {
                "direction": "output",
            },
            "out2": {
                "direction": "output",
            },
            "en": {
                "direction": "output",
                "optional": True,
            },
        }
        self.OPTIONS = {
            "frequency": {
                "default": 10000,
                "type": int,
                "min": 10,
                "max": 1000000,
                "unit": "Hz",
                "description": "PWM frequency",
            },
        }
        self.INTERFACE = {
            "dty": {
                "size": 32,
                "direction": "output",
            },
            "enable": {
                "size": 1,
                "direction": "output",
                "on_error": False,
            },
        }
        self.SIGNALS = {
            "dty": {
                "direction": "output",
                "min": -100,
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
                        "description": "minimum value (0% dty)",
                    },
                    "max": {
                        "default": 100,
                        "type": int,
                        "min": -1000000,
                        "max": 1000000,
                        "unit": "",
                        "description": "maximum value (100% dty)",
                    },
                },
            },
            "enable": {
                "direction": "output",
                "bool": True,
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        freq = int(self.plugin_setup.get("frequency", self.OPTIONS["frequency"]["default"]))
        divider = self.system_setup["speed"] // freq
        instance_parameter["DIVIDER"] = divider
        return instances

    def convert(self, signal_name, signal_setup, value):
        if signal_name == "dty":
            freq = int(self.plugin_setup.get("frequency", self.OPTIONS["frequency"]["default"]))
            vmin = int(signal_setup.get("userconfig", {}).get("min", self.SIGNALS["dty"]["min"]))
            vmax = int(signal_setup.get("userconfig", {}).get("max", self.SIGNALS["dty"]["max"]))
            value = int((value) * (self.system_setup["speed"] / freq) / (vmax))
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "dty":
            freq = int(self.plugin_setup.get("frequency", self.OPTIONS["frequency"]["default"]))
            vmin = int(signal_setup.get("userconfig", {}).get("min", self.SIGNALS["dty"]["min"]))
            vmax = int(signal_setup.get("userconfig", {}).get("max", self.SIGNALS["dty"]["max"]))
            return f"value = value * (OSC_CLOCK / {freq}) / ({vmax});"
        return ""
