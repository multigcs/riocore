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
        try:
            jdata = json.loads(open(breakout_file).read())
        except Exception as err:
            print(f"ERROR: loading json '{breakout_file}': {err}")
            jdata = {}

        self.IMAGE = f"boards/{node_type}.png"
        self.IMAGE_SHOW = True
        self.INFO = jdata.get("comment", "")
        for pin, data in jdata.get("main", {}).items():
            self.PINDEFAULTS[f"SLOT:{pin}"] = {"direction": "all", "edge": "target", "optional": True, "pintype": "BREAKOUT", "type": ["BREAKOUT"], "pos": data["pos"]}

        for slot in jdata.get("slots", []):
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
                        "pos": data.get("pos"),
                    }

        self.SUB_PLUGINS = []
        for spn, sub_plugin in enumerate(jdata.get("plugins", [])):
            if "uid" not in sub_plugin:
                sub_plugin["uid"] = f"{self.instances_name}_{sub_plugin['type']}{spn}"
            else:
                sub_plugin["uid"] = f"{self.instances_name}_{sub_plugin['uid']}"
            self.SUB_PLUGINS.append(sub_plugin)
