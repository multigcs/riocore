from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "bitout"
        self.INFO = "singe bit output pin"
        self.DESCRIPTION = "to control relais, leds, valves, ...."
        self.KEYWORDS = "led relais valve lamp motor magnet"
        self.ORIGIN = ""
        self.PINDEFAULTS = {
            "bit": {
                "direction": "output",
                "invert": False,
                "pull": None,
            },
        }
        self.INTERFACE = {
            "bit": {
                "size": 1,
                "direction": "output",
            },
        }
        self.SIGNALS = {
            "bit": {
                "direction": "output",
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
            direction = pin_config["direction"]
            pin_define_name = f"PIN{direction}_{self.instances_name}_{pin_name}".upper()
            output.append(f"    pinMode({pin_define_name}, {direction.upper()});")
        return "\n".join(output)

    def firmware_loop(self):
        output = []
        for pin_name, pin_config in self.pins().items():
            direction = pin_config["direction"]
            pin_define_name = f"PIN{direction}_{self.instances_name}_{pin_name}".upper()
            output.append(f"    digitalWrite({pin_define_name}, value_bit);")
        return "\n".join(output)
