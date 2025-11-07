import os
import json
from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "breakout"
        self.INFO = "breakout boards"
        self.KEYWORDS = ""
        self.DESCRIPTION = ""
        self.PLUGIN_TYPE = "breakout"
        self.PINDEFAULTS = {}
        self.OPTIONS = {
            "node_type": {
                "default": "china-bob5x",
                "type": "select",
                "options": [
                    "china-bob5x",
                    "db25-1205",
                    "rpi-db25hat",
                    "rio-icebreaker3x",
                    "rioctrl-shiftio",
                ],
                "description": "board type",
            },
        }
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        breakout_file = os.path.join(os.path.dirname(__file__), f"{node_type}.json")
        jdata = json.loads(open(breakout_file, "r").read())

        self.IMAGE = f"{node_type}.png"
        self.IMAGE_SHOW = True
        self.INFO = jdata.get("comment", "")
        for pin, data in jdata["main"].items():
            self.PINDEFAULTS[f"SLOT:{pin}"] = {"direction": "all", "edge": "target", "optional": True, "pintype": "BREAKOUT", "type": ["BREAKOUT"], "pos": data["pos"]}
        for slot in jdata["slots"]:
            slot_name = slot["name"]
            for pin, data in slot["pins"].items():
                source = data["pin"]
                direction = data.get("direction", "all")
                self.PINDEFAULTS[f"{slot_name}:{pin}"] = {
                    "source": f"SLOT:{source}",
                    "direction": direction,
                    "edge": "source",
                    "pintype": "PASSTHROUGH",
                    "type": ["PASSTHROUGH"],
                    "optional": True,
                    "pos": data["pos"],
                }
