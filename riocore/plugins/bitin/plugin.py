from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "bitin"
        self.INFO = "single input pin"
        self.DESCRIPTION = "to read switches or other 1bit signals"
        self.KEYWORDS = "switch limit estop keyboard"
        self.ORIGIN = ""
        self.PINDEFAULTS = {
            "bit": {
                "direction": "input",
            },
        }
        self.INTERFACE = {
            "bit": {
                "size": 1,
                "direction": "input",
            },
        }
        self.SIGNALS = {
            "bit": {
                "direction": "input",
                "bool": True,
            },
        }
        self.FIRMWARE_SUPPORT = True

    def gateware_instances(self):
        instances = self.gateware_instances_base(direct=True)
        return instances

    def firmware_defines(self):
        output = []
        for pin_name, pin_config in self.pins().items():
            pin = pin_config["pin"]
            direction = pin_config["direction"]
            pin_define_name = f"PIN{direction}_{self.instances_name}_{pin_name}".upper()
            output.append(f"#define {pin_define_name} {pin}")
        return "\n".join(output)

    def firmware_setup(self):
        output = []
        for pin_name, pin_config in self.pins().items():
            pull = pin_config.get("pull")
            direction = pin_config["direction"]
            pin_define_name = f"PIN{direction}_{self.instances_name}_{pin_name}".upper()
            if pull:
                output.append(f"    pinMode({pin_define_name}, {direction.upper()}_PULL{pull.upper()});")
            else:
                output.append(f"    pinMode({pin_define_name}, {direction.upper()});")
        return "\n".join(output)

    def firmware_loop(self):
        output = []
        for pin_name, pin_config in self.pins().items():
            direction = pin_config["direction"]
            pin_define_name = f"PIN{direction}_{self.instances_name}_{pin_name}".upper()
            output.append(f"    value_bit = digitalRead({pin_define_name});")
        return "\n".join(output)
