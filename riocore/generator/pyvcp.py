import os


class pyvcp:
    def __init__(self):
        pass

    def draw_begin(self, prefix="pyvcp", vcp_pos=None):
        self.cfgxml_data = []
        self.prefix = prefix
        self.cfgxml_data.append("<pyvcp>")

    def draw_end(self):
        self.cfgxml_data.append('<label><text>""</text><width>30</width></label>')
        self.cfgxml_data.append("</pyvcp>")

    def xml(self):
        return "\n".join(self.cfgxml_data)

    def save(self, configuration_path):
        xml_filename = os.path.join(configuration_path, "rio-gui.xml")
        open(xml_filename, "w").write("\n".join(self.cfgxml_data))

    def draw_tabs_begin(self, names):
        self.cfgxml_data.append("<tabs>")
        self.cfgxml_data.append(f"    <names>{names}</names>")

    def draw_tabs_end(self):
        self.cfgxml_data.append("</tabs>")

    def draw_tab_begin(self, name):
        self.cfgxml_data.append("    <vbox>")

    def draw_tab_end(self):
        self.cfgxml_data.append("    </vbox>")

    def draw_vbox_begin(self):
        self.cfgxml_data.append("    <vbox>")
        self.cfgxml_data.append("      <relief>RIDGE</relief>")
        self.cfgxml_data.append("      <bd>2</bd>")

    def draw_vbox_end(self):
        self.cfgxml_data.append("    </vbox>")

    def draw_hbox_begin(self):
        self.cfgxml_data.append("    <hbox>")
        self.cfgxml_data.append("      <relief>RIDGE</relief>")
        self.cfgxml_data.append("      <bd>2</bd>")

    def draw_hbox_end(self):
        self.cfgxml_data.append("    </hbox>")

    def draw_frame_begin(self, name=None):
        self.cfgxml_data.append('  <labelframe text="MDI-Commands">')
        self.cfgxml_data.append("    <relief>RAISED</relief>")
        self.cfgxml_data.append('    <font>("Helvetica", 10)</font>')

    def draw_frame_end(self):
        self.cfgxml_data.append("  </labelframe>")

    def draw_scale(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_initval = setup.get("initval", 0)
        resolution = setup.get("resolution", 0.1)
        self.cfgxml_data.append("  <hbox>")
        self.cfgxml_data.append("    <relief>RAISED</relief>")
        self.cfgxml_data.append("    <bd>2</bd>")
        self.cfgxml_data.append("    <scale>")
        self.cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        self.cfgxml_data.append(f"      <resolution>{resolution}</resolution>")
        self.cfgxml_data.append("      <orient>HORIZONTAL</orient>")
        self.cfgxml_data.append(f"      <initval>{display_initval}</initval>")
        self.cfgxml_data.append(f"      <min_>{display_min}</min_>")
        self.cfgxml_data.append(f"      <max_>{display_max}</max_>")
        self.cfgxml_data.append("      <param_pin>1</param_pin>")
        self.cfgxml_data.append("    </scale>")
        self.cfgxml_data.append("    <label>")
        self.cfgxml_data.append(f'      <text>"{title}"</text>')
        self.cfgxml_data.append("    </label>")
        self.cfgxml_data.append("  </hbox>")
        return f"{self.prefix}.{halpin}-f"

    def draw_fselect(self, name, halpin, setup={}):
        title = setup.get("title", name)
        values = setup.get("values", {"v0": 0, "v1": 1})
        display_min = 0
        display_max = len(values) - 1
        display_initval = setup.get("initval", 0)
        resolution = 1
        legends = list(values.keys())
        self.cfgxml_data.append(f'  <labelframe text="{title}">')
        self.cfgxml_data.append("   <vbox>")
        self.cfgxml_data.append("    <relief>RAISED</relief>")
        self.cfgxml_data.append("    <bd>2</bd>")
        self.cfgxml_data.append("    <multilabel>")
        self.cfgxml_data.append(f"     <legends>{legends}</legends>")
        self.cfgxml_data.append(f'     <halpin>"{halpin}-label"</halpin>')
        self.cfgxml_data.append('     <font>("Helvetica", 12)</font>')
        self.cfgxml_data.append('     <bg>"black"</bg>')
        self.cfgxml_data.append('     <fg>"yellow"</fg>')
        self.cfgxml_data.append("    </multilabel>")
        self.cfgxml_data.append("    <scale>")
        self.cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        self.cfgxml_data.append(f"      <resolution>{resolution}</resolution>")
        self.cfgxml_data.append("      <orient>HORIZONTAL</orient>")
        self.cfgxml_data.append(f"      <initval>{display_initval}</initval>")
        self.cfgxml_data.append(f"      <min_>{display_min}</min_>")
        self.cfgxml_data.append(f"      <max_>{display_max}</max_>")
        self.cfgxml_data.append("      <param_pin>1</param_pin>")
        self.cfgxml_data.append("    </scale>")
        self.cfgxml_data.append("   </vbox>")
        self.cfgxml_data.append("  </labelframe>")
        return f"{self.prefix}.{halpin}"

    def draw_spinbox(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_initval = setup.get("initval", 0.0)
        resolution = setup.get("resolution", 0.1)
        self.cfgxml_data.append("  <hbox>")
        self.cfgxml_data.append("    <relief>RAISED</relief>")
        self.cfgxml_data.append("    <bd>2</bd>")
        self.cfgxml_data.append("    <spinbox>")
        self.cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        self.cfgxml_data.append(f"      <resolution>{resolution}</resolution>")
        self.cfgxml_data.append(f"      <initval>{display_initval}</initval>")
        self.cfgxml_data.append(f"      <min_>{display_min}</min_>")
        self.cfgxml_data.append(f"      <max_>{display_max}</max_>")
        self.cfgxml_data.append("      <param_pin>1</param_pin>")
        self.cfgxml_data.append("    </spinbox>")
        self.cfgxml_data.append("    <label>")
        self.cfgxml_data.append(f'      <text>"{title}"</text>')
        self.cfgxml_data.append("    </label>")
        self.cfgxml_data.append("  </hbox>")
        return f"{self.prefix}.{halpin}"

    def draw_jogwheel(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        resolution = setup.get("resolution", 0.1)
        size = setup.get("size", 200)
        cpr = setup.get("cpr", 50)
        self.cfgxml_data.append("    <jogwheel>")
        self.cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        self.cfgxml_data.append(f'      <text>"{title}"</text>')
        self.cfgxml_data.append(f"      <size>{size}</size>")
        self.cfgxml_data.append(f"      <cpr>{cpr}</cpr>")
        self.cfgxml_data.append(f"      <resolution>{resolution}</resolution>")
        self.cfgxml_data.append("      <initval>0</initval>")
        self.cfgxml_data.append(f"      <min_>{display_min}</min_>")
        self.cfgxml_data.append(f"      <max_>{display_max}</max_>")
        self.cfgxml_data.append("      <param_pin>1</param_pin>")
        self.cfgxml_data.append("    </jogwheel>")
        return f"{self.prefix}.{halpin}"

    def draw_dial(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        resolution = setup.get("resolution", 0.1)
        dialcolor = setup.get("dialcolor", "yellow")
        edgecolor = setup.get("edgecolor", "green")
        dotcolor = setup.get("dotcolor", "black")
        size = setup.get("size", 200)
        cpr = setup.get("cpr", 50)
        self.cfgxml_data.append("    <dial>")
        self.cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        self.cfgxml_data.append(f'      <text>"{title}"</text>')
        self.cfgxml_data.append(f"      <size>{size}</size>")
        self.cfgxml_data.append(f"      <cpr>{cpr}</cpr>")
        self.cfgxml_data.append(f"      <resolution>{resolution}</resolution>")
        self.cfgxml_data.append(f'      <dialcolor>"{dialcolor}"</dialcolor>')
        self.cfgxml_data.append(f'      <edgecolor>"{edgecolor}"</edgecolor>')
        self.cfgxml_data.append(f'      <dotcolor>"{dotcolor}"</dotcolor>')
        self.cfgxml_data.append("      <initval>0</initval>")
        self.cfgxml_data.append(f"      <min_>{display_min}</min_>")
        self.cfgxml_data.append(f"      <max_>{display_max}</max_>")
        self.cfgxml_data.append("      <param_pin>1</param_pin>")
        self.cfgxml_data.append("    </dial>")
        return f"{self.prefix}.{halpin}"

    def draw_meter(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_subtext = setup.get("subtext", setup.get("unit", ""))
        display_region = setup.get("region", [])
        display_size = setup.get("size", 150)
        self.cfgxml_data.append("  <hbox>")
        self.cfgxml_data.append("    <relief>RAISED</relief>")
        self.cfgxml_data.append("    <bd>2</bd>")
        self.cfgxml_data.append("  <meter>")
        self.cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        self.cfgxml_data.append(f'      <text>"{title}"</text>')
        self.cfgxml_data.append(f'      <subtext>"{display_subtext}"</subtext>')
        self.cfgxml_data.append(f"      <size>{display_size}</size>")
        self.cfgxml_data.append(f"      <min_>{display_min}</min_>")
        self.cfgxml_data.append(f"      <max_>{display_max}</max_>")
        for rnum, region in enumerate(display_region):
            self.cfgxml_data.append(f'      <region{rnum + 1}>({region[0]},{region[1]},"{region[2]}")</region{rnum + 1}>')
        self.cfgxml_data.append("    </meter>")
        self.cfgxml_data.append("  </hbox>")
        return f"{self.prefix}.{halpin}"

    def draw_bar(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_range = setup.get("range", [])
        display_format = setup.get("format", "05d")
        display_fillcolor = setup.get("fillcolor", "red")
        display_bgcolor = setup.get("fillcolor", "grey")
        self.cfgxml_data.append("  <hbox>")
        self.cfgxml_data.append("    <relief>RAISED</relief>")
        self.cfgxml_data.append("    <bd>2</bd>")
        self.cfgxml_data.append("    <label>")
        self.cfgxml_data.append(f'      <text>"{title}"</text>')
        self.cfgxml_data.append("    </label>")
        self.cfgxml_data.append("    <bar>")
        self.cfgxml_data.append(f'    <halpin>"{halpin}"</halpin>')
        self.cfgxml_data.append(f"    <min_>{display_min}</min_>")
        self.cfgxml_data.append(f"    <max_>{display_max}</max_>")
        self.cfgxml_data.append(f'    <format>"{display_format}"</format>')
        self.cfgxml_data.append(f'    <bgcolor>"{display_bgcolor}"</bgcolor>')
        self.cfgxml_data.append(f'    <fillcolor>"{display_fillcolor}"</fillcolor>')
        for rnum, brange in enumerate(display_range):
            self.cfgxml_data.append(f'    <range{rnum + 1}>({brange[0]},{brange[1]},"{brange[2]}")</range{rnum + 1}>')
        self.cfgxml_data.append("    </bar>")
        self.cfgxml_data.append("  </hbox>")
        return f"{self.prefix}.{halpin}"

    def draw_number_u32(self, name, halpin, setup={}):
        return self.draw_number(name, halpin, hal_type="u32", setup=setup)

    def draw_number_s32(self, name, halpin, setup={}):
        return self.draw_number(name, halpin, hal_type="s32", setup=setup)

    def draw_number(self, name, halpin, hal_type="float", setup={}):
        title = setup.get("title", name)
        if hal_type == "float":
            display_format = setup.get("format", "07.2f")
            element = "number"
        else:
            display_format = setup.get("format", "d")
            element = hal_type
        unit = setup.get("unit")
        self.cfgxml_data.append("  <hbox>")
        self.cfgxml_data.append("    <relief>RAISED</relief>")
        self.cfgxml_data.append("    <bd>2</bd>")
        self.cfgxml_data.append("    <label>")
        self.cfgxml_data.append(f'      <text>"{title:10s}"</text>')
        self.cfgxml_data.append('      <font>("Helvetica",9)</font>')
        self.cfgxml_data.append("      <width>13</width>")
        self.cfgxml_data.append("    </label>")
        self.cfgxml_data.append(f"    <{element}>")
        self.cfgxml_data.append(f'        <halpin>"{halpin}"</halpin>')
        self.cfgxml_data.append('        <font>("Helvetica",14)</font>')
        self.cfgxml_data.append(f'        <format>"{display_format}"</format>')
        # self.cfgxml_data.append(f'        <width>13</width>')
        self.cfgxml_data.append("      <justify>LEFT</justify>")
        self.cfgxml_data.append(f"    </{element}>")
        if unit:
            self.cfgxml_data.append("    <label>")
            self.cfgxml_data.append('        <font>("Helvetica",14)</font>')
            self.cfgxml_data.append(f'      <text>"{unit}"</text>')
            self.cfgxml_data.append("    </label>")
        self.cfgxml_data.append("  </hbox>")
        return f"{self.prefix}.{halpin}"

    def draw_checkbutton(self, name, halpin, setup={}):
        title = setup.get("title", name)
        self.cfgxml_data.append("  <hbox>")
        self.cfgxml_data.append("    <relief>RAISED</relief>")
        self.cfgxml_data.append("    <bd>2</bd>")
        self.cfgxml_data.append("    <label>")
        self.cfgxml_data.append(f'      <text>"{title:10s}"</text>')
        self.cfgxml_data.append('      <font>("Helvetica",9)</font>')
        self.cfgxml_data.append("      <width>13</width>")
        self.cfgxml_data.append("    </label>")
        self.cfgxml_data.append("    <checkbutton>")
        self.cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        # self.cfgxml_data.append(f'      <text>"{title}"</text>')
        self.cfgxml_data.append("    </checkbutton>")
        self.cfgxml_data.append("  </hbox>")
        return f"{self.prefix}.{halpin}"

    def draw_checkbutton_rgb(self, name, halpin_g, halpin_b, halpin_r, setup={}):
        title = setup.get("title", name)
        self.cfgxml_data.append("  <hbox>")
        self.cfgxml_data.append("    <relief>RAISED</relief>")
        self.cfgxml_data.append("    <bd>2</bd>")
        self.cfgxml_data.append("    <label>")
        self.cfgxml_data.append(f'      <text>"{title}"</text>')
        self.cfgxml_data.append("    </label>")
        self.cfgxml_data.append("    <checkbutton>")
        self.cfgxml_data.append(f'      <halpin>"{halpin_g}"</halpin>')
        self.cfgxml_data.append('      <text>"G"</text>')
        self.cfgxml_data.append("    </checkbutton>")
        self.cfgxml_data.append("    <checkbutton>")
        self.cfgxml_data.append(f'      <halpin>"{halpin_b}"</halpin>')
        self.cfgxml_data.append('      <text>"B"</text>')
        self.cfgxml_data.append("    </checkbutton>")
        self.cfgxml_data.append("    <checkbutton>")
        self.cfgxml_data.append(f'      <halpin>"{halpin_r}"</halpin>')
        self.cfgxml_data.append('      <text>"R"</text>')
        self.cfgxml_data.append("    </checkbutton>")
        self.cfgxml_data.append("  </hbox>")
        return f"{self.prefix}.{halpin_g}"

    def draw_led(self, name, halpin, setup={}):
        title = setup.get("title", name)
        size = setup.get("size", 16)
        color = setup.get("color")
        self.cfgxml_data.append("  <hbox>")
        self.cfgxml_data.append("    <relief>RAISED</relief>")
        self.cfgxml_data.append("    <bd>2</bd>")
        self.cfgxml_data.append("    <label>")
        self.cfgxml_data.append(f'      <text>"{title:10s}"</text>')
        self.cfgxml_data.append('      <font>("Helvetica",9)</font>')
        self.cfgxml_data.append("      <width>13</width>")
        self.cfgxml_data.append("    </label>")
        self.cfgxml_data.append("    <led>")
        self.cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        self.cfgxml_data.append(f"      <size>{size}</size>")
        if color:
            self.cfgxml_data.append(f'      <on_color>"{color}"</on_color>')
        elif halpin.endswith(".R"):
            self.cfgxml_data.append('      <on_color>"red"</on_color>')
        elif halpin.endswith(".B"):
            self.cfgxml_data.append('      <on_color>"blue"</on_color>')
        else:
            self.cfgxml_data.append('      <on_color>"yellow"</on_color>')
        self.cfgxml_data.append('      <off_color>"red"</off_color>')
        self.cfgxml_data.append("    </led>")
        self.cfgxml_data.append("  </hbox>")
        return f"{self.prefix}.{halpin}"

    def draw_rectled(self, name, halpin, setup={}):
        title = setup.get("title", name)
        width = setup.get("width", 16)
        height = setup.get("height", 16)
        color = setup.get("color")
        self.cfgxml_data.append("  <hbox>")
        self.cfgxml_data.append("    <relief>RAISED</relief>")
        self.cfgxml_data.append("    <bd>2</bd>")
        self.cfgxml_data.append("    <label>")
        self.cfgxml_data.append(f'      <text>"{title:10s}"</text>')
        self.cfgxml_data.append('      <font>("Helvetica",9)</font>')
        self.cfgxml_data.append("      <width>13</width>")
        self.cfgxml_data.append("    </label>")
        self.cfgxml_data.append("    <led>")
        self.cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        self.cfgxml_data.append(f"      <width>{width}</width>")
        self.cfgxml_data.append(f"      <height>{height}</height>")
        if color:
            self.cfgxml_data.append(f'      <on_color>"{color}"</on_color>')
        elif halpin.endswith(".R"):
            self.cfgxml_data.append('      <on_color>"red"</on_color>')
        elif halpin.endswith(".B"):
            self.cfgxml_data.append('      <on_color>"blue"</on_color>')
        else:
            self.cfgxml_data.append('      <on_color>"green"</on_color>')
        self.cfgxml_data.append('      <off_color>"black"</off_color>')
        self.cfgxml_data.append("    </led>")
        self.cfgxml_data.append("  </hbox>")
        return f"{self.prefix}.{halpin}"

    def draw_button(self, name, halpin, setup={}):
        title = setup.get("title", name)
        self.cfgxml_data.append("  <button>")
        self.cfgxml_data.append("    <relief>RAISED</relief>")
        self.cfgxml_data.append("    <bd>3</bd>")
        self.cfgxml_data.append(f'    <halpin>"{halpin}"</halpin>')
        self.cfgxml_data.append(f'    <text>"{title}"</text>')
        self.cfgxml_data.append('    <font>("Helvetica", 12)</font>')
        self.cfgxml_data.append("  </button>")
        return f"{self.prefix}.{halpin}"

    def draw_multilabel(self, name, halpin, setup={}):
        legends = setup.get("legends", ["LABEL1", "LABEL2", "LABEL3", "LABEL4"])
        self.cfgxml_data.append("  <multilabel>")
        self.cfgxml_data.append(f"    <legends>{legends}</legends>")
        self.cfgxml_data.append(f'    <halpin>"{halpin}"</halpin>')
        self.cfgxml_data.append('    <font>("Helvetica", 12)</font>')
        self.cfgxml_data.append('    <bg>"black"</bg>')
        self.cfgxml_data.append('    <fg>"yellow"</fg>')
        self.cfgxml_data.append("  </multilabel>")
        return f"{self.prefix}.{halpin}"
