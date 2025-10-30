from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "ninjastepgen"
        self.COMPONENT = "ninjastepgen"
        self.INFO = "masa step pulse generation"
        self.DESCRIPTION = ""
        self.KEYWORDS = "stepper"
        self.IMAGES = ["stepper", "servo42"]
        self.TYPE = "joint"
        self.PLUGIN_TYPE = "ninja"
        self.JOINT_TYPE = "velocity"
        self.JOINT_TYPE = "position"
        self.JOINT_OPTIONS = []
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
            "step": {"direction": "output", "edge": "target", "type": "NINJAStepGenStep"},
            "dir": {"direction": "output", "edge": "target", "type": "NINJAStepGenDir"},
        }

    def update_pins(self, parent):
        return

    def hal(self, parent):
        if "joint_data" in self.plugin_setup:
            joint_data = self.plugin_setup["joint_data"]
            axis_name = joint_data["axis"]
            joint_n = joint_data["num"]
            pid_num = joint_n
            if self.JOINT_TYPE == "velocity":
                cmd_halname = f"{self.PREFIX}.stepgen.0.command"
                feedback_halname = f"{self.PREFIX}.stepgen.0.feedback"
                enable_halname = f"{self.PREFIX}.stepgen.0.enable"
                scale_halname = f"{self.PREFIX}.stepgen.0.step-scale"
                parent.halg.joint_add(
                    parent, axis_name, joint_n, "velocity", cmd_halname, feedback_halname=feedback_halname, scale_halname=scale_halname, enable_halname=enable_halname, pid_num=pid_num
                )
            else:
                cmd_halname = f"{self.PREFIX}.stepgen.0.command"
                feedback_halname = f"{self.PREFIX}.stepgen.0.command"
                enable_halname = f"{self.PREFIX}.stepgen.0.enable"
                scale_halname = f"{self.PREFIX}.stepgen.0.step-scale"
                parent.halg.joint_add(parent, axis_name, joint_n, "position", cmd_halname, feedback_halname=feedback_halname, scale_halname=scale_halname, enable_halname=enable_halname)
