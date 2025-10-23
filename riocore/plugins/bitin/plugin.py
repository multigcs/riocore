from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "bitin"
        self.INFO = "single input pin"
        self.DESCRIPTION = "to read switches or other 1bit signals"
        self.KEYWORDS = "switch limit estop keyboard"
        self.ORIGIN = ""
        self.PINDEFAULTS = {
            "bit": {
                "direction": "input",
            },
        }
        self.INTERFACE = {
            "bit": {
                "size": 1,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "bit": {
                "direction": "input",
                "bool": True,
            },
        }
        self.OPTIONS = {
            "image": {
                "default": "generic",
                "type": "select",
                "options": ["generic", "proximity", "estop", "probe"],
                "description": "hardware type",
            },
        }

        image = self.plugin_setup.get("image", self.option_default("image"))
        if image == "proximity":
            self.IMAGE_SHOW = True
            self.IMAGE = "proximity.png"
            self.PINDEFAULTS["bit"]["pos"] = (10, 60)
            self.SIGNALS["bit"]["pos"] = (360, 60)
        elif image == "estop":
            self.IMAGE_SHOW = True
            self.IMAGE = "estop.png"
            self.PINDEFAULTS["bit"]["pos"] = (10, 160)
            self.SIGNALS["bit"]["pos"] = (360, 160)
        elif image == "probe":
            self.IMAGE_SHOW = True
            self.IMAGE = "probe.png"
            self.PINDEFAULTS["bit"]["pos"] = (10, 160)
            self.SIGNALS["bit"]["pos"] = (280, 160)

    def gateware_instances(self):
        instances = self.gateware_instances_base(direct=True)
        return instances
