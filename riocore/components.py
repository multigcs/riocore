class stepgen:
    mode_pins = {
        "0": ("step:output", "dir:output"),
        "1": ("up:output", "down:output"),
        "2": ("phase-A:output", "phase-B:output"),
        "3": ("phase-A:output", "phase-B:output", "phase-C:output"),
        "4": ("phase-A:output", "phase-B:output", "phase-C:output"),
        "5": ("phase-A:output", "phase-B:output", "phase-C:output", "phase-D:output"),
        "6": ("phase-A:output", "phase-B:output", "phase-C:output", "phase-D:output"),
        "7": ("phase-A:output", "phase-B:output", "phase-C:output", "phase-D:output"),
        "8": ("phase-A:output", "phase-B:output", "phase-C:output", "phase-D:output"),
        "9": ("phase-A:output", "phase-B:output", "phase-C:output", "phase-D:output"),
        "10": ("phase-A:output", "phase-B:output", "phase-C:output", "phase-D:output"),
        "11": ("phase-A:output", "phase-B:output", "phase-C:output", "phase-D:output", "phase-E:output"),
        "12": ("phase-A:output", "phase-B:output", "phase-C:output", "phase-D:output", "phase-E:output"),
        "13": ("phase-A:output", "phase-B:output", "phase-C:output", "phase-D:output", "phase-E:output"),
        "14": ("phase-A:output", "phase-B:output", "phase-C:output", "phase-D:output", "phase-E:output"),
        "15": ("phase-A:output", "phase-B:output", "phase-C:output", "phase-D:output", "phase-E:output"),
    }

    def __init__(self, component):
        self.snum = component["num"]
        self.component = component
        self.setup = component
        self.PREFIX = f"stepgen.{self.snum}"
        self.instances_name = component.get("name", f"stepgen{self.snum}")
        self.TITLE = component.get("name", f"Stepgen-{self.snum}").title()
        self.plugin_setup = component
        self.TYPE = "stepgen"
        self.SIGNALNAMES = ("cmd", "fb")
        self.OPTIONS = ()
        comp_pins = component.get("pins", {})
        comp_mode = str(component.get("mode", "0"))
        self.PINS = self.mode_pins[comp_mode]

        self.PINDEFAULTS = {}
        for pin in self.PINS:
            pin_name = pin.split(":")[0]
            pin_dir = pin.split(":")[1]
            self.PINDEFAULTS[pin_name] = {"direction": pin_dir}

        self.SIGNALS = {
            "cmd": {
                "direction": "output",
                "min": -100000,
                "max": 100000,
                "unit": "Hz",
                "absolute": False,
                "description": "speed in steps per second",
            },
            "fb": {
                "direction": "input",
                "unit": "steps",
                "absolute": False,
                "description": "position feedback",
            },
        }

    def loader(cls, components):
        output = []
        complist = []
        for component in components:
            if component.get("type") == "stepgen":
                comp_mode = str(component.get("mode", "0"))
                complist.append(comp_mode)

        if complist:
            output.append(f"# stepgen component for {len(complist)} joint(s)")
            output.append(f"loadrt stepgen step_type={','.join(complist)}")
            output.append("addf stepgen.make-pulses base-thread")
            output.append("addf stepgen.capture-position servo-thread")
            output.append("addf stepgen.update-freq servo-thread")
            output.append("")

        return "\n".join(output)

    def signals(self):
        return {
            "position-scale": {
                "halname": f"{self.PREFIX}.position-scale",
            },
        }


class pwmgen:
    def __init__(self, component):
        self.snum = component["num"]
        self.component = component
        self.setup = component
        self.PREFIX = f"pwmgen.{self.snum}"
        self.instances_name = component.get("name", f"pwmgen{self.snum}")
        self.TITLE = component.get("name", f"Pwmgen-{self.snum}").title()
        self.plugin_setup = component
        self.TYPE = "pwmgen"
        self.SIGNALNAMES = ("enable", "value")
        self.OPTIONS = ("pwm-freq", "scale", "offset", "dither-pwm", "min-dc", "max-dc", "curr-dc")

        comp_pins = component.get("pins", {})
        comp_mode = str(component.get("mode", "1"))
        if comp_mode == "1":
            self.PINS = ("pwm:output", "dir:output")
        else:
            self.PINS = ("up:output", "down:output")

        self.PINDEFAULTS = {}
        for pin in self.PINS:
            pin_name = pin.split(":")[0]
            pin_dir = pin.split(":")[1]
            self.PINDEFAULTS[pin_name] = {"direction": pin_dir}

        self.SIGNALS = {
            "value": {
                "direction": "output",
            },
            "enable": {
                "direction": "output",
                "bool": True,
            },
        }

    def loader(cls, components):
        output = []
        complist = []
        for component in components:
            if component.get("type") == "pwmgen":
                comp_mode = str(component.get("mode", "0"))
                complist.append(comp_mode)

        if complist:
            output.append(f"# pwmgen component for {len(complist)} output(s)")
            output.append(f"loadrt pwmgen output_type={','.join(complist)}")
            output.append("addf pwmgen.make-pulses base-thread")
            output.append("addf pwmgen.update servo-thread")
            output.append("")

        return "\n".join(output)

    def signals(self):
        return {}


class encoder:
    def __init__(self, component):
        self.snum = component["num"]
        self.component = component
        self.setup = component
        self.PREFIX = f"encoder.{self.snum}"
        self.instances_name = component.get("name", f"encoder{self.snum}")
        self.TITLE = component.get("name", f"Encoder-{self.snum}").title()
        self.plugin_setup = component
        self.TYPE = "encoder"
        self.SIGNALNAMES = ("pos", "idx")
        self.OPTIONS = ("counter-mode", "missing-teeth", "x4-mode")

        comp_pins = component.get("pins", {})
        comp_mode = str(component.get("mode", "1"))
        self.PINS = ("phase-A:input", "phase-B:input", "phase-Z:input")

        self.PINDEFAULTS = {}
        for pin in self.PINS:
            pin_name = pin.split(":")[0]
            pin_dir = pin.split(":")[1]
            self.PINDEFAULTS[pin_name] = {"direction": pin_dir}

        self.SIGNALS = {
            "position": {
                "direction": "input",
                "description": "position feedback in steps",
            },
            "velocity": {
                "direction": "input",
                "source": "position",
                "description": "calculates revolutions per second",
            },
            "velocity-rpm": {
                "direction": "input",
                "source": "position",
                "description": "calculates revolutions per minute",
            },
        }

    def loader(cls, components):
        output = []
        complist = []
        for component in components:
            if component.get("type") == "encoder":
                comp_mode = str(component.get("mode", "0"))
                complist.append(comp_mode)

        if complist:
            output.append(f"# encoder component for {len(complist)} inputs(s)")
            output.append(f"loadrt encoder num_chan={len(complist)}")
            output.append("addf encoder.update-counters base-thread")
            output.append("addf encoder.capture-position servo-thread")
            output.append("")

        return "\n".join(output)

    def signals(self):
        return {}
