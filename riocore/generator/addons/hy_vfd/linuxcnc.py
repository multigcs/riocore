def hal(parent):
    output = []
    linuxcnc_config = parent.project.config["jdata"].get("linuxcnc", {})

    hy_vfd_config = linuxcnc_config.get("hy_vfd", {})
    hy_vfd_enable = hy_vfd_config.get("enable", False)
    hy_vfd_dev = hy_vfd_config.get("device")
    if hy_vfd_enable and hy_vfd_dev:
        hy_vfd_address = hy_vfd_config.get("address", 1)
        hy_vfd_baud = hy_vfd_config.get("baud", "9600")
        output.append(f"loadusr -Wn vfd hy_vfd -n vfd -d {hy_vfd_dev} -p none -r {hy_vfd_baud} -t {hy_vfd_address}")
        output.append("setp vfd.enable 1")
        output.append("net spindle0_speed spindle.0.speed-out-abs => vfd.speed-command")
        output.append("net spindle0_forward spindle.0.forward => vfd.spindle-forward")
        output.append("net spindle0_reverse spindle.0.reverse => vfd.spindle-reverse")
        output.append("net spindle0_on spindle.0.on => vfd.spindle-on")
        output.append("")
    return output
