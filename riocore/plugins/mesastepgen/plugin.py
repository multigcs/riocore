from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "mesastepgen"
        self.COMPONENT = "mesastepgen"
        self.INFO = "software step pulse generation"
        self.DESCRIPTION = ""
        self.KEYWORDS = "stepper"
        self.IMAGES = ["stepper", "servo42"]
        self.TYPE = "joint"
        self.PLUGIN_TYPE = "mesa"
        self.ORIGIN = ""
        self.OPTIONS = {}
        self.SIGNALS = {
            "velocity": {
                "direction": "output",
                "absolute": False,
                "description": "set position",
            },
            "position": {
                "direction": "input",
                "unit": "steps",
                "absolute": False,
                "description": "position feedback",
            },
            "position-scale": {
                "direction": "output",
                "absolute": False,
                "description": "steps / unit",
            },
        }
        self.PINDEFAULTS = {
            "step": {"direction": "output", "edge": "target", "type": "MESAStepGenStep"},
            "dir": {"direction": "output", "edge": "target", "type": "MESAStepGenDir"},
        }
