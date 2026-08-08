from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "pwmin"
        self.INFO = "pwm input"
        self.DESCRIPTION = "measuring pulse len"
        self.KEYWORDS = "pulse digital"
        self.ORIGIN = ""
        self.NEEDS = ["fpga"]
        self.VERILOGS = ["pwmin.v"]
        self.PINDEFAULTS = {
            "pwm": {
                "direction": "input",
                "invert": False,
                "pull": None,
            },
        }
        self.OPTIONS = {
            "freq_min": {
                "default": 10,
                "type": int,
                "min": 1,
                "max": 10000,
                "unit": "Hz",
                "description": "minimum measured frequency (for faster updates)",
            },
            "servo_mode": {
                "default": False,
                "type": bool,
                "description": "servo-mode 1/2ms -> -100/100%",
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
                "format": "0.3f",
            },
            "valid": {
                "direction": "input",
                "bool": True,
            },
        }
        self.servo_mode = self.plugin_setup.get("servo_mode", self.OPTIONS["servo_mode"]["default"])
        if self.servo_mode:
            self.SIGNALS["width"]["unit"] = "%"
            self.SIGNALS["width"]["min"] = -130
            self.SIGNALS["width"]["max"] = 130
            self.SIGNALS["width"]["format"] = "0.1f"

    def gateware_instances(self, gateware=None):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance["predefines"]
        instance_parameter = instance["parameter"]
        instance["arguments"]
        freq_min = int(self.plugin_setup.get("freq_min", self.OPTIONS["freq_min"]["default"]))
        instance_parameter["RESET_CNT"] = self.system_setup["speed"] // freq_min
        return instances

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "width":
            if self.servo_mode:
                return """
                if (value != 0) {
                    value = 1000 / (OSC_CLOCK / value);
                    value = (value - 1.5) * 200.0;
                }
                """
            return """
            if (value != 0) {
                value = 1000 / (OSC_CLOCK / value);
            }
            """
        return ""
