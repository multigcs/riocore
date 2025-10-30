from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "gpioout"
        self.COMPONENT = "gpioout"
        self.INFO = "gpio output"
        self.DESCRIPTION = ""
        self.KEYWORDS = "output"
        self.IMAGES = ["relay", "ssr", "ssr2a", "led"]
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
                "edge": "target",
                "type": "GPIO",
            },
        }
