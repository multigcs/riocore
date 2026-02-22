from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "robojog"
        self.INFO = "gui component to jog robot axis"
        self.DESCRIPTION = ""
        self.KEYWORDS = "jog gui robot"
        self.TYPE = "base"
        self.IMAGE_SHOW = True
        self.NEEDS = []
        self.IMAGE = ""
        self.ORIGIN = ""
        self.SIGNALS = {}
        self.PINDEFAULTS = {}
        self.FILES = ["robojog.py"]
        self.OPTIONS = {}

    def ini(self, parent, ini_setup):
        tabname = "robojog"
        ini_setup["DISPLAY"]["EMBED_TAB_NAME|robojog"] = tabname
        if parent.gui_tablocation:
            ini_setup["DISPLAY"]["EMBED_TAB_LOCATION|robojog"] = parent.gui_tablocation
        cmd_args = ["halcmd loadusr -Wn robojog ./robojog.py"]
        cmd_args.append("--xid {XID}")
        cmd_args.append(f"--joints {6}")
        ini_setup["DISPLAY"]["EMBED_TAB_COMMAND|robojog"] = f"{' '.join(cmd_args)}"

    def hal(self, parent):
        parent.halg.postgui_components_add("robojog")
        for axis in "xyzabc":
            if axis.upper() in parent.project.axis_dict:
                axis_config = parent.project.axis_dict.get(axis.upper())
                axis_lower = axis.lower()
                parent.halg.setp_add(f"axis.{axis_lower}.jog-vel-mode", 0)
                parent.halg.setp_add(f"axis.{axis_lower}.jog-enable", 1)
                parent.halg.setp_add(f"axis.{axis_lower}.jog-scale", 0.01)
                joints = axis_config["joints"]
                for joint in joints:
                    joint_num = joint["num"]
                    parent.halg.net_add(f"robojog.joint.{joint_num}.jog-counts", f"joint.{joint_num}.jog-counts")
                    parent.halg.net_add(f"joint.{joint_num}.pos-fb", f"robojog.joint.{joint_num}.position")
                    parent.halg.setp_add(f"robojog.joint.{joint_num}.max_limit", 1500.0)
                    parent.halg.setp_add(f"robojog.joint.{joint_num}.min_limit", -500.0)
                    parent.halg.setp_add(f"robojog.joint.{joint_num}.scale", 100.0)

                    parent.halg.setp_add(f"joint.{joint_num}.jog-vel-mode", 0)
                    parent.halg.setp_add(f"joint.{joint_num}.jog-enable", 1)
                    parent.halg.setp_add(f"joint.{joint_num}.jog-scale", 0.01)
