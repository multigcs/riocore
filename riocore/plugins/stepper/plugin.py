from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "stepper"
        self.INFO = "stepper driver output for H-Bridges like L298"
        self.DESCRIPTION = "direct stepper driver with 4pin's directly controlled by the FPGA"
        self.KEYWORDS = "stepper joint hbridge"
        self.ORIGIN = ""
        self.VERILOGS = ["stepper.v"]
        self.TYPE = "joint"
        self.PINDEFAULTS = {
            "a1": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
            "a2": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
            "b1": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
            "b2": {
                "direction": "output",
                "invert": False,
                "pull": None,
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
                "min": -1000000,
                "max": 1000000,
                "unit": "Hz",
                "description": "speed in steps per second",
            },
            "position": {
                "direction": "input",
                "unit": "Steps",
                "scale": 320.0,
                "description": "position feedback",
            },
            "enable": {
                "direction": "output",
                "bool": True,
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance["predefines"]
        instance_parameter = instance["parameter"]
        instance["arguments"]
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
