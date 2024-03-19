def hal(parent):
    output = []
    linuxcnc_config = parent.project.config["jdata"].get("linuxcnc", {})

    mxmpg_config = linuxcnc_config.get("mxmpg", {})
    mxmpg_enable = mxmpg_config.get("enable", False)
    mxmpg_device = mxmpg_config.get("device", "/dev/ttyACM0")
    if mxmpg_enable:
        output.append(f"loadusr mpg -d {mxmpg_device} -s")
        output.append("")

        # display status
        parent.hal_net_add("halui.machine.is-on", "mpg.machine.is-on")
        parent.hal_net_add("halui.program.is-running", "mpg.program.is-running")

        # programm control
        parent.hal_net_add("mpg.button.01", "halui.program.run")
        parent.hal_net_add("mpg.button.01-long", "halui.program.stop")
        parent.hal_net_add("mpg.button.01b", "halui.program.pause")
        parent.hal_net_add("mpg.button.01b-long", "halui.program.resume")

        # homing status
        for axis_name, joints in parent.axis_dict.items():
            axis_low = axis_name.lower()
            for joint, joint_setup in joints.items():
                parent.hal_net_add(f"joint.{joint}.homed", f"mpg.axis.{axis_low}.homed")

        # spindle control
        parent.hal_net_add("mpg.button.02-long", "halui.spindle.0.start")
        parent.hal_net_add("mpg.button.02", "halui.spindle.0.stop")

        # zero axis -> mdi commands
        bn = 1
        for axis_name, joints in parent.axis_dict.items():
            halpin = parent.ini_mdi_command(f"G92 {axis_name}0")
            parent.hal_net_add(f"mpg.button.sel{bn:02d}-long", halpin)
            bn += 1

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
