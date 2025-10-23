from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "bitout"
        self.INFO = "singe bit output pin"
        self.DESCRIPTION = "to control relay, leds, valves, ...."
        self.KEYWORDS = "led relais relay valve lamp motor magnet"
        self.ORIGIN = ""
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
        self.OPTIONS = {
            "htype": {
                "default": "generic",
                "type": "select",
                "options": ["generic", "relay"],
                "description": "hardware type",
            },
        }

        htype = self.plugin_setup.get("htype", self.option_default("htype"))
        if htype == "relay":
            self.IMAGE_SHOW = True
            self.IMAGE = "relay.png"
            self.PINDEFAULTS["bit"]["pos"] = (15, 150)
            self.SIGNALS["bit"]["pos"] = (355, 150)

    def gateware_instances(self):
        instances = self.gateware_instances_base(direct=True)
        return instances
