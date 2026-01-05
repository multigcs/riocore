from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "bitout"
        self.INFO = "singe bit output pin"
        self.DESCRIPTION = "to control relay, leds, valves, ...."
        self.KEYWORDS = "led relais relay valve lamp motor magnet"
        self.IMAGES = ["relay", "ssr", "ssr2a", "led", "smdled", "spindle500w"]
        self.ORIGIN = ""
        self.PLUGIN_CONFIG = "Wizard"
        self.PINDEFAULTS = {
            "bit": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
        }
        self.INTERFACE = {
            "bit": {
                "size": 1,
                "direction": "output",
            },
        }
        self.SIGNALS = {
            "bit": {
                "direction": "output",
                "bool": True,
            },
        }

    def gateware_instances(self):
        instances = self.gateware_instances_base(direct=True)
        return instances
