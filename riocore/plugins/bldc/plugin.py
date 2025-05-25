import math

from riocore.plugins import PluginBase


class Plugin(PluginBase):
    table_len = 64  # sinus table

    def setup(self):
        self.NAME = "bldc"
        self.INFO = "BLDC FOC"
        self.DESCRIPTION = """to control BLDC Motors

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
        self.EXPERIMENTAL = True
        self.TYPE = "joint"
        self.VERILOGS = ["bldc.v"]
        self.OPTIONS = {
            "frequency": {
                "default": 50000,
                "type": int,
                "min": 10,
                "max": 200000,
                "unit": "Hz",
                "description": "PWM frequency",
            },
            "pwmmode": {
                "default": 0,
                "type": int,
                "min": 0,
                "max": 3,
                "unit": "Hz",
                "description": "PWM mode",
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
        self.PINDEFAULTS = {
            "u_p": {
                "direction": "output",
            },
            "v_p": {
                "direction": "output",
            },
            "w_p": {
                "direction": "output",
            },
            "u_n": {
                "direction": "output",
                "optional": True,
            },
            "v_n": {
                "direction": "output",
                "optional": True,
            },
            "w_n": {
                "direction": "output",
                "optional": True,
            },
            "en": {
                "direction": "output",
                "optional": True,
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
        # builing sinus table
        self.SINE_TBL = f"sine_{self.instances_name}.mem"
        self.TLEN_BITS = 6
        self.TDEPTH_BITS = 8
        table_len = 1 << (self.TLEN_BITS)
        tabel_res = 1 << (self.TDEPTH_BITS)
        half_res = (tabel_res // 2) - 1
        mem_data = []
        for n in range(table_len):
            val = half_res * math.sin(2 * n * math.pi / table_len) + half_res
            mem_data.append(f"{int(val):x}")
        mem_data.append("")
        self.VERILOGS_DATA = {
            self.SINE_TBL: "\n".join(mem_data),
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
        pwmmode = int(self.plugin_setup.get("pwmmode", self.OPTIONS["pwmmode"]["default"]))
        instance_parameter["PWMMODE"] = pwmmode
        instance_parameter["SINE_TBL"] = f'"{self.SINE_TBL}"'
        instance_parameter["TLEN_BITS"] = self.TLEN_BITS
        instance_parameter["TDEPTH_BITS"] = self.TDEPTH_BITS

        # internal feedback
        instance["arguments"]["feedback"] = self.plugin_setup.get("halsensor", self.OPTIONS["halsensor"]["default"])

        return instances
