import shutil
import json
import os

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
        output_pos = self.project.buffer_size

        size = 32
        self.iface_out.append(["RX_HEADER", size])
        self.iface_in.append(["TX_HEADER", size])
        self.iface_in.append(["TITMESTAMP", size])

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
            for bit_num in range(0, size, 8):
                output_pos -= 8
            self.iface_out.append([variable_name, size])
            variable_name = "MULTIPLEXED_OUTPUT_ID"
            size = 8
            for bit_num in range(0, size, 8):
                output_pos -= 8
            self.iface_out.append([variable_name, size])

        for size, plugin_instance, data_name, data_config in self.project.get_interface_data():
            multiplexed = data_config.get("multiplexed", False)
            if multiplexed:
                continue
            variable_name = data_config["variable"]
            if data_config["direction"] == "input":
                if not data_config.get("expansion"):
                    self.iface_in.append([variable_name, size])
            elif data_config["direction"] == "output":
                if not data_config.get("expansion"):
                    if size >= 8:
                        for bit_num in range(0, size, 8):
                            output_pos -= 8
                    elif size > 1:
                        output_pos -= size
                    else:
                        output_pos -= 1
                    self.iface_out.append([variable_name, size])

        self.halgraph_png()
        self.interface_md()
        self.config_md()
        self.pins_md()
        self.linuxcnc_md()
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

    def config_md(self):
        output = [f'# {self.project.config["name"]}']
        jdata = self.project.config["jdata"]
        boardcfg = jdata.get("boardcfg", "")
        board_link = f"[{boardcfg}](https://github.com/multigcs/riocore/blob/main/riocore/boards/{boardcfg}/README.md)"

        img_path = os.path.join(riocore_path, "boards", boardcfg, "board.png")
        if os.path.exists(img_path):
            target = os.path.join(self.doc_path, "board.png")
            shutil.copy(img_path, target)
            image = '<img align="right" height="320" src="board.png">'
            output.append(image)

        output.append(jdata.get("description", ""))
        output.append("")
        output.append(f"* Board: {board_link}")
        output.append(f'* Config-Path: {self.project.config["json_file"]}')
        output.append(f'* Output-Path: {self.project.config["output_path"]}')
        output.append(f'* Toolchain: {self.project.config["toolchain"]}')
        output.append(f'* Protocol: {jdata.get("protocol", "")}')

        output.append("")

        output.append("## Axis/Joints")
        output.append("| Axis | Joint | Plugin | Home-Seq. |")
        output.append("| --- | --- | --- | --- |")
        for axis_name, axis_config in self.project.axis_dict.items():
            joints = axis_config["joints"]
            for joint, joint_setup in joints.items():
                plugin_instance = joint_setup["plugin_instance"]
                link = f"[{plugin_instance.NAME}](https://github.com/multigcs/riocore/blob/main/riocore/plugins/{plugin_instance.NAME}/README.md)"
                plugin = plugin_instance.instances_name
                home_seq = joint_setup["HOME_SEQUENCE"]
                output.append(f"| {axis_name} | {joint} | {plugin} ({link}) | {home_seq} | ")
        output.append("")

        plugin_infos = {}
        for plugin_instance in self.project.plugin_instances:
            link = f"[{plugin_instance.NAME}](https://github.com/multigcs/riocore/blob/main/riocore/plugins/{plugin_instance.NAME}/README.md)"
            info = plugin_instance.INFO
            if plugin_instance.NAME not in plugin_infos:
                image = "-"
                img_path = os.path.join(riocore_path, "plugins", plugin_instance.NAME, "image.png")
                if os.path.exists(img_path):
                    target = os.path.join(self.doc_path, f"{plugin_instance.NAME}.png")
                    shutil.copy(img_path, target)
                    image = f'<img src="{plugin_instance.NAME}.png" height="48">'
                plugin_infos[plugin_instance.NAME] = {
                    "info": info,
                    "instances": [],
                    "link": link,
                    "image": image,
                }
            plugin_infos[plugin_instance.NAME]["instances"].append(plugin_instance.instances_name)

        output.append("## Plugins")
        output.append("| Type | Info | Instance | Image |")
        output.append("| --- | --- | --- | --- |")
        for name, plugin in plugin_infos.items():
            output.append(f"| {plugin['link']} | {plugin['info']} | {', '.join(plugin['instances'])} | {plugin['image']} |")
        output.append("")

        output.append("## JSON-Config")
        output.append("```")
        output.append(json.dumps(jdata, indent=4))
        output.append("```")
        output.append("")
        open(os.path.join(self.doc_path, "CONFIG.md"), "w").write("\n".join(output))

    def pins_md(self):
        self.linked_pins = []
        self.virtual_pins = []
        self.expansion_pins = []
        self.pinmapping = {}
        self.pinmapping_rev = {}
        for plugin_instance in self.project.plugin_instances:
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" in pin_config and pin_config["pin"].startswith("VIRT:"):
                    pinname = pin_config["pin"]
                    if pinname not in self.virtual_pins:
                        self.virtual_pins.append(pinname)
            for pin in plugin_instance.expansion_outputs():
                self.expansion_pins.append(pin)
            for pin in plugin_instance.expansion_inputs():
                self.expansion_pins.append(pin)

        self.slots = self.project.config["board_data"].get("slots", []) + self.project.config["jdata"].get("slots", [])
        for slot in self.slots:
            slot_name = slot.get("name")
            slot_pins = slot.get("pins", {})
            for pin_name, pin in slot_pins.items():
                if isinstance(pin, dict):
                    pin = pin["pin"]
                pin_id = f"{slot_name}:{pin_name}"
                self.pinmapping[pin_id] = pin
                self.pinmapping_rev[pin] = pin_id

        output = ["# Pins"]
        output.append("| Plugin | Name | FPGA | Alias |")
        output.append("| --- | --- | --- | --- |")

        last_plugin = ""
        for plugin_instance in self.project.plugin_instances:
            # self.project.config["pinlists"][plugin_instance.instances_name] = {}
            for pin_name, pin_config in plugin_instance.pins().items():
                row = []
                if plugin_instance.instances_name != last_plugin:
                    row.append(plugin_instance.instances_name)
                else:
                    row.append("")
                row.append(pin_name)

                if "pin" not in pin_config:
                    row.append("-")
                elif pin_config["pin"] in self.expansion_pins:
                    row.append(f'EXP: {self.expansion_pins[pin_config["pin"]]}')
                elif pin_config["pin"] in self.virtual_pins:
                    row.append(f'VIRT: {self.virtual_pins[pin_config["pin"]]}')
                elif pin_config["varname"] in self.linked_pins:
                    row.append(f'LINKED:: {self.linked_pins[pin_config["pin"]]}')
                else:
                    pin_real = self.pinmapping.get(pin_config["pin"], pin_config["pin"])
                    row.append(pin_real)

                if "pin" in pin_config and pin_real != pin_config["pin"]:
                    row.append(pin_config["pin"])
                else:
                    row.append("")
                output.append(f"| {' | '.join(row)} |")
                last_plugin = plugin_instance.instances_name

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

        sections = ("CONFIG", "PINS", "INTERFACE", "LINUXCNC")

        output.append('<div class="tab">')
        for section in sections:
            output.append(f'  <button class="tablinks" onclick="openSection(event, \'{section}\')">{section}</button>')
        output.append("</div>")

        for section in sections:
            output.append(f'<div id="{section}" class="tabcontent">')
            output.append("<github-md>")
            output.append(open(os.path.join(self.doc_path, f"{section}.md"), "r").read())
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
