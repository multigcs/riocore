#!/usr/bin/env python3
#
#

import sys
import os.path
import graphviz

if os.path.isfile(os.path.join("riocore", "__init__.py")):
    sys.path.insert(0, os.getcwd())

from riocore import halpins

clusters = {
    "MPG": ["mpg"],
    "RoboJog": ["robojog"],
    "Spacemouse": ["spnav"],
    "Axis": ["axis"],
    "GUI": ["pyvcp", "qtdragon"],
    "RIO": ["rio"],
    "EtherCAT": ["lcec"],
    "Joints": ["joint", "pid"],
    "UI": ["halui", "axisui"],
    "IOcontrol": ["iocontrol"],
    "Spindle": ["spindle"],
}


class HalGraph:
    def __init__(
        self,
    ):
        pass

    def png(self, ini_file, clustering=False, html=True):
        try:
            self.gAll = graphviz.Digraph("G", format="png")
            self.gAll.attr(rankdir="LR")
            # self.gAll.attr(splines="ortho")
            base_dir = os.path.dirname(ini_file)
            ini_data = open(ini_file, "r").read()

            self.signals = {}
            self.components = {}
            self.setps = {}
            self.setss = {}
            self.LIB_PATH = "/usr/share/linuxcnc/hallib"

            section = None
            for line in ini_data.split("\n"):
                if line.startswith("["):
                    section = line.strip("[]")
                elif "=" in line:
                    if section == "HAL":
                        if line.split()[0] == "#":
                            continue
                        name, value = line.split("=", 1)
                        name = name.strip()
                        value = value.strip()
                        if name == "HALFILE":
                            self.load_halfile(base_dir, value)
                        elif name == "POSTGUI_HALFILE":
                            self.load_halfile(base_dir, value)
            groups = {}
            for signal_name, parts in self.signals.items():
                source_parts = parts["source"].split(".")
                source_value = parts.get("source_value", "")
                source_group = ".".join(source_parts[:-1])
                source_pin = source_parts[-1]
                if source_group.startswith("halui."):
                    source_group = ".".join(source_parts[0:1])
                    source_pin = ".".join(source_parts[1:])
                elif "vcp." in source_group or "qtdragon" in source_group:
                    source_group = ".".join(source_parts[0:1])
                    source_pin = ".".join(source_parts[1:])

                if not source_group:
                    source_group = source_pin

                source = f"{source_group}:{source_pin}"

                if not source_group:
                    source_group = source_parts[0]

                if source_group:
                    if source_group not in groups:
                        groups[source_group] = []

                    if source_value:
                        groups[source_group].append(f"{source_pin}={source_value}")
                    else:
                        groups[source_group].append(source_pin)

                for target in parts["targets"]:
                    target_parts = target.split(".")
                    target_group = ".".join(target_parts[:-1])
                    target_pin = target_parts[-1]
                    if target_group.startswith("halui."):
                        target_group = ".".join(target_parts[0:1])
                        target_pin = ".".join(target_parts[1:])
                    elif "vcp." in target_group or "qtdragon" in target_group:
                        target_group = ".".join(target_parts[0:1])
                        target_pin = ".".join(target_parts[1:])
                    target_name = f"{target_group}:{target_pin}"

                    if not target_group:
                        target_group = target_parts[0]

                    if target_group not in groups:
                        groups[target_group] = []
                    groups[target_group].append(target_pin)

                    elabel = ""
                    # if args.elabel:
                    #    elabel = signal_name

                    source_name = source.split("=")[0]

                    if source.startswith("pyvcp"):
                        self.gAll.edge(target_name, source_name, dir="back", label=elabel)
                    elif target.startswith("pyvcp"):
                        self.gAll.edge(source_name, target_name, label=elabel)
                    elif source.startswith("rio.") or source.startswith("lcec.0.rio."):
                        self.gAll.edge(target_name, source_name, dir="back", label=elabel)
                    else:
                        self.gAll.edge(source_name, target_name, label=elabel)

            for group_name, pins in groups.items():
                cgroup = group_name.split(".")[0]
                pin_strs = []
                for pin in pins:
                    port = pin.split("=")[0]
                    if html:
                        pin_str = f'<tr><td port="{port}">{pin}</td></tr>'
                    else:
                        pin_str = f"<{port}>{pin}"
                    pin_strs.append(pin_str)

                color = "lightyellow"
                title = group_name
                if group_name in self.components:
                    comp = self.components[group_name]
                    title = f"{group_name}\\n--{comp}--"
                    color = "lightgray"

                for setp, value in self.setps.items():
                    if setp.startswith(group_name):
                        setp = setp.split(".")[-1]
                        if html:
                            pin_str = f'<tr><td port="{setp}">{setp}={value}</td></tr>'
                        else:
                            pin_str = f"<{setp}>{setp}={value}"
                        pin_strs.append(pin_str)

                if html:
                    title = title.replace("\\n", "<br/>")
                    label = f'<<table border="0" cellborder="1" cellspacing="0"><tr><td  bgcolor="black"><font color="white">{title}</font></td></tr>{"".join(pin_strs)}</table>>'
                else:
                    label = f"{title} | {'|'.join(pin_strs)} "
                cluster = None
                for title, prefixes in clusters.items():
                    if cgroup in prefixes:
                        cluster = title
                        break

                if html:
                    style = ""
                    shape = "plaintext"
                else:
                    style = "rounded, filled"
                    shape = "record"
                if cluster and clustering:
                    with self.gAll.subgraph(name=f"cluster_{cluster}") as gr:
                        gr.attr(label=cluster)
                        gr.node(
                            group_name,
                            shape=shape,
                            label=label,
                            fontsize="11pt",
                            style=style,
                            fillcolor=color,
                        )
                else:
                    self.gAll.node(
                        group_name,
                        shape=shape,
                        label=label,
                        fontsize="11pt",
                        style=style,
                        fillcolor=color,
                    )

            return self.gAll.pipe()

        except Exception as error:
            if clustering:
                return self.png(ini_file, clustering=False)
            else:
                print(f"ERROR(HAL_GRAPH): {error}")
        return None

    def load_halfile(self, basepath, filepath):
        if filepath.startswith("LIB:"):
            basepath = self.LIB_PATH
            filepath = filepath.split(":", 1)[-1]

        if filepath.endswith(".tcl"):
            print(f"ERROR: tcl is not sulorted yet: {basepath}/{filepath}")

            """
            set KINS(KINEMATICS)  "trivkins"
            set KINS(JOINTS)  "d"
            set TRAJ(COORDINATES) ""
            set EMCMOT(SERVO_PERIOD) ""
            set EMCMOT(EMCMOT) ""
            source [file join $::env(HALLIB_DIR) basic_sim.tcl]
            """

            return

        if not os.path.exists(os.path.join(basepath, filepath)):
            if os.path.exists(os.path.join(self.LIB_PATH, filepath)):
                basepath = "/usr/share/linuxcnc/hallib"
            else:
                print(f"ERROR: file: {filepath} not found")
                return

        # if not args.quiet:
        #    print(f"loading {basepath}/{filepath}")

        halfile_data = open(os.path.join(basepath, filepath), "r").read()
        for line in halfile_data.split("\n"):
            line = line.strip()

            if line.startswith("source "):
                self.load_halfile(basepath, line.split()[-1])

            elif line.startswith("loadrt "):
                comp_name = line.split()[1]
                for part in line.split()[2:]:
                    if part.startswith("names="):
                        names = part.split("=")[1].split(",")
                        for name in names:
                            self.components[name] = comp_name

            elif line.startswith("setp "):
                parts = line.split()
                halpin = parts[1]
                value = parts[2]
                self.setps[halpin] = value

            elif line.startswith("sets "):
                parts = line.split()
                halpin = parts[1]
                value = parts[2]
                self.setss[halpin] = value

                signalname = halpin
                if signalname not in self.signals:
                    self.signals[signalname] = {
                        "source": f"{halpin}",
                        "source_value": value,
                        "targets": [],
                    }
                else:
                    self.signals[signalname]["source"] = f"{halpin}"
                    self.signals[signalname]["source_value"] = value

            elif line.startswith("net "):
                parts = line.split()
                signalname = ""
                next_dir = ""
                for part in parts[1:]:
                    if not signalname:
                        signalname = part
                        if signalname not in self.signals:
                            self.signals[signalname] = {
                                "source": "",
                                "targets": [],
                            }
                        continue
                    if part == "=>":
                        next_dir = "input"
                    elif part == "<=":
                        next_dir = "output"

                    elif part == "<=>":
                        next_dir = "inout"

                    elif next_dir == "inout":
                        self.signals[signalname]["targets"].append(part)

                    elif (part in halpins.LINUXCNC_SIGNALS["input"] and part not in halpins.LINUXCNC_SIGNALS["output"]) or next_dir == "input":
                        if (part in halpins.LINUXCNC_SIGNALS["input"] and part not in halpins.LINUXCNC_SIGNALS["output"]) and next_dir == "output":
                            print(f"WARNING: {signalname}: wrong direction-marker: {part}")
                        self.signals[signalname]["targets"].append(part)
                    else:
                        if not self.signals[signalname]["source"]:
                            self.signals[signalname]["source"] = part
                        else:
                            if not self.signals[signalname]["targets"]:
                                # swapping IN/OUT
                                self.signals[signalname]["targets"].append(self.signals[signalname]["source"])
                                self.signals[signalname]["source"] = part
                            else:
                                print("ERROR: double input", signalname, part, self.signals[signalname]["source"])


if __name__ == "__main__":
    ini_path = sys.argv[1]
    graph = HalGraph()
    png_data = graph.png(ini_path)
    if png_data:
        open("/tmp/test.png", "wb").write(png_data)
        # print(png_data.decode())
