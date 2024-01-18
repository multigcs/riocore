from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "stepper"
        self.VERILOGS = ["stepper.v"]
        self.PINDEFAULTS = {
            "a1": {
                "direction": "output",
                "invert": False,
                "pullup": False,
            },
            "a2": {
                "direction": "output",
                "invert": False,
                "pullup": False,
            },
            "b1": {
                "direction": "output",
                "invert": False,
                "pullup": False,
            },
            "b2": {
                "direction": "output",
                "invert": False,
                "pullup": False,
            },
        }
        self.INTERFACE = {
            "velocity": {
                "size": 32,
                "direction": "output",
            },
            "position": {
                "size": 32,
                "direction": "input",
            },
            "enable": {
                "direction": "output",
                "size": 1,
            },
        }
        self.SIGNALS = {
            "velocity": {
                "direction": "output",
            },
            "position": {
                "direction": "input",
            },
            "enable": {
                "direction": "output",
                "bool": True,
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_predefines = instance["predefines"]
        instance_parameter = instance["parameter"]
        instance_arguments = instance["arguments"]
        instance_parameter["STEPTYPE"] = self.plugin_setup.get("steptype", "1")
        return instances

    def convert(self, signal_name, signal_setup, value):
        if signal_name == "velocity":
            if value != 0:
                value = self.system_setup["speed"] / value / 2
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "velocity":
            return """
            if (value != 0) {
                value = OSC_CLOCK / value / 2;
            }
            """
        return ""
