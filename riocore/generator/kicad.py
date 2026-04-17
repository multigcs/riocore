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

        setup = {}
        for plugin_instance in self.project.plugin_instances:
            kicad_path = f"{plugin_instance.PLUGIN_PATH}/{plugin_instance.KICAD_FOLDER}"

            if not os.path.isdir(kicad_path):
                continue
            kmodules = glob.glob(f"{kicad_path}/*")
            if not kmodules:
                continue

            kname = kmodules[0].split("/")[-1]

            if kname not in setup:
                setup[kname] = {"num": 0}
            setup[kname]["path"] = kicad_path
            setup[kname]["num"] += 1
            if plugin_instance.gmaster is None:
                setup[kname]["main"] = True

        # print("##", json.dumps(setup, indent=4))
        open(os.path.join(self.kicad_path, "setup.json"), "w").write(json.dumps(setup, indent=4))
        os.system(f"cd {self.kicad_path} && python3 {riocore_path}/files/kicad-builder.py setup.json")
