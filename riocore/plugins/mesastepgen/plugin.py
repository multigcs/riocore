from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "mesastepgen"
        self.COMPONENT = "mesastepgen"
        self.INFO = "masa step pulse generation"
        self.DESCRIPTION = ""
        self.KEYWORDS = "stepper"
        self.IMAGES = ["stepper", "servo42"]
        self.TYPE = "joint"
        self.PLUGIN_TYPE = "mesa"
        self.JOINT_TYPE = "velocity"
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

    def hal(self, parent):
        if "joint_data" in self.plugin_setup:
            joint_data = self.plugin_setup["joint_data"]
            axis_name = joint_data["axis"]
            joint_n = joint_data["num"]
            pid_num = joint_n
            cmd_halname = f"{self.PREFIX}.velocity-cmd"
            feedback_halname = f"{self.PREFIX}.position-fb"
            enable_halname = f"{self.PREFIX}.enable"
            scale_halname = f"{self.PREFIX}.position-scale"
            for key in ("dirsetup", "dirhold", "steplen", "stepspace", "maxaccel", "maxvel"):
                value = f"MESA_{key.upper()}"
                value = {"MESA_MAXACCEL": "MESA_STEPGEN_MAXACCEL", "MESA_MAXVEL": "MESA_STEPGEN_MAXVEL"}.get(value, value)
                parent.halg.setp_add(f"{self.PREFIX}.{key}", f"[JOINT_{joint_n}]{value}")
            parent.halg.joint_add(parent, axis_name, joint_n, "velocity", cmd_halname, feedback_halname=feedback_halname, scale_halname=scale_halname, enable_halname=enable_halname, pid_num=pid_num)
