import linuxcnc as emc


def toggle(parent):
    btn = parent.sender()
    on_text = btn.property("on_text")
    off_text = btn.property("off_text")

    if btn.isChecked():  # probing is enabled
        parent.probing = True
        for item in parent.probe_controls:
            getattr(parent, item).setEnabled(True)
        parent.spindle_speed = 0
        if "spindle_speed_lb" in parent.children:
            parent.spindle_speed_lb.setText(f"{parent.spindle_speed}")
        parent.command.spindle(emc.SPINDLE_OFF)

        for key, value in parent.program_running.items():
            getattr(parent, key).setEnabled(False)

        if None not in [on_text, off_text]:
            btn.setText(on_text)

        if "probing_enable_pb" in parent.children and hasattr(parent.probing_enable_pb, "led"):
            parent.probing_enable_pb.led = True

        if parent.probe_enable_on_color:
            parent.probing_enable_pb.setStyleSheet(parent.probe_enable_on_color)

    else:  # probing is disabled
        parent.probing = False
        for item in parent.probe_controls:
            getattr(parent, item).setEnabled(False)

        for key, value in parent.program_running.items():
            getattr(parent, key).setEnabled(True)

        if None not in [on_text, off_text]:
            btn.setText(off_text)

        if "probing_enable_pb" in parent.children and hasattr(parent.probing_enable_pb, "led"):
            parent.probing_enable_pb.led = False

        if parent.probe_enable_off_color:
            parent.probing_enable_pb.setStyleSheet(parent.probe_enable_off_color)
