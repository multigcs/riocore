import glob
import json
import os

import riocore

riocore_path = os.path.dirname(riocore.__file__)


class kicad:
    def __init__(self, project):
        self.project = project
        self.kicad_path = os.path.join(self.project.config["output_path"], "KICAD")
        os.makedirs(self.kicad_path, exist_ok=True)

        self.linked_pins = []
        self.virtual_pins = []
        self.expansion_pins = []
        self.pinmapping = {}
        self.pinmapping_rev = {}

        for plugin_instance in self.project.plugin_instances:
            for pin_name, pin_config in plugin_instance.PINDEFAULTS.items():
                if "pin" in pin_config:
                    self.pinmapping[f"{plugin_instance.instances_name}:{pin_name}"] = pin_config["pin"]
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" in pin_config and pin_config.get("pin") and pin_config["pin"].startswith("VIRT:"):
                    pinname = pin_config["pin"]
                    if pinname not in self.virtual_pins:
                        self.virtual_pins.append(pinname)
            for pin in plugin_instance.expansion_outputs():
                self.expansion_pins.append(pin)
            for pin in plugin_instance.expansion_inputs():
                self.expansion_pins.append(pin)

        plugin_names = {}
        for plugin_instance in self.project.plugin_instances:
            plugin_names[plugin_instance.instances_name] = plugin_instance

        setup = {}
        for plugin_instance in self.project.plugin_instances:
            kicad_path = f"{plugin_instance.PLUGIN_PATH}/{plugin_instance.KICAD_FOLDER}"
            if not os.path.isdir(kicad_path):
                continue
            kmodules = glob.glob(f"{kicad_path}/*")
            if not kmodules:
                continue
            kname = kmodules[0].split("/")[-1]
            instances_name = plugin_instance.instances_name
            if kname not in setup:
                setup[kname] = {"num": 0}
            setup[kname]["path"] = kicad_path
            setup[kname]["num"] += 1
            if plugin_instance.gmaster is None:
                setup[kname]["main"] = True
            if "instances" not in setup[kname]:
                setup[kname]["instances"] = {}
            setup[kname]["instances"][instances_name] = {"pins": {}}
            for pin_name, pin_config in plugin_instance.pins().items():
                if pin := pin_config.get("pin"):
                    pin_real = self.pinmapping.get(pin, pin) or ""
                    setup[kname]["instances"][instances_name]["pins"][pin_name] = pin_real

        # print("##", json.dumps(setup, indent=4))
        open(os.path.join(self.kicad_path, "setup.json"), "w").write(json.dumps(setup, indent=4))
        os.system(f"cd {self.kicad_path} && python3 {riocore_path}/files/kicad-builder.py setup.json")
