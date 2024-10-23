from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "wled"
        self.INFO = "ws2812b interface acting as an expansion port"
        self.DESCRIPTION = "simple ws2812b led driver / same as the wled plugin but integrated as an expansion to combinate with other plugins"
        self.KEYWORDS = "expansion led rgb status info"
        self.ORIGIN = "https://github.com/mattvenn/ws2812-core"
        self.TYPE = "expansion"
        self.VERILOGS = ["ws2812.v", "wled.v"]
        self.PINDEFAULTS = {
            "data": {
                "direction": "output",
            },
        }
        self.OPTIONS = {
            "leds": {
                "default": 1,
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

    def gateware_defines(self, direct=False):
        defines = []
        num_leds = self.plugin_setup.get("leds", 1)
        defines.append(f"wire [{num_leds-1}:0] {self.expansion_prefix}_GREEN;")
        defines.append(f"wire [{num_leds-1}:0] {self.expansion_prefix}_BLUE;")
        defines.append(f"wire [{num_leds-1}:0] {self.expansion_prefix}_RED;")

        return defines

    def expansion_outputs(self):
        expansion_pins = []
        num_leds = self.plugin_setup.get("leds", 1)
        for led in range(num_leds):
            expansion_pins.append(f"{self.expansion_prefix}_GREEN[{num_leds-led-1}]")
            expansion_pins.append(f"{self.expansion_prefix}_BLUE[{num_leds-led-1}]")
            expansion_pins.append(f"{self.expansion_prefix}_RED[{num_leds-led-1}]")
        return expansion_pins

    def expansion_inputs(self):
        return []

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance["predefines"]
        instance_parameter = instance["parameter"]
        num_leds = self.plugin_setup.get("leds", 1)
        level = self.plugin_setup.get("level", 127)
        instance["arguments"] = {
            "clk": instance["arguments"]["clk"],
            "data": instance["arguments"]["data"],
            "green": f"{self.expansion_prefix}_GREEN",
            "blue": f"{self.expansion_prefix}_BLUE",
            "red": f"{self.expansion_prefix}_RED",
        }
        instance_parameter["NUM_LEDS"] = num_leds
        instance_parameter["LEVEL"] = level
        instance_parameter["CLK_MHZ"] = self.system_setup["speed"] // 1000000
        return instances
