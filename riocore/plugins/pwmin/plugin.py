from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "pwmin"
        self.VERILOGS = ["pwmin.v"]
        self.PINDEFAULTS = {
            "pwm": {
                "direction": "input",
                "invert": False,
                "pullup": False,
            },
        }
        self.INTERFACE = {
            "width": {
                "size": 32,
                "direction": "input",
            },
            "valid": {
                "size": 1,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "width": {
                "direction": "input",
                "unit": "ms",
                "format": "0.4f",
            },
            "valid": {
                "direction": "input",
                "bool": True,
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_predefines = instance["predefines"]
        instance_parameter = instance["parameter"]
        instance_arguments = instance["arguments"]
        freq_min = int(self.plugin_setup.get("freq_min", 10))
        instance_parameter["RESET_CNT"] = self.system_setup["speed"] // freq_min
        return instances

    def convert(self, signal_name, signal_setup, value):
        if signal_name == "width":
            if value != 0:
                value = 1000 / (self.system_setup["speed"] / value)
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "width":
            return """
            if (value != 0) {
                value = 1000 / (OSC_CLOCK / value);
            }
            """
        return ""
