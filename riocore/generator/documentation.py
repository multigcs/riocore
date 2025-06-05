import shutil
import os

from riocore.gui import halgraph


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
        self.readme_md()
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

    def readme_md(self):
        output = [""]

        data = self.project.config["board_data"]
        name = data["name"]

        output.append(f"# {name}")
        description = ""
        if "description" in data:
            description = data["description"]
            output.append(f"**{description}**")
        output.append("")

        if "comment" in data:
            comment = data["comment"]
            output.append(comment)
            output.append("")

        if "url" in data:
            output.append(f"* URL: [{data['url']}]({data['url']})")

        for key in ("toolchain", "family", "type", "package", "flashcmd"):
            if key in data:
                if key == "toolchain":
                    if "toolchains" in data:
                        toolchains = []
                        for toolchain in data["toolchains"]:
                            if toolchain == data[key]:
                                continue
                            toolchains.append(f"[{toolchain}](https://github.com/multigcs/riocore/blob/main/riocore/generator/toolchains/{toolchain}/README.md)")
                        output.append(f"* {key.title()}: [{data[key]}](https://github.com/multigcs/riocore/blob/main/riocore/generator/toolchains/{data[key]}/README.md) ({', '.join(toolchains)})")
                    else:
                        output.append(f"* {key.title()}: [{data[key]}](https://github.com/multigcs/riocore/blob/main/riocore/generator/toolchains/{data[key]}/README.md)")
                else:
                    output.append(f"* {key.title()}: {data[key]}")

        if "clock" in data:
            speed_mhz = float(data["clock"]["speed"]) / 1000000
            if "osc" in data["clock"]:
                osc_mhz = float(data["clock"]["osc"]) / 1000000
                output.append(f"* Clock: {osc_mhz:0.3f}Mhz -> PLL -> {speed_mhz:0.3f}Mhz (Pin:{data['clock']['pin']})")
            else:
                output.append(f"* Clock: {speed_mhz:0.3f}Mhz (Pin:{data['clock']['pin']})")
        output.append("")

        img_path = os.path.join(self.project.config["riocore_path"], "boards", name, "board.png")
        if os.path.isfile(img_path):
            output.append("![board.png](board.png)")
            output.append("")
            target = os.path.join(self.doc_path, "board.png")
            shutil.copy(img_path, target)

        output.append("")
        open(os.path.join(self.doc_path, "README.md"), "w").write("\n".join(output))

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
            #self.project.config["pinlists"][plugin_instance.instances_name] = {}
            for pin_name, pin_config in plugin_instance.pins().items():
                if "pin" not in pin_config:
                    print("NONE")
                elif pin_config["pin"] in self.expansion_pins:
                    print("EXP")
                elif pin_config["pin"] in self.virtual_pins:
                    print("VIRT")
                elif pin_config["varname"] in self.linked_pins:
                    print("LINKED")
                else:
                    pin_real = self.pinmapping.get(pin_config["pin"], pin_config["pin"])

                    row = []
                    if plugin_instance.instances_name != last_plugin:
                        row.append(plugin_instance.instances_name)
                    else:
                        row.append("")
                    row.append(pin_name)
                    row.append(pin_real)
                    if pin_real != pin_config['pin']:
                        row.append(pin_config['pin'])
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
        output.append("</header>")
        output.append("<body>")
        for md in ("README.md", "PINS.md", "INTERFACE.md", "LINUXCNC.md"):
            output.append("<github-md>")
            output.append(open(os.path.join(self.doc_path, md), "r").read())
            output.append("</github-md>")
            output.append("<HR/>")
        output.append("</body>")
        output.append("</html>")
        open(os.path.join(self.doc_path, "index.html"), "w").write("\n".join(output))
