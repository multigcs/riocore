import os
import shutil
import stat

addon_path = os.path.dirname(__file__)


def hal(parent):
    linuxcnc_config = parent.project.config["jdata"].get("linuxcnc", {})

    spnav_config = linuxcnc_config.get("spnav", {})
    spnav_enable = spnav_config.get("enable", False)
    spnav_jointjog = spnav_config.get("jointjog", False)
    spnav_scale = {}
    spnav_scale["x"] = spnav_config.get("x-scale", -0.2)
    spnav_scale["y"] = spnav_config.get("y-scale", -0.2)
    spnav_scale["z"] = spnav_config.get("z-scale", 0.2)
    spnav_scale["a"] = spnav_config.get("a-scale", 0.0)
    spnav_scale["b"] = spnav_config.get("b-scale", 0.0)
    spnav_scale["c"] = spnav_config.get("c-scale", 0.02)
    spnav_button0 = spnav_config.get("botton-0", "")
    spnav_button1 = spnav_config.get("botton-1", "")

    if spnav_enable:
        parent.halg.fmt_add("loadusr -Wn spnav ./spnav.py")
        parent.halg.fmt_add("")

        source = f"{addon_path}/spnav.py"
        target = f"{parent.component_path}/spnav.py"
        shutil.copy(source, target)
        os.chmod(target, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

        for axis in "xyzabc":
            if axis.upper() in parent.project.axis_dict and spnav_scale[axis] != 0.0:
                parent.halg.setp_add(f"spnav.axis.{axis}.scale", spnav_scale[axis])
                parent.halg.net_add(f"spnav.axis.{axis}.jog-counts", f"axis.{axis}.jog-counts")
                parent.halg.setp_add(f"axis.{axis}.jog-vel-mode", 1)
                parent.halg.setp_add(f"axis.{axis}.jog-enable", 1)
                parent.halg.setp_add(f"axis.{axis}.jog-scale", 0.01)
                if not spnav_jointjog:
                    continue
                axis_config = parent.project.axis_dict.get(axis.upper())
                joints = axis_config["joints"]
                for joint, joint_setup in joints.items():
                    parent.halg.setp_add(f"spnav.axis.{axis}.scale", spnav_scale[axis])
                    parent.halg.net_add(f"spnav.axis.{axis}.jog-counts", f"joint.{joint}.jog-counts")
                    parent.halg.setp_add(f"joint.{joint}.jog-vel-mode", 1)
                    parent.halg.setp_add(f"joint.{joint}.jog-enable", 1)
                    parent.halg.setp_add(f"joint.{joint}.jog-scale", 0.01)

        if spnav_button0:
            if spnav_button0.startswith("MDI|"):
                parts = spnav_button0.split("|")
                button_title = parts[1]
                mdi_command = parts[2]
                halpin = parent.ini_mdi_command(mdi_command, title=button_title)
                parent.halg.net_add("spnav.button.0", halpin)
            else:
                parent.halg.net_add("spnav.button.0", spnav_button0)
        if spnav_button1:
            if spnav_button1.startswith("MDI|"):
                parts = spnav_button1.split("|")
                button_title = parts[1]
                mdi_command = parts[2]
                halpin = parent.ini_mdi_command(mdi_command, title=button_title)
                parent.halg.net_add("spnav.button.1", halpin)
            else:
                parent.halg.net_add("spnav.button.1", spnav_button1)
