def ini(parent, ini_setup):
    linuxcnc_config = parent.project.config["jdata"].get("linuxcnc", {})
    gui = parent.project.config["jdata"].get("gui", "axis")
    for camera_num, camera in enumerate(linuxcnc_config.get("camera", [])):
        if camera and camera.get("enable"):
            camera_device = camera.get("device", f"/dev/video{camera_num}")
            tabname = camera.get("tabname", f"Camera-{camera_num}")
            tablocation = camera.get("tablocation", "Pyngcgui")
            ini_setup["DISPLAY"][f"EMBED_TAB_NAME|CAM{camera_num}"] = tabname
            if gui != "axis":
                ini_setup["DISPLAY"][f"EMBED_TAB_LOCATION|CAM{camera_num}"] = tablocation
            ini_setup["DISPLAY"][f"EMBED_TAB_COMMAND|CAM{camera_num}"] = (
                f"mplayer -wid {{XID}} tv:// -tv driver=v4l2:device={camera_device} -vf rectangle=-1:2:-1:240,rectangle=2:-1:320:-1 -really-quiet"
            )


def gui(parent):
    linuxcnc_config = parent.project.config["jdata"].get("linuxcnc", {})
    gui = parent.project.config["jdata"].get("gui", "axis")
    if gui != "qtdragon":
        offset_num = 0
        for camera_num, camera in enumerate(linuxcnc_config.get("camera", [])):
            if camera and camera.get("enable"):
                offsets = camera.get("offset", {})
                if offset_num == 0:
                    mdi_command = ["G92"]
                    for axis_name, axis_config in parent.axis_dict.items():
                        diff = 0
                        if axis_name in offsets:
                            diff = offsets[axis_name]
                            mdi_command.append(f"{axis_name}{diff}")
                    offset_num += 1
                elif offsets:
                    print("WARNING: offset works only on one camera")
    return []
