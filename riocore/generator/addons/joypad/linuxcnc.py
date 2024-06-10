def hal(parent):
    output = []

    linuxcnc_config = parent.project.config["jdata"].get("linuxcnc", {})
    joypad = linuxcnc_config.get("joypad", {})
    if not joypad or not joypad.get("enable"):
        return output

    joypad_type = joypad.get("name")
    joypad_btn_slow = joypad.get("slow")
    joypad_btn_medium = joypad.get("medium")
    joypad_btn_fast = joypad.get("fast")

    muxes = []
    for axis_name, axis_config in parent.axis_dict.items():
        joints = axis_config["joints"]
        axis_lower = axis_name.lower()
        muxes.append(f"mux2_{axis_lower}")

    output = []
    output.append(f"loadusr -W hal_input -KRAL {joypad_type}")
    output.append("loadrt or2 names=joy_or2_sel0,joy_or2_sel1")
    output.append("loadrt mux4 names=joy_mux4")
    output.append(f"loadrt mux2 names={','.join(muxes)}")
    output.append("")
    output.append("addf joy_or2_sel0 servo-thread")
    output.append("addf joy_or2_sel1 servo-thread")
    output.append("addf joy_mux4 servo-thread")
    output.append("")
    output.append("setp joy_mux4.in0 0.0    # Setting this input to 0 prevents motion unless one of the other buttons is pressed.")
    output.append("setp joy_mux4.in1 50.0   # Max jog speed when first speed select button is pressed.")
    output.append("setp joy_mux4.in2 500.0  # Max jog speed when second speed select button is pressed.")
    output.append("setp joy_mux4.in3 2000.0 # Max jog speed when third speed select button is pressed.")
    output.append("")
    if joypad_btn_slow:
        parent.hal_net_add(f"input.0.{joypad_btn_slow}", "joy_or2_sel0.in0")
    if joypad_btn_medium:
        parent.hal_net_add(f"input.0.{joypad_btn_medium}", "joy_or2_sel1.in0")
    if joypad_btn_fast:
        parent.hal_net_add(f"input.0.{joypad_btn_fast}", "joy_or2_sel0.in1")
        parent.hal_net_add(f"input.0.{joypad_btn_fast}", "joy_or2_sel1.in1")

    parent.hal_net_add("joy_or2_sel0.out", "joy_mux4.sel0")
    parent.hal_net_add("joy_or2_sel1.out", "joy_mux4.sel1")
    # parent.hal_net_add(f"joy_mux4.out", f"halui.axis.jog-speed")
    # parent.hal_net_add(f"joy_mux4.out", f"halui.joint.jog-speed")

    for axis_name, axis_config in parent.axis_dict.items():
        joints = axis_config["joints"]
        axis_lower = axis_name.lower()
        jaxis = joypad.get(axis_lower)
        reverse = False
        if jaxis:
            output.append(f"# {axis_name}-Axis")
            if reverse:
                output.append(f"setp input.0.{jaxis}-scale -127.5")
            output.append(f"addf mux2_{axis_lower} servo-thread")
            parent.hal_net_add("halui.machine.is-on", f"mux2_{axis_lower}.sel")
            parent.hal_net_add(f"input.0.{jaxis}-position", f"mux2_{axis_lower}.in1")
            parent.hal_net_add(f"mux2_{axis_lower}.out", f"halui.axis.{axis_lower}.analog")
            for joint, joint_setup in joints.items():
                parent.hal_net_add(f"mux2_{axis_lower}.out", f"halui.joint.{joint}.analog")
    return output
