from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "rpigpio"
        self.INFO = "gpio support"
        self.DESCRIPTION = """gpio support for Raspberry PI4/5 and maybe other boards

gpio modes:
* rpi5: hal_gpio: gpioinfo shows GPIO7 for GPIO7
* rpi4: hal_gpio: gpioinfo shows SPI_CE1_N for GPIO7
* pi_gpio: hal_pi_gpio: no invert support, not for rpi5

"""
        self.KEYWORDS = "rpi gpio raspberry rpi4 rpi5"
        self.BASETHREAD = True
        self.PROVIDES = ["gpio", "basethread", "base", "rpigpio"]
        self.NEEDS = []
        self.TYPE = "base"
        self.IMAGE_SHOW = True
        self.ORIGIN = ""
        self.OPTIONS = {
            "mode": {
                "default": "rpi5",
                "type": "select",
                "options": ["rpi5", "rpi4", "pi_gpio"],
                "description": "gpio mode (rpi5: gpioinfo shows GPIO7 / rpi4: gpioinfo shows SPI_CE1_N for GPIO7)",
            },
        }
        self.SIGNALS = {}
        gpio_mode = self.plugin_setup.get("mode", self.option_default("mode"))
        if gpio_mode in {"rpi5", "pi_gpio"}:
            self.PINDEFAULTS = {
                "GPIO:P3": {"pin": f"{self.instances_name}:GPIO2", "pos": [264, 53.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P5": {"pin": f"{self.instances_name}:GPIO3", "pos": [264, 66.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P7": {"pin": f"{self.instances_name}:GPIO4", "pos": [264, 78.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P8": {"pin": f"{self.instances_name}:GPIO14", "pos": [276, 78.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P10": {"pin": f"{self.instances_name}:GPIO15", "pos": [276, 91.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P11": {"pin": f"{self.instances_name}:GPIO17", "pos": [264, 104.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P12": {"pin": f"{self.instances_name}:GPIO18", "pos": [276, 104.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P13": {"pin": f"{self.instances_name}:GPIO27", "pos": [264, 116.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P15": {"pin": f"{self.instances_name}:GPIO22", "pos": [264, 129.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P16": {"pin": f"{self.instances_name}:GPIO23", "pos": [276, 129.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P18": {"pin": f"{self.instances_name}:GPIO24", "pos": [276, 142.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P19": {"pin": f"{self.instances_name}:GPIO10", "pos": [264, 154.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P21": {"pin": f"{self.instances_name}:GPIO9", "pos": [264, 167.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P22": {"pin": f"{self.instances_name}:GPIO25", "pos": [276, 167.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P23": {"pin": f"{self.instances_name}:GPIO11", "pos": [264, 180.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P24": {"pin": f"{self.instances_name}:GPIO8", "pos": [276, 180.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P26": {"pin": f"{self.instances_name}:GPIO7", "pos": [276, 192.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P29": {"pin": f"{self.instances_name}:GPIO5", "pos": [264, 218.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P31": {"pin": f"{self.instances_name}:GPIO6", "pos": [264, 230.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P32": {"pin": f"{self.instances_name}:GPIO12", "pos": [276, 230.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P33": {"pin": f"{self.instances_name}:GPIO13", "pos": [264, 243.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P35": {"pin": f"{self.instances_name}:GPIO19", "pos": [264, 256.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P36": {"pin": f"{self.instances_name}:GPIO16", "pos": [276, 256.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P37": {"pin": f"{self.instances_name}:GPIO26", "pos": [264, 268.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P38": {"pin": f"{self.instances_name}:GPIO20", "pos": [276, 268.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P40": {"pin": f"{self.instances_name}:GPIO21", "pos": [276, 281.0], "direction": "all", "edge": "source", "type": "GPIO"},
            }
        elif gpio_mode == "rpi4":
            self.PINDEFAULTS = {
                "GPIO:P3": {"pin": f"{self.instances_name}:SDA1", "pos": [264, 53.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P5": {"pin": f"{self.instances_name}:SCL1", "pos": [264, 66.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P7": {"pin": f"{self.instances_name}:GPIO_GCLK", "pos": [264, 78.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P8": {"pin": f"{self.instances_name}:TXD1", "pos": [276, 78.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P10": {"pin": f"{self.instances_name}:RXD1", "pos": [276, 91.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P11": {"pin": f"{self.instances_name}:GPIO17", "pos": [264, 104.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P12": {"pin": f"{self.instances_name}:GPIO18", "pos": [276, 104.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P13": {"pin": f"{self.instances_name}:GPIO27", "pos": [264, 116.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P15": {"pin": f"{self.instances_name}:GPIO22", "pos": [264, 129.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P16": {"pin": f"{self.instances_name}:GPIO23", "pos": [276, 129.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P18": {"pin": f"{self.instances_name}:GPIO24", "pos": [276, 142.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P19": {"pin": f"{self.instances_name}:SPI_MOSI", "pos": [264, 154.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P21": {"pin": f"{self.instances_name}:SPI_MISO", "pos": [264, 167.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P22": {"pin": f"{self.instances_name}:GPIO25", "pos": [276, 167.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P23": {"pin": f"{self.instances_name}:SPI_SCLK", "pos": [264, 180.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P24": {"pin": f"{self.instances_name}:SPI_CE0_N", "pos": [276, 180.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P26": {"pin": f"{self.instances_name}:SPI_CE1_N", "pos": [276, 192.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P29": {"pin": f"{self.instances_name}:GPIO5", "pos": [264, 218.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P31": {"pin": f"{self.instances_name}:GPIO6", "pos": [264, 230.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P32": {"pin": f"{self.instances_name}:GPIO12", "pos": [276, 230.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P33": {"pin": f"{self.instances_name}:GPIO13", "pos": [264, 243.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P35": {"pin": f"{self.instances_name}:GPIO19", "pos": [264, 256.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P36": {"pin": f"{self.instances_name}:GPIO16", "pos": [276, 256.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P37": {"pin": f"{self.instances_name}:GPIO26", "pos": [264, 268.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P38": {"pin": f"{self.instances_name}:GPIO20", "pos": [276, 268.0], "direction": "all", "edge": "source", "type": "GPIO"},
                "GPIO:P40": {"pin": f"{self.instances_name}:GPIO21", "pos": [276, 281.0], "direction": "all", "edge": "source", "type": "GPIO"},
            }

        self.gpio2pin = {
            2: 3,
            3: 5,
            4: 7,
            5: 29,
            6: 31,
            7: 26,
            8: 24,
            9: 21,
            10: 19,
            11: 23,
            12: 32,
            13: 33,
            14: 8,
            15: 10,
            16: 36,
            17: 11,
            18: 12,
            19: 35,
            20: 38,
            21: 40,
            22: 15,
            23: 16,
            24: 18,
            25: 22,
            26: 37,
            27: 13,
        }

    def update_pins(self, parent):
        gpio_mode = self.plugin_setup.get("mode", self.option_default("mode"))
        self.hal_gpios = {
            "input": [],
            "output": [],
            "invert": [],
            "reset": [],
        }
        for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=self.instances_name):
            pin = connected_pin["pin"]
            psetup = connected_pin["setup"]
            direction = connected_pin["direction"]
            reset = connected_pin["reset"]
            inverted = connected_pin["inverted"]

            self.hal_gpios[direction].append(pin)
            if reset:
                self.hal_gpios["reset"].append(pin)
            if inverted and direction == "output":
                self.hal_gpios["invert"].append(pin)

            if gpio_mode == "pi_gpio":
                gpio = int(pin[4:])
                pin_number = self.gpio2pin[gpio]
                if direction == "output":
                    psetup["pin"] = f"hal_pi_gpio.pin-{pin_number:02d}-out"
                elif direction == "input":
                    psetup["pin"] = f"hal_pi_gpio.pin-{pin_number:02d}-in"
            elif direction == "output":
                psetup["pin"] = f"hal_gpio.{pin}-out"
            elif direction == "input":
                if inverted:
                    psetup["pin"] = f"hal_gpio.{pin}-in-not"
                else:
                    psetup["pin"] = f"hal_gpio.{pin}-in"

    @classmethod
    def component_loader(cls, instances):
        gpio_mode = instances[0].plugin_setup.get("mode", instances[0].option_default("mode"))
        if gpio_mode == "pi_gpio":
            output = []
            output.append("# load hal_pi_gpio")

            mask_dir = 0
            mask_excl = 0
            for kn, gpio in enumerate(instances[0].gpio2pin):
                dec = 2**kn
                gpio_name = f"GPIO{gpio}"
                pin_number = instances[0].gpio2pin[gpio]
                if gpio_name in instances[0].hal_gpios["output"]:
                    mask_dir |= dec
                    output.append(f"#   {gpio_name:6s} | hal_pi_gpio.pin-{pin_number:02d}-out | 0x{dec:x}")
                elif gpio_name in instances[0].hal_gpios["input"]:
                    output.append(f"#   {gpio_name:6s} | hal_pi_gpio.pin-{pin_number:02d}-in  | 0x{dec:x}")
                else:
                    mask_excl |= dec

            output.append(f"loadrt hal_pi_gpio dir=0x{mask_dir:x} exclude=0x{mask_excl:x}")
            output.append("addf hal_pi_gpio.read base-thread")
            output.append("addf hal_pi_gpio.write base-thread")
            output.append("")

        else:
            output = []
            args = []
            if instances[0].hal_gpios["input"]:
                args.append(f"inputs={','.join(instances[0].hal_gpios['input'])}")
            if instances[0].hal_gpios["output"]:
                args.append(f"outputs={','.join(instances[0].hal_gpios['output'])}")
            if instances[0].hal_gpios["invert"]:
                args.append(f"invert={','.join(instances[0].hal_gpios['invert'])}")
            if instances[0].hal_gpios["reset"]:
                args.append(f"reset={','.join(instances[0].hal_gpios['reset'])}")
            output.append("# load hal_gpio")
            output.append(f"loadrt hal_gpio {' '.join(args)}")
            output.append("addf hal_gpio.read base-thread")
            output.append("addf hal_gpio.write base-thread")
            output.append("")
        return "\n".join(output)
