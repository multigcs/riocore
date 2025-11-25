from .config import BUTTON_FUNCS, BUTTON_NAMES, DEFAULTS


def hal(parent):
    linuxcnc_config = parent.project.config["jdata"].get("linuxcnc", {})
    mxmpg_config = linuxcnc_config.get("mxmpg", {})
    mxmpg_enable = mxmpg_config.get("enable", False)
    mxmpg_device = mxmpg_config.get("device", "/dev/ttyACM0")
    mxmpg_buttons = mxmpg_config.get("buttons", {})
    if mxmpg_enable:
        parent.halg.fmt_add(f"loadusr -W mpg -d {mxmpg_device} -s")
        parent.halg.fmt_add("")

        # display status
        parent.halg.net_add("halui.machine.is-on", "mpg.machine.is-on")
        parent.halg.net_add("halui.program.is-running", "mpg.program.is-running")
        parent.halg.setp_add("mpg.display-mode", 1)
        parent.halg.net_add("halui.mode.is-auto", "mpg.mode.is-auto")
        parent.halg.net_add("halui.mode.is-manual", "mpg.mode.is-manual")
        parent.halg.net_add("halui.mode.is-mdi", "mpg.mode.is-mdi")
        parent.halg.net_add("iocontrol.0.coolant-mist", "mpg.coolant-mist")
        parent.halg.net_add("iocontrol.0.coolant-flood", "mpg.coolant-flood")
        parent.halg.net_add("iocontrol.0.tool-number", "mpg.tool-number")

        for button_name in BUTTON_NAMES:
            for bfunc in BUTTON_FUNCS:
                button_function = mxmpg_buttons.get(button_name, {}).get(bfunc, DEFAULTS.get(f"{button_name}-{bfunc}", ""))
                if not button_function:
                    continue
                pinname = f"mpg.button.{button_name}-{bfunc}".replace("-short", "")
                if button_function.startswith("MDI|"):
                    parts = button_function.split("|")
                    button_title = parts[1]
                    mdi_command = parts[2]
                    halpin = parent.ini_mdi_command(mdi_command, title=button_title)
                    parent.halg.net_add(pinname, halpin)
                else:
                    parent.halg.net_add(pinname, button_function)

        # homing status
        for axis_name, axis_config in parent.project.axis_dict.items():
            joints = axis_config["joints"]
            axis_low = axis_name.lower()
            for joint, joint_setup in joints.items():
                parent.halg.net_add(f"joint.{joint}.homed", f"mpg.axis.{axis_low}.homed")

        # zero axis -> mdi commands
        bn = 1
        for axis_name, axis_config in parent.project.axis_dict.items():
            joints = axis_config["joints"]
            halpin = parent.ini_mdi_command(f"G92 {axis_name}0")
            parent.halg.net_add(f"mpg.button.sel{bn:02d}-long", halpin)
            bn += 1

        # axis selection
        bn = 1
        for axis_name, axis_config in parent.project.axis_dict.items():
            joints = axis_config["joints"]
            axis_low = axis_name.lower()
            parent.halg.net_add(f"mpg.button.sel{bn:02d}", f"halui.axis.{axis_low}.select")
            for joint, joint_setup in joints.items():
                parent.halg.net_add(f"mpg.button.sel{bn:02d}", f"halui.joint.{joint}.select")
            bn += 1

        # jog axis
        for axis_name, axis_config in parent.project.axis_dict.items():
            joints = axis_config["joints"]
            axis_low = axis_name.lower()
            parent.halg.setp_add(f"axis.{axis_low}.jog-vel-mode", 1)
            parent.halg.setp_add(f"axis.{axis_low}.jog-enable", 1)
            parent.halg.net_add("mpg.jog-scale", f"axis.{axis_low}.jog-scale")
            parent.halg.net_add(f"mpg.axis.{axis_low}.jog-counts", f"axis.{axis_low}.jog-counts")
            for joint, joint_setup in joints.items():
                parent.halg.setp_add(f"joint.{joint}.jog-vel-mode", 1)
                parent.halg.setp_add(f"joint.{joint}.jog-enable", 1)
                parent.halg.net_add("mpg.jog-scale", f"joint.{joint}.jog-scale")
                parent.halg.net_add(f"mpg.axis.{axis_low}.jog-counts", f"joint.{joint}.jog-counts")

        # display axis positions
        for axis_name, axis_config in parent.project.axis_dict.items():
            joints = axis_config["joints"]
            axis_low = axis_name.lower()
            parent.halg.net_add(f"halui.axis.{axis_low}.pos-relative", f"mpg.axis.{axis_low}.pos")

        # overwrites
        for ov in ("feed", "rapid"):
            parent.halg.setp_add(f"halui.{ov}-override.scale", 0.01)
            parent.halg.net_add(f"mpg.override.{ov}.counts", f"halui.{ov}-override.counts")
            parent.halg.net_add(f"halui.{ov}-override.value", f"mpg.override.{ov}.value")

        parent.halg.setp_add("halui.spindle.0.override.scale", 0.01)
        parent.halg.net_add("mpg.override.spindle.counts", "halui.spindle.0.override.counts")
        parent.halg.net_add("halui.spindle.0.override.value", "mpg.override.spindle.value")
