def hal(parent):
    output = []
    linuxcnc_config = parent.project.config["jdata"].get("linuxcnc", {})

    mxmpg_config = linuxcnc_config.get("mxmpg", {})
    mxmpg_enable = mxmpg_config.get("enable", False)
    if mxmpg_enable:
        output.append(f"loadusr mpg -d /dev/ttyACM0 -s")
        output.append("")

        # zero axis -> mdi commands
        parent.hal_net_add("mpg.button.sel01-long", "|halui.mdi-command-00")
        parent.hal_net_add("mpg.button.sel02-long", "|halui.mdi-command-01")
        parent.hal_net_add("mpg.button.sel03-long", "|halui.mdi-command-02")

        # display status
        parent.hal_net_add("halui.machine.is-on", "mpg.machine.is-on")
        parent.hal_net_add("halui.program.is-running", "mpg.program.is-running")

        # programm control
        parent.hal_net_add("mpg.button.01", "halui.program.run")
        parent.hal_net_add("mpg.button.01-long", "halui.program.stop")
        parent.hal_net_add("mpg.button.01b", "halui.program.pause")
        parent.hal_net_add("mpg.button.01b-long", "halui.program.resume")

        # homing status
        parent.hal_net_add("joint.0.homed", "mpg.axis.x.homed")
        parent.hal_net_add("joint.1.homed", "mpg.axis.y.homed")
        parent.hal_net_add("joint.2.homed", "mpg.axis.z.homed")

        # spindle control
        parent.hal_net_add("mpg.button.02-long", "halui.spindle.0.start")
        parent.hal_net_add("mpg.button.02", "halui.spindle.0.stop")

        # axis selection
        bn = 1
        for axis_name, joints in parent.axis_dict.items():
            axis_low = axis_name.lower()
            parent.hal_net_add(f"mpg.button.sel{bn:02d}", f"halui.axis.{axis_low}.select")
            for joint, joint_setup in joints.items():
                parent.hal_net_add(f"mpg.button.sel{bn:02d}", f"halui.joint.{joint}.select")
            bn += 1

        # jog axis
        for axis_name, joints in parent.axis_dict.items():
            axis_low = axis_name.lower()
            parent.hal_setp_add(f"axis.{axis_low}.jog-vel-mode", 1)
            parent.hal_setp_add(f"axis.{axis_low}.jog-enable", 1)
            parent.hal_net_add(f"mpg.jog-scale", f"axis.{axis_low}.jog-scale")
            parent.hal_net_add(f"mpg.axis.{axis_low}.jog-counts", f"axis.{axis_low}.jog-counts")
            for joint, joint_setup in joints.items():
                parent.hal_setp_add(f"joint.{joint}.jog-vel-mode", 1)
                parent.hal_setp_add(f"joint.{joint}.jog-enable", 1)
                parent.hal_net_add(f"mpg.jog-scale", f"joint.{joint}.jog-scale")
                parent.hal_net_add(f"mpg.axis.{axis_low}.jog-counts", f"joint.{joint}.jog-counts")

        # display axis positions
        for axis_name, joints in parent.axis_dict.items():
            axis_low = axis_name.lower()
            parent.hal_net_add(f"halui.axis.{axis_low}.pos-relative", f"mpg.axis.{axis_low}.pos")

        # overwrites
        for ov in ("feed", "rapid"):
            parent.hal_setp_add(f"halui.{ov}-override.scale", 0.01)
            parent.hal_net_add(f"mpg.override.{ov}.counts", f"halui.{ov}-override.counts")
            parent.hal_net_add(f"halui.{ov}-override.value", f"mpg.override.{ov}.value")

        parent.hal_setp_add(f"halui.spindle.0.override.scale", 0.01)
        parent.hal_net_add(f"mpg.override.spindle.counts", f"halui.spindle.0.override.counts")
        parent.hal_net_add(f"halui.spindle.0.override.value", f"mpg.override.spindle.value")

        output.append("")

    return output
