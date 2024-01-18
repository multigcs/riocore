from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "wled"
        self.VERILOGS = ["ws2812.v", "wled.v"]
        self.PINDEFAULTS = {
            "data": {
                "direction": "output",
                "invert": False,
                "pullup": False,
            },
        }
        self.OPTIONS = {
            "leds": {
                "default": 1,
                "type": int,
            },
            "level": {
                "default": 127,
                "type": int,
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
            "green": f"WLED{self.plugin_id}_GREEN",
            "blue": f"WLED{self.plugin_id}_BLUE",
            "red": f"WLED{self.plugin_id}_RED",
        }
        instance_predefines.append(f"wire [{num_leds-1}:0] WLED{self.plugin_id}_GREEN;")
        instance_predefines.append(f"wire [{num_leds-1}:0] WLED{self.plugin_id}_BLUE;")
        instance_predefines.append(f"wire [{num_leds-1}:0] WLED{self.plugin_id}_RED;")
        for led in range(num_leds):
            instance_predefines.append(f"assign WLED{self.plugin_id}_GREEN[{num_leds-led-1}] = VAROUT1_WLED{self.plugin_id}_{led}_GREEN;")
            instance_predefines.append(f"assign WLED{self.plugin_id}_BLUE[{num_leds-led-1}] = VAROUT1_WLED{self.plugin_id}_{led}_BLUE;")
            instance_predefines.append(f"assign WLED{self.plugin_id}_RED[{num_leds-led-1}] = VAROUT1_WLED{self.plugin_id}_{led}_RED;")
        instance_parameter["NUM_LEDS"] = num_leds
        instance_parameter["LEVEL"] = level
        instance_parameter["CLK_MHZ"] = self.system_setup["speed"] // 1000000
        return instances
