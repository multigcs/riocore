from riocore.plugins import PluginBase


class Plugin(PluginBase):
    def setup(self):
        self.NAME = "parport"
        self.COMPONENT = "parport"
        self.INFO = "gpio support over parallel port"
        self.DESCRIPTION = "PC parallel port used as gpio"
        self.KEYWORDS = "parport gpio"
        self.TYPE = "base"
        self.IMAGE_SHOW = True
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
        self.SIGNALS = {}
        self.PINDEFAULTS = {
            "DB25:P1": {
                "pin": f"{self.instances_name}:1",
                "comment": "in:out|out:out|x:in",
                "pos": [57, 88.0],
                "direction": "all",
                "edge": "source",
                "type": "GPIO",
            },
            "DB25:P2": {
                "pin": f"{self.instances_name}:2",
                "comment": "in:in|out:out|x:out",
                "pos": [57, 114.1],
                "direction": "all",
                "edge": "source",
                "type": "GPIO",
            },
            "DB25:P3": {
                "pin": f"{self.instances_name}:3",
                "comment": "in:in|out:out|x:out",
                "pos": [57, 140.2],
                "direction": "all",
                "edge": "source",
                "type": "GPIO",
            },
            "DB25:P4": {
                "pin": f"{self.instances_name}:4",
                "comment": "in:in|out:out|x:out",
                "pos": [57, 166.3],
                "direction": "all",
                "edge": "source",
                "type": "GPIO",
            },
            "DB25:P5": {
                "pin": f"{self.instances_name}:5",
                "comment": "in:in|out:out|x:out",
                "pos": [57, 192.4],
                "direction": "all",
                "edge": "source",
                "type": "GPIO",
            },
            "DB25:P6": {
                "pin": f"{self.instances_name}:6",
                "comment": "in:in|out:out|x:out",
                "pos": [57, 218.5],
                "direction": "all",
                "edge": "source",
                "type": "GPIO",
            },
            "DB25:P7": {
                "pin": f"{self.instances_name}:7",
                "comment": "in:in|out:out|x:out",
                "pos": [57, 244.60000000000002],
                "direction": "all",
                "edge": "source",
                "type": "GPIO",
            },
            "DB25:P8": {
                "pin": f"{self.instances_name}:8",
                "comment": "in:in|out:out|x:out",
                "pos": [57, 270.70000000000005],
                "direction": "all",
                "edge": "source",
                "type": "GPIO",
            },
            "DB25:P9": {
                "pin": f"{self.instances_name}:9",
                "comment": "in:in|out:out|x:out",
                "pos": [57, 296.8],
                "direction": "all",
                "edge": "source",
                "type": "GPIO",
            },
            "DB25:P10": {
                "pin": f"{self.instances_name}:10",
                "comment": "",
                "pos": [57, 322.9],
                "direction": "input",
                "edge": "source",
                "type": "GPIO",
            },
            "DB25:P11": {
                "pin": f"{self.instances_name}:11",
                "comment": "",
                "pos": [57, 349.0],
                "direction": "input",
                "edge": "source",
                "type": "GPIO",
            },
            "DB25:P12": {
                "pin": f"{self.instances_name}:12",
                "comment": "",
                "pos": [57, 375.1],
                "direction": "input",
                "edge": "source",
                "type": "GPIO",
            },
            "DB25:P13": {
                "pin": f"{self.instances_name}:13",
                "comment": "",
                "pos": [57, 401.20000000000005],
                "direction": "input",
                "edge": "source",
                "type": "GPIO",
            },
            "DB25:P14": {
                "pin": f"{self.instances_name}:14",
                "comment": "in:out|out:out|x:in",
                "pos": [83.1, 101.05],
                "direction": "all",
                "edge": "source",
                "type": "GPIO",
            },
            "DB25:P15": {
                "pin": f"{self.instances_name}:15",
                "comment": "",
                "pos": [83.1, 127.15000000000002],
                "direction": "input",
                "edge": "source",
                "type": "GPIO",
            },
            "DB25:P16": {
                "pin": f"{self.instances_name}:16",
                "comment": "in:out|out:out|x:in",
                "pos": [83.1, 153.25],
                "direction": "all",
                "edge": "source",
                "type": "GPIO",
            },
            "DB25:P17": {
                "pin": f"{self.instances_name}:17",
                "comment": "in:out|out:out|x:in",
                "pos": [83.1, 179.35000000000002],
                "direction": "all",
                "edge": "source",
                "type": "GPIO",
            },
        }

    def update_prefixes(cls, instances):
        for num, instance in enumerate(instances):
            instance.instance_num = num

    def update_pins(self, parent):
        self.parport_mode = ""
        active = False
        mode_outputs = {
            "in": [1, 14, 16, 17],
            "out": [1, 2, 3, 4, 5, 6, 7, 8, 9, 14, 16, 17],
            "x": [2, 3, 4, 5, 6, 7, 8, 9],
        }
        matching_errors = {"in": [], "out": [], "x": []}

        for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=self.instances_name):
            pin = connected_pin["pin"]
            psetup = connected_pin["setup"]
            direction = connected_pin["direction"]
            active = True
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

        # mapping halnames to real prefix
        for connected_pin in parent.get_all_plugin_pins(configured=True, prefix=self.instances_name):
            pin = connected_pin["pin"]
            psetup = connected_pin["setup"]
            direction = connected_pin["direction"]
            inverted = connected_pin["inverted"]
            if direction == "output":
                psetup["pin"] = f"parport.{self.instance_num}.pin-{int(pin):02d}-out"
                if inverted:
                    parent.halg.setp_add(f"parport.{self.instance_num}.pin-{int(pin):02d}-out-invert", 1)
            elif direction == "input":
                if inverted:
                    psetup["pin"] = f"parport.{self.instance_num}.pin-{int(pin):02d}-in-not"
                else:
                    psetup["pin"] = f"parport.{self.instance_num}.pin-{int(pin):02d}-in"

    def component_loader(cls, instances):
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
