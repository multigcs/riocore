from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "gpioin"
        self.COMPONENT = "gpioin"
        self.INFO = "gpio input"
        self.DESCRIPTION = ""
        self.KEYWORDS = "input"
        self.TYPE = "io"
        self.PLUGIN_TYPE = "gpio"
        self.SIGNALS = {
            "bit": {
                "direction": "input",
                "bool": True,
            },
        }
        self.PINDEFAULTS = {
            "bit": {
                "direction": "input",
            },
        }
        self.OPTIONS = {
            "image": {
                "default": "generic",
                "type": "select",
                "options": ["generic", "proximity", "estop", "probe", "switch"],
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
        elif image == "switch":
            self.IMAGE_SHOW = True
            self.IMAGE = "switch.png"
            self.PINDEFAULTS["bit"]["pos"] = (90, 100)
            self.SIGNALS["bit"]["pos"] = (270, 100)

    def update_prefixes(cls, instances):
        for num, instance in enumerate(instances):
            instance.PREFIX = f"gpioin.{num}"
