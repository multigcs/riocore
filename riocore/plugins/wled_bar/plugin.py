from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "wled_bar"
        self.INFO = "ws2812b interface for bar-displays"
        self.DESCRIPTION = "simple ws2812b driver with variable input to build led-bars"
        self.KEYWORDS = "led rgb status info"
        self.ORIGIN = "https://github.com/mattvenn/ws2812-core"
        self.VERILOGS = ["ws2812.v", "wled_bar.v"]
        self.PINDEFAULTS = {
            "data": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
        }
        self.OPTIONS = {
            "leds": {
                "default": 12,
                "type": int,
                "min": 0,
                "max": 100,
                "description": "number of LED's",
            },
            "level": {
                "default": 127,
                "type": int,
                "min": 0,
                "max": 255,
                "description": "LED brighness",
            },
        }
        self.INTERFACE = {
            "value": {
                "size": 8,
                "direction": "output",
            },
        }
        self.SIGNALS = {
            "value": {
                "direction": "output",
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance["predefines"]
        instance_parameter = instance["parameter"]
        num_leds = self.plugin_setup.get("leds", 12)
        level = self.plugin_setup.get("level", 127)
        instance_parameter["NUM_LEDS"] = num_leds
        instance_parameter["LEVEL"] = level
        instance_parameter["CLK_MHZ"] = self.system_setup["speed"] // 1000000
        return instances

    def convert(self, signal_name, signal_setup, value):
        if signal_name == "value":
            num_leds = self.plugin_setup.get("leds", 12)
            vmin = self.plugin_setup.get("min", 0)
            vmax = self.plugin_setup.get("max", num_leds)
            scale = self.plugin_setup.get("scale", 1.0)
            if scale is not None:
                value *= scale
            if value < vmin:
                value = vmin
            if value > vmax:
                value = vmax
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "value":
            num_leds = self.plugin_setup.get("leds", 12)
            vmin = self.plugin_setup.get("min", 0)
            vmax = self.plugin_setup.get("max", num_leds)
            scale = self.plugin_setup.get("scale", 1.0)
            print("scale", scale, signal_setup)
            return f"""
            value *= {scale};
            if (value < {vmin}) {{
                value = {vmin};
            }} else if (value > {vmax}) {{
                value = {vmax};
            }}
            """
        return ""
