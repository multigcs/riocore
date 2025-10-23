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

    def update_prefixes(cls, instances):
        for num, instance in enumerate(instances):
            instance.PREFIX = f"gpioout.{num}"

    def hal(self, generator):
        return

    def loader(cls, instances):
        return ""
