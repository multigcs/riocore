from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "pwmout"
        self.INFO = "pwm output"
        self.DESCRIPTION = "to control AC/DC-Motors or for analog outputs"
        self.KEYWORDS = "joint dcservo acservo 10v 5v dac analog"
        self.ORIGIN = ""
        self.VERILOGS = ["pwmout.v"]
        self.TYPE = "joint"
        self.PINDEFAULTS = {
            "pwm": {
                "direction": "output",
            },
            "dir": {
                "direction": "output",
                "optional": True,
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
        if "dir" in self.plugin_setup.get("pins", {}):
            self.SIGNALS["dty"]["min"] = -self.SIGNALS["dty"]["max"]

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance["predefines"]
        instance_parameter = instance["parameter"]
        instance["arguments"]
        freq = int(self.plugin_setup.get("frequency", self.OPTIONS["frequency"]["default"]))
        divider = self.system_setup["speed"] // freq
        instance_parameter["DIVIDER"] = divider
        return instances

    def convert(self, signal_name, signal_setup, value):
        if signal_name == "dty":
            freq = int(self.plugin_setup.get("frequency", self.OPTIONS["frequency"]["default"]))
            vmin = int(signal_setup.get("userconfig", {}).get("min", self.SIGNALS["dty"]["min"]))
            vmax = int(signal_setup.get("userconfig", {}).get("max", self.SIGNALS["dty"]["max"]))
            if "dir" in self.plugin_setup.get("pins", {}):
                value = int((value) * (self.system_setup["speed"] / freq) / (vmax))
            else:
                value = int((value - vmin) * (self.system_setup["speed"] / freq) / (vmax - vmin))
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "dty":
            freq = int(self.plugin_setup.get("frequency", self.OPTIONS["frequency"]["default"]))
            vmin = int(signal_setup.get("userconfig", {}).get("min", self.SIGNALS["dty"]["min"]))
            vmax = int(signal_setup.get("userconfig", {}).get("max", self.SIGNALS["dty"]["max"]))
            if "dir" in self.plugin_setup.get("pins", {}):
                return f"value = value * (OSC_CLOCK / {freq}) / ({vmax});"
            else:
                return f"value = (value - {vmin}) * (OSC_CLOCK / {freq}) / ({vmax} - {vmin});"
        return ""
