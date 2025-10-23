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
            "image": {
                "default": "generic",
                "type": "select",
                "options": ["generic", "stepper"],
                "description": "hardware type",
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
            "0": {"step": {"direction": "output", "reset": True}, "dir": {"direction": "output"}},
            "1": {"up": {"direction": "output"}, "down": {"direction": "output"}},
            "2": {"phase-A": {"direction": "output"}, "phase-B": {"direction": "output"}},
            "3": {"phase-A": {"direction": "output"}, "phase-B": {"direction": "output"}, "phase-C": {"direction": "output"}},
            "4": {"phase-A": {"direction": "output"}, "phase-B": {"direction": "output"}, "phase-C": {"direction": "output"}},
            "5": {"phase-A": {"direction": "output"}, "phase-B": {"direction": "output"}, "phase-C": {"direction": "output"}, "phase-D": {"direction": "output"}},
            "6": {"phase-A": {"direction": "output"}, "phase-B": {"direction": "output"}, "phase-C": {"direction": "output"}, "phase-D": {"direction": "output"}},
            "7": {"phase-A": {"direction": "output"}, "phase-B": {"direction": "output"}, "phase-C": {"direction": "output"}, "phase-D": {"direction": "output"}},
            "8": {"phase-A": {"direction": "output"}, "phase-B": {"direction": "output"}, "phase-C": {"direction": "output"}, "phase-D": {"direction": "output"}},
            "9": {"phase-A": {"direction": "output"}, "phase-B": {"direction": "output"}, "phase-C": {"direction": "output"}, "phase-D": {"direction": "output"}},
            "10": {"phase-A": {"direction": "output"}, "phase-B": {"direction": "output"}, "phase-C": {"direction": "output"}, "phase-D": {"direction": "output"}},
            "11": {"phase-A": {"direction": "output"}, "phase-B": {"direction": "output"}, "phase-C": {"direction": "output"}, "phase-D": {"direction": "output"}, "phase-E": {"direction": "output"}},
            "12": {"phase-A": {"direction": "output"}, "phase-B": {"direction": "output"}, "phase-C": {"direction": "output"}, "phase-D": {"direction": "output"}, "phase-E": {"direction": "output"}},
            "13": {"phase-A": {"direction": "output"}, "phase-B": {"direction": "output"}, "phase-C": {"direction": "output"}, "phase-D": {"direction": "output"}, "phase-E": {"direction": "output"}},
            "14": {"phase-A": {"direction": "output"}, "phase-B": {"direction": "output"}, "phase-C": {"direction": "output"}, "phase-D": {"direction": "output"}, "phase-E": {"direction": "output"}},
            "15": {"phase-A": {"direction": "output"}, "phase-B": {"direction": "output"}, "phase-C": {"direction": "output"}, "phase-D": {"direction": "output"}, "phase-E": {"direction": "output"}},
        }
        mode = self.plugin_setup.get("mode", self.option_default("mode"))
        self.PINDEFAULTS = self.mode_pins[mode]

        image = self.plugin_setup.get("image", self.option_default("image"))
        if image == "stepper":
            self.IMAGE_SHOW = True
            self.IMAGE = "stepper.png"
            self.PINDEFAULTS["step"]["pos"] = (30, 380)
            self.PINDEFAULTS["dir"]["pos"] = (30, 320)
            self.SIGNALS["position-cmd"]["pos"] = (360, 240)
            self.SIGNALS["position-fb"]["pos"] = (360, 270)
            self.SIGNALS["position-scale"]["pos"] = (360, 300)

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
