from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "hx711"
        self.INFO = "digital weight sensor"
        self.DESCRIPTION = "to measure weight's"
        self.KEYWORDS = "adc analog weight"
        self.ORIGIN = ""
        self.VERILOGS = ["hx711.v"]
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
            "weight": {
                "size": 32,
                "direction": "input",
                "multiplexed": True,
            },
        }
        self.SIGNALS = {
            "weight": {
                "direction": "input",
                "unit": "Kg",
                "format": "0.3f",
            },
            "tare": {
                "direction": "input",
                "bool": True,
                "virtual": True,
                "component": True,
            },
            "toffset": {
                "direction": "output",
                "virtual": True,
                "component": True,
            },
        }
        self.OPTIONS = {
            "zero": {
                "default": 0,
                "type": int,
                "description": "zero value",
            },
            "scale": {
                "default": 1.0,
                "type": float,
                "decimals": 5,
                "description": "scale value",
            },
            "mode": {
                "default": "CHA_128",
                "type": "select",
                "options": ["CHA_128", "CHB_32", "CHB_64"],
                "description": "sensor mode",
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance["predefines"]
        instance_parameter = instance["parameter"]
        instance["arguments"]
        mode = self.plugin_setup.get("mode", self.OPTIONS["mode"]["default"])
        mode_num = self.OPTIONS["mode"]["options"].index(mode)
        instance_parameter["MODE"] = mode_num + 24
        divider = self.system_setup["speed"] // 1000000 // 2
        instance_parameter["DIVIDER"] = divider
        return instances

    def convert(self, signal_name, signal_setup, value):
        scale = self.plugin_setup.get("scale", self.OPTIONS["scale"]["default"])
        zero = self.plugin_setup.get("zero", self.OPTIONS["zero"]["default"])
        value -= zero
        if self.SIGNALS["tare"]["value"] == 1:
            self.SIGNALS["toffset"]["value"] = value
        value -= self.SIGNALS["toffset"]["value"]
        value *= scale
        return value

    def convert_c(self, signal_name, signal_setup):
        scale = self.plugin_setup.get("scale", self.OPTIONS["scale"]["default"])
        zero = self.plugin_setup.get("zero", self.OPTIONS["zero"]["default"])
        instances_name = self.instances_name.upper()
        return f"""
            value -= {zero};
            if (*data->SIGIN_{instances_name}_TARE == 1) {{
                *data->SIGOUT_{instances_name}_TOFFSET = value;
            }}
            value -= *data->SIGOUT_{instances_name}_TOFFSET;
            value *= {scale};
        """
