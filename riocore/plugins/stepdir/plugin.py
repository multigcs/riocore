from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "stepdir"
        self.INFO = "step/dir output for stepper drivers"
        self.DESCRIPTION = "to control motor drivers via step/dir pin's and an optional enable pin"
        self.KEYWORDS = "stepper servo joint"
        self.ORIGIN = ""
        self.VERILOGS = ["stepdir.v"]
        self.TYPE = "joint"
        self.PINDEFAULTS = {
            "step": {
                "direction": "output",
            },
            "dir": {
                "direction": "output",
            },
            "en": {
                "direction": "output",
                "optional": True,
            },
        }
        self.INTERFACE = {
            "velocity": {
                "size": 32,
                "direction": "output",
            },
            "enable": {
                "size": 1,
                "direction": "output",
                "on_error": False,
            },
            "position": {
                "size": 32,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "velocity": {
                "direction": "output",
                "min": -100000,
                "max": 100000,
                "unit": "Hz",
                "absolute": False,
                "description": "speed in steps per second",
            },
            "position": {
                "direction": "input",
                "unit": "steps",
                "absolute": False,
                "description": "position feedback",
            },
            "enable": {
                "direction": "output",
                "bool": True,
            },
        }
        self.OPTIONS = {
            "pulse_len": {
                "default": 4.0,
                "type": float,
                "min": 0.0,
                "max": 1000.0,
                "unit": "us",
                "description": "step pulse len",
            },
            "dir_delay": {
                "default": 0.7,
                "type": float,
                "min": 0.1,
                "max": 1000.0,
                "unit": "us",
                "description": "delay after dir change",
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        pulse_len = self.plugin_setup.get("pulse_len", self.OPTIONS["pulse_len"]["default"])
        instance_parameter["PULSE_LEN"] = int(self.system_setup["speed"] * pulse_len / 1000000)
        if instance_parameter["PULSE_LEN"] == 0 and pulse_len > 0:
            instance_parameter["PULSE_LEN"] = 1
        dir_delay = self.plugin_setup.get("dir_delay", self.OPTIONS["dir_delay"]["default"])
        instance_parameter["DIR_DELAY"] = int(self.system_setup["speed"] * dir_delay / 1000000)
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
