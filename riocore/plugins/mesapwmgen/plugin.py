from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "mesapwmgen"
        self.COMPONENT = "mesapwmgen"
        self.INFO = "mesa pwm pulse generation"
        self.DESCRIPTION = ""
        self.KEYWORDS = "pwm"
        self.IMAGES = ["spindle500w", "laser", "led"]
        self.TYPE = "io"
        self.PLUGIN_TYPE = "mesa"
        self.ORIGIN = ""
        self.OPTIONS = {
            "scale": {
                "default": 100,
                "type": float,
                "min": 0.1,
                "max": 100000,
                "description": "max pwm value",
            },
        }
        scale = self.plugin_setup.get("scale", self.option_default("scale"))
        self.SIGNALS = {
            "value": {
                "direction": "output",
                "min": 0.0,
                "max": scale,
            },
            "enable": {
                "direction": "output",
                "bool": True,
            },
        }
        self.PINDEFAULTS = {
            "pwm": {"direction": "output", "edge": "target", "type": "MESAPWMPWM"},
        }

    def hal(self, parent):
        scale = self.plugin_setup.get("scale", self.option_default("scale"))
        parent.halg.setp_add(f"{self.PREFIX}.scale", scale)
