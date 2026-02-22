from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "rmpg"
        self.COMPONENT = "rmpg"
        self.INFO = "remote mpg server"
        self.DESCRIPTION = "see riocore/plugins/rmpg/clients/ for clients"
        self.KEYWORDS = "jog cam remote"
        self.TYPE = "base"
        self.IMAGE_SHOW = True
        self.NEEDS = []
        self.IMAGE = ""
        self.ORIGIN = ""
        self.SIGNALS = {}
        self.PINDEFAULTS = {}
        self.FILES = ["rmpg.py"]
        self.OPTIONS = {
            "port": {
                "type": int,
                "default": 10000,
            },
        }
        self.rmpg_num = 0

    @classmethod
    def component_loader(cls, instances):
        for cnum, instance in enumerate(instances):
            instance.rmpg_num = cnum

    def cmd_args(self):
        port = self.plugin_setup.get("port", self.option_default("port"))
        cmd_args = [f"loadusr -Wn rmpg{self.rmpg_num} ./rmpg.py"]
        cmd_args.append(f"--name rmpg{self.rmpg_num}")
        cmd_args.append(f"--port {port}")
        return " ".join(cmd_args)

    def hal(self, parent):
        parent.halg.postgui_components_add(f"rmpg{self.rmpg_num}")
        parent.halg.fmt_add(f"{self.cmd_args()}")
        for axis_name, axis_config in parent.project.axis_dict.items():
            if axis_name not in {"X", "Y", "Z"}:
                continue
            joints = axis_config["joints"]
            axis_lower = axis_name.lower()
            parent.halg.net_add(f"rmpg{self.rmpg_num}.axis.{axis_lower}.jog-counts", f"axis.{axis_lower}.jog-counts")
            parent.halg.setp_add(f"rmpg{self.rmpg_num}.axis.{axis_lower}.jog-scale", 0.15)
            parent.halg.setp_add(f"axis.{axis_lower}.jog-vel-mode", 0)
            parent.halg.setp_add(f"axis.{axis_lower}.jog-enable", 1)
            parent.halg.setp_add(f"axis.{axis_lower}.jog-scale", 0.15)
            for joint_setup in joints:
                joint = joint_setup["num"]
                parent.halg.net_add(f"rmpg{self.rmpg_num}.axis.{axis_lower}.jog-counts", f"joint.{joint}.jog-counts")
                parent.halg.setp_add(f"joint.{joint}.jog-vel-mode", 0)
                parent.halg.setp_add(f"joint.{joint}.jog-enable", 1)
                parent.halg.setp_add(f"joint.{joint}.jog-scale", 0.15)

        for overwrite in ("feed-override", "rapid-override", "spindle.0.override", "max-velocity"):
            parent.halg.net_add(f"rmpg{self.rmpg_num}.{overwrite}.counts", f"halui.{overwrite}.counts")
            parent.halg.net_add(f"halui.{overwrite}.value", f"rmpg{self.rmpg_num}.{overwrite}.value")
            parent.halg.setp_add(f"halui.{overwrite}.count-enable", True)
            if overwrite == "max-velocity":
                parent.halg.setp_add(f"halui.{overwrite}.scale", 1.0)
            else:
                parent.halg.setp_add(f"halui.{overwrite}.scale", 0.1)
