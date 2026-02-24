from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "gpioout"
        self.INFO = "gpio output"
        self.DESCRIPTION = ""
        self.KEYWORDS = "output"
        self.IMAGES = ["relay", "ssr", "ssr2a", "led", "smdled", "spindle500w", "compressor", "vacuum", "valve", "dinrailplug", "motor"]
        self.TYPE = "io"
        self.NEEDS = ["gpio"]
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
                "type": ["GPIO", "FPGA"],
            },
        }
        self.INTERFACE = {
            "bit": {
                "size": 1,
                "direction": "output",
            },
        }
