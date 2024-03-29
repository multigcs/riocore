RIO_FUNCTIONS = {
    "inout": {},
    "output": {
        "jog.selected-x": {"help": "X is the selected axis", "type": bool},
        "jog.selected-y": {"help": "Y is the selected axis", "type": bool},
        "jog.selected-z": {"help": "Z is the selected axis", "type": bool},
        "jog.position": {"help": "Position of selected axis", "type": float},
    },
    "input": {
        "jog.wheel_x": {"help": "Jog-Wheel X-Axis", "type": float},
        "jog.wheel_y": {"help": "Jog-Wheel Y-Axis", "type": float},
        "jog.wheel_z": {"help": "Jog-Wheel Z-Axis", "type": float},
        "jog.select-x": {"help": "Jog-Select X-Axis", "type": bool},
        "jog.select-y": {"help": "Jog-Select Y-Axis", "type": bool},
        "jog.select-z": {"help": "Jog-Select Z-Axis", "type": bool},
        "jog.plus": {"help": "Jog selected axis plus", "type": bool},
        "jog.minus": {"help": "Jog selected axis minus", "type": bool},
        "jog.fast": {"help": "Jog set fast", "type": bool},
    },
}

LINUXCNC_SIGNALS = {
    "inout": {"joint.0.index-enable": {"help": "Joint", "type": bool}, "spindle.0.index-enable": {"help": "", "type": bool}},
    "input": {
        "axis.x.eoffset-clear": {"help": "Axis", "type": bool},
        "axis.x.eoffset-counts": {"help": "Axis", "type": int},
        "axis.x.eoffset-enable": {"help": "Axis", "type": bool},
        "axis.x.eoffset-scale": {"help": "Axis", "type": float},
        "axis.x.jog-accel-fraction": {"help": "Axis", "type": float},
        "axis.x.jog-counts": {"help": "Axis", "type": int},
        "axis.x.jog-enable": {"help": "Axis", "type": bool},
        "axis.x.jog-scale": {"help": "Axis", "type": float},
        "axis.x.jog-vel-mode": {"help": "Axis", "type": bool},
        "axisui.notifications-clear": {"help": "", "type": bool},
        "axisui.notifications-clear-error": {"help": "", "type": bool},
        "axisui.notifications-clear-info": {"help": "", "type": bool},
        "axisui.resume-inhibit": {"help": "", "type": bool},
        "hal_manualtoolchange.change": {"help": "", "type": bool},
        "hal_manualtoolchange.change_button": {"help": "", "type": bool},
        "hal_manualtoolchange.number": {"help": "", "type": int},
        "halui.abort": {"help": "", "type": bool},
        "halui.axis.x.analog": {"help": "Axis", "type": float},
        "halui.axis.x.increment": {"help": "Axis", "type": float},
        "halui.axis.x.increment-minus": {"help": "Axis", "type": bool},
        "halui.axis.x.increment-plus": {"help": "Axis", "type": bool},
        "halui.axis.x.minus": {"help": "Axis", "type": bool},
        "halui.axis.x.plus": {"help": "Axis", "type": bool},
        "halui.axis.x.select": {"help": "Axis", "type": bool},
        "halui.estop.activate": {"help": "", "type": bool},
        "halui.estop.reset": {"help": "", "type": bool},
        "halui.feed-override.count-enable": {"help": "", "type": bool},
        "halui.feed-override.counts": {"help": "", "type": int},
        "halui.feed-override.decrease": {"help": "", "type": bool},
        "halui.feed-override.direct-value": {"help": "", "type": bool},
        "halui.feed-override.increase": {"help": "", "type": bool},
        "halui.feed-override.reset": {"help": "", "type": bool},
        "halui.feed-override.scale": {"help": "", "type": float},
        "halui.flood.off": {"help": "", "type": bool},
        "halui.flood.on": {"help": "", "type": bool},
        "halui.home-all": {"help": "", "type": bool},
        "halui.joint.0.analog": {"help": "Joint", "type": float},
        "halui.joint.0.home": {"help": "Joint", "type": bool},
        "halui.joint.0.increment": {"help": "Joint", "type": float},
        "halui.joint.0.increment-minus": {"help": "Joint", "type": bool},
        "halui.joint.0.increment-plus": {"help": "Joint", "type": bool},
        "halui.joint.0.minus": {"help": "Joint", "type": bool},
        "halui.joint.0.plus": {"help": "Joint", "type": bool},
        "halui.joint.0.select": {"help": "Joint", "type": bool},
        "halui.joint.0.unhome": {"help": "Joint", "type": bool},
        "halui.lube.off": {"help": "", "type": bool},
        "halui.lube.on": {"help": "", "type": bool},
        "halui.machine.off": {"help": "", "type": bool},
        "halui.machine.on": {"help": "", "type": bool},
        "halui.max-velocity.count-enable": {"help": "", "type": bool},
        "halui.max-velocity.counts": {"help": "", "type": int},
        "halui.max-velocity.decrease": {"help": "", "type": bool},
        "halui.max-velocity.direct-value": {"help": "", "type": bool},
        "halui.max-velocity.increase": {"help": "", "type": bool},
        "halui.max-velocity.scale": {"help": "", "type": float},
        "halui.mdi-command-00": {"help": "", "type": bool},
        "halui.mdi-command-01": {"help": "", "type": bool},
        "halui.mdi-command-02": {"help": "", "type": bool},
        "halui.mdi-command-03": {"help": "", "type": bool},
        "halui.mdi-command-04": {"help": "", "type": bool},
        "halui.mdi-command-05": {"help": "", "type": bool},
        "halui.mdi-command-06": {"help": "", "type": bool},
        "halui.mist.off": {"help": "", "type": bool},
        "halui.mist.on": {"help": "", "type": bool},
        "halui.mode.auto": {"help": "", "type": bool},
        "halui.mode.joint": {"help": "", "type": bool},
        "halui.mode.manual": {"help": "", "type": bool},
        "halui.mode.mdi": {"help": "", "type": bool},
        "halui.mode.teleop": {"help": "", "type": bool},
        "halui.program.block-delete.off": {"help": "", "type": bool},
        "halui.program.block-delete.on": {"help": "", "type": bool},
        "halui.program.optional-stop.off": {"help": "", "type": bool},
        "halui.program.optional-stop.on": {"help": "", "type": bool},
        "halui.program.pause": {"help": "", "type": bool},
        "halui.program.resume": {"help": "", "type": bool},
        "halui.program.run": {"help": "", "type": bool},
        "halui.program.step": {"help": "", "type": bool},
        "halui.program.stop": {"help": "", "type": bool},
        "halui.rapid-override.count-enable": {"help": "", "type": bool},
        "halui.rapid-override.counts": {"help": "", "type": int},
        "halui.rapid-override.decrease": {"help": "", "type": bool},
        "halui.rapid-override.direct-value": {"help": "", "type": bool},
        "halui.rapid-override.increase": {"help": "", "type": bool},
        "halui.rapid-override.reset": {"help": "", "type": bool},
        "halui.rapid-override.scale": {"help": "", "type": float},
        "halui.spindle.0.brake-off": {"help": "", "type": bool},
        "halui.spindle.0.brake-on": {"help": "", "type": bool},
        "halui.spindle.0.decrease": {"help": "", "type": bool},
        "halui.spindle.0.forward": {"help": "", "type": bool},
        "halui.spindle.0.increase": {"help": "", "type": bool},
        "halui.spindle.0.override.count-enable": {"help": "", "type": bool},
        "halui.spindle.0.override.counts": {"help": "", "type": int},
        "halui.spindle.0.override.decrease": {"help": "", "type": bool},
        "halui.spindle.0.override.direct-value": {"help": "", "type": bool},
        "halui.spindle.0.override.increase": {"help": "", "type": bool},
        "halui.spindle.0.override.reset": {"help": "", "type": bool},
        "halui.spindle.0.override.scale": {"help": "", "type": float},
        "halui.spindle.0.reverse": {"help": "", "type": bool},
        "halui.spindle.0.start": {"help": "", "type": bool},
        "halui.spindle.0.stop": {"help": "", "type": bool},
        "iocontrol.0.emc-enable-in": {"help": "Estop input", "type": bool},
        "iocontrol.0.lube_level": {"help": "", "type": bool},
        "iocontrol.0.tool-changed": {"help": "", "type": bool},
        "iocontrol.0.tool-prepared": {"help": "", "type": bool},
        "joint.0.amp-fault-in": {"help": "Joint", "type": bool},
        "joint.0.home-sw-in": {"help": "Homeswitch input", "type": bool},
        "joint.0.jog-accel-fraction": {"help": "Joint", "type": float},
        "joint.0.jog-counts": {"help": "Joint", "type": int},
        "joint.0.jog-enable": {"help": "Joint", "type": bool},
        "joint.0.jog-scale": {"help": "Joint", "type": float},
        "joint.0.jog-vel-mode": {"help": "Joint", "type": bool},
        "joint.0.motor-pos-fb": {"help": "Joint", "type": float},
        "joint.0.neg-lim-sw-in": {"help": "Joint", "type": bool},
        "joint.0.pos-lim-sw-in": {"help": "Joint", "type": bool},
        "joint.1.home-sw-in": {"help": "Homeswitch input", "type": bool},
        "joint.2.home-sw-in": {"help": "Homeswitch input", "type": bool},
        "joint.3.home-sw-in": {"help": "Homeswitch input", "type": bool},
        "joint.4.home-sw-in": {"help": "Homeswitch input", "type": bool},
        "joint.5.home-sw-in": {"help": "Homeswitch input", "type": bool},
        "motion.adaptive-feed": {"help": "", "type": float},
        "motion.analog-in-00": {"help": "", "type": float},
        "motion.analog-in-01": {"help": "", "type": float},
        "motion.analog-in-02": {"help": "", "type": float},
        "motion.digital-in-00": {"help": "Digital Input: M66", "type": bool},
        "motion.digital-in-01": {"help": "Digital Input: M66", "type": bool},
        "motion.digital-in-02": {"help": "Digital Input: M66", "type": bool},
        "motion.digital-in-03": {"help": "Digital Input: M66", "type": bool},
        "motion.enable": {"help": "", "type": bool},
        "motion.feed-hold": {"help": "", "type": bool},
        "motion.feed-inhibit": {"help": "", "type": bool},
        "motion.homing-inhibit": {"help": "", "type": bool},
        "motion.jog-inhibit": {"help": "", "type": bool},
        "motion.jog-stop": {"help": "", "type": bool},
        "motion.jog-stop-immediate": {"help": "", "type": bool},
        "motion.probe-input": {"help": "Touch-Probe input", "type": bool},
        "spindle.0.amp-fault-in": {"help": "", "type": bool},
        "spindle.0.at-speed": {"help": "", "type": bool},
        "spindle.0.inhibit": {"help": "", "type": bool},
        "spindle.0.is-oriented": {"help": "", "type": bool},
        "spindle.0.orient-fault": {"help": "", "type": int},
        "spindle.0.revs": {"help": "", "type": float},
        "spindle.0.speed-in": {"help": "", "type": float},
    },
    "output": {
        "axis.x.eoffset": {"help": "Axis", "type": float},
        "axis.x.eoffset-request": {"help": "Axis", "type": float},
        "axis.x.kb-jog-active": {"help": "Axis", "type": bool},
        "axis.x.pos-cmd": {"help": "Axis", "type": float},
        "axis.x.teleop-pos-cmd": {"help": "Axis", "type": float},
        "axis.x.teleop-tp-enable": {"help": "Axis", "type": bool},
        "axis.x.teleop-vel-cmd": {"help": "Axis", "type": float},
        "axis.x.teleop-vel-lim": {"help": "Axis", "type": float},
        "axis.x.wheel-jog-active": {"help": "Axis", "type": bool},
        "axisui.abort": {"help": "", "type": bool},
        "axisui.error": {"help": "", "type": bool},
        "axisui.jog.x": {"help": "Jog", "type": bool},
        "hal_manualtoolchange.changed": {"help": "", "type": bool},
        "halui.axis.x.is-selected": {"help": "Axis", "type": bool},
        "halui.axis.x.pos-commanded": {"help": "Axis", "type": float},
        "halui.axis.x.pos-feedback": {"help": "Axis", "type": float},
        "halui.axis.x.pos-relative": {"help": "Axis", "type": float},
        "halui.estop.is-activated": {"help": "", "type": bool},
        "halui.feed-override.value": {"help": "", "type": float},
        "halui.flood.is-on": {"help": "", "type": bool},
        "halui.joint.0.has-fault": {"help": "Joint", "type": bool},
        "halui.joint.0.is-homed": {"help": "Joint", "type": bool},
        "halui.joint.0.is-selected": {"help": "Joint", "type": bool},
        "halui.joint.0.on-hard-max-limit": {"help": "Joint", "type": bool},
        "halui.joint.0.on-hard-min-limit": {"help": "Joint", "type": bool},
        "halui.joint.0.on-soft-max-limit": {"help": "Joint", "type": bool},
        "halui.joint.0.on-soft-min-limit": {"help": "Joint", "type": bool},
        "halui.joint.0.override-limits": {"help": "Joint", "type": bool},
        "halui.lube.is-on": {"help": "", "type": bool},
        "halui.machine.is-on": {"help": "", "type": bool},
        "halui.machine.units-per-mm": {"help": "", "type": float},
        "halui.max-velocity.value": {"help": "", "type": float},
        "halui.mist.is-on": {"help": "", "type": bool},
        "halui.mode.is-auto": {"help": "", "type": bool},
        "halui.mode.is-joint": {"help": "", "type": bool},
        "halui.mode.is-manual": {"help": "", "type": bool},
        "halui.mode.is-mdi": {"help": "", "type": bool},
        "halui.mode.is-teleop": {"help": "", "type": bool},
        "halui.program.block-delete.is-on": {"help": "", "type": bool},
        "halui.program.is-idle": {"help": "", "type": bool},
        "halui.program.is-paused": {"help": "", "type": bool},
        "halui.program.is-running": {"help": "", "type": bool},
        "halui.program.optional-stop.is-on": {"help": "", "type": bool},
        "halui.rapid-override.value": {"help": "", "type": float},
        "halui.spindle.0.brake-is-on": {"help": "", "type": bool},
        "halui.spindle.0.is-on": {"help": "", "type": bool},
        "halui.spindle.0.override.value": {"help": "", "type": float},
        "halui.spindle.0.runs-backward": {"help": "", "type": bool},
        "halui.spindle.0.runs-forward": {"help": "", "type": bool},
        "halui.tool.diameter": {"help": "", "type": float},
        "halui.tool.length_offset.a": {"help": "", "type": float},
        "halui.tool.length_offset.b": {"help": "", "type": float},
        "halui.tool.length_offset.c": {"help": "", "type": float},
        "halui.tool.length_offset.u": {"help": "", "type": float},
        "halui.tool.length_offset.v": {"help": "", "type": float},
        "halui.tool.length_offset.w": {"help": "", "type": float},
        "halui.tool.length_offset.x": {"help": "", "type": float},
        "halui.tool.length_offset.y": {"help": "", "type": float},
        "halui.tool.length_offset.z": {"help": "", "type": float},
        "halui.tool.number": {"help": "", "type": int},
        "iocontrol.0.coolant-flood": {"help": "", "type": bool},
        "iocontrol.0.coolant-mist": {"help": "", "type": bool},
        "iocontrol.0.lube": {"help": "", "type": bool},
        "iocontrol.0.tool-change": {"help": "", "type": bool},
        "iocontrol.0.tool-from-pocket": {"help": "", "type": int},
        "iocontrol.0.tool-number": {"help": "", "type": int},
        "iocontrol.0.tool-prep-index": {"help": "", "type": int},
        "iocontrol.0.tool-prep-number": {"help": "", "type": int},
        "iocontrol.0.tool-prep-pocket": {"help": "", "type": int},
        "iocontrol.0.tool-prepare": {"help": "", "type": bool},
        "iocontrol.0.user-enable-out": {"help": "", "type": bool},
        "iocontrol.0.user-request-enable": {"help": "", "type": bool},
        "joint.0.acc-cmd": {"help": "Joint", "type": float},
        "joint.0.active": {"help": "Joint", "type": bool},
        "joint.0.amp-enable-out": {"help": "Joint", "type": bool},
        "joint.0.backlash-corr": {"help": "Joint", "type": float},
        "joint.0.backlash-filt": {"help": "Joint", "type": float},
        "joint.0.backlash-vel": {"help": "Joint", "type": float},
        "joint.0.coarse-pos-cmd": {"help": "Joint", "type": float},
        "joint.0.error": {"help": "Joint", "type": bool},
        "joint.0.f-error": {"help": "Joint", "type": float},
        "joint.0.f-error-lim": {"help": "Joint", "type": float},
        "joint.0.f-errored": {"help": "Joint", "type": bool},
        "joint.0.faulted": {"help": "Joint", "type": bool},
        "joint.0.free-pos-cmd": {"help": "Joint", "type": float},
        "joint.0.free-tp-enable": {"help": "Joint", "type": bool},
        "joint.0.free-vel-lim": {"help": "Joint", "type": float},
        "joint.0.home-state": {"help": "Joint", "type": int},
        "joint.0.homed": {"help": "Joint", "type": bool},
        "joint.0.homing": {"help": "Joint", "type": bool},
        "joint.0.in-position": {"help": "Joint", "type": bool},
        "joint.0.kb-jog-active": {"help": "Joint", "type": bool},
        "joint.0.motor-offset": {"help": "Joint", "type": float},
        "joint.0.motor-pos-cmd": {"help": "Joint", "type": float},
        "joint.0.neg-hard-limit": {"help": "Joint", "type": bool},
        "joint.0.pos-cmd": {"help": "Joint", "type": float},
        "joint.0.pos-fb": {"help": "Joint", "type": float},
        "joint.0.pos-hard-limit": {"help": "Joint", "type": bool},
        "joint.0.vel-cmd": {"help": "Joint", "type": float},
        "joint.0.wheel-jog-active": {"help": "Joint", "type": bool},
        "motion-command-handler.time": {"help": "", "type": int},
        "motion-controller.time": {"help": "", "type": int},
        "motion.analog-out-00": {"help": "", "type": float},
        "motion.analog-out-01": {"help": "", "type": float},
        "motion.analog-out-02": {"help": "", "type": float},
        "motion.coord-error": {"help": "", "type": bool},
        "motion.coord-mode": {"help": "", "type": bool},
        "motion.current-vel": {"help": "", "type": float},
        "motion.digital-out-00": {"help": "Digital Output: M62-M65", "type": bool},
        "motion.digital-out-01": {"help": "Digital Output: M62-M65", "type": bool},
        "motion.digital-out-02": {"help": "Digital Output: M62-M65", "type": bool},
        "motion.digital-out-03": {"help": "Digital Output: M62-M65", "type": bool},
        "motion.distance-to-go": {"help": "", "type": float},
        "motion.eoffset-active": {"help": "", "type": bool},
        "motion.eoffset-limited": {"help": "", "type": bool},
        "motion.feed-inches-per-minute": {"help": "", "type": float},
        "motion.feed-inches-per-second": {"help": "", "type": float},
        "motion.feed-mm-per-minute": {"help": "", "type": float},
        "motion.feed-mm-per-second": {"help": "", "type": float},
        "motion.feed-upm": {"help": "", "type": float},
        "motion.in-position": {"help": "", "type": bool},
        "motion.is-all-homed": {"help": "", "type": bool},
        "motion.jog-is-active": {"help": "", "type": bool},
        "motion.motion-enabled": {"help": "", "type": bool},
        "motion.motion-type": {"help": "", "type": int},
        "motion.on-soft-limit": {"help": "", "type": bool},
        "motion.program-line": {"help": "", "type": int},
        "motion.requested-vel": {"help": "", "type": float},
        "motion.servo.last-period": {"help": "", "type": int},
        "motion.teleop-mode": {"help": "", "type": bool},
        "motion.tooloffset.a": {"help": "", "type": float},
        "motion.tooloffset.b": {"help": "", "type": float},
        "motion.tooloffset.c": {"help": "", "type": float},
        "motion.tooloffset.u": {"help": "", "type": float},
        "motion.tooloffset.v": {"help": "", "type": float},
        "motion.tooloffset.w": {"help": "", "type": float},
        "motion.tooloffset.x": {"help": "", "type": float},
        "motion.tooloffset.y": {"help": "", "type": float},
        "motion.tooloffset.z": {"help": "", "type": float},
        "motion.tp-reverse": {"help": "", "type": bool},
        "servo-thread.time": {"help": "", "type": int},
        "spindle.0.brake": {"help": "", "type": bool},
        "spindle.0.forward": {"help": "Spindle 0 Forward", "type": bool},
        "spindle.0.locked": {"help": "", "type": bool},
        "spindle.0.on": {"help": "Spindle 0 Reverse", "type": bool},
        "spindle.0.orient": {"help": "", "type": bool},
        "spindle.0.orient-angle": {"help": "", "type": float},
        "spindle.0.orient-mode": {"help": "", "type": int},
        "spindle.0.reverse": {"help": "Spindle 0 Reverse", "type": bool},
        "spindle.0.speed-cmd-rps": {"help": "", "type": float},
        "spindle.0.speed-out": {"help": "Spindle 0 Speed output", "type": float},
        "spindle.0.speed-out-abs": {"help": "Spindle 0 Speed output " "(Absolut)", "type": float},
        "spindle.0.speed-out-rps": {"help": "", "type": float},
        "spindle.0.speed-out-rps-abs": {"help": "", "type": float},
    },
}
