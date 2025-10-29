from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "stepgen"
        self.COMPONENT = "stepgen"
        self.INFO = "software step pulse generation"
        self.DESCRIPTION = """stepgen is used to control stepper motors.
The maximum step rate depends on the CPU and other factors,
and is usually in the range of 5 kHz to 25 kHz.
If higher rates are needed, a hardware step generator is a better choice."""
        self.KEYWORDS = "stepper"
        self.IMAGES = ["stepper", "servo42"]
        self.TYPE = "joint"
        self.PLUGIN_TYPE = "gpio"
        self.ORIGIN = ""
        self.OPTIONS = {
            "mode": {
                "default": "0",
                "type": "select",
                "options": [
                    "0|step/dir",
                    "1|up/down",
                    "2|quadrature",
                    "3|three phase, full step",
                    "4|three phase, half step",
                    "5|four phase, full step (unipolar)",
                    "6|four phase, full step (unipolar)",
                    "7|four phase, full step (bipolar)",
                    "8|four phase, full step (bipolar)",
                    "9|four phase, half step (unipolar)",
                    "10|four phase, half step (bipolar)",
                    "11|five phase, full step",
                    "12|five phase, full step",
                    "13|five phase, half step",
                    "14|five phase, half step",
                    "15|user-specified",
                ],
                "description": "Modus",
            },
        }
        self.SIGNALS = {
            "position-cmd": {
                "direction": "output",
                "absolute": False,
                "description": "set position",
            },
            "position-fb": {
                "direction": "input",
                "unit": "steps",
                "absolute": False,
                "description": "position feedback",
            },
            "position-scale": {
                "direction": "output",
                "absolute": False,
                "description": "steps / unit",
            },
        }
        self.mode_pins = {
            "0": {
                "step": {"direction": "output", "reset": True, "edge": "target", "type": "GPIO"},
                "dir": {"direction": "output", "edge": "target", "type": "GPIO"},
            },
            "1": {
                "up": {"direction": "output", "edge": "target", "type": "GPIO"},
                "down": {"direction": "output", "edge": "target", "type": "GPIO"},
            },
            "2": {
                "phase-A": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-B": {"direction": "output", "edge": "target", "type": "GPIO"},
            },
            "3": {
                "phase-A": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-B": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-C": {"direction": "output", "edge": "target", "type": "GPIO"},
            },
            "4": {
                "phase-A": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-B": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-C": {"direction": "output", "edge": "target", "type": "GPIO"},
            },
            "5": {
                "phase-A": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-B": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-C": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-D": {"direction": "output", "edge": "target", "type": "GPIO"},
            },
            "6": {
                "phase-A": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-B": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-C": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-D": {"direction": "output", "edge": "target", "type": "GPIO"},
            },
            "7": {
                "phase-A": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-B": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-C": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-D": {"direction": "output", "edge": "target", "type": "GPIO"},
            },
            "8": {
                "phase-A": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-B": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-C": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-D": {"direction": "output", "edge": "target", "type": "GPIO"},
            },
            "9": {
                "phase-A": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-B": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-C": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-D": {"direction": "output", "edge": "target", "type": "GPIO"},
            },
            "10": {
                "phase-A": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-B": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-C": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-D": {"direction": "output", "edge": "target", "type": "GPIO"},
            },
            "11": {
                "phase-A": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-B": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-C": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-D": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-E": {"direction": "output", "edge": "target", "type": "GPIO"},
            },
            "12": {
                "phase-A": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-B": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-C": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-D": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-E": {"direction": "output", "edge": "target", "type": "GPIO"},
            },
            "13": {
                "phase-A": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-B": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-C": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-D": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-E": {"direction": "output", "edge": "target", "type": "GPIO"},
            },
            "14": {
                "phase-A": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-B": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-C": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-D": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-E": {"direction": "output", "edge": "target", "type": "GPIO"},
            },
            "15": {
                "phase-A": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-B": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-C": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-D": {"direction": "output", "edge": "target", "type": "GPIO"},
                "phase-E": {"direction": "output", "edge": "target", "type": "GPIO"},
            },
        }
        mode = self.plugin_setup.get("mode", self.option_default("mode"))
        self.PINDEFAULTS = self.mode_pins[mode]

    def update_prefixes(cls, instances):
        for num, instance in enumerate(instances):
            instance.PREFIX = f"stepgen.{num}"

    def loader(cls, instances):
        output = []
        modes = []
        for num, instance in enumerate(instances):
            mode = instance.plugin_setup.get("mode", instance.option_default("mode"))
            modes.append(mode)
        output.append(f"# stepgen component for {len(instances)} joint(s)")
        output.append(f"loadrt stepgen step_type={','.join(modes)}")
        output.append("addf stepgen.make-pulses base-thread")
        output.append("addf stepgen.capture-position servo-thread")
        output.append("addf stepgen.update-freq servo-thread")
        output.append("")
        return "\n".join(output)

    def hal(self, parent):
        if "joint_data" in self.plugin_setup:
            joint_data = self.plugin_setup["joint_data"]
            axis_name = joint_data["axis"]
            joint_n = joint_data["num"]

            for key in ("dirsetup", "dirhold", "steplen", "stepspace", "maxaccel"):
                value = f"STEPGEN_{key.upper()}"
                parent.halg.setp_add(f"{self.PREFIX}.{key}", f"[JOINT_{joint_n}]{value}")

            cmd_halname = f"{self.PREFIX}.position-cmd"
            feedback_halname = f"{self.PREFIX}.position-cmd"
            enable_halname = f"{self.PREFIX}.enable"
            scale_halname = f"{self.PREFIX}.position-scale"

            for name, psetup in self.plugin_setup.get("pins", {}).items():
                pin = psetup["pin"]
                parent.halg.net_add(f"{self.PREFIX}.{name}", pin, f"j{joint_n}{name}-pin")

            parent.halg.joint_add(parent, axis_name, joint_n, "position", cmd_halname, feedback_halname=feedback_halname, scale_halname=scale_halname, enable_halname=enable_halname)
