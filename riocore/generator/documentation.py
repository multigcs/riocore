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

        self.interface_html()
        self.interface_md()
        self.readme_md()
        self.halgraph_png()
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

    def index_html(self):
        output = [""]
        """
        output.append(f"<h2>LinuxCNC</h2>")
        output.append(f"<br />")
        output.append(f'<a href="../LinuxCNC/rio.ini">rio.ini</a><br />')
        output.append(f'<a href="../LinuxCNC/rio.hal">rio.hal</a><br />')
        output.append(f"<br />")
        output.append(f"<br />")

        output.append(f"<h2>Gateware</h2>")
        output.append(f"<br />")
        output.append(f'<a href="../Gateware/rio.v">rio.v</a><br />')
        output.append(f"<br />")
        output.append(f"<br />")
        """

        data = self.project.config["board_data"]
        name = data["name"]
        output.append(f"<h2>Board: {name}</h2>")
        description = ""
        if "description" in data:
            description = data["description"]
            output.append(f"<b>{description}</b><br />")
        output.append("<br />")

        if "comment" in data:
            comment = data["comment"]
            output.append(f"{comment}<br />")
            output.append("<br />")

        if "url" in data:
            output.append(f'* URL: <a href="{data["url"]}">{data["url"]}</a><br />')

        for key in ("toolchain", "family", "type", "package", "flashcmd"):
            if key in data:
                if key == "toolchain":
                    if "toolchains" in data:
                        toolchains = []
                        for toolchain in data["toolchains"]:
                            if toolchain == data[key]:
                                continue
                            toolchains.append(f'<a href="https://github.com/multigcs/riocore/blob/main/riocore/generator/toolchains/{toolchain}/README.md">{toolchain}</a>')
                        output.append(
                            f'* {key.title()}: <a href="https://github.com/multigcs/riocore/blob/main/riocore/generator/toolchains/{data[key]}/README.md">{data[key]}</a> ({", ".join(toolchains)})<br />'
                        )
                    else:
                        output.append(f"* {key.title()}: [{data[key]}]()")
                        output.append(f'* {key.title()}: <a href="https://github.com/multigcs/riocore/blob/main/riocore/generator/toolchains/{data[key]}/README.md">{data[key]}</a><br />')
                else:
                    output.append(f"* {key.title()}: {data[key]}<br />")

        if "clock" in data:
            speed_mhz = float(data["clock"]["speed"]) / 1000000
            if "osc" in data["clock"]:
                osc_mhz = float(data["clock"]["osc"]) / 1000000
                output.append(f"* Clock: {osc_mhz:0.3f}Mhz -> PLL -> {speed_mhz:0.3f}Mhz (Pin:{data['clock']['pin']})<br />")
            else:
                output.append(f"* Clock: {speed_mhz:0.3f}Mhz (Pin:{data['clock']['pin']})<br />")
        output.append("<br />")

        img_path = os.path.join(self.project.config["riocore_path"], "boards", name, "board.png")
        if os.path.isfile(img_path):
            output.append('<img src="board.png" /><br />')
            output.append("<br />")
            target = os.path.join(self.doc_path, "board.png")
            shutil.copy(img_path, target)

        output.append("<br />")
        open(os.path.join(self.doc_path, "index.html"), "w").write("\n".join(output))

    def interface_html(self):
        output = []
        output.append("<h1>Interface</h1>")
        output.append("<table width='100%'>")
        output.append("<tr><td valign='top'>")
        output.append("<h3>FPGA to Host</h3>")
        output.append("<table width='100%'>")
        pos = 0
        for data in self.iface_in:
            name = data[0]
            size = data[1]
            output.append(
                f"<tr><td style='padding: 1px; border: 1px solid black;' align='left'>{pos}</td><td style='padding: 3px; border: 1px solid black;'>{size}{'bits' if size > 1 else 'bit'}</td><td style='padding: 3px; border: 1px solid black;' align='center'>{name}</td></tr>"
            )
            pos += size
        output.append("</table>")
        output.append("</td><td valign='top'>")
        output.append("<h3>Host to FPGA</h3>")
        output.append("<table width='100%'>")
        pos = 0
        for data in self.iface_out:
            name = data[0]
            size = data[1]
            output.append(
                f"<tr><td style='padding: 1px; border: 1px solid black;' align='left'>{pos}</td><td style='padding: 3px; border: 1px solid black;'>{size}{'bits' if size > 1 else 'bit'}</td><td style='padding: 3px; border: 1px solid black;' align='center'>{name}</td></tr>"
            )
            pos += size
        output.append("</table>")
        output.append("</td></tr>")
        output.append("</table>")

        open(os.path.join(self.doc_path, "interface.html"), "w").write("\n".join(output))

    def interface_md(self):
        output = []
        output.append("# Interface")
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
        output.append("## FPGA to Host")
        output.append("| POS | SIZE | NAME |")
        output.append("| --- | --- | --- |")
        pos = 0
        for data in self.iface_out:
            name = data[0]
            size = data[1]
            output.append(f"| {pos} | {size}{'bits' if size > 1 else 'bit'} | {name} |")
            pos += size
        output.append("")

        open(os.path.join(self.doc_path, "INTERFACE.md"), "w").write("\n".join(output))
