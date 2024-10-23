from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "signal"
        self.INFO = "virtual signal"
        self.DESCRIPTION = "virtual signal"
        self.KEYWORDS = "virtual"
        self.ORIGIN = ""
        self.VERILOGS = []
        self.OPTIONS = {
            "dir": {
                "default": "input",
                "type": "select",
                "options": ["input", "output"],
                "description": "signal direction",
            },
            "vtype": {
                "default": "float",
                "type": "select",
                "options": ["float", "bool"],
                "description": "signal type",
            },
        }
        self.SIGNALS = {}
        direction = self.plugin_setup.get("dir", self.OPTIONS["dir"]["default"])
        vtype = self.plugin_setup.get("vtype", self.OPTIONS["vtype"]["default"])
        self.SIGNALS["value"] = {
            "direction": direction,
            "virtual": True,
        }
        if vtype == "bool":
            self.SIGNALS["value"]["bool"] = True

    def gateware_instances(self):
        return None
