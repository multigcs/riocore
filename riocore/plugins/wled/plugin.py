from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "wled"
        self.INFO = "ws2812b interface"
        self.DESCRIPTION = "simple ws2812b led driver / you can only turn on/off each color (R/G/B) of each led"
        self.KEYWORDS = "led rgb status info"
        self.ORIGIN = "https://github.com/mattvenn/ws2812-core"
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
        num_leds = self.plugin_setup.get("leds", 1)
        for led in range(num_leds):
            for color in ("green", "blue", "red"):
                self.INTERFACE[f"{led}_{color}"] = {
                    "size": 1,
                    "direction": "output",
                }
                self.SIGNALS[f"{led}_{color}"] = {
                    "direction": "output",
                    "bool": True,
                }

    def cfg_info(self):
        num_leds = self.plugin_setup.get("leds", 1)
        level = self.plugin_setup.get("level", 127)
        return f"LED's: {num_leds}\nLevel: {level}"

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_predefines = instance["predefines"]
        instance_parameter = instance["parameter"]
        num_leds = self.plugin_setup.get("leds", 1)
        level = self.plugin_setup.get("level", 127)
        instance["arguments"] = {
            "clk": instance["arguments"]["clk"],
            "data": instance["arguments"]["data"],
            "green": f"{self.instances_name.upper()}_GREEN",
            "blue": f"{self.instances_name.upper()}_BLUE",
            "red": f"{self.instances_name.upper()}_RED",
        }
        instance_predefines.append(f"wire [{num_leds - 1}:0] {self.instances_name.upper()}_GREEN;")
        instance_predefines.append(f"wire [{num_leds - 1}:0] {self.instances_name.upper()}_BLUE;")
        instance_predefines.append(f"wire [{num_leds - 1}:0] {self.instances_name.upper()}_RED;")
        for led in range(num_leds):
            instance_predefines.append(f"assign {self.instances_name.upper()}_GREEN[{num_leds - led - 1}] = VAROUT1_{self.instances_name.upper()}_{led}_GREEN;")
            instance_predefines.append(f"assign {self.instances_name.upper()}_BLUE[{num_leds - led - 1}] = VAROUT1_{self.instances_name.upper()}_{led}_BLUE;")
            instance_predefines.append(f"assign {self.instances_name.upper()}_RED[{num_leds - led - 1}] = VAROUT1_{self.instances_name.upper()}_{led}_RED;")
        instance_parameter["NUM_LEDS"] = num_leds
        instance_parameter["LEVEL"] = level
        instance_parameter["CLK_MHZ"] = self.system_setup["speed"] // 1000000
        return instances
