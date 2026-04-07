from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "max7219"
        self.INFO = "7segment display based on max7219"
        self.KEYWORDS = "info display"
        self.DESCRIPTION = "to display values on 7segment display's (needs 5V power)"
        self.NEEDS = ["fpga"]
        self.IMAGE_SHOW = True
        self.IMAGE = "image.png"
        self.ORIGIN = ""
        self.VERILOGS = ["max7219.v"]
        self.PINDEFAULTS = {
            "mosi": {
                "direction": "output",
                "pull": None,
                "pos": (32, 35),
            },
            "sclk": {
                "direction": "output",
                "pull": None,
                "pos": (32, 46),
            },
            "sel": {
                "direction": "output",
                "pull": None,
                "pos": (32, 57),
            },
        }
        self.OPTIONS = {
            "brightness": {
                "min": 0,
                "max": 15,
                "default": 15,
                "type": int,
                "description": "display brightness",
            },
            "frequency": {
                "min": 100000,
                "max": 10000000,
                "default": 1000000,
                "type": int,
                "description": "interface clock frequency",
            },
            "displays": {
                "min": 1,
                "max": 10,
                "default": 1,
                "type": int,
                "description": "number of displays / values",
            },
        }
        self.INTERFACE = {}
        self.SIGNALS = {}
        displays = self.plugin_setup.get("displays", self.OPTIONS["displays"]["default"])
        self.IMAGE = f"image{min(displays, 4)}x.png"
        for vn in range(displays):
            self.INTERFACE[f"value{vn}"] = {
                "size": 24,
                "direction": "output",
                "multiplexed": True,
            }
            self.SIGNALS[f"value{vn}"] = {
                "min": -999999,
                "max": 999999,
                "direction": "output",
            }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        instance_arguments = instance["arguments"]
        brightness = self.plugin_setup.get("brightness", self.OPTIONS["brightness"]["default"])
        instance_parameter["BRIGHTNESS"] = f"8'h0{brightness:x}"
        displays = self.plugin_setup.get("displays", self.OPTIONS["displays"]["default"])
        instance_parameter["DISPLAYS"] = displays
        frequency = int(self.plugin_setup.get("frequency", self.OPTIONS["frequency"]["default"]))
        divider = self.system_setup["speed"] // frequency // 5
        instance_parameter["DIVIDER"] = divider
        values = []
        for vn in range(displays):
            del instance_arguments[f"value{vn}"]
            values.append(f"VAROUT24_{self.instances_name.upper()}_VALUE{displays - vn - 1}")
        instance_arguments["values"] = f"{{{', '.join(values)}}}"

        return instances
