import math

from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "bldc"
        self.INFO = "BLDC FOC"
        self.DESCRIPTION = """to control BLDC Motors

Motor-Setup:
* set motor poles and encoder resolution in the options
* start rio-test gui
* set mode to calibration (2)
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
            "sine_len": {
                "default": 6,
                "type": int,
                "min": 4,
                "max": 12,
                "unit": "bits",
                "description": "sinus table lenght in bits",
            },
            "sine_res": {
                "default": 0,
                "type": int,
                "min": 8,
                "max": 16,
                "unit": "bits",
                "description": "sinus table lenght in bits (0 = auto)",
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

        self.poles = int(self.plugin_setup.get("poles", self.OPTIONS["poles"]["default"]))
        self.feedback_res = int(self.plugin_setup.get("feedback_res", self.OPTIONS["feedback_res"]["default"]))

        self.SINE_TBL = f"sine_{self.instances_name}.mem"
        self.SINE_LEN_BITS = int(self.plugin_setup.get("sine_len", self.OPTIONS["sine_len"]["default"]))
        self.SINE_RES_BITS = int(self.plugin_setup.get("sine_res", self.OPTIONS["sine_res"]["default"]))

        if self.SINE_LEN_BITS == 0:
            optimum_sine_len = self.feedback_res / self.poles
            self.SINE_LEN_BITS = int(math.log(optimum_sine_len, 2))

        # building sinus table
        self.sine_len = 1 << (self.SINE_LEN_BITS)
        self.table_len = 1 << (self.SINE_LEN_BITS - 1)
        tabel_res = 1 << (self.SINE_RES_BITS)
        half_res = (tabel_res // 2) - 1
        mem_data = []
        for n in range(self.table_len):
            val = half_res * math.sin(2 * n * math.pi / self.sine_len)
            if val < 0:
                val *= -1
            mem_data.append(f"{int(val):x}")

        mem_data.append("")
        self.VERILOGS_DATA = {
            self.SINE_TBL: "\n".join(mem_data),
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
                "size": 16,
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
        self.vel_range = 256
        self.SIGNALS = {
            "velocity": {
                "direction": "output",
                "min": -self.vel_range + 1,
                "max": self.vel_range - 1,
                "unit": "%",
            },
            "offset": {
                "direction": "output",
                "min": -self.sine_len,
                "max": self.sine_len,
                "unit": "",
            },
            "enable": {
                "direction": "output",
                "bool": True,
            },
            "mode": {
                "direction": "output",
                "titles": ["VELOCITY", "POSITION", "CALIBRATION"],
                "min": 0,
                "max": 2,
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]

        feedback_divider = self.feedback_res / self.poles / self.sine_len
        instance_parameter["FEEDBACK_DIVIDER"] = int(feedback_divider)

        # velocity range 0->(VEL_RANGE-1)
        instance_parameter["VEL_RANGE"] = self.vel_range

        # pwm frequency divider (clock / freq / (2*range))
        frequency = int(self.plugin_setup.get("frequency", self.OPTIONS["frequency"]["default"]))
        divider = self.system_setup["speed"] // frequency // ((1 << self.SINE_RES_BITS) * 2)
        instance_parameter["PWM_DIVIDER"] = int(divider)

        instance_parameter["SINE_TBL"] = f'"{self.SINE_TBL}"'
        instance_parameter["SINE_LEN_BITS"] = self.SINE_LEN_BITS
        instance_parameter["SINE_RES_BITS"] = self.SINE_RES_BITS

        # internal feedback
        instance["arguments"]["feedback"] = self.plugin_setup.get("halsensor", self.OPTIONS["halsensor"]["default"])

        return instances
