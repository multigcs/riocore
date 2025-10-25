from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "gpioin"
        self.COMPONENT = "gpioin"
        self.INFO = "gpio input"
        self.DESCRIPTION = ""
        self.KEYWORDS = "input"
        self.IMAGES = ["proximity", "estop", "probe", "switch", "opto"]
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

    def update_prefixes(cls, instances):
        for num, instance in enumerate(instances):
            instance.PREFIX = f"gpioin.{num}"
