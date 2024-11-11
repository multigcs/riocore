import os.path
import graphviz


class AxisGraph:
    def __init__(self, hal_file, ini_file):
        self.gAll = graphviz.Digraph("G", format="svg")
        self.gAll.attr(rankdir="LR")
        self.gAll.attr(bgcolor="black")
        base_dir = os.path.dirname(ini_file)
        self.hal_data = open(hal_file, "r").read()
        self.ini_data = open(ini_file, "r").read()

    def svg(self):
        try:
            ja_links = {}
            last_axis = None
            last_jnum = None
            axis = {}
            joints = {}
            for line in self.ini_data.split("\n"):
                if line.startswith("[AXIS_"):
                    last_axis = line.strip()[:-1].split("_")[1]
                    last_jnum = None
                    axis[last_axis] = {
                        "info": [],
                    }
                elif line.startswith("[JOINT_"):
                    last_jnum = line.strip()[:-1].split("_")[1]
                    joints[last_jnum] = {
                        "info": [],
                    }
                    ja_links[f"joint-{last_jnum}"] = (f"axis-{last_axis}", "")

                elif (line.startswith("MIN_") or line.startswith("MAX_")) and not last_jnum and last_axis:
                    key = line.split("=")[0].strip()
                    value = line.split("=")[-1].strip()
                    axis[last_axis]["info"].append(f"{key}={value}")

                elif line.startswith("HOME") and last_jnum:
                    key = line.split("=")[0].strip()
                    value = line.split("=")[-1].strip()
                    joints[last_jnum]["info"].append(f"{key}={value}")

            for line in self.hal_data.split("\n"):
                if line.startswith("net joint-") and "-home-sw-in <= " in line:
                    jnum = line.split("-")[1]
                    halname = line.split()[-1]
                    joints[jnum]["info"].append(f"{halname}")

            for name, data in axis.items():
                infos = "|".join(data["info"])
                label = f"{{{{Axis-{name}|{infos}}}}}"
                self.gAll.node(
                    f"axis-{name}",
                    shape="record",
                    label=label,
                    fontsize="11pt",
                    style="rounded, filled",
                    fillcolor="lightblue",
                )

            for name, data in joints.items():
                infos = "|".join(data["info"])
                label = f"{{{{Joint-{name}|{infos}}}}}"
                self.gAll.node(
                    f"joint-{name}",
                    shape="record",
                    label=label,
                    fontsize="11pt",
                    style="rounded, filled",
                    fillcolor="lightblue",
                )

            for joint, target in ja_links.items():
                self.gAll.edge(joint, target[0], label=target[1], color="white", fontcolor="white")

            return self.gAll.pipe()

        except Exception as error:
            print(f"ERROR(AXIS_GRAPH): {error}")
        return None
