def ini(parent, ini_setup):
    linuxcnc_config = parent.project.config["jdata"].get("linuxcnc", {})
    gui = parent.project.config["jdata"].get("gui", "axis")
    offset_num = 0
    for camera_num, camera in enumerate(linuxcnc_config.get("camera", [])):
        if camera and camera.get("enable"):
            camera_device = camera.get("device", f"/dev/video{camera_num}")
            tabname = camera.get("tabname", f"Camera-{camera_num}")
            tablocation = camera.get("tablocation", "Pyngcgui")
            offsets = camera.get("offset", {})
            ini_setup["DISPLAY"][f"EMBED_TAB_NAME|CAM{camera_num}"] = tabname
            if gui != "axis":
                ini_setup["DISPLAY"][f"EMBED_TAB_LOCATION|CAM{camera_num}"] = tablocation
            ini_setup["DISPLAY"][f"EMBED_TAB_COMMAND|CAM{camera_num}"] = (
                f"mplayer -wid {{XID}} tv:// -tv driver=v4l2:device={camera_device} -vf rectangle=-1:2:-1:240,rectangle=2:-1:320:-1 -really-quiet"
            )
            if not offsets and offset_num == 0:
                offsets = {}
                for axis_name, joints in parent.axis_dict.items():
                    offsets[axis_name] = 0

            if offset_num == 0:
                mdi_command = ["G92"]
                for axis_name, joints in parent.axis_dict.items():
                    diff = 0
                    if axis_name in offsets:
                        diff = offsets[axis_name]
                    mdi_command.append(f"{axis_name}{diff}")
                ini_setup["HALUI"]["MDI_COMMAND|06"] = " ".join(mdi_command)
                offset_num += 1
            elif offsets:
                print("WARNING: offset works only on one camera")


def gui(parent):
    cfgxml_data = {"status": []}
    valid = False
    gui = parent.project.config["jdata"].get("gui", "axis")
    if gui != "qtdragon":
        cfgxml_data["status"].append('  <labelframe text="MDI-Commands">')
        cfgxml_data["status"].append("    <relief>RAISED</relief>")
        cfgxml_data["status"].append('    <font>("Helvetica", 10)</font>')
        cfgxml_data["status"].append("    <hbox>")
        cfgxml_data["status"].append("      <relief>RIDGE</relief>")
        cfgxml_data["status"].append("      <bd>2</bd>")
        for camera_num, camera in enumerate(parent.project.config["jdata"].get("camera", [])):
            if camera and camera.get("enable"):
                offsets = camera.get("offset")
                if offsets:
                    parent.custom_net_add("rio.zerocam", "halui.mdi-command-06")
                    cfgxml_data["status"] += parent.gui_gen.draw_button("zero-cam", "zerocam")
                    valid = True
                    break
        cfgxml_data["status"].append("    </hbox>")
        cfgxml_data["status"].append("  </labelframe>")

    if valid:
        return cfgxml_data
    return {}
