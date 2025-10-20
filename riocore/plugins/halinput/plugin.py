from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "halinput"
        self.COMPONENT = "halinput"
        self.INFO = "joypad support"
        self.DESCRIPTION = "halinput joypad support"
        self.KEYWORDS = "jog joypad usb"
        self.TYPE = "base"
        self.PLUGIN_TYPE = "gpio"
        self.IMAGE = ""
        self.ORIGIN = ""
        self.SIGNALS = {}
        self.PINDEFAULTS = {}
        self.FILES = []
        self.OPTIONS = {
            "joypad_name": {
                "type": str,
                "default": "Joystick",
            },
            "slow": {
                "type": str,
                "default": "btn-top2",
            },
            "medium": {
                "type": str,
                "default": "btn-base",
            },
            "fast": {
                "type": str,
                "default": "btn-pinkie",
            },
        }
        for axis, default in {
            "x": "abs-x",
            "y": "-abs-y",
            "z": "-abs-rz",
            "a": "",
            "b": "",
            "c": "",
        }.items():
            self.OPTIONS[axis] = {
                "type": float,
                "default": default,
            }

    def update_prefixes(cls, instances):
        for instance in instances:
            instance.PREFIX = f"halinput.{instance.instances_name}"

    def hal(self, parent):
        joypad_btn_slow = self.plugin_setup.get("slow", self.option_default("slow"))
        joypad_btn_medium = self.plugin_setup.get("medium", self.option_default("medium"))
        joypad_btn_fast = self.plugin_setup.get("fast", self.option_default("fast"))

        muxes = []
        for axis_name, axis_config in parent.project.axis_dict.items():
            joints = axis_config["joints"]
            axis_lower = axis_name.lower()
            muxes.append(f"mux2_{axis_lower}")

        parent.halg.fmt_add(f"loadrt mux2 names={','.join(muxes)}")

        parent.halg.setp_add("joy_mux4.in0", 0.0)
        parent.halg.setp_add("joy_mux4.in1", 50.0)
        parent.halg.setp_add("joy_mux4.in2", 500.0)
        parent.halg.setp_add("joy_mux4.in3", 2000.0)

        joy_mux4_sel0 = []
        joy_mux4_sel1 = []

        if joypad_btn_slow:
            joy_mux4_sel0.append(f"input.0.{joypad_btn_slow}")
        else:
            joy_mux4_sel0.append("0")

        if joypad_btn_medium:
            joy_mux4_sel1.append(f"input.0.{joypad_btn_medium}")
        else:
            joy_mux4_sel1.append("0")

        if joypad_btn_fast:
            joy_mux4_sel0.append(f"input.0.{joypad_btn_fast}")
            joy_mux4_sel1.append(f"input.0.{joypad_btn_fast}")
        else:
            joy_mux4_sel0.append("0")
            joy_mux4_sel1.append("0")

        parent.halg.net_add(" or ".join(joy_mux4_sel0), "joy_mux4.sel0")
        parent.halg.net_add(" or ".join(joy_mux4_sel1), "joy_mux4.sel1")

        parent.halg.net_add("joy_mux4.out", "halui.axis.jog-speed")
        parent.halg.net_add("joy_mux4.out", "halui.joint.jog-speed")

        for axis_name, axis_config in parent.project.axis_dict.items():
            joints = axis_config["joints"]
            axis_lower = axis_name.lower()
            jaxis = self.plugin_setup.get(axis_lower, self.option_default(axis_lower))
            reverse = False
            if jaxis:
                if jaxis[0] == "-":
                    jaxis = jaxis[1:]
                    reverse = True
                if reverse:
                    parent.halg.setp_add(f"input.0.{jaxis}-scale", -127.5)
                else:
                    parent.halg.setp_add(f"input.0.{jaxis}-scale", 127.5)
                parent.halg.fmt_add(f"addf mux2_{axis_lower} servo-thread")
                parent.halg.net_add("halui.machine.is-on", f"mux2_{axis_lower}.sel")
                parent.halg.net_add(f"input.0.{jaxis}-position", f"mux2_{axis_lower}.in1")
                parent.halg.net_add(f"mux2_{axis_lower}.out", f"halui.axis.{axis_lower}.analog")
                for joint, joint_setup in joints.items():
                    parent.halg.net_add(f"mux2_{axis_lower}.out", f"halui.joint.{joint}.analog")

    def loader(cls, instances):
        output = []
        for instance in instances:
            joypad_name = instance.plugin_setup.get("joypad_name", instance.option_default("joypad_name"))
        output.append(f"loadusr -W hal_input -KRAL {joypad_name}")
        output.append("loadrt mux4 names=joy_mux4")
        output.append("addf joy_mux4 servo-thread")
        output.append("")
        return "\n".join(output)
