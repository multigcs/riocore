from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "hx710"
        self.INFO = "24bit adc"
        self.DESCRIPTION = "24bit adc (HX710B)"
        self.KEYWORDS = "adc analog"
        self.ORIGIN = ""
        self.VERILOGS = ["hx710.v"]
        self.PINDEFAULTS = {
            "miso": {
                "direction": "input",
                "invert": False,
                "pull": None,
            },
            "sclk": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
        }
        self.INTERFACE = {
            "pressure": {
                "size": 32,
                "direction": "input",
                "multiplexed": True,
            },
        }
        self.SIGNALS = {
            "pressure": {
                "direction": "input",
                "unit": "?",
                "format": "0.3f",
            },
        }
        self.OPTIONS = {
            "zero": {
                "default": 1379496,
                "type": int,
                "description": "zero value",
            },
            "scale": {
                "default": 0.00001,
                "type": float,
                "decimals": 5,
                "description": "scale value",
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance["predefines"]
        instance_parameter = instance["parameter"]
        instance["arguments"]
        # mode 0 == 25 pulses == diff in 10Hz
        # mode 1 == 26 pulses == temp 40Hz
        # mode 2 == 27 pulses == diff in 40Hz
        mode_num = 0

        instance_parameter["MODE"] = mode_num + 24
        divider = self.system_setup["speed"] // 1000000 // 2
        instance_parameter["DIVIDER"] = divider
        return instances

    def convert(self, signal_name, signal_setup, value):
        if (value & (1<<23)):
            value = value - 16777216
        scale = self.plugin_setup.get("scale", self.OPTIONS["scale"]["default"])
        zero = self.plugin_setup.get("zero", self.OPTIONS["zero"]["default"])
        value -= zero
        value *= scale
        print(value)
        return value

    def convert_c(self, signal_name, signal_setup):
        scale = self.plugin_setup.get("scale", self.OPTIONS["scale"]["default"])
        zero = self.plugin_setup.get("zero", self.OPTIONS["zero"]["default"])
        instances_name = self.instances_name.upper()
        return f"""
            if (((uint32_t)value & (1<<23))) {{
                value = value - 16777216;
            }}
            value -= {zero};
            value *= {scale};
        """
