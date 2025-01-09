import os


class pyvcp:
    def draw_begin(self, configuration_path, prefix="pyvcp"):
        self.configuration_path = configuration_path
        self.prefix = prefix
        cfgxml_data = []
        cfgxml_data.append("<pyvcp>")
        return cfgxml_data

    def draw_end(self):
        cfgxml_data = []
        cfgxml_data.append('<label><text>""</text><width>30</width></label>')
        cfgxml_data.append("</pyvcp>")
        return cfgxml_data

    def save(self, cfgxml_data):
        xml_filename = os.path.join(self.configuration_path, "rio-gui.xml")
        open(xml_filename, "w").write("\n".join(cfgxml_data))

    def draw_tabs_begin(self, names):
        cfgxml_data = []
        cfgxml_data.append("<tabs>")
        cfgxml_data.append(f"    <names>{names}</names>")
        return cfgxml_data

    def draw_tabs_end(self):
        cfgxml_data = []
        cfgxml_data.append("</tabs>")
        return cfgxml_data

    def draw_tab_begin(self, name):
        cfgxml_data = []
        cfgxml_data.append("    <vbox>")
        return cfgxml_data

    def draw_tab_end(self):
        cfgxml_data = []
        cfgxml_data.append("    </vbox>")
        return cfgxml_data

    def draw_vbox_begin(self):
        cfgxml_data = []
        cfgxml_data.append("    <vbox>")
        cfgxml_data.append("      <relief>RIDGE</relief>")
        cfgxml_data.append("      <bd>2</bd>")
        return cfgxml_data

    def draw_vbox_end(self):
        cfgxml_data = []
        cfgxml_data.append("    </vbox>")
        return cfgxml_data

    def draw_hbox_begin(self):
        cfgxml_data = []
        cfgxml_data.append("    <hbox>")
        cfgxml_data.append("      <relief>RIDGE</relief>")
        cfgxml_data.append("      <bd>2</bd>")
        return cfgxml_data

    def draw_hbox_end(self):
        cfgxml_data = []
        cfgxml_data.append("    </hbox>")
        return cfgxml_data

    def draw_frame_begin(self, name=None):
        cfgxml_data = []
        cfgxml_data.append('  <labelframe text="MDI-Commands">')
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append('    <font>("Helvetica", 10)</font>')
        return cfgxml_data

    def draw_frame_end(self):
        cfgxml_data = []
        cfgxml_data.append("  </labelframe>")
        return cfgxml_data

    def draw_scale(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_initval = setup.get("initval", 0)
        resolution = setup.get("resolution", 0.1)
        cfgxml_data = []
        cfgxml_data.append("  <hbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("    <scale>")
        cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        cfgxml_data.append(f"      <resolution>{resolution}</resolution>")
        cfgxml_data.append("      <orient>HORIZONTAL</orient>")
        cfgxml_data.append(f"      <initval>{display_initval}</initval>")
        cfgxml_data.append(f"      <min_>{display_min}</min_>")
        cfgxml_data.append(f"      <max_>{display_max}</max_>")
        cfgxml_data.append("      <param_pin>1</param_pin>")
        cfgxml_data.append("    </scale>")
        cfgxml_data.append("    <label>")
        cfgxml_data.append(f'      <text>"{title}"</text>')
        cfgxml_data.append("    </label>")
        cfgxml_data.append("  </hbox>")
        return (f"{self.prefix}.{halpin}-f", cfgxml_data)

    def draw_fselect(self, name, halpin, setup={}):
        title = setup.get("title", name)
        values = setup.get("values", {"v0": 0, "v1": 1})
        display_min = 0
        display_max = len(values) - 1
        display_initval = setup.get("initval", 0)
        resolution = 1
        legends = list(values.keys())
        cfgxml_data = []
        cfgxml_data.append(f'  <labelframe text="{title}">')
        cfgxml_data.append("   <vbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("    <multilabel>")
        cfgxml_data.append(f"     <legends>{legends}</legends>")
        cfgxml_data.append(f'     <halpin>"{halpin}-label"</halpin>')
        cfgxml_data.append('     <font>("Helvetica", 12)</font>')
        cfgxml_data.append('     <bg>"black"</bg>')
        cfgxml_data.append('     <fg>"yellow"</fg>')
        cfgxml_data.append("    </multilabel>")
        cfgxml_data.append("    <scale>")
        cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        cfgxml_data.append(f"      <resolution>{resolution}</resolution>")
        cfgxml_data.append("      <orient>HORIZONTAL</orient>")
        cfgxml_data.append(f"      <initval>{display_initval}</initval>")
        cfgxml_data.append(f"      <min_>{display_min}</min_>")
        cfgxml_data.append(f"      <max_>{display_max}</max_>")
        cfgxml_data.append("      <param_pin>1</param_pin>")
        cfgxml_data.append("    </scale>")
        cfgxml_data.append("   </vbox>")
        cfgxml_data.append("  </labelframe>")
        return (f"{self.prefix}.{halpin}", cfgxml_data)

    def draw_spinbox(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_initval = setup.get("initval", 0.0)
        resolution = setup.get("resolution", 0.1)
        cfgxml_data = []
        cfgxml_data.append("  <hbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("    <spinbox>")
        cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        cfgxml_data.append(f"      <resolution>{resolution}</resolution>")
        cfgxml_data.append(f"      <initval>{display_initval}</initval>")
        cfgxml_data.append(f"      <min_>{display_min}</min_>")
        cfgxml_data.append(f"      <max_>{display_max}</max_>")
        cfgxml_data.append("      <param_pin>1</param_pin>")
        cfgxml_data.append("    </spinbox>")
        cfgxml_data.append("    <label>")
        cfgxml_data.append(f'      <text>"{title}"</text>')
        cfgxml_data.append("    </label>")
        cfgxml_data.append("  </hbox>")
        return (f"{self.prefix}.{halpin}", cfgxml_data)

    def draw_jogwheel(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        resolution = setup.get("resolution", 0.1)
        size = setup.get("size", 200)
        cpr = setup.get("cpr", 50)
        cfgxml_data = []
        cfgxml_data.append("    <jogwheel>")
        cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        cfgxml_data.append(f'      <text>"{title}"</text>')
        cfgxml_data.append(f"      <size>{size}</size>")
        cfgxml_data.append(f"      <cpr>{cpr}</cpr>")
        cfgxml_data.append(f"      <resolution>{resolution}</resolution>")
        cfgxml_data.append("      <initval>0</initval>")
        cfgxml_data.append(f"      <min_>{display_min}</min_>")
        cfgxml_data.append(f"      <max_>{display_max}</max_>")
        cfgxml_data.append("      <param_pin>1</param_pin>")
        cfgxml_data.append("    </jogwheel>")
        return (f"{self.prefix}.{halpin}", cfgxml_data)

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
        cfgxml_data = []
        cfgxml_data.append("    <dial>")
        cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        cfgxml_data.append(f'      <text>"{title}"</text>')
        cfgxml_data.append(f"      <size>{size}</size>")
        cfgxml_data.append(f"      <cpr>{cpr}</cpr>")
        cfgxml_data.append(f"      <resolution>{resolution}</resolution>")
        cfgxml_data.append(f'      <dialcolor>"{dialcolor}"</dialcolor>')
        cfgxml_data.append(f'      <edgecolor>"{edgecolor}"</edgecolor>')
        cfgxml_data.append(f'      <dotcolor>"{dotcolor}"</dotcolor>')
        cfgxml_data.append("      <initval>0</initval>")
        cfgxml_data.append(f"      <min_>{display_min}</min_>")
        cfgxml_data.append(f"      <max_>{display_max}</max_>")
        cfgxml_data.append("      <param_pin>1</param_pin>")
        cfgxml_data.append("    </dial>")
        return (f"{self.prefix}.{halpin}", cfgxml_data)

    def draw_meter(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_subtext = setup.get("subtext", setup.get("unit", ""))
        display_region = setup.get("region", [])
        display_size = setup.get("size", 150)
        cfgxml_data = []
        cfgxml_data.append("  <hbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("  <meter>")
        cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        cfgxml_data.append(f'      <text>"{title}"</text>')
        cfgxml_data.append(f'      <subtext>"{display_subtext}"</subtext>')
        cfgxml_data.append(f"      <size>{display_size}</size>")
        cfgxml_data.append(f"      <min_>{display_min}</min_>")
        cfgxml_data.append(f"      <max_>{display_max}</max_>")
        for rnum, region in enumerate(display_region):
            cfgxml_data.append(f'      <region{rnum + 1}>({region[0]},{region[1]},"{region[2]}")</region{rnum + 1}>')
        cfgxml_data.append("    </meter>")
        cfgxml_data.append("  </hbox>")
        return (f"{self.prefix}.{halpin}", cfgxml_data)

    def draw_bar(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_range = setup.get("range", [])
        display_format = setup.get("format", "05d")
        display_fillcolor = setup.get("fillcolor", "red")
        display_bgcolor = setup.get("fillcolor", "grey")
        cfgxml_data = []
        cfgxml_data.append("  <hbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("    <label>")
        cfgxml_data.append(f'      <text>"{title}"</text>')
        cfgxml_data.append("    </label>")
        cfgxml_data.append("    <bar>")
        cfgxml_data.append(f'    <halpin>"{halpin}"</halpin>')
        cfgxml_data.append(f"    <min_>{display_min}</min_>")
        cfgxml_data.append(f"    <max_>{display_max}</max_>")
        cfgxml_data.append(f'    <format>"{display_format}"</format>')
        cfgxml_data.append(f'    <bgcolor>"{display_bgcolor}"</bgcolor>')
        cfgxml_data.append(f'    <fillcolor>"{display_fillcolor}"</fillcolor>')
        for rnum, brange in enumerate(display_range):
            cfgxml_data.append(f'    <range{rnum + 1}>({brange[0]},{brange[1]},"{brange[2]}")</range{rnum + 1}>')
        cfgxml_data.append("    </bar>")
        cfgxml_data.append("  </hbox>")
        return (f"{self.prefix}.{halpin}", cfgxml_data)

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
        cfgxml_data = []
        cfgxml_data.append("  <hbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("    <label>")
        cfgxml_data.append(f'      <text>"{title:10s}"</text>')
        cfgxml_data.append('      <font>("Helvetica",9)</font>')
        cfgxml_data.append("      <width>13</width>")
        cfgxml_data.append("    </label>")
        cfgxml_data.append(f"    <{element}>")
        cfgxml_data.append(f'        <halpin>"{halpin}"</halpin>')
        cfgxml_data.append('        <font>("Helvetica",14)</font>')
        cfgxml_data.append(f'        <format>"{display_format}"</format>')
        # cfgxml_data.append(f'        <width>13</width>')
        cfgxml_data.append("      <justify>LEFT</justify>")
        cfgxml_data.append(f"    </{element}>")
        if unit:
            cfgxml_data.append("    <label>")
            cfgxml_data.append('        <font>("Helvetica",14)</font>')
            cfgxml_data.append(f'      <text>"{unit}"</text>')
            cfgxml_data.append("    </label>")
        cfgxml_data.append("  </hbox>")
        return (f"{self.prefix}.{halpin}", cfgxml_data)

    def draw_checkbutton(self, name, halpin, setup={}):
        title = setup.get("title", name)
        cfgxml_data = []
        cfgxml_data.append("  <hbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("    <label>")
        cfgxml_data.append(f'      <text>"{title:10s}"</text>')
        cfgxml_data.append('      <font>("Helvetica",9)</font>')
        cfgxml_data.append("      <width>13</width>")
        cfgxml_data.append("    </label>")
        cfgxml_data.append("    <checkbutton>")
        cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        # cfgxml_data.append(f'      <text>"{title}"</text>')
        cfgxml_data.append("    </checkbutton>")
        cfgxml_data.append("  </hbox>")
        return (f"{self.prefix}.{halpin}", cfgxml_data)

    def draw_checkbutton_rgb(self, name, halpin_g, halpin_b, halpin_r, setup={}):
        title = setup.get("title", name)
        cfgxml_data = []
        cfgxml_data.append("  <hbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("    <label>")
        cfgxml_data.append(f'      <text>"{title}"</text>')
        cfgxml_data.append("    </label>")
        cfgxml_data.append("    <checkbutton>")
        cfgxml_data.append(f'      <halpin>"{halpin_g}"</halpin>')
        cfgxml_data.append('      <text>"G"</text>')
        cfgxml_data.append("    </checkbutton>")
        cfgxml_data.append("    <checkbutton>")
        cfgxml_data.append(f'      <halpin>"{halpin_b}"</halpin>')
        cfgxml_data.append('      <text>"B"</text>')
        cfgxml_data.append("    </checkbutton>")
        cfgxml_data.append("    <checkbutton>")
        cfgxml_data.append(f'      <halpin>"{halpin_r}"</halpin>')
        cfgxml_data.append('      <text>"R"</text>')
        cfgxml_data.append("    </checkbutton>")
        cfgxml_data.append("  </hbox>")
        return (f"{self.prefix}.{halpin_g}", cfgxml_data)

    def draw_led(self, name, halpin, setup={}):
        title = setup.get("title", name)
        size = setup.get("size", 16)
        color = setup.get("color")
        cfgxml_data = []
        cfgxml_data.append("  <hbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("    <label>")
        cfgxml_data.append(f'      <text>"{title:10s}"</text>')
        cfgxml_data.append('      <font>("Helvetica",9)</font>')
        cfgxml_data.append("      <width>13</width>")
        cfgxml_data.append("    </label>")
        cfgxml_data.append("    <led>")
        cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        cfgxml_data.append(f"      <size>{size}</size>")
        if color:
            cfgxml_data.append(f'      <on_color>"{color}"</on_color>')
        elif halpin.endswith(".R"):
            cfgxml_data.append('      <on_color>"red"</on_color>')
        elif halpin.endswith(".B"):
            cfgxml_data.append('      <on_color>"blue"</on_color>')
        else:
            cfgxml_data.append('      <on_color>"yellow"</on_color>')
        cfgxml_data.append('      <off_color>"red"</off_color>')
        cfgxml_data.append("    </led>")
        cfgxml_data.append("  </hbox>")
        return (f"{self.prefix}.{halpin}", cfgxml_data)

    def draw_rectled(self, name, halpin, setup={}):
        title = setup.get("title", name)
        width = setup.get("width", 16)
        height = setup.get("height", 16)
        color = setup.get("color")
        cfgxml_data = []
        cfgxml_data.append("  <hbox>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>2</bd>")
        cfgxml_data.append("    <label>")
        cfgxml_data.append(f'      <text>"{title:10s}"</text>')
        cfgxml_data.append('      <font>("Helvetica",9)</font>')
        cfgxml_data.append("      <width>13</width>")
        cfgxml_data.append("    </label>")
        cfgxml_data.append("    <led>")
        cfgxml_data.append(f'      <halpin>"{halpin}"</halpin>')
        cfgxml_data.append(f"      <width>{width}</width>")
        cfgxml_data.append(f"      <height>{height}</height>")
        if color:
            cfgxml_data.append(f'      <on_color>"{color}"</on_color>')
        elif halpin.endswith(".R"):
            cfgxml_data.append('      <on_color>"red"</on_color>')
        elif halpin.endswith(".B"):
            cfgxml_data.append('      <on_color>"blue"</on_color>')
        else:
            cfgxml_data.append('      <on_color>"green"</on_color>')
        cfgxml_data.append('      <off_color>"black"</off_color>')
        cfgxml_data.append("    </led>")
        cfgxml_data.append("  </hbox>")
        return (f"{self.prefix}.{halpin}", cfgxml_data)

    def draw_button(self, name, halpin, setup={}):
        title = setup.get("title", name)
        cfgxml_data = []
        cfgxml_data.append("  <button>")
        cfgxml_data.append("    <relief>RAISED</relief>")
        cfgxml_data.append("    <bd>3</bd>")
        cfgxml_data.append(f'    <halpin>"{halpin}"</halpin>')
        cfgxml_data.append(f'    <text>"{title}"</text>')
        cfgxml_data.append('    <font>("Helvetica", 12)</font>')
        cfgxml_data.append("  </button>")
        return (f"{self.prefix}.{halpin}", cfgxml_data)

    def draw_multilabel(self, name, halpin, setup={}):
        legends = setup.get("legends", ["LABEL1", "LABEL2", "LABEL3", "LABEL4"])
        cfgxml_data = []
        cfgxml_data.append("  <multilabel>")
        cfgxml_data.append(f"    <legends>{legends}</legends>")
        cfgxml_data.append(f'    <halpin>"{halpin}"</halpin>')
        cfgxml_data.append('    <font>("Helvetica", 12)</font>')
        cfgxml_data.append('    <bg>"black"</bg>')
        cfgxml_data.append('    <fg>"yellow"</fg>')
        cfgxml_data.append("  </multilabel>")
        return (f"{self.prefix}.{halpin}", cfgxml_data)
