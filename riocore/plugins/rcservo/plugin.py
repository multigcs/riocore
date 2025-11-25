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
        self.JOINT_TYPE = "position"
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
        for pin_name in self.pins():
            output.append(f"    servo_{self.instances_name}.write(value_{pin_name});")
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
