from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "esp32_ledc"
        self.PINDEFAULTS = {
            "pwm1": {
                "direction": "output",
                "invert": False,
                "pullup": False,
            },
        }
        self.INTERFACE = {
            "pwm1": {
                "size": 8,
                "direction": "output",
            },
        }
        self.SIGNALS = {
            "pwm1": {
                "direction": "output",
            },
        }
        self.INFO = "ledc plugin to generate up to 16 PWM signals"
        self.DESCRIPTION = "only for esp32"

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
        channel = 0
        for pin_name, pin_config in self.pins().items():
            pin = pin_config["pin"]
            direction = pin_config["direction"]
            pin_define_name = f"PIN{direction}_{self.instances_name}_{pin_name}".upper()
            #output.append(f"    pinMode({pin_define_name}, {direction.upper()});")
            freq = 5000
            resolution = 8
            output.append(f"    ledcSetup({channel}, {freq}, {resolution});")
            output.append(f"    ledcAttachPin({pin_define_name}, {channel});")
            channel += 1


        return "\n".join(output)

    def firmware_loop(self):
        output = []
        channel = 0
        for pin_name, pin_config in self.pins().items():
            pin = pin_config["pin"]
            direction = pin_config["direction"]
            pin_define_name = f"PIN{direction}_{self.instances_name}_{pin_name}".upper()
            output.append(f"    ledcWrite({channel}, value_pwm1);")
            channel += 1
        return "\n".join(output)
