from copy import deepcopy

from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "sinepwm"
        self.INFO = "sine pwm output"
        self.DESCRIPTION = "generates sine waves (multi phase support)"
        self.KEYWORDS = "sine wave pwm bldc stepper"
        self.ORIGIN = ""
        self.VERILOGS = ["sinepwm.v"]
        self.OPTIONS = {
            "pwmfreq": {
                "default": 25000,
                "type": int,
                "min": 10,
                "max": 100000,
                "unit": "Hz",
                "description": "pwm frequency",
            },
            "start": {
                "default": 0,
                "type": int,
                "min": 0,
                "max": 28,
                "unit": "",
                "description": "wace start point",
            },
            "phases": {
                "default": 1,
                "type": int,
                "min": 0,
                "max": 10,
                "unit": "",
                "description": "number of output phases",
            },
        }
        self.INTERFACE = {
            "freq": {
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
            "freq": {
                "direction": "output",
                "min": -255,
                "max": 255,
                "unit": "Hz",
                "absolute": False,
            },
            "enable": {
                "direction": "output",
                "bool": True,
            },
        }
        phases = self.plugin_setup.get("phases", self.OPTIONS["phases"]["default"])
        self.PINDEFAULTS = {
            "en": {
                "direction": "output",
                "optional": True,
            },
        }
        for phase in range(phases):
            self.PINDEFAULTS[f"out{phase}"] = {
                "direction": "output",
            }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        phases = self.plugin_setup.get("phases", self.OPTIONS["phases"]["default"])
        start = self.plugin_setup.get("start", self.OPTIONS["start"]["default"])
        pwmfreq = int(self.plugin_setup.get("pwmfreq", self.OPTIONS["pwmfreq"]["default"]))
        divider = self.system_setup["speed"] // pwmfreq // 512
        instance_parameter["DIVIDER"] = divider
        instance_parameter["START"] = start

        new_instances = {}
        new_instances["pre"] = {"predefines": instance["predefines"]}
        for ins in instances:
            if ins != self.instances_name:
                new_instances[ins] = instances[ins]

        for inst_n in range(phases):
            inst = f"{self.instances_name}_{inst_n}"
            new_instances[inst] = deepcopy(instance)
            new_instances[inst]["parameter"]["START"] = 30 // phases * inst_n
            for phase in range(phases):
                if inst_n == phase:
                    new_instances[inst]["arguments"]["pwm_out"] = instance["arguments"][f"out{phase}"]
                del new_instances[inst]["arguments"][f"out{phase}"]
            del new_instances[inst]["predefines"]

        return new_instances

    def convert(self, signal_name, signal_setup, value):
        if signal_name == "freq":
            if value != 0:
                value = int(self.system_setup["speed"] / value / 30)
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "freq":
            return """
    if (value != 0) {
        value = (OSC_CLOCK / value / 30);
    }
            """
        return ""
