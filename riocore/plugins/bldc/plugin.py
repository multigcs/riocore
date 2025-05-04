from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "bldc"
        self.INFO = "BLDC FOC"
        self.DESCRIPTION = "to control BLDC Motors - experimental"
        self.KEYWORDS = "joint brushless"
        self.ORIGIN = ""
        self.VERILOGS = ["bldc.v"]
        self.TYPE = "joint"
        self.PINDEFAULTS = {
            "u": {
                "direction": "output",
            },
            "v": {
                "direction": "output",
            },
            "w": {
                "direction": "output",
            },
            "en": {
                "direction": "output",
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
            "halsensor": {
                "default": "",
                "type": str,
                "unit": "",
                "description": "encoder instance",
            },
            "poles": {
                "default": 4,
                "type": int,
                "min": 2,
                "max": 100,
                "unit": "",
                "description": "motor poles",
            },
            "feedback_res": {
                "default": 4096,
                "type": int,
                "min": 10,
                "max": 100000,
                "unit": "",
                "description": "encoder resolution",
            },
        }
        self.INTERFACE = {
            "velocity": {
                "size": 16,
                "direction": "output",
            },
            "offset": {
                "size": 8,
                "direction": "output",
            },
            "torque": {
                "size": 8,
                "direction": "output",
            },
            "enable": {
                "size": 1,
                "direction": "output",
                "_on_error": False,
            },
            "testmode": {
                "size": 1,
                "direction": "output",
            },
        }
        self.SIGNALS = {
            "velocity": {
                "direction": "output",
                "min": -100,
                "max": 100,
                "unit": "%",
            },
            "offset": {
                "direction": "output",
                "min": -63,
                "max": 63,
                "unit": "%",
            },
            "torque": {
                "direction": "output",
                "min": 0,
                "max": 15,
                "unit": "",
            },
            "enable": {
                "direction": "output",
                "bool": True,
            },
            "testmode": {
                "direction": "output",
                "bool": True,
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]

        poles = int(self.plugin_setup.get("poles", self.OPTIONS["poles"]["default"]))
        feedback_res = int(self.plugin_setup.get("feedback_res", self.OPTIONS["feedback_res"]["default"]))
        table_len = 64 # sinus table
        feedback_divider = feedback_res / poles / table_len
        instance_parameter["FEEDBACK_DIVIDER"] = int(feedback_divider)
        frequency = int(self.plugin_setup.get("frequency", self.OPTIONS["frequency"]["default"]))
        divider = self.system_setup["speed"] // frequency // 512
        instance_parameter["DIVIDER"] = int(divider)

        # internal feedback
        instance["arguments"]["feedback"] = self.plugin_setup.get("halsensor", self.OPTIONS["halsensor"]["default"])

        return instances
