from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "pwmgen"
        self.COMPONENT = "pwmgen"
        self.INFO = "software PWM/PDM generation"
        self.DESCRIPTION = """pwmgen is used to generate PWM (pulse width modulation) or PDM (pulse density modulation) signals.
The maximum PWM frequency and the resolution is quite limited compared to hardware-based approaches,
but in many cases software PWM can be very useful. If better performance is needed,
a hardware PWM generator is a better choice."""
        self.KEYWORDS = "pwm"
        self.IMAGES = ["spindle500w", "laser", "led"]
        self.TYPE = "io"
        self.PLUGIN_TYPE = "gpio"
        self.ORIGIN = ""
        self.OPTIONS = {
            "mode": {
                "default": "1",
                "type": "select",
                "options": [
                    "1|pwm/direction",
                    "2|up/down",
                ],
                "description": "modus",
            },
            "pwm-freq": {
                "default": 100,
                "type": float,
                "min": 1,
                "max": 100000,
                "unit": "Hz",
                "description": "pwm frequency",
            },
            "scale": {
                "default": 100.0,
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
                "default": 1.0,
                "type": float,
                "min": 0.0,
                "max": 1.0,
                "unit": "",
                "description": "maximum duty cycle",
            },
            "dither-pwm": {
                "default": False,
                "type": bool,
                "description": "dither-pwm",
            },
        }

        self.SIGNALS = {
            "value": {
                "direction": "output",
                "min": -100.0,
                "max": 100.0,
            },
            "enable": {
                "direction": "output",
                "bool": True,
            },
        }
        self.mode_pins = {
            "1": {
                "pwm": {
                    "direction": "output",
                    "edge": "target",
                    "type": "GPIO",
                },
                "dir": {
                    "direction": "output",
                    "optional": True,
                    "edge": "target",
                    "type": "GPIO",
                },
            },
            "2": {
                "up": {
                    "direction": "output",
                    "edge": "target",
                    "type": "GPIO",
                },
                "down": {
                    "direction": "output",
                    "optional": True,
                    "edge": "target",
                    "type": "GPIO",
                },
            },
        }
        mode = self.plugin_setup.get("mode", self.option_default("mode"))
        self.PINDEFAULTS = self.mode_pins[mode]

    def hal(self, generator):
        for option in ("pwm-freq", "scale", "offset", "min-dc", "max-dc", "dither-pwm"):
            value = self.plugin_setup.get(option, self.option_default(option))
            if self.OPTIONS[option]["type"] is bool:
                value = 1 if value else 0
            generator.halg.setp_add(f"{self.PREFIX}.{option}", f"{value}")

    def component_loader(cls, instances):
        output = []
        modes = []
        for num, instance in enumerate(instances):
            mode = instance.plugin_setup.get("mode", instance.option_default("mode"))
            modes.append(mode)
        output.append(f"# pwmgen component for {len(instances)} output(s)")
        output.append(f"loadrt pwmgen output_type={','.join(modes)}")
        output.append("addf pwmgen.make-pulses base-thread")
        output.append("addf pwmgen.update servo-thread")
        output.append("")
        return "\n".join(output)
