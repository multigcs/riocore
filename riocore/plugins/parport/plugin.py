from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "parport"
        self.COMPONENT = "parport"
        self.INFO = "gpio support over parallel port"
        self.DESCRIPTION = "PC parallel port used as gpio"
        self.KEYWORDS = "parport gpio"
        self.TYPE = "base"
        self.PLUGIN_TYPE = "gpio"
        self.ORIGIN = ""
        self.OPTIONS = {
            "portaddr": {
                "default": "0",
                "type": "select",
                "options": [
                    "0|1. port",
                    "1|2. port",
                    "2|3. port",
                ],
                "description": "parport address",
            },
        }
        portaddr = self.plugin_setup.get("portaddr", self.option_default("portaddr"))

        self.SIGNALS = {}
        self.PINDEFAULTS = {}
        self.GPIODEFAULTS = {
            "DB25:P1": {"pin": f"{portaddr}:1", "comment": "in:out|out:out|x:in", "pos": [57, 88.0], "direction": "all"},
            "DB25:P2": {"pin": f"{portaddr}:2", "comment": "in:in|out:out|x:out", "pos": [57, 114.1], "direction": "all"},
            "DB25:P3": {"pin": f"{portaddr}:3", "comment": "in:in|out:out|x:out", "pos": [57, 140.2], "direction": "all"},
            "DB25:P4": {"pin": f"{portaddr}:4", "comment": "in:in|out:out|x:out", "pos": [57, 166.3], "direction": "all"},
            "DB25:P5": {"pin": f"{portaddr}:5", "comment": "in:in|out:out|x:out", "pos": [57, 192.4], "direction": "all"},
            "DB25:P6": {"pin": f"{portaddr}:6", "comment": "in:in|out:out|x:out", "pos": [57, 218.5], "direction": "all"},
            "DB25:P7": {"pin": f"{portaddr}:7", "comment": "in:in|out:out|x:out", "pos": [57, 244.60000000000002], "direction": "all"},
            "DB25:P8": {"pin": f"{portaddr}:8", "comment": "in:in|out:out|x:out", "pos": [57, 270.70000000000005], "direction": "all"},
            "DB25:P9": {"pin": f"{portaddr}:9", "comment": "in:in|out:out|x:out", "pos": [57, 296.8], "direction": "all"},
            "DB25:P10": {"pin": f"{portaddr}:10", "comment": "", "pos": [57, 322.9], "direction": "input"},
            "DB25:P11": {"pin": f"{portaddr}:11", "comment": "", "pos": [57, 349.0], "direction": "input"},
            "DB25:P12": {"pin": f"{portaddr}:12", "comment": "", "pos": [57, 375.1], "direction": "input"},
            "DB25:P13": {"pin": f"{portaddr}:13", "comment": "", "pos": [57, 401.20000000000005], "direction": "input"},
            "DB25:P14": {"pin": f"{portaddr}:14", "comment": "in:out|out:out|x:in", "pos": [83.1, 101.05], "direction": "all"},
            "DB25:P15": {"pin": f"{portaddr}:15", "comment": "", "pos": [83.1, 127.15000000000002], "direction": "input"},
            "DB25:P16": {"pin": f"{portaddr}:16", "comment": "in:out|out:out|x:in", "pos": [83.1, 153.25], "direction": "all"},
            "DB25:P17": {"pin": f"{portaddr}:17", "comment": "in:out|out:out|x:in", "pos": [83.1, 179.35000000000002], "direction": "all"},
        }

    def precheck(self, parent):
        portaddr = self.plugin_setup.get("portaddr", self.option_default("portaddr"))
        self.parport_mode = ""
        active = False
        mode_outputs = {
            "in": [1, 14, 16, 17],
            "out": [1, 2, 3, 4, 5, 6, 7, 8, 9, 14, 16, 17],
            "x": [2, 3, 4, 5, 6, 7, 8, 9],
        }
        matching_errors = {"in": [], "out": [], "x": []}
        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE == "gpio":
                for name, psetup in plugin_instance.plugin_setup.get("pins", {}).items():
                    pin = psetup["pin"]
                    if ":" not in pin:
                        continue
                    port = pin.split(":")[0]
                    if port != portaddr:
                        continue
                    active = True
                    pin = int(pin.split(":")[1])
                    direction = plugin_instance.PINDEFAULTS[name]["direction"]
                    if direction == "output":
                        for mode in mode_outputs:
                            if pin not in mode_outputs[mode]:
                                matching_errors[mode].append(f"{pin} must be input")
                    else:
                        for mode in mode_outputs:
                            if pin in mode_outputs[mode]:
                                matching_errors[mode].append(f"{pin} must be output")

        self.parport_mode = ""
        for mode in matching_errors:
            if not matching_errors[mode]:
                self.parport_mode = mode

        if not self.parport_mode:
            print("ERROR: no usable parport mode found")
            for mode in matching_errors:
                if matching_errors[mode]:
                    print(f"  mode({mode}): {', '.join(matching_errors[mode])}")
            exit(1)
        if not active:
            self.parport_mode = ""

    def hal(self, parent):
        portaddr = self.plugin_setup.get("portaddr", self.option_default("portaddr"))
        for plugin_instance in parent.project.plugin_instances:
            if plugin_instance.PLUGIN_TYPE == "gpio":
                for name, psetup in plugin_instance.plugin_setup.get("pins", {}).items():
                    pin = psetup["pin"]
                    if ":" not in pin:
                        continue
                    port = pin.split(":")[0]
                    if port != portaddr:
                        continue
                    pin = int(pin.split(":")[1])

                    direction = plugin_instance.PINDEFAULTS[name]["direction"]
                    reset = plugin_instance.PINDEFAULTS[name].get("reset", False)
                    invert = 0
                    for modifier in psetup.get("modifier", []):
                        if modifier["type"] == "invert":
                            invert = 1 - invert
                        else:
                            print(f"WARNING: modifier {modifier['type']} is not supported for gpio's")
                    if direction == "output":
                        psetup["pin"] = f"parport.{self.instance_num}.pin-{pin:02d}-out"
                        if invert:
                            parent.halg.setp_add(f"parport.{self.instance_num}.pin-{pin:02d}-out-invert", 1)
                    elif direction == "input":
                        if invert:
                            psetup["pin"] = f"parport.{self.instance_num}.pin-{pin:02d}-in-not"
                        else:
                            psetup["pin"] = f"parport.{self.instance_num}.pin-{pin:02d}-in"
                    if reset:
                        parent.halg.setp_add(f"parport.{self.instance_num}.pin-{pin:02d}-out-reset", 1)

    def loader(cls, instances):
        output = []
        modes = []
        instance_num = 0
        for instance in instances:
            if instance.parport_mode:
                instance.instance_num = instance_num
                portaddr = instance.plugin_setup.get("portaddr", instance.option_default("portaddr"))
                modes.append(f"{portaddr} {instance.parport_mode}")
                instance_num += 1

        output.append(f"# parport component for {len(modes)} port(s)")
        output.append(f'loadrt hal_parport cfg="{" ".join(modes)}"')
        for pnum, mode in enumerate(modes):
            output.append(f"addf parport.{pnum}.read base-thread")
            output.append(f"addf parport.{pnum}.write base-thread")
            output.append(f"addf parport.{pnum}.reset base-thread")
            output.append(f"setp parport.{pnum}.reset-time 5000")
        output.append("")
        return "\n".join(output)
