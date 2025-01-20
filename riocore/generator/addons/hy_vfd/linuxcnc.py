def hal(parent):
    linuxcnc_config = parent.project.config["jdata"].get("linuxcnc", {})
    hy_vfd_config = linuxcnc_config.get("hy_vfd", {})
    hy_vfd_enable = hy_vfd_config.get("enable", False)
    hy_vfd_dev = hy_vfd_config.get("device")
    if hy_vfd_enable and hy_vfd_dev:
        hy_vfd_address = hy_vfd_config.get("address", 1)
        hy_vfd_baud = hy_vfd_config.get("baud", "9600")
        parent.halg.fmt_add(f"loadusr -Wn vfd hy_vfd -n vfd -d {hy_vfd_dev} -p none -r {hy_vfd_baud} -t {hy_vfd_address}")
        parent.halg.setp_add("vfd.enable", 1)
        parent.halg.net_add("spindle.0.speed-out-abs", "vfd.speed-command", "spindle0_speed")
        parent.halg.net_add("spindle.0.forward", "vfd.spindle-forward", "spindle0_forward")
        parent.halg.net_add("spindle.0.reverse", "vfd.spindle-reverse", "spindle0_reverse")
        parent.halg.net_add("spindle.0.on", "vfd.spindle-on", "spindle0_on")
