from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "gpioout"
        self.COMPONENT = "gpioout"
        self.INFO = "gpio output"
        self.DESCRIPTION = ""
        self.KEYWORDS = "output"
        self.TYPE = "io"
        self.PLUGIN_TYPE = "gpio"
        self.ORIGIN = ""
        self.OPTIONS = {}
        self.SIGNALS = {
            "bit": {
                "direction": "output",
                "bool": True,
            },
        }
        self.PINDEFAULTS = {
            "bit": {
                "direction": "output",
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

    def update_prefixes(cls, instances):
        for num, instance in enumerate(instances):
            instance.PREFIX = f"gpioout.{num}"

    def hal(self, generator):
        return

    def loader(cls, instances):
        return ""
