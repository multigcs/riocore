#!/usr/bin/env python3
#
#

import os.path
import sys

import graphviz

if os.path.isfile(os.path.join("riocore", "__init__.py")):
    sys.path.insert(0, os.getcwd())

from riocore import halpins

clusters = {
    "MPG": ["mpg"],
    "RoboJog": ["robojog"],
    "Spacemouse": ["spnav"],
    # "Axis": ["axis"],
    # "GUI": ["pyvcp", "qtdragon"],
    # "RIO": ["rio"],
    # "EtherCAT": ["lcec"],
    # "Joints": ["joint", "pid"],
    # "UI": ["halui", "axisui"],
    # "IOcontrol": ["iocontrol"],
    # "Spindle": ["spindle"],
    # "Joints": ["joint"],
    # "PIDs": ["pid"],
}


class HalGraph:
    def __init__(
        self,
    ):
        pass

    def export(self, ini_file, clustering=False, html=True, fmt="png", fill=None, colors=None):
        if colors is None:
            """
            colors = {
                "bg": "gray",
                "edge": "red",
                "header_bg": "gray",
                "header_text": "white",
                "port_bg": "yellow",
                "port_text": "black",
                "setp_bg": "green",
                "setp_text": "black",
            }
            """
            colors = {
                "bg": "",
                "edge": "black",
                "header_bg": "black",
                "header_text": "white",
                "port_bg": "white",
                "port_text": "black",
                "setp_bg": "white",
                "setp_text": "black",
            }

        # try:
        if True:
            self.gAll = graphviz.Digraph("G", format=fmt, engine="dot")
            if colors["bg"]:
                self.gAll.attr(bgcolor=colors["bg"])
            self.gAll.attr(rankdir="LR")
            # self.gAll.attr(splines="ortho")
            base_dir = os.path.dirname(ini_file)
            ini_data = open(ini_file).read()

            self.signals = {}
            self.components = {}
            self.setps = {}
            self.setss = {}
            self.LIB_PATH = "/usr/share/linuxcnc/hallib"

            section = None
            for line in ini_data.split("\n"):
                if line.startswith("["):
                    section = line.strip("[]")
                elif "=" in line and section == "HAL":
                    if line.split()[0] == "#":
                        continue
                    name, value = line.split("=", 1)
                    name = name.strip()
                    value = value.strip()
                    if name in {"HALFILE", "POSTGUI_HALFILE"}:
                        self.load_halfile(base_dir, value)

            # checking signals
            for signalname, signal in self.signals.items():
                if not signal["source"]:
                    print(f"WARNING: signal {signalname} has no source >= {', '.join(signal['targets'])} ({', '.join(signal['files'])})")
                elif not signal["targets"]:
                    print(f"WARNING: signal {signalname} has no target: <= {signal['source']} ({', '.join(signal['files'])})")

            groups = {}
            for signal_name, parts in self.signals.items():
                source_parts = parts["source"].split(".")
                source_value = parts.get("source_value", "")
                source_group = ".".join(source_parts[:-1])
                source_pin = source_parts[-1]
                if source_group.startswith("halui.") or "vcp." in source_group or "qtdragon" in source_group:
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
                    if target_group.startswith("halui.") or "vcp." in target_group or "qtdragon" in target_group:
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

                    if not source_group and not source_pin:
                        continue
                    if not target_name:
                        continue

                    source_name = source.split("=")[0]
                    eid = source_name.replace(":", ".")
                    if source.startswith("pyvcp"):
                        self.gAll.edge(target_name, source_name, dir="back", label=elabel, id=eid, penwidth="2", color=colors["edge"])
                    elif target.startswith("pyvcp"):
                        self.gAll.edge(source_name, target_name, label=elabel, id=eid, penwidth="2", color=colors["edge"])
                    elif source.startswith(("rio.", "lcec.0.rio.")):
                        self.gAll.edge(target_name, source_name, dir="back", label=elabel, id=eid, penwidth="2", color=colors["edge"])
                    else:
                        self.gAll.edge(source_name, target_name, label=elabel, id=eid, penwidth="2", color=colors["edge"])

            used = []
            for group_name in sorted(groups, reverse=True):
                pins = groups[group_name]
                # cgroup = group_name.split(".")[0]
                pin_strs = []
                for pin in pins:
                    port = pin.split("=")[0]
                    if html:
                        pin_str = f'<tr><td bgcolor="{colors["port_bg"]}" port="{port}"><font color="{colors["port_text"]}">{pin}{fill or ""}</font></td></tr>'
                    else:
                        pin_str = f"<{port}>{pin}"
                    pin_strs.append(pin_str)

                # color = "lightyellow"
                title = group_name
                if group_name in self.components:
                    comp = self.components[group_name]
                    title = f"{group_name}\\n--{comp}--"
                    # color = "lightgray"

                for setp_raw, value in self.setps.items():
                    if setp_raw.startswith(group_name) and setp_raw not in used:
                        used.append(setp_raw)
                        setp = setp_raw.replace(f"{group_name}.", "")
                        if html:
                            pin_str = f'<tr><td bgcolor="{colors["setp_bg"]}" port="{setp}"><font color="{colors["setp_text"]}">{setp}={value}</font></td></tr>'
                        else:
                            pin_str = f"<{setp}>{setp}={value}"
                        pin_strs.append(pin_str)

                if html:
                    title = title.replace("\\n", "<br/>")
                    label = f'<<table border="0" cellborder="1" cellspacing="0"><tr><td bgcolor="{colors["header_bg"]}"><font color="{colors["header_text"]}">{title}</font></td></tr>{"".join(pin_strs)}</table>>'
                else:
                    label = f"{title} | {'|'.join(pin_strs)} "
                cluster = None
                for title, prefixes in clusters.items():
                    for prefix in prefixes:
                        if group_name.startswith(prefix):
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
                            # fillcolor=color,
                        )
                else:
                    self.gAll.node(
                        group_name,
                        shape=shape,
                        label=label,
                        fontsize="11pt",
                        style=style,
                        # fillcolor=color,
                    )

            return self.gAll.pipe()

        # except Exception as error:
        #    if clustering:
        #        return self.png(ini_file, clustering=False)
        #    print(f"ERROR(HAL_GRAPH): {error}")
        return None

    def png(self, ini_file, clustering=False, html=True, fill=None, colors=None):
        return self.export(ini_file, clustering=clustering, html=html, fmt="png", fill=fill, colors=colors)

    def svg(self, ini_file, clustering=False, html=True, fill=None, colors=None):
        return self.export(ini_file, clustering=clustering, html=html, fmt="svg", fill=fill, colors=colors)

    def pin_direction(self, pin):
        if pin in halpins.LINUXCNC_SIGNALS["input"] and pin not in halpins.LINUXCNC_SIGNALS["output"]:
            return "input"
        if pin in halpins.LINUXCNC_SIGNALS["output"] and pin not in halpins.LINUXCNC_SIGNALS["input"]:
            return "output"
        if pin.startswith(("conv-", "conv_", "toggle.", "or2.", "and2.", "xor2.", "timedelay.", "not.", "mux2.")):
            if pin.endswith((".in", ".in0", ".in1", ".sel")):
                return "input"
            if pin.endswith(".out"):
                return "output"
        if pin.startswith(("estop-latch.")):
            if pin.endswith("-in"):
                return "input"
            if pin.endswith("-out"):
                return "output"
            if pin.endswith(".reset"):
                return "input"
        if pin.startswith("siggen.") and pin.endswith(".clock"):
            return "output"
        if pin.startswith("hm2_"):
            if ".analogin" in pin:
                return "output"
            if pin.endswith(".velocity-cmd"):
                return "input"
            if pin.endswith(".position-fb"):
                return "output"
            if pin.endswith(".enable"):
                return "input"
        if pin.startswith("lcec."):
            if pin.endswith(".slave-state-op"):
                return "output"
            if ".pwm-" in pin:
                return "input"
            if ".din-" in pin:
                return "output"
            if ".dout-" in pin:
                return "input"
        if pin.startswith("halui.mdi-command-"):
            return "input"
        if pin.startswith("time."):
            if pin.endswith(".start"):
                return "input"
            return "output"
        # print(pin)
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

        halfile_data = open(os.path.join(basepath, filepath)).read()
        for line_num, line_raw in enumerate(halfile_data.split("\n"), 1):
            line = line_raw.split("#")[0].strip()
            if not line:
                continue

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
                        "files": [f"{filepath}:{line_num}"],
                    }
                else:
                    self.signals[signalname]["source"] = f"{halpin}"
                    self.signals[signalname]["source_value"] = value
                    if filepath not in self.signals[signalname]["files"]:
                        self.signals[signalname]["files"].append(f"{filepath}:{line_num}")

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
                                "files": [f"{filepath}:{line_num}"],
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
                    elif self.pin_direction(part) == "input" or next_dir == "input":
                        if next_dir == "output":
                            print(f"WARNING: {signalname}: wrong direction-marker: {part} ({filepath}:{line_num})")
                        self.signals[signalname]["targets"].append(part)
                    elif not self.signals[signalname]["source"]:
                        self.signals[signalname]["source"] = part
                    elif not self.signals[signalname]["targets"]:
                        pdir = self.pin_direction(part)
                        if next_dir and pdir and next_dir != pdir:
                            print(f"WARNING: {signalname}: wrong direction-marker: {part} ({filepath}:{line_num})")
                        if self.pin_direction(self.signals[signalname]["source"]) == "output" or pdir == "input":
                            self.signals[signalname]["targets"].append(part)
                        else:
                            # swapping IN/OUT
                            self.signals[signalname]["targets"].append(self.signals[signalname]["source"])
                            self.signals[signalname]["source"] = part
                    else:
                        ignore = False
                        if signalname in self.signals and part == self.signals.get(signalname, {}).get("source"):
                            ignore = True
                        if not ignore:
                            files = self.signals.get(signalname, {}).get("files", [])
                            if filepath not in files:
                                files.append(filepath)
                            if not next_dir:
                                # using as output
                                if signalname in self.signals:
                                    self.signals[signalname]["targets"].append(part)
                            else:
                                print(f"WARNING: {signalname}: double input {part}: {self.signals[signalname]['source']} ->  {', '.join(self.signals[signalname]['targets'])} ({', '.join(files)})")


if __name__ == "__main__":
    ini_path = sys.argv[1]
    graph = HalGraph()
    png_data = graph.png(ini_path)
    if png_data:
        open("/tmp/test.png", "wb").write(png_data)
        # print(png_data.decode())
