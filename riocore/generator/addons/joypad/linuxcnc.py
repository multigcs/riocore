def hal(parent):
    linuxcnc_config = parent.project.config["jdata"].get("linuxcnc", {})
    joypad = linuxcnc_config.get("joypad", {})
    if not joypad or not joypad.get("enable"):
        return

    joypad_type = joypad.get("name")
    joypad_btn_slow = joypad.get("slow")
    joypad_btn_medium = joypad.get("medium")
    joypad_btn_fast = joypad.get("fast")

    muxes = []
    for axis_name, axis_config in parent.project.axis_dict.items():
        joints = axis_config["joints"]
        axis_lower = axis_name.lower()
        muxes.append(f"mux2_{axis_lower}")

    parent.halg.fmt_add(f"loadusr -W hal_input -KRAL {joypad_type}")
    parent.halg.fmt_add("loadrt mux4 names=joy_mux4")
    parent.halg.fmt_add(f"loadrt mux2 names={','.join(muxes)}")
    parent.halg.fmt_add("")
    parent.halg.fmt_add("addf joy_mux4 servo-thread")
    parent.halg.fmt_add("")
    parent.halg.fmt_add("setp joy_mux4.in0 0.0    # Setting this input to 0 prevents motion unless one of the other buttons is pressed.")
    parent.halg.fmt_add("setp joy_mux4.in1 50.0   # Max jog speed when first speed select button is pressed.")
    parent.halg.fmt_add("setp joy_mux4.in2 500.0  # Max jog speed when second speed select button is pressed.")
    parent.halg.fmt_add("setp joy_mux4.in3 2000.0 # Max jog speed when third speed select button is pressed.")
    parent.halg.fmt_add("")

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
        jaxis = joypad.get(axis_lower)
        reverse = False
        if jaxis:
            if jaxis[0] == "-":
                jaxis = jaxis[1:]
                reverse = True
            parent.halg.fmt_add(f"# {axis_name}-Axis")
            if reverse:
                parent.halg.fmt_add(f"setp input.0.{jaxis}-scale -127.5")
            parent.halg.fmt_add(f"addf mux2_{axis_lower} servo-thread")
            parent.halg.net_add("halui.machine.is-on", f"mux2_{axis_lower}.sel")
            parent.halg.net_add(f"input.0.{jaxis}-position", f"mux2_{axis_lower}.in1")
            parent.halg.net_add(f"mux2_{axis_lower}.out", f"halui.axis.{axis_lower}.analog")
            for joint, joint_setup in joints.items():
                parent.halg.net_add(f"mux2_{axis_lower}.out", f"halui.joint.{joint}.analog")
