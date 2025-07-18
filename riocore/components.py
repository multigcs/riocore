class basecomp:
    def signals(self):
        signals = {}
        for name, setup in self.SIGNALS.items():
            if "value" not in setup:
                setup["value"] = 0
            signals[name] = setup
            for key in setup:
                if key in self.plugin_setup:
                    setup[key] = self.plugin_setup[key]
            signal_prefix = self.PREFIX
            halname = f"{signal_prefix}.{name}"
            direction_short = setup["direction"].upper().replace("PUT", "")
            signals[name]["signal_prefix"] = signal_prefix
            signals[name]["var_prefix"] = signal_prefix.replace(".", "_").replace("-", "_").upper()
            signals[name]["plugin_instance"] = self
            signals[name]["halname"] = halname
            signals[name]["varname"] = f"SIG{direction_short}_{halname.replace('.', '_').replace('-', '_').upper()}"
            signals[name]["userconfig"] = self.plugin_setup.get("signals", {}).get(name, {})
            net = self.plugin_setup.get("net")
            netname = net
            if len(self.SIGNALS) > 1 and net:
                netname = f"{net}.{name}"
            signals[name]["netname"] = signals[name]["userconfig"].get("net", netname)
        return signals


class comp_stepgen(basecomp):
    INFO = "software step pulse generation"
    DESCRIPTION = """stepgen is used to control stepper motors.
The maximum step rate depends on the CPU and other factors,
and is usually in the range of 5 kHz to 25 kHz.
If higher rates are needed, a hardware step generator is a better choice."""
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
        self.OPTIONS = ()
        component.get("pins", {})
        comp_mode = str(component.get("mode", "0"))
        self.PINS = self.mode_pins[comp_mode]

        self.PINDEFAULTS = {}
        for pin in self.PINS:
            pin_name = pin.split(":")[0]
            pin_dir = pin.split(":")[1]
            self.PINDEFAULTS[pin_name] = {"direction": pin_dir}

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
                "min": -100000,
                "max": 100000,
                "unit": "Hz",
                "absolute": False,
                "description": "speed in steps per second",
            },
            "position-fb": {
                "direction": "input",
                "unit": "steps",
                "absolute": False,
                "description": "position feedback",
            },
            "position-scale": {
                "direction": "output",
                "min": -100000,
                "max": 100000,
                "unit": "Hz",
                "absolute": False,
                "description": "speed in steps per second",
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


class comp_pwmgen(basecomp):
    INFO = "software PWM/PDM generation"
    DESCRIPTION = """pwmgen is used to generate PWM (pulse width modulation) or PDM (pulse density modulation) signals.
The maximum PWM frequency and the resolution is quite limited compared to hardware-based approaches,
but in many cases software PWM can be very useful. If better performance is needed,
a hardware PWM generator is a better choice."""

    def __init__(self, component):
        self.snum = component["num"]
        self.component = component
        self.setup = component
        self.PREFIX = f"pwmgen.{self.snum}"
        self.instances_name = component.get("name", f"pwmgen{self.snum}")
        self.TITLE = component.get("name", f"Pwmgen-{self.snum}").title()
        self.plugin_setup = component
        self.TYPE = "pwmgen"

        component.get("pins", {})
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

        self.OPTIONS = {
            "mode": {
                "default": "1",
                "type": "select",
                "options": [
                    "1|pwm/direction",
                    "2|up/down",
                ],
                "description": "Modus",
            },
            "pwm-freq": {
                "default": 10000,
                "type": float,
                "min": 1,
                "max": 100000,
                "unit": "Hz",
                "description": "pwm frequency",
            },
            "scale": {
                "default": 1.0,
                "type": float,
                "min": -10000.0,
                "max": 10000.0,
                "unit": "",
                "description": "scale",
            },
            "offset": {
                "default": 0.0,
                "type": float,
                "min": 0.0,
                "max": 10000.0,
                "unit": "",
                "description": "offset",
            },
            "min-dc": {
                "default": 0.0,
                "type": float,
                "min": 0.0,
                "max": 100.0,
                "unit": "",
                "description": "minimum duty cycle",
            },
            "max-dc": {
                "default": 100.0,
                "type": float,
                "min": 0.0,
                "max": 100.0,
                "unit": "",
                "description": "maximum duty cycle",
            },
            "dither-pwm": {
                "default": "false",
                "type": "select",
                "options": [
                    "true",
                    "false",
                ],
                "description": "dither-pwm",
            },
        }

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


class comp_encoder(basecomp):
    INFO = "software counting of quadrature encoder signals"
    DESCRIPTION = """encoder is used to measure position by counting the pulses generated by a quadrature encoder.
As a software-based implementation it is much less expensive than hardware,
but has a limited maximum count rate.
The limit is in the range of 10 kHz to 50 kHz, depending on the computer speed and other factors.
If better performance is needed, a hardware encoder counter is a better choice.
Some hardware-based systems can count at MHz rates."""

    def __init__(self, component):
        self.snum = component["num"]
        self.component = component
        self.setup = component
        self.PREFIX = f"encoder.{self.snum}"
        self.instances_name = component.get("name", f"encoder{self.snum}")
        self.TITLE = component.get("name", f"Encoder-{self.snum}").title()
        self.plugin_setup = component
        self.TYPE = "encoder"

        component.get("pins", {})
        self.PINS = ("phase-A:input", "phase-B:input", "phase-Z:input")

        self.PINDEFAULTS = {}
        for pin in self.PINS:
            pin_name = pin.split(":")[0]
            pin_dir = pin.split(":")[1]
            self.PINDEFAULTS[pin_name] = {"direction": pin_dir}

        self.OPTIONS = {
            "counter-mode": {
                "default": False,
                "type": bool,
                "unit": "",
                "description": "counter-mode",
            },
            "x4-mode": {
                "default": False,
                "type": bool,
                "unit": "",
                "description": "x4-mode",
            },
            "missing-teeth": {
                "default": 0,
                "type": int,
                "min": 0,
                "max": 10,
                "unit": "",
                "description": "missing-teeth",
            },
            "position-scale": {
                "default": 1.0,
                "type": float,
                "min": -10000.0,
                "max": 10000.0,
                "unit": "",
                "description": "scale",
            },
        }

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
