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
            "image": {
                "default": "generic",
                "type": "select",
                "options": ["generic", "relay", "ssr"],
                "description": "hardware type",
            },
        }

        image = self.plugin_setup.get("image", self.option_default("image"))
        if image == "relay":
            self.IMAGE_SHOW = True
            self.IMAGE = "relay.png"
            self.PINDEFAULTS["bit"]["pos"] = (15, 150)
            self.SIGNALS["bit"]["pos"] = (355, 150)
        elif image == "ssr":
            self.IMAGE_SHOW = True
            self.IMAGE = "ssr.png"
            self.PINDEFAULTS["bit"]["pos"] = (36, 36)
            self.SIGNALS["bit"]["pos"] = (278, 40)

    def gateware_instances(self):
        instances = self.gateware_instances_base(direct=True)
        return instances
