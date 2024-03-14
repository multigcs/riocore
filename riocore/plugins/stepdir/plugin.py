from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "stepdir"
        self.TYPE = "joint"
        self.VERILOGS = ["stepdir.v"]
        self.PINDEFAULTS = {
            "step": {
                "direction": "output",
            },
            "dir": {
                "direction": "output",
            },
            "en": {
                "direction": "output",
                "optional": True,
            },
        }
        self.INTERFACE = {
            "velocity": {
                "size": 32,
                "direction": "output",
            },
            "enable": {
                "size": 1,
                "direction": "output",
                "on_error": False,
            },
            "position": {
                "size": 32,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "velocity": {
                "direction": "output",
                "min": -1000000,
                "max": 1000000,
                "unit": "Hz",
                "absolute": False,
                "description": "speed in steps per second",
            },
            "position": {
                "direction": "input",
                "unit": "steps",
                "absolute": False,
                "description": "position feedback",
            },
            "enable": {
                "direction": "output",
                "bool": True,
            },
        }
        self.INFO = "step/dir output for stepper drivers"
        self.DESCRIPTION = "to control motor drivers via step/dir pin's and an optional enable pin"
        if self.system_setup:
            if "joint_n" not in self.system_setup:
                self.system_setup["joint_n"] = 0

    def gateware_instances(self):
        instances = self.gateware_instances_base()
        instance = instances[self.instances_name]
        instance_predefines = instance["predefines"]
        instance_parameter = instance["parameter"]
        instance_arguments = instance["arguments"]
        return instances

    def convert(self, signal_name, signal_setup, value):
        if signal_name == "velocity":
            if value != 0:
                value = self.system_setup["speed"] / value / 2
        return value

    def convert_c(self, signal_name, signal_setup):
        if signal_name == "velocity":
            return """
            if (value != 0) {
                value = OSC_CLOCK / value / 2;
            }
            """
        return ""

    def firmware_defines(self):
        output = []
        for pin_name, pin_config in self.pins().items():
            if "pin" not in pin_config:
                continue
            pin = pin_config["pin"]
            direction = pin_config["direction"]
            pin_define_name = f"PIN{direction}_{self.instances_name}_{pin_name}".upper()
            output.append(f"#define {pin_define_name} {pin}")
        return "\n".join(output)

    def firmware_setup(self):
        output = []
        for pin_name, pin_config in self.pins().items():
            if "pin" not in pin_config:
                continue
            pin = pin_config["pin"]
            direction = pin_config["direction"]
            pin_define_name = f"PIN{direction}_{self.instances_name}_{pin_name}".upper()
            output.append(f"    pinMode({pin_define_name}, {direction.upper()});")

        for pin_name, pin_config in self.pins().items():
            if "pin" not in pin_config:
                continue
            pin = pin_config["pin"]
            direction = pin_config["direction"]
            pin_define_name = f"PIN{direction}_{self.instances_name}_{pin_name}".upper()
            if pin_name == "step":
                output.append(f"    step_pins[{self.system_setup['joint_n']}] = {pin_define_name};")
            elif pin_name == "dir":
                output.append(f"    dir_pins[{self.system_setup['joint_n']}] = {pin_define_name};")

        self.system_setup["joint_n"] += 1
        return "\n".join(output)

    def firmware_loop(self):
        output = []
        for pin_name, pin_config in self.pins().items():
            if "pin" not in pin_config:
                continue
            pin = pin_config["pin"]
            direction = pin_config["direction"]
            pin_define_name = f"PIN{direction}_{self.instances_name}_{pin_name}".upper()
            # output.append(f"    digitalWrite({pin_define_name}, value_bit);")
        return "\n".join(output)
