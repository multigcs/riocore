from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "robojog"
        self.COMPONENT = "robojog"
        self.INFO = "gui component to jog robot axis"
        self.DESCRIPTION = ""
        self.KEYWORDS = "jog gui robot"
        self.TYPE = "base"
        self.PLUGIN_TYPE = "gpio"
        self.IMAGE = ""
        self.ORIGIN = ""
        self.SIGNALS = {}
        self.PINDEFAULTS = {}
        self.FILES = []
        self.OPTIONS = {}

    def update_prefixes(cls, instances):
        for instance in instances:
            instance.PREFIX = f"robojog.{instance.instances_name}"

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
        for axis in "xyzabc":
            if axis.upper() in parent.project.axis_dict:
                axis_config = parent.project.axis_dict.get(axis.upper())
                joints = axis_config["joints"]
                for joint, joint_setup in joints.items():
                    parent.halg.net_add(f"robojog.joint.{joint}.jog-counts", f"joint.{joint}.jog-counts")
                    parent.halg.net_add(f"joint.{joint}.pos-fb", f"robojog.joint.{joint}.position")
                    parent.halg.setp_add(f"robojog.joint.{joint}.max_limit", 1500.0)
                    parent.halg.setp_add(f"robojog.joint.{joint}.min_limit", -500.0)
                    parent.halg.setp_add(f"robojog.joint.{joint}.scale", 100.0)

    def loader(cls, instances):
        return ""
