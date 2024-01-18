from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "pwmout"
        self.VERILOGS = ["pwmout.v"]
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
                "absolute": False,
            },
            "enable": {
                "direction": "output",
                "bool": True,
            },
        }
        if "dir" in self.plugin_setup["pins"]:
            self.SIGNALS["dty"]["min"] = -self.SIGNALS["dty"]["max"]

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_predefines = instance["predefines"]
        instance_parameter = instance["parameter"]
        instance_arguments = instance["arguments"]
        freq = int(self.plugin_setup.get("frequency", 10000))
        divider = self.system_setup["speed"] // freq
        instance_parameter["DIVIDER"] = divider
        return instances

    def convert(self, signal_name, signal_setup, value):
        if signal_name == "dty":
            freq = int(self.plugin_setup.get("frequency", 10000))
            vmin = int(signal_setup.get("min", 0))
            vmax = int(signal_setup.get("max", 100))
            if "dir" in signal_setup:
                value = int((value) * (self.system_setup["speed"] / freq) / (vmax))
            else:
                value = int((value - vmin) * (self.system_setup["speed"] / freq) / (vmax - vmin))
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "dty":
            freq = int(self.plugin_setup.get("frequency", 10000))
            vmin = int(signal_setup.get("min", 0))
            vmax = int(signal_setup.get("max", 100))
            if "dir" in signal_setup:
                return f"value = value * (OSC_CLOCK / {freq}) / ({vmax});"
            else:
                return f"value = (value - {vmin}) * (OSC_CLOCK / {freq}) / ({vmax} - {vmin});"
        return ""
