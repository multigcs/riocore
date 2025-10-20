from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "spacenav"
        self.COMPONENT = "spacenav"
        self.INFO = "3d mouse support"
        self.DESCRIPTION = "spacenav 3d mouse jog support"
        self.KEYWORDS = "jog usb"
        self.TYPE = "base"
        self.PLUGIN_TYPE = "gpio"
        self.IMAGE = ""
        self.ORIGIN = ""
        self.SIGNALS = {}
        self.PINDEFAULTS = {}
        self.FILES = ["spnav.py"]
        self.OPTIONS = {
            "jointjog": {
                "type": bool,
                "default": False,
            },
            "botton-0": {
                "type": str,
                "default": "halui.spindle.0.start",
            },
            "botton-1": {
                "type": str,
                "default": "halui.spindle.0.stop",
            },
        }
        for axis, scale in {
            "x": -0.2,
            "y": -0.2,
            "z": 0.2,
            "a": 0.02,
            "b": 0.02,
            "c": 0.02,
        }.items():
            self.OPTIONS[f"{axis}-scale"] = {
                "type": float,
                "default": scale,
            }

    def update_prefixes(cls, instances):
        for instance in instances:
            instance.PREFIX = f"spacenav.{instance.instances_name}"

    def precheck(self, parent):
        pass

    def hal(self, parent):
        spacenav_scale = {}
        for axis in "xyzabc":
            spacenav_scale[axis] = self.plugin_setup.get(f"{axis}-scale", self.option_default(f"{axis}-scale"))
        spacenav_jointjog = self.plugin_setup.get("jointjog", self.option_default("jointjog"))
        spacenav_button0 = self.plugin_setup.get("botton-0", self.option_default("botton-0"))
        spacenav_button1 = self.plugin_setup.get("botton-1", self.option_default("botton-1"))

        for axis in "xyzabc":
            if axis.upper() in parent.project.axis_dict and spacenav_scale[axis] != 0.0:
                parent.halg.setp_add(f"spacenav.axis.{axis}.scale", spacenav_scale[axis])
                parent.halg.net_add(f"spacenav.axis.{axis}.jog-counts", f"axis.{axis}.jog-counts")
                parent.halg.setp_add(f"axis.{axis}.jog-vel-mode", 1)
                parent.halg.setp_add(f"axis.{axis}.jog-enable", 1)
                parent.halg.setp_add(f"axis.{axis}.jog-scale", 0.01)
                if not spacenav_jointjog:
                    continue
                axis_config = parent.project.axis_dict.get(axis.upper())
                joints = axis_config["joints"]
                for joint, joint_setup in joints.items():
                    parent.halg.net_add(f"spacenav.axis.{axis}.jog-counts", f"joint.{joint}.jog-counts")
                    parent.halg.setp_add(f"joint.{joint}.jog-vel-mode", 1)
                    parent.halg.setp_add(f"joint.{joint}.jog-enable", 1)
                    parent.halg.setp_add(f"joint.{joint}.jog-scale", 0.01)

        if spacenav_button0:
            if spacenav_button0.startswith("MDI|"):
                parts = spacenav_button0.split("|")
                button_title = parts[1]
                mdi_command = parts[2]
                halpin = parent.ini_mdi_command(mdi_command, title=button_title)
                parent.halg.net_add("spacenav.button.0", halpin)
            else:
                parent.halg.net_add("spacenav.button.0", spacenav_button0)
        if spacenav_button1:
            if spacenav_button1.startswith("MDI|"):
                parts = spacenav_button1.split("|")
                button_title = parts[1]
                mdi_command = parts[2]
                halpin = parent.ini_mdi_command(mdi_command, title=button_title)
                parent.halg.net_add("spacenav.button.1", halpin)
            else:
                parent.halg.net_add("spacenav.button.1", spacenav_button1)

    def loader(cls, instances):
        output = []
        output.append("loadusr -Wn spacenav ./spnav.py")
        output.append("")
        return "\n".join(output)
