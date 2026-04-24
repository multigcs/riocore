import json
import os
import stat

riocore_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class kicad:
    def __init__(self, project, instance):
        self.project = project
        self.instance = instance
        self.prefix = instance.hal_prefix
        self.kicad_path = os.path.join(self.project.config["output_path"], "KICAD", instance.instances_name)
        os.makedirs(self.kicad_path, exist_ok=True)
        self.setup_json()
        self.build_sh()

    def setup_json(self):
        self.linked_pins = []
        self.virtual_pins = []
        self.expansion_pins = []
        self.pinmapping = {}
        self.pinmapping_rev = {}

        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.master != self.instance.instances_name and plugin_instance.gmaster != self.instance.instances_name:
                continue
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

        setup = {
            "name": self.instance.instances_name,
            "modules": {},
        }
        for plugin_instance in self.project.plugin_instances:
            if plugin_instance.master != self.instance.instances_name and plugin_instance.gmaster != self.instance.instances_name:
                continue
            kicad_path = f"{plugin_instance.PLUGIN_PATH}/{plugin_instance.KICAD_FOLDER}"
            if not plugin_instance.KICAD_MODULE:
                continue
            kname = plugin_instance.KICAD_MODULE
            instances_name = plugin_instance.instances_name
            if kname not in setup["modules"]:
                setup["modules"][kname] = {"num": 0}
            setup["modules"][kname]["path"] = kicad_path
            setup["modules"][kname]["num"] += 1
            if plugin_instance.gmaster is None:
                setup["modules"][kname]["main"] = True
            if "instances" not in setup["modules"][kname]:
                setup["modules"][kname]["instances"] = {}
            setup["modules"][kname]["instances"][instances_name] = {"pins": {}}

            pos = plugin_instance.plugin_setup.get("pos")
            if pos:
                x = pos[0] / 4.5
                y = pos[1] / 4.5
                setup["modules"][kname]["instances"][instances_name]["pos"] = [x, y]
            rotate = plugin_instance.plugin_setup.get("rotate")
            if rotate:
                setup["modules"][kname]["instances"][instances_name]["rotate"] = rotate

            for pin_name, pin_config in plugin_instance.pins().items():
                if pin := pin_config.get("pin"):
                    pin_real = self.pinmapping.get(pin, pin) or ""
                    setup["modules"][kname]["instances"][instances_name]["pins"][pin_name] = pin_real

        open(os.path.join(self.kicad_path, "setup.json"), "w").write(json.dumps(setup, indent=4))

    def build_sh(self):
        output = ["#!/bin/sh"]
        output.append("")
        output.append('DIRNAME=`dirname "$0"`')
        output.append("")
        output.append(f"(cd $DIRNAME && python3 {riocore_path}/files/kicad-builder.py setup.json)")
        output.append("")
        output.append(f'echo "    # kicad $DIRNAME/{self.instance.instances_name}.kicad_pro"')
        output.append("")

        build_sh = os.path.join(self.kicad_path, "build.sh")
        open(build_sh, "w").write("\n".join(output))
        os.chmod(build_sh, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
