from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "tlc5615"
        self.INFO = "spi dac"
        self.DESCRIPTION = "Analog-Output via spi dac"
        self.KEYWORDS = "analog dac"
        self.URL = "https://www.ti.com/lit/ds/symlink/tlc5615.pdf?ts=1774302230717"
        self.IMAGE = "image.png"
        self.IMAGE_SHOW = True
        self.ORIGIN = ""
        self.NEEDS = ["fpga"]
        self.VERILOGS = ["tlc5615.v"]
        self.PINDEFAULTS = {
            "mosi": {
                "direction": "output",
                "comment": "DIN",
                "pos": (8, 58),
            },
            "sclk": {
                "direction": "output",
                "comment": "SCLK",
                "pos": (8, 70),
            },
            "sel": {
                "direction": "output",
                "comment": "CS",
                "pos": (8, 82),
            },
        }
        self.SIGNALS = {
            "value": {
                "min": 0,
                "max": 1023,
                "direction": "output",
            },
        }
        self.INTERFACE = {
            "value": {
                "size": 16,
                "direction": "output",
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        frequency = 10000 * 60  # update rate
        divider = self.system_setup["speed"] // frequency
        instance_parameter["DIVIDER"] = divider
        return instances
