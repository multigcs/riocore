import os

from lxml import etree


class pyvcp:
    def __init__(self, prefix="pyvcp", vcp_pos=None):
        self.prefix = prefix
        self.vcp_pos = vcp_pos

    def check(self, configuration_path):
        return True

    def draw_begin(self):
        self.root = etree.Element("pyvcp")
        self.parent = self.root

    def draw_end(self):
        self.parent = self.parent.getparent()

    def xml(self):
        formated = etree.tostring(self.root, pretty_print=True).decode()
        return formated

    def save(self, configuration_path):
        xml_filename = os.path.join(configuration_path, "rio-gui.xml")
        formated = etree.tostring(self.root, pretty_print=True).decode()
        open(xml_filename, "w").write(formated)

    def draw_tabs_begin(self, names):
        e_tabs = etree.Element("tabs")
        e_names = etree.Element("names")
        e_names.text = str(names)
        e_tabs.append(e_names)
        self.parent.append(e_tabs)
        self.parent = e_tabs

    def draw_tabs_end(self):
        self.parent = self.parent.getparent()

    def draw_tab_begin(self, name):
        e_vbox = etree.Element("vbox")
        self.parent.append(e_vbox)
        self.parent = e_vbox

    def draw_tab_end(self):
        # if len(self.parent) == 0:
        #    self.parent = self.parent.getparent()
        #    self.parent.remove(self.parent[-1])
        # else:
        #    self.parent = self.parent.getparent()
        self.parent = self.parent.getparent()

    def draw_vbox_begin(self):
        e_vbox = etree.Element("vbox")
        self.parent.append(e_vbox)
        self.parent = e_vbox

    def draw_vbox_end(self):
        self.parent = self.parent.getparent()

    def draw_hbox_begin(self):
        e_hbox = etree.Element("hbox")
        e_boxexpand = etree.Element("boxexpand", expand="yes")
        e_hbox.append(e_boxexpand)
        e_boxfill = etree.Element("boxfill", fill="both")
        e_hbox.append(e_boxfill)
        e_boxanchor = etree.Element("boxanchor", anchor="e")
        e_hbox.append(e_boxanchor)
        self.parent.append(e_hbox)
        self.parent = e_hbox

    def draw_hbox_end(self):
        self.parent = self.parent.getparent()

    def draw_frame_begin(self, name=None):
        name = name or ""
        e_labelframe = etree.Element("labelframe", text=name)
        e_relief = etree.Element("relief")
        e_relief.text = "GROOVE"
        e_labelframe.append(e_relief)
        e_font = etree.Element("font")
        e_font.text = '("Helvetica", 10)'
        e_labelframe.append(e_font)
        self.parent.append(e_labelframe)
        self.parent = e_labelframe

    def draw_frame_end(self):
        self.parent = self.parent.getparent()

    def draw_title(self, title, size=15):
        e_label = etree.Element("label")
        e_text = etree.Element("text")
        e_text.text = f'"{title:10s}"'
        e_label.append(e_text)
        e_anchor = etree.Element("anchor")
        e_anchor.text = '"w"'
        e_label.append(e_anchor)
        e_font = etree.Element("font")
        e_font.text = '("Helvetica",9)'
        e_label.append(e_font)
        if size >= 0:
            e_width = etree.Element("width")
            e_width.text = str(size)
            e_label.append(e_width)
        self.parent.append(e_label)

    def draw_scale(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_initval = setup.get("initval", 0)
        resolution = setup.get("resolution", 0.1)
        self.draw_hbox_begin()
        self.draw_title(title)
        e_scale = etree.Element("scale")
        self.parent.append(e_scale)
        e_halpin = etree.Element("halpin")
        e_halpin.text = f'"{halpin}"'
        e_scale.append(e_halpin)
        e_min = etree.Element("min_")
        e_min.text = str(int(display_min))
        e_scale.append(e_min)
        e_max = etree.Element("max_")
        e_max.text = str(int(display_max))
        e_scale.append(e_max)
        e_resolution = etree.Element("resolution")
        e_resolution.text = str(resolution)
        e_scale.append(e_resolution)
        e_orient = etree.Element("orient")
        e_orient.text = "HORIZONTAL"
        e_scale.append(e_orient)
        e_initval = etree.Element("initval")
        e_initval.text = str(int(display_initval))
        e_scale.append(e_initval)
        e_param_pin = etree.Element("param_pin")
        e_param_pin.text = "1"
        e_scale.append(e_param_pin)
        self.parent.append(e_scale)
        self.draw_hbox_end()
        return f"{self.prefix}.{halpin}-f"

    def draw_fselect(self, name, halpin, setup={}):
        title = setup.get("title", name)
        values = setup.get("values", {"v0": 0, "v1": 1})
        display_min = 0
        display_max = len(values) - 1
        display_initval = setup.get("initval", 0)
        resolution = 1
        legends = list(values.keys())
        e_labelframe = etree.Element("labelframe", text=title)
        self.draw_vbox_begin()
        e_multilabel = etree.Element("multilabel")
        self.parent.append(e_multilabel)
        e_legends = etree.Element("legends")
        e_legends.text = str(legends)
        e_multilabel.append(e_legends)
        e_halpin = etree.Element("halpin")
        e_halpin.text = f'"{halpin}"'
        e_multilabel.append(e_halpin)
        e_font = etree.Element("font")
        e_font.text = '("Helvetica", 12)'
        e_multilabel.append(e_font)
        e_bg = etree.Element("bg")
        e_bg.text = '"black"'
        e_multilabel.append(e_bg)
        e_fg = etree.Element("fg")
        e_fg.text = '"yellow"'
        e_multilabel.append(e_fg)
        e_labelframe.append(e_multilabel)
        e_scale = etree.Element("scale")
        self.parent.append(e_scale)
        e_halpin = etree.Element("halpin")
        e_halpin.text = f'"{halpin}"'
        e_scale.append(e_halpin)
        e_min = etree.Element("min_")
        e_min.text = str(int(display_min))
        e_scale.append(e_min)
        e_max = etree.Element("max_")
        e_max.text = str(int(display_max))
        e_scale.append(e_max)
        e_resolution = etree.Element("resolution")
        e_resolution.text = str(resolution)
        e_scale.append(e_resolution)
        e_orient = etree.Element("orient")
        e_orient.text = "HORIZONTAL"
        e_scale.append(e_orient)
        e_initval = etree.Element("initval")
        e_initval.text = str(int(display_initval))
        e_scale.append(e_initval)
        e_param_pin = etree.Element("param_pin")
        e_param_pin.text = "1"
        e_scale.append(e_param_pin)
        e_labelframe.append(e_scale)
        self.parent.append(e_labelframe)
        self.draw_vbox_end()
        return f"{self.prefix}.{halpin}"

    def draw_spinbox(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        # display_min = setup.get("min", vmin)
        # display_max = setup.get("max", vmax)
        display_initval = setup.get("initval", 0.0)
        resolution = setup.get("resolution", 0.1)
        self.draw_hbox_begin()
        self.draw_title(title)
        e_spinbox = etree.Element("spinbox")
        self.parent.append(e_spinbox)
        e_halpin = etree.Element("halpin")
        e_halpin.text = f'"{halpin}"'
        e_spinbox.append(e_halpin)
        e_resolution = etree.Element("resolution")
        e_resolution.text = str(resolution)
        e_spinbox.append(e_resolution)
        e_initval = etree.Element("initval")
        e_initval.text = str(int(display_initval))
        e_spinbox.append(e_initval)
        e_param_pin = etree.Element("param_pin")
        e_param_pin.text = "1"
        e_spinbox.append(e_param_pin)
        self.parent.append(e_spinbox)
        self.draw_hbox_end()
        return f"{self.prefix}.{halpin}"

    def draw_jogwheel(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_initval = setup.get("initval", 0.0)
        resolution = setup.get("resolution", 0.1)
        size = setup.get("size", 200)
        cpr = setup.get("cpr", 50)
        e_jogwheel = etree.Element("jogwheel")
        self.parent.append(e_jogwheel)
        e_halpin = etree.Element("halpin")
        e_halpin.text = f'"{halpin}"'
        e_jogwheel.append(e_halpin)
        e_text = etree.Element("text")
        e_text.text = f'"{title}"'
        e_jogwheel.append(e_text)
        e_size = etree.Element("size")
        e_size.text = str(size)
        e_jogwheel.append(e_size)
        e_cpr = etree.Element("cpr")
        e_cpr.text = str(cpr)
        e_jogwheel.append(e_cpr)
        e_min = etree.Element("min_")
        e_min.text = str(int(display_min))
        e_jogwheel.append(e_min)
        e_max = etree.Element("max_")
        e_max.text = str(int(display_max))
        e_jogwheel.append(e_max)
        e_resolution = etree.Element("resolution")
        e_resolution.text = str(resolution)
        e_jogwheel.append(e_resolution)
        e_initval = etree.Element("initval")
        e_initval.text = str(int(display_initval))
        e_jogwheel.append(e_initval)
        e_param_pin = etree.Element("param_pin")
        e_param_pin.text = "1"
        e_jogwheel.append(e_param_pin)
        self.parent.append(e_jogwheel)
        return f"{self.prefix}.{halpin}"

    def draw_dial(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_initval = setup.get("initval", 0.0)
        resolution = setup.get("resolution", 0.1)
        dialcolor = setup.get("dialcolor", "yellow")
        edgecolor = setup.get("edgecolor", "green")
        dotcolor = setup.get("dotcolor", "black")
        size = setup.get("size", 200)
        cpr = setup.get("cpr", 50)
        e_dial = etree.Element("dial")
        self.parent.append(e_dial)
        e_halpin = etree.Element("halpin")
        e_halpin.text = f'"{halpin}"'
        e_dial.append(e_halpin)
        e_text = etree.Element("text")
        e_text.text = f'"{title}"'
        e_dial.append(e_text)
        e_size = etree.Element("size")
        e_size.text = str(size)
        e_dial.append(e_size)
        e_cpr = etree.Element("cpr")
        e_cpr.text = str(cpr)
        e_dial.append(e_cpr)
        e_min = etree.Element("min_")
        e_min.text = str(int(display_min))
        e_dial.append(e_min)
        e_max = etree.Element("max_")
        e_max.text = str(int(display_max))
        e_dial.append(e_max)
        e_resolution = etree.Element("resolution")
        e_resolution.text = str(resolution)
        e_dial.append(e_resolution)
        e_dialcolor = etree.Element("dialcolor")
        e_dialcolor.text = f'"{dialcolor}"'
        e_dial.append(e_dialcolor)
        e_edgecolor = etree.Element("edgecolor")
        e_edgecolor.text = f'"{edgecolor}"'
        e_dial.append(e_edgecolor)
        e_dotcolor = etree.Element("dotcolor")
        e_dotcolor.text = f'"{dotcolor}"'
        e_dial.append(e_dotcolor)
        e_initval = etree.Element("initval")
        e_initval.text = str(int(display_initval))
        e_dial.append(e_initval)
        e_param_pin = etree.Element("param_pin")
        e_param_pin.text = "1"
        e_dial.append(e_param_pin)
        self.parent.append(e_dial)
        return f"{self.prefix}.{halpin}"

    def draw_meter(self, name, halpin, setup={}, vmin=0, vmax=100):
        display_unit = setup.get("unit", "")
        if not display_unit and "." in name:
            display_unit = name.split(".")[-1]
            name = ".".join(name.split(".")[:-1])
        title = setup.get("title", name)
        display_initval = setup.get("initval", 0)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_subtext = setup.get("subtext", display_unit)
        display_region = setup.get("range", setup.get("region", []))
        display_size = setup.get("size", 150)
        self.draw_hbox_begin()
        e_meter = etree.Element("meter")
        self.parent.append(e_meter)
        e_halpin = etree.Element("halpin")
        e_halpin.text = f'"{halpin}"'
        e_meter.append(e_halpin)
        e_text = etree.Element("text")
        e_text.text = f'"{title}"'
        e_meter.append(e_text)
        e_subtext = etree.Element("subtext")
        e_subtext.text = f'"{display_subtext}"'
        e_meter.append(e_subtext)
        e_size = etree.Element("size")
        e_size.text = str(display_size)
        e_meter.append(e_size)
        e_min = etree.Element("min_")
        e_min.text = str(int(display_min))
        e_meter.append(e_min)
        e_max = etree.Element("max_")
        e_max.text = str(int(display_max))
        e_meter.append(e_max)
        e_initval = etree.Element("initval")
        e_initval.text = str(int(display_initval))
        e_meter.append(e_initval)
        e_size = etree.Element("size")
        e_size.text = str(display_size)
        e_meter.append(e_size)
        e_param_pin = etree.Element("param_pin")
        e_param_pin.text = "1"
        e_meter.append(e_param_pin)
        for rnum, region in enumerate(display_region):
            e_region = etree.Element(f"region{rnum + 1}")
            e_region.text = f'({region[0]},{region[1]},"{region[2]}")'
            e_meter.append(e_region)
        self.parent.append(e_meter)
        self.draw_hbox_end()
        return f"{self.prefix}.{halpin}"

    def draw_bar(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_initval = setup.get("initval", 0)
        display_range = setup.get("range", setup.get("region", []))
        display_unit = setup.get("unit")
        display_format = setup.get("format", "05d")

        if display_unit and len(display_format) < 5:
            display_format = f"{display_format} {display_unit}"

        display_fillcolor = setup.get("fillcolor", "red")
        display_bgcolor = setup.get("fillcolor", "grey")
        self.draw_hbox_begin()
        self.draw_title(title)
        e_bar = etree.Element("bar")
        self.parent.append(e_bar)
        e_halpin = etree.Element("halpin")
        e_halpin.text = f'"{halpin}"'
        e_bar.append(e_halpin)
        e_min = etree.Element("min_")
        e_min.text = str(int(display_min))
        e_bar.append(e_min)
        e_max = etree.Element("max_")
        e_max.text = str(int(display_max))
        e_bar.append(e_max)
        e_initval = etree.Element("initval")
        e_initval.text = str(int(display_initval))
        e_bar.append(e_initval)
        e_format = etree.Element("format")
        e_format.text = f'"{display_format}"'
        e_bar.append(e_format)
        e_bgcolor = etree.Element("bgcolor")
        e_bgcolor.text = f'"{display_bgcolor}"'
        e_bar.append(e_bgcolor)
        e_fillcolor = etree.Element("fillcolor")
        e_fillcolor.text = f'"{display_fillcolor}"'
        e_bar.append(e_fillcolor)
        e_param_pin = etree.Element("param_pin")
        e_param_pin.text = "1"
        e_bar.append(e_param_pin)
        for rnum, brange in enumerate(display_range):
            e_range = etree.Element(f"range{rnum + 1}")
            e_range.text = f'({brange[0]},{brange[1]},"{brange[2]}")'
            e_bar.append(e_range)
        self.parent.append(e_bar)
        self.draw_hbox_end()
        return f"{self.prefix}.{halpin}"

    def draw_number_u32(self, name, halpin, setup={}):
        return self.draw_number(name, halpin, hal_type="u32", setup=setup)

    def draw_number_s32(self, name, halpin, setup={}):
        return self.draw_number(name, halpin, hal_type="s32", setup=setup)

    def draw_number(self, name, halpin, setup={}, hal_type="float"):
        title = setup.get("title", name)
        if hal_type == "float":
            display_format = setup.get("format", "07.2f")
            element = "number"
        else:
            display_format = setup.get("format", "d")
            element = hal_type
        unit = setup.get("unit")
        self.draw_hbox_begin()
        self.draw_title(title)
        element = etree.Element(element)
        self.parent.append(element)
        e_halpin = etree.Element("halpin")
        e_halpin.text = f'"{halpin}"'
        element.append(e_halpin)
        e_font = etree.Element("font")
        e_font.text = '("Helvetica",14)'
        element.append(e_font)
        e_format = etree.Element("format")
        e_format.text = f'"{display_format}"'
        element.append(e_format)
        e_anchor = etree.Element("anchor")
        e_anchor.text = '"e"'
        element.append(e_anchor)
        e_width = etree.Element("width")
        e_width.text = "13"
        element.append(e_width)
        self.parent.append(element)
        if unit:
            self.draw_title(unit, size=-1)

        self.draw_hbox_end()
        return f"{self.prefix}.{halpin}"

    def draw_checkbutton(self, name, halpin, setup={}):
        title = setup.get("title", name)
        self.draw_hbox_begin()
        self.draw_title(title)
        e_checkbutton = etree.Element("checkbutton")
        self.parent.append(e_checkbutton)
        e_halpin = etree.Element("halpin")
        e_halpin.text = f'"{halpin}"'
        e_checkbutton.append(e_halpin)
        e_anchor = etree.Element("anchor")
        e_anchor.text = '"e"'
        e_checkbutton.append(e_anchor)
        e_width = etree.Element("width")
        e_width.text = "13"
        e_checkbutton.append(e_width)
        self.parent.append(e_checkbutton)
        self.draw_hbox_end()
        return f"{self.prefix}.{halpin}"

    def draw_checkbutton_rgb(self, name, halpin_g, halpin_b, halpin_r, setup={}):
        title = setup.get("title", name)
        self.draw_hbox_begin()
        self.draw_title(title)
        e_checkbutton = etree.Element("checkbutton")
        self.parent.append(e_checkbutton)
        e_halpin = etree.Element("halpin")
        e_halpin.text = f'"{halpin_g}"'
        e_checkbutton.append(e_halpin)
        e_text = etree.Element("text")
        e_text.text = '"G"'
        e_checkbutton.append(e_text)
        self.parent.append(e_checkbutton)
        e_checkbutton = etree.Element("checkbutton")
        self.parent.append(e_checkbutton)
        e_halpin = etree.Element("halpin")
        e_halpin.text = f'"{halpin_b}"'
        e_checkbutton.append(e_halpin)
        e_text = etree.Element("text")
        e_text.text = '"B"'
        e_checkbutton.append(e_text)
        self.parent.append(e_checkbutton)
        e_checkbutton = etree.Element("checkbutton")
        self.parent.append(e_checkbutton)
        e_halpin = etree.Element("halpin")
        e_halpin.text = f'"{halpin_r}"'
        e_checkbutton.append(e_halpin)
        e_text = etree.Element("text")
        e_text.text = '"R"'
        e_checkbutton.append(e_text)
        self.parent.append(e_checkbutton)
        self.draw_hbox_end()
        return f"{self.prefix}.{halpin_g}"

    def draw_led(self, name, halpin, setup={}):
        title = setup.get("title", name)
        size = setup.get("size", 16)
        self.draw_hbox_begin()
        if title:
            self.draw_title(title, size=30)
        color = setup.get("color")
        on_color = "yellow"
        off_color = "red"
        if color:
            on_color = color
            off_color = setup.get("off_color", "black")
        elif halpin.endswith(".R"):
            on_color = "red"
            off_color = setup.get("off_color", "black")
        elif halpin.endswith(".G"):
            on_color = "green"
            off_color = setup.get("off_color", "black")
        elif halpin.endswith(".B"):
            on_color = "blue"
            off_color = setup.get("off_color", "black")
        e_led = etree.Element("led")
        self.parent.append(e_led)
        e_halpin = etree.Element("halpin")
        e_halpin.text = f'"{halpin}"'
        e_led.append(e_halpin)
        e_size = etree.Element("size")
        e_size.text = str(size)
        e_led.append(e_size)
        e_on_color = etree.Element("on_color")
        e_on_color.text = f'"{on_color}"'
        e_led.append(e_on_color)
        e_off_color = etree.Element("off_color")
        e_off_color.text = f'"{off_color}"'
        e_led.append(e_off_color)
        e_anchor = etree.Element("anchor")
        e_anchor.text = '"e"'
        e_led.append(e_anchor)
        e_width = etree.Element("width")
        e_width.text = "16"
        e_led.append(e_width)
        self.parent.append(e_led)
        self.draw_hbox_end()
        return f"{self.prefix}.{halpin}"

    def draw_rectled(self, name, halpin, setup={}):
        title = setup.get("title", name)
        width = setup.get("width", 16)
        height = setup.get("height", 16)
        color = setup.get("color")
        off_color = setup.get("off_color", "yellow")
        self.draw_hbox_begin()
        if title:
            self.draw_title(title, size=30)
        on_color = "red"
        off_color = "yellow"
        if color:
            on_color = color
            off_color = setup.get("off_color", "black")
        elif halpin.endswith(".R"):
            on_color = "red"
            off_color = setup.get("off_color", "black")
        elif halpin.endswith(".G"):
            on_color = "green"
            off_color = setup.get("off_color", "black")
        elif halpin.endswith(".B"):
            on_color = "blue"
            off_color = setup.get("off_color", "black")
        e_led = etree.Element("rectled")
        self.parent.append(e_led)
        e_halpin = etree.Element("halpin")
        e_halpin.text = f'"{halpin}"'
        e_led.append(e_halpin)
        e_width = etree.Element("width")
        e_width.text = str(width)
        e_led.append(e_width)
        e_height = etree.Element("height")
        e_height.text = str(height)
        e_led.append(e_height)
        e_on_color = etree.Element("on_color")
        e_on_color.text = f'"{on_color}"'
        e_led.append(e_on_color)
        e_off_color = etree.Element("off_color")
        e_off_color.text = f'"{off_color}"'
        e_led.append(e_off_color)
        e_anchor = etree.Element("anchor")
        e_anchor.text = '"e"'
        e_led.append(e_anchor)
        e_width = etree.Element("width")
        e_width.text = "16"
        e_led.append(e_width)
        self.parent.append(e_led)
        self.draw_hbox_end()
        return f"{self.prefix}.{halpin}"

    def draw_button(self, name, halpin, setup={}):
        title = setup.get("title", name)
        e_button = etree.Element("button")
        self.parent.append(e_button)
        e_relief = etree.Element("relief")
        e_relief.text = "GROOVE"
        e_button.append(e_relief)
        e_bd = etree.Element("bd")
        e_bd.text = "3"
        e_button.append(e_bd)
        e_halpin = etree.Element("halpin")
        e_halpin.text = f'"{halpin}"'
        e_button.append(e_halpin)
        e_text = etree.Element("text")
        e_text.text = f'"{title}"'
        e_button.append(e_text)
        e_font = etree.Element("font")
        e_font.text = '("Helvetica", 12)'
        e_button.append(e_font)
        self.parent.append(e_button)
        return f"{self.prefix}.{halpin}"

    def draw_multilabel(self, name, halpin, setup={}):
        legends = setup.get("legends", ["LABEL1", "LABEL2", "LABEL3", "LABEL4"])
        e_multilabel = etree.Element("multilabel")
        self.parent.append(e_multilabel)
        e_legends = etree.Element("legends")
        e_legends.text = str(legends)
        e_multilabel.append(e_legends)
        e_halpin = etree.Element("halpin")
        e_halpin.text = f'"{halpin}"'
        e_multilabel.append(e_halpin)
        e_font = etree.Element("font")
        e_font.text = '("Helvetica", 12)'
        e_multilabel.append(e_font)
        e_bg = etree.Element("bg")
        e_bg.text = '"black"'
        e_multilabel.append(e_bg)
        e_fg = etree.Element("fg")
        e_fg.text = '"yellow"'
        e_multilabel.append(e_fg)
        self.parent.append(e_multilabel)
        return f"{self.prefix}.{halpin}"
