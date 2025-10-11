from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "rpii2c"
        self.COMPONENT = "rpii2c"
        self.INFO = "gpio support over i2c port"
        self.DESCRIPTION = "gpio support over i2c port"
        self.KEYWORDS = "ii2c gpio"
        self.TYPE = "base"
        self.PLUGIN_TYPE = "gpio"
        self.IMAGE = ""
        self.ORIGIN = ""
        self.SIGNALS = {}
        self.PINDEFAULTS = {}
        self.FILES = ["rpii2c.py"]
        self.OPTIONS = {
            "device": {
                "default": "pcf8574",
                "type": "select",
                "options": [
                    "pcf8574",
                    "ads1115",
                    "lm75",
                ],
                "description": "i2c device",
            },
            "address": {
                "default": "0x20",
                "type": "select",
                "options": [
                    "0x20",
                    "0x21",
                    "0x22",
                    "0x23",
                    "0x24",
                    "0x25",
                    "0x26",
                    "0x27",
                    "0x48",
                    "0x49",
                ],
                "description": "slave address",
            },
        }
        device = self.plugin_setup.get("device", self.option_default("device"))
        self.IMAGE = f"{device}.png"
        if device == "pcf8574":
            self.GPIODEFAULTS = {
                "IO:P7": {"pin": f"{self.instances_name}:7", "comment": "", "pos": [140, 176.0], "direction": "all"},
                "IO:P6": {"pin": f"{self.instances_name}:6", "comment": "", "pos": [140, 200.0], "direction": "all"},
                "IO:P5": {"pin": f"{self.instances_name}:5", "comment": "", "pos": [140, 224.0], "direction": "all"},
                "IO:P4": {"pin": f"{self.instances_name}:4", "comment": "", "pos": [140, 248.0], "direction": "all"},
                "IO:P3": {"pin": f"{self.instances_name}:3", "comment": "", "pos": [140, 272.0], "direction": "all"},
                "IO:P2": {"pin": f"{self.instances_name}:2", "comment": "", "pos": [140, 296.0], "direction": "all"},
                "IO:P1": {"pin": f"{self.instances_name}:1", "comment": "", "pos": [140, 320.0], "direction": "all"},
                "IO:P0": {"pin": f"{self.instances_name}:0", "comment": "", "pos": [140, 344.0], "direction": "all"},
            }
        elif device == "lm75":
            self.SIGNALS = {
                "temp_c": {
                    "direction": "input",
                    "format": "0.2f",
                    "unit": "°C",
                    "pos": [145, 69],
                },
                "temp_f": {
                    "direction": "input",
                    "format": "0.2f",
                    "unit": "°F",
                    "pos": [145, 91],
                },
            }
        elif device == "ads1115":
            self.SIGNALS = {}
            for channel in range(4):
                self.SIGNALS[f"adc{channel}"] = {
                    "direction": "input",
                    "format": "0.2f",
                    "unit": "V",
                    "pos": [152, 30 + channel * 24],
                }

    def update_prefixes(cls, instances):
        for instance in instances:
            instance.PREFIX = f"rpii2c.{instance.instances_name}"

    def precheck(self, parent):
        self.invert_mask = ""
        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE == "gpio":
                for name, psetup in plugin_instance.plugin_setup.get("pins", {}).items():
                    if ":" not in psetup["pin"]:
                        continue
                    prefix = psetup["pin"].split(":", 1)[0]
                    if self.instances_name != prefix:
                        continue
                    invert = 0
                    for modifier in psetup.get("modifier", []):
                        if modifier["type"] == "invert":
                            invert = 1 - invert
                        else:
                            print(f"WARNING: modifier {modifier['type']} is not supported for gpio's")
                    if invert:
                        self.invert_mask += "1"
                    else:
                        self.invert_mask += "0"
        if not self.invert_mask:
            self.invert_mask = "00000000"

    def hal(self, parent):
        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE == "gpio":
                for name, psetup in plugin_instance.plugin_setup.get("pins", {}).items():
                    direction = plugin_instance.PINDEFAULTS[name]["direction"]
                    if ":" not in psetup["pin"]:
                        continue
                    prefix = psetup["pin"].split(":", 1)[0]
                    if self.instances_name != prefix:
                        continue
                    pin = int(psetup["pin"].split(":", 1)[1])

                    if direction == "output":
                        psetup["pin"] = f"rpii2c.{self.instances_name}.p{pin:02d}-out"
                    elif direction == "input":
                        psetup["pin"] = f"rpii2c.{self.instances_name}.p{pin:02d}-in"

    def loader(cls, instances):
        output = []
        args = []
        for instance in instances:
            device = instance.plugin_setup.get("device", instance.option_default("device"))
            address = instance.plugin_setup.get("address", instance.option_default("address"))
            args.append(f"{instance.instances_name} {device} {address} {instance.invert_mask}")
        output.append("# load rpii2c")
        output.append(f"loadusr -Wn rpii2c ./rpii2c.py {' '.join(args)}")
        output.append("")
        return "\n".join(output)
