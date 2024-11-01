import os
import shutil
import stat

addon_path = os.path.dirname(__file__)


def ini(parent, ini_setup):
    linuxcnc_config = parent.project.config["jdata"].get("linuxcnc", {})
    gui = parent.project.config["jdata"].get("gui", "axis")

    source = f"{addon_path}/camjog.py"
    target = f"{parent.component_path}/camjog.py"
    shutil.copy(source, target)
    os.chmod(target, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    for camjog_num, camjog in enumerate(linuxcnc_config.get("camjog", [])):
        if camjog and camjog.get("enable"):
            camjog_device = camjog.get("device", f"/dev/video{camjog_num}")
            width = camjog.get("width", 640)
            height = camjog.get("height", 480)
            scale = camjog.get("scale", 1.0)
            tabname = camjog.get("tabname", f"camjog-{camjog_num}")
            tablocation = camjog.get("tablocation", "Pyngcgui")
            ini_setup["DISPLAY"][f"EMBED_TAB_NAME|CAMJOG{camjog_num}"] = tabname
            if gui != "axis":
                ini_setup["DISPLAY"][f"EMBED_TAB_LOCATION|CAMJOG{camjog_num}"] = tablocation

            cmd_args = ["halcmd loadusr -Wn camjog ./camjog.py"]
            cmd_args.append("--xid {XID}")
            if camjog_device.startswith("/dev/video"):
                cmd_args.append(f"--video {camjog_device[-1]}")
            elif len(camjog_device) <= 2:
                cmd_args.append(f"--video {camjog_device}")
            else:
                cmd_args.append(f"--camera {camjog_device[-1]}")
            cmd_args.append(f"--width {width}")
            cmd_args.append(f"--height {height}")
            cmd_args.append(f"--scale {scale}")
            ini_setup["DISPLAY"][f"EMBED_TAB_COMMAND|CAMJOG{camjog_num}"] = f"{' '.join(cmd_args)}"


def gui(parent):
    linuxcnc_config = parent.project.config["jdata"].get("linuxcnc", {})
    gui = parent.project.config["jdata"].get("gui", "axis")
    if gui != "qtdragon":
        offset_num = 0
        for camjog_num, camjog in enumerate(linuxcnc_config.get("camjog", [])):
            if camjog and camjog.get("enable"):
                offsets = camjog.get("offset", {})
                if offset_num == 0:
                    mdi_command = ["G92"]
                    for axis_name, axis_config in parent.axis_dict.items():
                        diff = 0
                        if axis_name in offsets:
                            diff = offsets[axis_name]
                            mdi_command.append(f"{axis_name}{diff}")
                    offset_num += 1
                elif offsets:
                    print("WARNING: offset works only on one camjog")
    return []


def hal(parent):
    output = []
    linuxcnc_config = parent.project.config["jdata"].get("linuxcnc", {})
    parent.postgui_components_add("camjog")
    for camjog_num, camjog in enumerate(linuxcnc_config.get("camjog", [])):
        if camjog and camjog.get("enable"):
            # jog axis
            for axis_name, axis_config in parent.axis_dict.items():
                if axis_name not in {"X", "Y"}:
                    continue

                joints = axis_config["joints"]
                axis_low = axis_name.lower()
                parent.hal_setp_add(f"axis.{axis_low}.jog-vel-mode", 0)
                parent.hal_setp_add(f"axis.{axis_low}.jog-enable", 1)
                parent.hal_setp_add(f"axis.{axis_low}.jog-scale", 0.01)
                parent.hal_net_add(f"camjog.axis.{axis_low}.jog-counts", f"axis.{axis_low}.jog-counts")
                for joint, joint_setup in joints.items():
                    parent.hal_setp_add(f"joint.{joint}.jog-vel-mode", 0)
                    parent.hal_setp_add(f"joint.{joint}.jog-enable", 1)
                    parent.hal_setp_add(f"joint.{joint}.jog-scale", 0.01)
                    parent.hal_net_add(f"camjog.axis.{axis_low}.jog-counts", f"joint.{joint}.jog-counts")

            output.append("")
            break

    return output
