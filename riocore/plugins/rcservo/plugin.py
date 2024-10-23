from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "rcservo"
        self.INFO = "rc-servo output"
        self.DESCRIPTION = "to control rc-servos, usable as joint or as variable/analog output in LinuxCNC"
        self.KEYWORDS = "joint rcservo"
        self.ORIGIN = ""
        self.VERILOGS = ["rcservo.v"]
        self.TYPE = "joint"
        self.PINDEFAULTS = {
            "pwm": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
        }
        self.OPTIONS = {
            "frequency": {
                "default": 100,
                "type": int,
                "min": 20,
                "max": 150,
                "description": "update frequency",
            },
        }
        self.INTERFACE = {
            "position": {
                "size": 32,
                "direction": "output",
            },
            "enable": {
                "size": 1,
                "direction": "output",
                "on_error": False,
            },
        }
        self.SIGNALS = {
            "position": {
                "direction": "output",
                "min": -100.0,
                "max": 100.0,
                "scale": 1.0,
                "max_velocity": 1000.0,
                "description": "absolute position (-100 = 1ms / 100 = 2ms)",
            },
            "enable": {
                "direction": "output",
                "bool": True,
            },
        }
        self.FIRMWARE_SUPPORT = True

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_parameter = instance["parameter"]
        freq = int(self.plugin_setup.get("frequency", self.OPTIONS["frequency"]["default"]))
        divider = self.system_setup["speed"] // freq
        instance_parameter["DIVIDER"] = divider
        return instances

    def convert(self, signal_name, signal_setup, value):
        if signal_name == "position":
            value = int((value + 300) * self.system_setup["speed"] / 200000)
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "position":
            return """
            value = ((value + 300)) * OSC_CLOCK / 200000;
            """
        return ""

    def firmware_defines(self):
        output = ["#include <Servo.h>"]
        output.append("")
        for pin_name, pin_config in self.pins().items():
            pin = pin_config["pin"]
            direction = pin_config["direction"]
            pin_define_name = f"PIN{direction}_{self.instances_name}_{pin_name}".upper()
            output.append(f"#define {pin_define_name} {pin}")
        output.append("")
        for pin_name, pin_config in self.pins().items():
            pin = pin_config["pin"]
            direction = pin_config["direction"]
            pin_define_name = f"PIN{direction}_{self.instances_name}_{pin_name}".upper()
            output.append(f"Servo servo_{self.instances_name};")
        return "\n".join(output)

    def firmware_setup(self):
        output = []
        for pin_name, pin_config in self.pins().items():
            direction = pin_config["direction"]
            pin_define_name = f"PIN{direction}_{self.instances_name}_{pin_name}".upper()
            output.append(f"    servo_{self.instances_name}.attach({pin_define_name});")

        return "\n".join(output)

    def firmware_loop(self):
        output = []
        for pin_name, pin_config in self.pins().items():
            output.append(f"    servo_{self.instances_name}.write(value_{pin_name});")
        return "\n".join(output)
