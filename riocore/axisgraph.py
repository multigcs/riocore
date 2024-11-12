import graphviz


class AxisGraph:
    def __init__(self, hal_file, ini_file):
        self.gAll = graphviz.Digraph("G", format="svg")
        self.gAll.attr(rankdir="LR")
        self.gAll.attr(bgcolor="black")
        self.hal_data = open(hal_file, "r").read()
        self.ini_data = open(ini_file, "r").read()

    def svg(self):
        try:
            ja_links = {}
            last_section = None
            last_axis = None
            last_jnum = None
            axis = {}
            joints = {}
            kins = None
            for line in self.ini_data.split("\n"):
                if line.startswith("#"):
                    continue
                elif line.startswith("["):
                    last_section = line.split("[")[1].split("]")[0]
                    if last_section.startswith("AXIS_"):
                        last_axis = last_section.split("_")[1]
                        last_jnum = None
                        axis[last_axis] = {
                            "info": [],
                        }
                    elif last_section.startswith("JOINT_"):
                        last_jnum = last_section.split("_")[1]
                        joints[last_jnum] = {
                            "info": [],
                        }
                        ja_links[f"joint-{last_jnum}"] = (f"axis-{last_axis}", "")
                    else:
                        last_axis = None
                        last_jnum = None

                elif "=" in line:
                    parts = line.split("=", 1)
                    key = parts[0].strip()
                    value = parts[1].strip()
                    if last_axis and not last_jnum:
                        axis[last_axis]["info"].append(f"{key}={value}")
                    elif last_jnum:
                        if key in {"TYPE", "MIN_LIMIT", "MAX_LIMIT", "SCALE_OUT", "SCALE_IN", "HOME_SEQUENCE"}:
                            joints[last_jnum]["info"].append(f"{key}={value}")
                    elif last_section == "KINS" and key == "KINEMATICS":
                        kins = value

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

            if kins:
                infos = "|".join(kins.split())
                label = f"{{{{Kins|{infos}}}}}"
                self.gAll.node(
                    f"kins",
                    shape="record",
                    label=label,
                    fontsize="11pt",
                    style="rounded, filled",
                    fillcolor="lightblue",
                )
                for name in axis:
                    self.gAll.edge(f"axis-{name}", "kins", color="white", fontcolor="white")

            return self.gAll.pipe()

        except Exception as error:
            print(f"ERROR(AXIS_GRAPH): {error}")
        return None
