import glob
import json
import os

from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "breakout"
        self.INFO = "breakout boards"
        self.KEYWORDS = ""
        self.DESCRIPTION = ""
        self.PLUGIN_TYPE = "breakout"
        self.PINDEFAULTS = {}
        board_list = []
        for jboard in glob.glob(os.path.join(os.path.dirname(__file__), "boards", "*.json")):
            board_list.append(os.path.basename(jboard).replace(".json", ""))
        self.OPTIONS = {
            "node_type": {
                "default": "china-bob5x",
                "type": "select",
                "options": board_list,
                "description": "board type",
                "reload": True,
            },
        }
        node_type = self.plugin_setup.get("node_type", self.option_default("node_type"))
        breakout_file = os.path.join(os.path.dirname(__file__), "boards", f"{node_type}.json")
        jdata = json.loads(open(breakout_file).read())

        if node_type == "rioctrl-shiftio":
            self.VERILOGS = ["shiftreg.v"]
            self.PINDEFAULTS = {
                "out": {
                    "direction": "output",
                    "description": "output data (DS on 74HC595)",
                    "optional": True,
                },
                "in": {
                    "direction": "input",
                    "description": "input data (SER_OUT on 74HC165)",
                    "optional": True,
                },
                "sclk": {
                    "direction": "output",
                    "description": "input data (CLK on 74HC165/ CH_CP/SRCLK on 74HC595)",
                },
                "load": {
                    "direction": "output",
                    "description": "input data (SH/LD on 74HC165/ ST_CP/RCLK on 74HC595)",
                },
            }
            self.TYPE = "expansion"
            self.BITS_OUT = 8
            self.BITS_IN = 8

        self.IMAGE = f"boards/{node_type}.png"
        self.IMAGE_SHOW = True
        self.INFO = jdata.get("comment", "")
        for pin, data in jdata.get("main", {}).items():
            self.PINDEFAULTS[f"SLOT:{pin}"] = {"direction": "all", "edge": "target", "optional": True, "pintype": "BREAKOUT", "type": ["BREAKOUT"], "pos": data["pos"]}

        for slot in jdata["slots"]:
            slot_name = slot["name"]
            for pin, data in slot["pins"].items():
                if "edge" in data:
                    # new style
                    self.PINDEFAULTS[f"{slot_name}:{pin}"] = data
                else:
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
