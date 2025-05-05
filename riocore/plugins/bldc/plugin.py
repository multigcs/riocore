from riocore.plugins import PluginBase


class Plugin(PluginBase):
    table_len = 64  # sinus table

    def setup(self):
        self.NAME = "bldc"
        self.INFO = "BLDC FOC"
        self.DESCRIPTION = """to control BLDC Motors - experimental

Motor-Setup:
* set motor poles and encoder resolution in the options
* start rio-test gui
* set mode to calibration (1)
* set enable
* set velocity to ~30% (warning: motor will start to spin !)
* adjust the offset until the motor stop's (should between -15<->15)
* add the offset value to your json config
```
    "signals": {
        "offset": {
            "setp": "-11"
        }
    }
```



        """
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
                "multiplexed": True,
            },
            "enable": {
                "size": 1,
                "direction": "output",
                "on_error": False,
            },
            "mode": {
                "size": 8,
                "direction": "output",
                "multiplexed": True,
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
                "min": -self.table_len,
                "max": self.table_len,
                "unit": "",
            },
            "enable": {
                "direction": "output",
                "bool": True,
            },
            "mode": {
                "direction": "output",
                "min": 0,
                "max": 3,
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]

        poles = int(self.plugin_setup.get("poles", self.OPTIONS["poles"]["default"]))
        feedback_res = int(self.plugin_setup.get("feedback_res", self.OPTIONS["feedback_res"]["default"]))
        feedback_divider = feedback_res / poles / self.table_len
        instance_parameter["FEEDBACK_DIVIDER"] = int(feedback_divider)
        frequency = int(self.plugin_setup.get("frequency", self.OPTIONS["frequency"]["default"]))
        divider = self.system_setup["speed"] // frequency // 512
        instance_parameter["DIVIDER"] = int(divider)

        # internal feedback
        instance["arguments"]["feedback"] = self.plugin_setup.get("halsensor", self.OPTIONS["halsensor"]["default"])

        return instances
