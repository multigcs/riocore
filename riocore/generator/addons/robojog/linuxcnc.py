import os
import shutil
import stat

addon_path = os.path.dirname(__file__)


def ini(parent, ini_setup):
    linuxcnc_config = parent.project.config["jdata"].get("linuxcnc", {})
    robojog_config = linuxcnc_config.get("robojog", {})
    robojog_enable = robojog_config.get("enable", False)
    if robojog_enable:
        source = os.path.join(addon_path, "robojog.py")
        target = os.path.join(parent.component_path, "robojog.py")
        shutil.copy(source, target)
        os.chmod(target, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
        tabname = robojog_config.get("tabname", "robojog")
        ini_setup["DISPLAY"]["EMBED_TAB_NAME|robojog"] = tabname
        if parent.gui_tablocation:
            ini_setup["DISPLAY"]["EMBED_TAB_LOCATION|robojog"] = parent.gui_tablocation

        cmd_args = ["halcmd loadusr -Wn robojog ./robojog.py"]
        cmd_args.append("--xid {XID}")
        cmd_args.append(f"--joints {6}")
        ini_setup["DISPLAY"]["EMBED_TAB_COMMAND|robojog"] = f"{' '.join(cmd_args)}"


def hal(parent):
    linuxcnc_config = parent.project.config["jdata"].get("linuxcnc", {})

    robojog_config = linuxcnc_config.get("robojog", {})
    robojog_enable = robojog_config.get("enable", False)
    if robojog_enable:
        parent.halg.postgui_components_add("robojog")

        # jog axis
        for axis_name, axis_config in parent.project.axis_dict.items():
            joints = axis_config["joints"]
            # axis_low = axis_name.lower()
            # parent.halg.setp_add(f"axis.{axis_low}.jog-vel-mode", 0)
            # parent.halg.setp_add(f"axis.{axis_low}.jog-enable", 1)
            # parent.halg.setp_add(f"axis.{axis_low}.jog-scale", 0.01)
            # parent.halg.net_add(f"robojog.joint.{joint}.jog-counts", f"axis.{axis_low}.jog-counts")
            for joint, joint_setup in joints.items():
                min_limit = joint_setup.get("MIN_LIMIT", -180)
                max_limit = joint_setup.get("MAX_LIMIT", 180)
                if joint_setup.get("TYPE") == "ANGULAR":
                    min_limit = max(joint_setup.get("MIN_LIMIT", -180), -180)
                    max_limit = min(joint_setup.get("MAX_LIMIT", 180), 180)

                parent.halg.setp_add(f"robojog.joint.{joint}.scale", 100.0)
                parent.halg.setp_add(f"robojog.joint.{joint}.min_limit", min_limit)
                parent.halg.setp_add(f"robojog.joint.{joint}.max_limit", max_limit)
                parent.halg.setp_add(f"joint.{joint}.jog-vel-mode", 0)
                parent.halg.setp_add(f"joint.{joint}.jog-enable", 1)
                parent.halg.setp_add(f"joint.{joint}.jog-scale", 0.01)
                parent.halg.net_add(f"robojog.joint.{joint}.jog-counts", f"joint.{joint}.jog-counts")
                parent.halg.net_add(f"joint.{joint}.pos-fb", f"robojog.joint.{joint}.position")
