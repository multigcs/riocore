def hal(parent):
    output = []
    linuxcnc_config = parent.project.config["jdata"].get("linuxcnc", {})

    classicladder_config = linuxcnc_config.get("classicladder", {})
    classicladder_enable = classicladder_config.get("enable", False)
    if classicladder_enable:
        output.append("loadrt classicladder_rt")
        output.append("addf classicladder.0.refresh servo-thread")
        output.append("")
    return output
