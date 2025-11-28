import json
import os
import shutil

import riocore
from riocore.gui import halgraph

riocore_path = os.path.dirname(riocore.__file__)


class documentation:
    def __init__(self, project):
        self.project = project
        self.doc_path = os.path.join(self.project.config["output_path"], "DOC")
        os.makedirs(self.doc_path, exist_ok=True)

        self.iface_in = []
        self.iface_out = []
        # output_pos = self.project.buffer_size

        size = 32
        self.iface_out.append(["RX_HEADER", size])
        self.iface_in.append(["TX_HEADER", size])
        self.iface_in.append(["TIMESTAMP", size])

        """
        if self.project.multiplexed_input:
            variable_name = "MULTIPLEXED_INPUT_VALUE"
            size = self.project.multiplexed_input_size
            self.iface_in.append([variable_name, size])
            variable_name = "MULTIPLEXED_INPUT_ID"
            size = 8
            self.iface_in.append([variable_name, size])

        if self.project.multiplexed_output:
            variable_name = "MULTIPLEXED_OUTPUT_VALUE"
            size = self.project.multiplexed_output_size
            #for bit_num in range(0, size, 8):
            #    output_pos -= 8
            self.iface_out.append([variable_name, size])
            variable_name = "MULTIPLEXED_OUTPUT_ID"
            size = 8
            #for bit_num in range(0, size, 8):
            #    output_pos -= 8
            self.iface_out.append([variable_name, size])

        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            if multiplexed:
                continue
            variable_name = data_config["variable"]
            hal_name = f"{plugin_instance.instances_name}.{data_name}"
            if data_config["direction"] == "input":
                if not data_config.get("expansion"):
                    self.iface_in.append([variable_name, size, hal_name])
            elif data_config["direction"] == "output":
                if not data_config.get("expansion"):
                    if size >= 8:
                        #for bit_num in range(0, size, 8):
                        #    output_pos -= 8
                        pass
                    elif size > 1:
                        #output_pos -= size
                        pass
                    else:
                        #output_pos -= 1
                        pass
                    self.iface_out.append([variable_name, size, hal_name])
        """

        self.builds_md()
        self.halgraph_png()
        self.config_md()
        self.axis_md()
        self.pins_md()
        self.signals_md()
        self.json_md()
        self.linuxcnc_md()
        self.readme_md()
        self.index_html()

    def halgraph_png(self):
        try:
            ini_path = os.path.join(self.project.config["output_path"], "LinuxCNC", "rio.ini")
            svg_path = os.path.join(self.doc_path, "halgraph.png")
            graph = halgraph.HalGraph()
            svg_data = graph.png(ini_path)
            if svg_data:
                open(svg_path, "wb").write(svg_data)
        except Exception as error:
            print(f"WARING: failed to write halgraph.png: {error}")

    def builds_md(self):
        output = ["# builds"]

        for plugin_instance in self.project.plugin_instances:
            if not plugin_instance.BUILDER:
                continue

            output.append(f"## {plugin_instance.title}")
            image_path = plugin_instance.image_path()
            if os.path.isfile(image_path):
                target = os.path.join(self.doc_path, f"build_{plugin_instance.NAME}.png")
                shutil.copy(image_path, target)
                image = f'<img style="float: right;" src="build_{plugin_instance.NAME}.png" height="128" />'
                output.append(image)
                output.append("")

            for command in plugin_instance.BUILDER:
                cmd = plugin_instance.builder(self.project, command)
                output.append(f"### {command}")
                output.append(f"```{cmd}```")
            output.append("")

        output.append("")
        open(os.path.join(self.doc_path, "BUILDS.md"), "w").write("\n".join(output))

    def axis_md(self):
        output = ["# Axis/Joints"]
        output.append("## Overview")
        output.append("| Axis | Joint | Plugin | Home-Seq. | Setup |")
        output.append("| --- | --- | --- | --- | --- |")
        for axis_name, axis_config in self.project.axis_dict.items():
            for joint_setup in axis_config["joints"]:
                joint = joint_setup["num"]
                plugin_instance = joint_setup["instance"]
                link = f"[{plugin_instance.NAME}](https://github.com/multigcs/riocore/blob/main/riocore/plugins/{plugin_instance.NAME}/README.md)"
                plugin = plugin_instance.instances_name
                home_seq = joint_setup["HOME_SEQUENCE"]
                setup = []
                for key in {"mode", "homeswitch", "TYPE", "MIN_LIMIT", "MAX_LIMIT", "MAX_VELOCITY", "MAX_ACCELERATION", "SCALE_OUT", "SCALE_IN"}:
                    value = joint_setup.get(key)
                    if value is None:
                        continue
                    if key in {"instance", "homeswitch"}:
                        value = value.instances_name
                    setup.append(f"{key.replace('_', '-').title()}: {value}")
                output.append(f"| {axis_name} | {joint} | {plugin} ({link}) | {home_seq} | {'<br>'.join(setup)} |")

        output.append("")
        open(os.path.join(self.doc_path, "AXIS.md"), "w").write("\n".join(output))

    def config_md(self):
        output = [f"# {self.project.config['name']}"]
        jdata = self.project.config["jdata"]

        flow_path = os.path.join(self.doc_path, "flow.png")
        if os.path.exists(flow_path):
            image = '<img align="right" height="320" src="flow.png">'
            output.append(image)

        output.append(jdata.get("description", ""))
        output.append("")
        if self.project.config["json_file"]:
            output.append(f"* Config-Path: {self.project.config['json_file']}")
        output.append(f"* Output-Path: {self.project.config['output_path']}")
        output.append("")

        self.plugin_infos = {}
        for plugin_instance in self.project.plugin_instances:
            link = f"[{plugin_instance.NAME}](https://github.com/multigcs/riocore/blob/main/riocore/plugins/{plugin_instance.NAME}/README.md)"
            info = plugin_instance.INFO
            if plugin_instance.NAME not in self.plugin_infos:
                image = "-"
                image_path = plugin_instance.image_path()
                if os.path.exists(image_path):
                    target = os.path.join(self.doc_path, f"{plugin_instance.NAME}.png")
                    shutil.copy(image_path, target)
                    image = f'<img src="{plugin_instance.NAME}.png" height="48">'
                self.plugin_infos[plugin_instance.NAME] = {
                    "info": info,
                    "instances": [],
                    "link": link,
                    "image": image,
                }
            self.plugin_infos[plugin_instance.NAME]["instances"].append(plugin_instance.instances_name)

        output.append("## Plugins")
        output.append("| Type | Info | Instance | Image |")
        output.append("| --- | --- | --- | --- |")
        for name, plugin in self.plugin_infos.items():
            output.append(f"| {plugin['link']} | {plugin['info']} | {', '.join(plugin['instances'])} | {plugin['image']} |")
        output.append("")
        open(os.path.join(self.doc_path, "CONFIG.md"), "w").write("\n".join(output))

    def struct_clean(self, data):
        # removing empty lists and dicts
        for key in list(data):
            if isinstance(data[key], list):
                for pn, part in enumerate(data[key]):
                    if isinstance(part, dict):
                        if not part:
                            riocore.log(f"DEL1 {key} {pn} {data[key][pn]}")
                            del data[key][pn]
                        else:
                            self.struct_clean(data[key][pn])
                if not data[key]:
                    del data[key]
            elif isinstance(data[key], dict):
                self.struct_clean(data[key])
                if not data[key]:
                    del data[key]
            elif data[key] is None or key in {"instance", "homeswitch"}:
                del data[key]

    def json_md(self):
        jdata = self.project.config["jdata"]
        self.struct_clean(jdata)
        output = ["# JSON-Config"]
        output.append("```")
        if "jdata_str" in self.project.config:
            output.append(self.project.config["jdata_str"])
        else:
            output.append(json.dumps(jdata, indent=4))
        output.append("```")
        output.append("")
        open(os.path.join(self.doc_path, "JSON.md"), "w").write("\n".join(output))

    def signals_md(self):
        plugin_names = {}
        for plugin_instance in self.project.plugin_instances:
            plugin_names[plugin_instance.instances_name] = plugin_instance

        output = ["# Signals"]
        output.append("| Plugin | ID | Name | Dir | Hal-Pin | Type | Description |")
        output.append("| --- | --- | --- | --- | --- | --- | --- |")

        last_plugin = ""
        last_type = ""
        for plugin_type in self.plugin_infos:
            for instances_name in sorted(plugin_names):
                plugin_instance = plugin_names[instances_name]
                if plugin_type != plugin_instance.NAME:
                    continue
                for signal_name, signal_config in plugin_instance.signals().items():
                    userconfig = signal_config.get("userconfig") or {}
                    halname = signal_config.get("halname") or ""
                    direction = signal_config.get("direction")
                    description = signal_config.get("description") or ""
                    net = userconfig.get("net") or ""
                    setp = userconfig.get("setp")
                    arrow = "<-"
                    stype = ""
                    pname = ""
                    ptype = ""
                    if direction == "input":
                        arrow = "->"
                    stype = ""
                    if net:
                        stype = "net"
                    elif setp:
                        arrow = "<-"
                        stype = "setp"
                        net = setp
                    else:
                        net = ""
                    if not net:
                        continue

                    if last_type != plugin_instance.NAME:
                        ptype = plugin_instance.NAME
                    if instances_name != last_plugin:
                        pname = instances_name

                    output.append(f"| {ptype} | {pname} | {halname} | {arrow} | {net} | {stype} | {description} |")

                    last_plugin = instances_name
                    last_type = plugin_instance.NAME

        output.append("")
        open(os.path.join(self.doc_path, "SIGNALS.md"), "w").write("\n".join(output))

    def pins_md(self):
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

        output = ["# Pins"]
        output.append("| Plugin | ID | Name | Board | Pin | Alias |")
        output.append("| --- | --- | --- | --- | --- | --- |")

        plugin_names = {}
        for plugin_instance in self.project.plugin_instances:
            plugin_names[plugin_instance.instances_name] = plugin_instance

        last_plugin = ""
        last_type = ""
        for plugin_type in self.plugin_infos:
            for instances_name in sorted(plugin_names):
                plugin_instance = plugin_names[instances_name]
                if plugin_type != plugin_instance.NAME:
                    continue
                for pin_name, pin_config in plugin_instance.pins().items():
                    row = []
                    pname = ""
                    ptype = ""

                    if last_type != plugin_instance.NAME:
                        ptype = plugin_instance.NAME
                    if instances_name != last_plugin:
                        pname = instances_name

                    row.append(ptype)
                    row.append(pname)
                    row.append(pin_name)

                    if hasattr(plugin_instance, "master") and plugin_instance.master:
                        row.append(plugin_instance.master)
                    else:
                        row.append("---")

                    if "pin" not in pin_config:
                        row.append("-")
                    elif pin_config["pin"] in self.expansion_pins:
                        row.append(pin_config["pin"])
                    elif pin_config["pin"] in self.virtual_pins:
                        row.append(f"VIRT: {self.virtual_pins[pin_config['pin']]}")
                    elif pin_config["varname"] in self.linked_pins:
                        row.append(f"LINKED:: {self.linked_pins[pin_config['pin']]}")
                    else:
                        pin_real = self.pinmapping.get(pin_config["pin"], pin_config["pin"]) or ""
                        row.append(pin_real)

                    if "pin" in pin_config and pin_config.get("pin") and pin_real != pin_config["pin"]:
                        row.append(pin_config["pin"])
                    else:
                        row.append("")
                    output.append(f"| {' | '.join(row)} |")
                    last_plugin = plugin_instance.instances_name
                    last_type = plugin_instance.NAME

        output.append("")
        open(os.path.join(self.doc_path, "PINS.md"), "w").write("\n".join(output))

    def interface_md(self):
        output = ["# Interface"]
        output.append("## Host to FPGA")
        output.append("| POS | SIZE | NAME |")
        output.append("| --- | --- | --- |")
        pos = 0
        for data in self.iface_out:
            name = data[0]
            size = data[1]
            output.append(f"| {pos} | {size}{'bits' if size > 1 else 'bit'} | {name} |")
            pos += size
        output.append("")
        output.append("## FPGA to Host")
        output.append("| POS | SIZE | NAME |")
        output.append("| --- | --- | --- |")
        pos = 0
        for data in self.iface_in:
            name = data[0]
            size = data[1]
            output.append(f"| {pos} | {size}{'bits' if size > 1 else 'bit'} | {name} |")
            pos += size
        output.append("")
        open(os.path.join(self.doc_path, "INTERFACE.md"), "w").write("\n".join(output))

    def linuxcnc_md(self):
        output = ["# LinuxCNC"]
        output.append("## Hal-Graph")
        output.append("![halgraph](./halgraph.png)")
        open(os.path.join(self.doc_path, "LINUXCNC.md"), "w").write("\n".join(output))

    def index_html(self):
        output = [""]
        output.append("<html>")
        output.append("<header>")
        output.append('<script src="https://cdn.jsdelivr.net/gh/MarketingPipeline/Markdown-Tag/markdown-tag-commonmark.js"></script>')
        output.append("""<style>
body {font-family: Arial;}

/* Style the tab */
.tab {
  overflow: hidden;
  border: 1px solid #ccc;
  background-color: #f1f1f1;
}

/* Style the buttons inside the tab */
.tab button {
  background-color: inherit;
  float: left;
  border: none;
  outline: none;
  cursor: pointer;
  padding: 14px 16px;
  transition: 0.3s;
  font-size: 17px;
}

/* Change background color of buttons on hover */
.tab button:hover {
  background-color: #ddd;
}

/* Create an active/current tablink class */
.tab button.active {
  background-color: #ccc;
}

/* Style the tab content */
.tabcontent {
  display: none;
  padding: 6px 12px;
  border: 1px solid #ccc;
  border-top: none;
}
</style>""")
        output.append("</header>")
        output.append("<body>")

        sections = ("CONFIG", "AXIS", "PINS", "SIGNALS", "BUILDS", "INTERFACE", "LINUXCNC", "JSON")
        output.append('<div class="tab">')
        for section in sections:
            md_path = os.path.join(self.doc_path, f"{section}.md")
            if os.path.exists(md_path):
                output.append(f'  <button class="tablinks" onclick="openSection(event, \'{section}\')">{section}</button>')
        output.append("</div>")

        for section in sections:
            md_path = os.path.join(self.doc_path, f"{section}.md")
            if os.path.exists(md_path):
                output.append(f'<div id="{section}" class="tabcontent">')
                output.append("<github-md>")
                output.append(open(md_path).read())
                output.append("</github-md>")
                output.append("</div>")
        output.append("</body>")

        output.append("""<script>
function openSection(evt, sectionName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  document.getElementById(sectionName).style.display = "block";
  evt.currentTarget.className += " active";
}
openSection(event, \'CONFIG\');
</script>""")

        output.append("</html>")
        open(os.path.join(self.doc_path, "index.html"), "w").write("\n".join(output))

    def readme_md(self):
        output = [""]
        output.append("## Table of Contents")
        output.append("- [Config](./CONFIG.md)")
        output.append("- [Axis/Joints](./AXIS.md)")
        output.append("- [Pins](./PINS.md)")
        output.append("- [Builds](./BUILDS.md)")
        output.append("- [Interface](./INTERFACE.md)")
        output.append("- [LinuxCNC](./LINUXCNC.md)")
        output.append("")
        open(os.path.join(self.doc_path, "README.md"), "w").write("\n".join(output))
