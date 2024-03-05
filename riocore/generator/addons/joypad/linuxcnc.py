def generator(parent):
    linuxcnc_config = parent.project.config["jdata"].get("linuxcnc", {})
    joypad = linuxcnc_config.get("joypad", {})
    if not joypad or not joypad.get("enable"):
        return

    joypad_type = joypad.get("name", "Microntek")
    joypad_btn_slow = joypad.get("btn_slow", "btn-base")
    joypad_btn_medium = joypad.get("btn_medium", "btn-base2")
    joypad_btn_fast = joypad.get("btn_fast", "btn-top2")

    joypad_axis = joypad.get(
        "axis",
        {
            "x": {
                "input": "x",
            },
            "y": {
                "input": "x",
            },
            "z": {
                "input": "z",
            },
            "a": {
                "input": "rz",
            },
        },
    )

    muxes = []
    for axis_name, joints in parent.axis_dict.items():
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
    output.append(f"net slow   <= joy_or2_sel0.in0 <= input.0.{joypad_btn_slow}")
    output.append(f"net medium <= joy_or2_sel1.in0 <= input.0.{joypad_btn_medium}")
    output.append(f"net fast   <= joy_or2_sel0.in1 joy_or2_sel1.in1 <= input.0.{joypad_btn_fast}")
    output.append("")
    output.append("net joy-speed-sel0 <= joy_or2_sel0.out  => joy_mux4.sel0 ")
    output.append("net joy-speed-sel1 <= joy_or2_sel1.out  => joy_mux4.sel1 ")
    output.append("net jog-speed      <= joy_mux4.out => halui.axis.jog-speed halui.joint.jog-speed")
    output.append("")

    for axis_name, joints in parent.axis_dict.items():
        axis_lower = axis_name.lower()
        jaxis = joypad_axis.get(axis_lower, {}).get("input", axis_lower)
        reverse = joypad_axis.get(axis_lower, {}).get("reverse", False)
        output.append(f"# {axis_name}-Axis")
        if reverse:
            output.append(f"setp input.0.abs-{jaxis}-scale -127.5")

        output.append(f"addf mux2_{axis_lower} servo-thread")
        output.append(f"net rio.machine-is-on => mux2_{axis_lower}.sel")

        output.append(f"net jog-{axis_lower}-pre input.0.abs-{jaxis}-position => mux2_{axis_lower}.in1")

        output.append(f"net jog-{axis_lower}-analog mux2_{axis_lower}.out => halui.axis.{axis_lower}.analog")
        for joint, joint_setup in joints.items():
            output.append(f"net jog-{axis_lower}-analog => halui.joint.{joint}.analog")
        output.append("")
    output.append("")

    open(f"{parent.configuration_path}/joypad.hal", "w").write("\n".join(output))
    parent.postgui_call_list.append("source joypad.hal")
