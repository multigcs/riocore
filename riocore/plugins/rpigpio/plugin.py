from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "rpigpio"
        self.COMPONENT = "rpigpio"
        self.INFO = "gpio support"
        self.DESCRIPTION = "gpio support for Raspberry PI4/5 and maybe other boards"
        self.KEYWORDS = "rpi gpio raspberry rpi4 rpi5"
        self.TYPE = "base"
        self.PLUGIN_TYPE = "gpio"
        self.ORIGIN = ""
        self.OPTIONS = {}
        self.SIGNALS = {}
        self.PINDEFAULTS = {}
        self.GPIODEFAULTS = {
            "GPIO:P3": {"pin": "GPIO2", "pos": [528, 107.3], "direction": "all"},
            "GPIO:P5": {"pin": "GPIO3", "pos": [528, 132.6], "direction": "all"},
            "GPIO:P7": {"pin": "GPIO4", "pos": [528, 157.9], "direction": "all"},
            "GPIO:P8": {"pin": "GPIO14", "pos": [553, 157.89999999999998], "direction": "all"},
            "GPIO:P10": {"pin": "GPIO15", "pos": [553, 183.2], "direction": "all"},
            "GPIO:P11": {"pin": "GPIO17", "pos": [528, 208.5], "direction": "all"},
            "GPIO:P12": {"pin": "GPIO18", "pos": [553, 208.5], "direction": "all"},
            "GPIO:P13": {"pin": "GPIO27", "pos": [528, 233.8], "direction": "all"},
            "GPIO:P15": {"pin": "GPIO22", "pos": [528, 259.1], "direction": "all"},
            "GPIO:P16": {"pin": "GPIO23", "pos": [553, 259.09999999999997], "direction": "all"},
            "GPIO:P18": {"pin": "GPIO24", "pos": [553, 284.40000000000003], "direction": "all"},
            "GPIO:P19": {"pin": "GPIO10", "pos": [528, 309.70000000000005], "direction": "all"},
            "GPIO:P21": {"pin": "GPIO9", "pos": [528, 335.0], "direction": "all"},
            "GPIO:P22": {"pin": "GPIO25", "pos": [553, 335.0], "direction": "all"},
            "GPIO:P23": {"pin": "GPIO11", "pos": [528, 360.3], "direction": "all"},
            "GPIO:P24": {"pin": "GPIO8", "pos": [553, 360.3], "direction": "all"},
            "GPIO:P26": {"pin": "GPIO7", "pos": [553, 385.6], "direction": "all"},
            "GPIO:P29": {"pin": "GPIO5", "pos": [528, 436.2], "direction": "all"},
            "GPIO:P31": {"pin": "GPIO6", "pos": [528, 461.5], "direction": "all"},
            "GPIO:P32": {"pin": "GPIO12", "pos": [553, 461.5], "direction": "all"},
            "GPIO:P33": {"pin": "GPIO13", "pos": [528, 486.8], "direction": "all"},
            "GPIO:P35": {"pin": "GPIO19", "pos": [528, 512.1], "direction": "all"},
            "GPIO:P36": {"pin": "GPIO16", "pos": [553, 512.1000000000001], "direction": "all"},
            "GPIO:P37": {"pin": "GPIO26", "pos": [528, 537.4000000000001], "direction": "all"},
            "GPIO:P38": {"pin": "GPIO20", "pos": [553, 537.4000000000001], "direction": "all"},
            "GPIO:P40": {"pin": "GPIO21", "pos": [553, 562.7], "direction": "all"},
        }

    def precheck(self, parent):
        self.hal_gpios = {
            "input": [],
            "output": [],
            "invert": [],
            "reset": [],
        }
        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE == "gpio":
                for name, psetup in plugin_instance.plugin_setup.get("pins", {}).items():
                    direction = plugin_instance.PINDEFAULTS[name]["direction"]
                    reset = plugin_instance.PINDEFAULTS[name].get("reset", False)
                    pin = psetup["pin"]
                    invert = 0
                    for modifier in psetup.get("modifier", []):
                        if modifier["type"] == "invert":
                            invert = 1 - invert
                        else:
                            print(f"WARNING: modifier {modifier['type']} is not supported for gpio's")
                    self.hal_gpios[direction].append(pin)
                    if reset:
                        self.hal_gpios["reset"].append(pin)
                    if invert:
                        self.hal_gpios["invert"].append(pin)

    def hal(self, parent):
        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE == "gpio":
                for name, psetup in plugin_instance.plugin_setup.get("pins", {}).items():
                    direction = plugin_instance.PINDEFAULTS[name]["direction"]
                    pin = psetup["pin"]
                    if direction == "output":
                        psetup["pin"] = f"hal_gpio.{pin}-out"
                    elif direction == "input":
                        psetup["pin"] = f"hal_gpio.{pin}-in"
        return

    def loader(cls, instances):
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
