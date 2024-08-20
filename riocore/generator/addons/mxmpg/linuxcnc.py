def hal(parent):
    output = []
    linuxcnc_config = parent.project.config["jdata"].get("linuxcnc", {})

    mxmpg_config = linuxcnc_config.get("mxmpg", {})
    mxmpg_enable = mxmpg_config.get("enable", False)
    mxmpg_device = mxmpg_config.get("device", "/dev/ttyACM0")
    mxmpg_buttons = mxmpg_config.get("buttons")
    if mxmpg_enable:
        output.append(f"loadusr -W mpg -d {mxmpg_device} -s")
        output.append("")

        # display status
        parent.hal_net_add("halui.machine.is-on", "mpg.machine.is-on")
        parent.hal_net_add("halui.program.is-running", "mpg.program.is-running")

        if mxmpg_buttons:
            for button_name, button_function in mxmpg_buttons.items():
                if button_function.startswith("MDI|"):
                    parts = button_function.split("|")
                    button_title = parts[1]
                    mdi_command = parts[2]
                    halpin = parent.ini_mdi_command(mdi_command, title=button_title)
                    parent.hal_net_add(f"mpg.button.{button_name}", halpin)
                else:
                    parent.hal_net_add(f"mpg.button.{button_name}", button_function)
        else:
            # programm control
            parent.hal_net_add("mpg.button.01", "halui.program.run")
            parent.hal_net_add("mpg.button.01-long", "halui.program.stop")
            parent.hal_net_add("mpg.button.01b", "halui.program.pause")
            parent.hal_net_add("mpg.button.01b-long", "halui.program.resume")

            # spindle control
            parent.hal_net_add("mpg.button.02-long", "halui.spindle.0.start")
            parent.hal_net_add("mpg.button.02", "halui.spindle.0.stop")
            # robot gripper
            # halpin = parent.ini_mdi_command(f"M68 E0 Q-100")
            # parent.hal_net_add(f"mpg.button.02", halpin)
            # halpin = parent.ini_mdi_command(f"M68 E0 Q40")
            # parent.hal_net_add(f"mpg.button.03", halpin)
            # halpin = parent.ini_mdi_command(f"M68 E0 Q100")
            # parent.hal_net_add(f"mpg.button.04", halpin)

        # homing status
        for axis_name, axis_config in parent.axis_dict.items():
            joints = axis_config["joints"]
            axis_low = axis_name.lower()
            for joint, joint_setup in joints.items():
                parent.hal_net_add(f"joint.{joint}.homed", f"mpg.axis.{axis_low}.homed")

        # zero axis -> mdi commands
        bn = 1
        for axis_name, axis_config in parent.axis_dict.items():
            joints = axis_config["joints"]
            halpin = parent.ini_mdi_command(f"G92 {axis_name}0")
            parent.hal_net_add(f"mpg.button.sel{bn:02d}-long", halpin)
            bn += 1

        # axis selection
        bn = 1
        for axis_name, axis_config in parent.axis_dict.items():
            joints = axis_config["joints"]
            axis_low = axis_name.lower()
            parent.hal_net_add(f"mpg.button.sel{bn:02d}", f"halui.axis.{axis_low}.select")
            for joint, joint_setup in joints.items():
                parent.hal_net_add(f"mpg.button.sel{bn:02d}", f"halui.joint.{joint}.select")
            bn += 1

        # jog axis
        for axis_name, axis_config in parent.axis_dict.items():
            joints = axis_config["joints"]
            axis_low = axis_name.lower()
            parent.hal_setp_add(f"axis.{axis_low}.jog-vel-mode", 1)
            parent.hal_setp_add(f"axis.{axis_low}.jog-enable", 1)
            parent.hal_net_add("mpg.jog-scale", f"axis.{axis_low}.jog-scale")
            parent.hal_net_add(f"mpg.axis.{axis_low}.jog-counts", f"axis.{axis_low}.jog-counts")
            for joint, joint_setup in joints.items():
                parent.hal_setp_add(f"joint.{joint}.jog-vel-mode", 1)
                parent.hal_setp_add(f"joint.{joint}.jog-enable", 1)
                parent.hal_net_add("mpg.jog-scale", f"joint.{joint}.jog-scale")
                parent.hal_net_add(f"mpg.axis.{axis_low}.jog-counts", f"joint.{joint}.jog-counts")

        # display axis positions
        for axis_name, axis_config in parent.axis_dict.items():
            joints = axis_config["joints"]
            axis_low = axis_name.lower()
            parent.hal_net_add(f"halui.axis.{axis_low}.pos-relative", f"mpg.axis.{axis_low}.pos")

        # overwrites
        for ov in ("feed", "rapid"):
            parent.hal_setp_add(f"halui.{ov}-override.scale", 0.01)
            parent.hal_net_add(f"mpg.override.{ov}.counts", f"halui.{ov}-override.counts")
            parent.hal_net_add(f"halui.{ov}-override.value", f"mpg.override.{ov}.value")

        parent.hal_setp_add("halui.spindle.0.override.scale", 0.01)
        parent.hal_net_add("mpg.override.spindle.counts", "halui.spindle.0.override.counts")
        parent.hal_net_add("halui.spindle.0.override.value", "mpg.override.spindle.value")

        output.append("")

    return output
