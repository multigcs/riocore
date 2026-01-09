import os


class gladevcp:
    colormapping = {
        "white": "#ffffffffffff",
        "black": "#000000000000",
        "yellow": "#ffffffff0000",
        "red": "#ffff00000000",
        "green": "#0000ffff0000",
        "blue": "#00000000ffff",
    }

    def __init__(self, prefix="gladevcp", vcp_pos=None):
        self.prefix = prefix
        self.vcp_pos = vcp_pos
        self.inits = []

    def check(self, configuration_path):
        return True

    def draw_begin(self):
        self.cfgxml_data = []
        self.adjustment = []
        self.cfgxml_data.append("""<?xml version="1.0"?>
<interface>
  <!-- interface-requires gladevcp 0.0 -->
  <requires lib="gtk+" version="2.16"/>
  <!-- interface-naming-policy project-wide -->
  <object class="GtkWindow" id="window1">

    <child>
      <object class="GtkBox" id="vbox_tab_{name}">
        <property name="margin">10</property>
        <property name="spacing">10</property>
        <property name="visible">True</property>
        <property name="can-focus">False</property>
        <property name="orientation">vertical</property>
        """)

    def draw_end(self):
        self.cfgxml_data.append("""

      </object>
    </child>

  </object>
        """)

        self.cfgxml_data += self.adjustment
        self.cfgxml_data.append("</interface>")

    def xml(self):
        return "\n".join(self.cfgxml_data)

    def save(self, configuration_path):
        ui_filename = os.path.join(configuration_path, "rio-gui.ui")
        gvcp_filename = os.path.join(configuration_path, "rio-gui.py")
        inits = "\n        ".join(self.inits)
        handler_py = []
        handler_py.append(f"""
import hal
import glib
import time

class HandlerClass:
    def __init__(self, halcomp,builder,useropts):
        self.halcomp = halcomp
        self.builder = builder
        self.nhits = 0
        {inits}

def get_handlers(halcomp, builder, useropts):
    return [HandlerClass(halcomp, builder, useropts)]

""")
        open(gvcp_filename, "w").write("\n".join(handler_py))
        open(ui_filename, "w").write("\n".join(self.cfgxml_data))

    def draw_tabs_begin(self, names):
        self.cfgxml_data.append("""
            <child>
              <object class="GtkNotebook">
                <property name="visible">True</property>
                <property name="can-focus">True</property>
        """)

    def draw_tabs_end(self):
        self.cfgxml_data.append("""
              </object>
            </child>
        """)

    def draw_tab_begin(self, name):
        self.tabname = name
        self.cfgxml_data.append(f"""
    <child>
      <object class="GtkBox" id="vbox_tab_{name}">
        <property name="margin">10</property>
        <property name="spacing">10</property>
        <property name="visible">True</property>
        <property name="can-focus">False</property>
        <property name="orientation">vertical</property>
        """)

    def draw_tab_end(self):
        # remove emty tabs
        if "vbox_tab_" in self.cfgxml_data[-1]:
            self.cfgxml_data = self.cfgxml_data[:-1]
        else:
            self.cfgxml_data.append(f"""
              </object>
            </child>
                <child type="tab">
                  <object class="GtkLabel">
                    <property name="visible">True</property>
                    <property name="can-focus">False</property>
                    <property name="label" translatable="yes">{self.tabname}</property>
                  </object>
                  <packing>
                    <property name="tab-fill">False</property>
                  </packing>
                </child>
            """)

    def draw_frame_begin(self, name=None):
        self.cfgxml_data.append(f"""
           <child>
            <object class="GtkFrame">
            <property name="visible">True</property>
            <property name="label_xalign">0.5</property>
            <child type="label">
              <object class="GtkLabel">
                <property name="visible">True</property>
                <property name="label" translatable="yes">{name}</property>
                <property name="use_markup">True</property>
              </object>
            </child>
        """)

        self.draw_vbox_begin()

    def draw_frame_end(self):
        self.draw_vbox_end()

        self.cfgxml_data.append("""
            </object>
           </child>
        """)

    def draw_vbox_begin(self):
        self.cfgxml_data.append("""
    <child>
      <object class="GtkBox">
        <property name="margin">5</property>
        <property name="spacing">0</property>
        <property name="visible">True</property>
        <property name="can-focus">False</property>
        <property name="orientation">vertical</property>
        """)

    def draw_vbox_end(self):
        self.cfgxml_data.append("              </object>")
        self.cfgxml_data.append("            </child>")

    def draw_hbox_begin(self):
        self.cfgxml_data.append("""
    <child>
      <object class="GtkBox">
        <property name="margin">0</property>
        <property name="spacing">0</property>
        <property name="visible">True</property>
        <property name="can-focus">False</property>
        <property name="orientation">horizontal</property>
        """)

    def draw_hbox_end(self):
        self.cfgxml_data.append("              </object>")
        self.cfgxml_data.append("            </child>")

    def draw_title(self, title):
        self.cfgxml_data.append("                <child>")
        self.cfgxml_data.append('                  <object class="GtkLabel">')
        self.cfgxml_data.append('                    <property name="visible">True</property>')
        self.cfgxml_data.append('                    <property name="can-focus">False</property>')
        self.cfgxml_data.append(f'                    <property name="label" translatable="yes">{title}</property>')
        self.cfgxml_data.append('                     <property name="xpad">6</property>')
        self.cfgxml_data.append('                     <property name="xalign">0</property>')
        self.cfgxml_data.append("                  </object>")
        self.cfgxml_data.append("                  <packing>")
        self.cfgxml_data.append('                    <property name="expand">True</property>')
        self.cfgxml_data.append('                    <property name="fill">True</property>')
        self.cfgxml_data.append('                    <property name="position">1</property>')
        self.cfgxml_data.append("                  </packing>")
        self.cfgxml_data.append("                </child>")

    def draw_button(self, name, halpin, setup={}):
        self.cfgxml_data.append("            <child>")
        self.cfgxml_data.append(f'              <object class="HAL_Button" id="{halpin}">')
        self.cfgxml_data.append(f'                <property name="label" translatable="yes">{name}</property>')
        self.cfgxml_data.append('                <property name="visible">True</property>')
        self.cfgxml_data.append('                <property name="can-focus">True</property>')
        self.cfgxml_data.append('                <property name="receives-default">True</property>')
        self.cfgxml_data.append("              </object>")
        self.cfgxml_data.append("              <packing>")
        self.cfgxml_data.append('                <property name="expand">True</property>')
        self.cfgxml_data.append('                <property name="fill">True</property>')
        self.cfgxml_data.append('                <property name="position">1</property>')
        self.cfgxml_data.append("              </packing>")
        self.cfgxml_data.append("            </child>")
        return f"{self.prefix}.{halpin}"

    def draw_spinbox(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        # display_initval = setup.get("initval", 0.0)
        resolution = setup.get("resolution", 0.1)
        self.cfgxml_data.append("    <child>")
        self.cfgxml_data.append('      <object class="GtkHBox">')
        self.cfgxml_data.append('        <property name="visible">True</property>')
        self.cfgxml_data.append('        <property name="spacing">2</property>')
        self.draw_title(title)
        self.cfgxml_data.append("                    <child>")
        self.cfgxml_data.append(f'                      <object class="HAL_SpinButton" id="{halpin}">')
        self.cfgxml_data.append('                        <property name="visible">True</property>')
        self.cfgxml_data.append('                        <property name="can_focus">True</property>')
        self.cfgxml_data.append('                        <property name="digits">2</property>')
        self.cfgxml_data.append(f'                        <property name="adjustment">adj_{halpin}</property>')
        self.cfgxml_data.append("                      </object>")
        self.cfgxml_data.append("                  <packing>")
        self.cfgxml_data.append('                    <property name="expand">True</property>')
        self.cfgxml_data.append('                    <property name="fill">True</property>')
        self.cfgxml_data.append('                    <property name="position">1</property>')
        self.cfgxml_data.append("                  </packing>")
        self.cfgxml_data.append("                    </child>")
        self.cfgxml_data.append("      </object>")
        self.cfgxml_data.append("    </child>")
        self.adjustment.append(f'  <object class="GtkAdjustment" id="adj_{halpin}">')
        self.adjustment.append(f'    <property name="lower">{display_min}</property>')
        self.adjustment.append(f'    <property name="upper">{display_max}</property>')
        self.adjustment.append(f'    <property name="step_increment">{resolution}</property>')
        self.adjustment.append("  </object>")
        return f"{self.prefix}.{halpin}-f"

    def draw_scale_s32(self, name, halpin, setup={}, vmin=0, vmax=100):
        if "resolution" not in setup:
            setup["resolution"] = 1
        self.draw_scale(name, halpin, setup=setup, vmin=vmin, vmax=vmax)
        return f"{self.prefix}.{halpin}-s"

    def draw_scale(self, name, halpin, setup={}, vmin=0, vmax=100):
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_initval = setup.get("initval", 0)
        self.inits.append(f"self.builder.get_object('{halpin}').set_value({display_initval})")
        digits = len(str(float(str(setup.get("resolution", 0.1)))).split(".")[-1].rstrip("0"))
        title = setup.get("title", name)
        self.cfgxml_data.append("    <child>")
        self.cfgxml_data.append('      <object class="GtkHBox">')
        self.cfgxml_data.append('        <property name="visible">True</property>')
        self.cfgxml_data.append('        <property name="spacing">2</property>')
        self.draw_title(title)
        self.cfgxml_data.append("                    <child>")
        self.cfgxml_data.append(f'                      <object class="HAL_HScale" id="{halpin}">')
        self.cfgxml_data.append('                        <property name="visible">True</property>')
        self.cfgxml_data.append('                        <property name="can_focus">True</property>')
        self.cfgxml_data.append('                        <property name="value-pos">left</property>')
        self.cfgxml_data.append(f'                        <property name="adjustment">adj_{halpin}</property>')
        self.cfgxml_data.append(f'                        <property name="digits">{digits}</property>')
        self.cfgxml_data.append("                      </object>")
        self.cfgxml_data.append("                  <packing>")
        self.cfgxml_data.append('                    <property name="expand">True</property>')
        self.cfgxml_data.append('                    <property name="fill">True</property>')
        self.cfgxml_data.append('                    <property name="position">1</property>')
        self.cfgxml_data.append("                  </packing>")
        self.cfgxml_data.append("                    </child>")
        self.cfgxml_data.append("      </object>")
        self.cfgxml_data.append("    </child>")
        self.adjustment.append(f'  <object class="GtkAdjustment" id="adj_{halpin}">')
        self.adjustment.append(f'    <property name="lower">{display_min}</property>')
        self.adjustment.append(f'    <property name="upper">{display_max}</property>')
        self.adjustment.append("  </object>")
        return f"{self.prefix}.{halpin}"

    def draw_meter(self, name, halpin, setup={}, vmin=0, vmax=100):
        display_unit = setup.get("unit", "")
        if not display_unit and "." in name:
            display_unit = name.split(".")[-1]
            name = ".".join(name.split(".")[:-1])
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_text = setup.get("text", title)
        display_region = setup.get("region", [])
        display_zone = setup.get("zone")
        display_size = setup.get("size", "150")

        self.cfgxml_data.append("            <child>")
        self.cfgxml_data.append(f'                      <object class="HAL_Meter" id="{halpin}">')
        self.cfgxml_data.append('                        <property name="visible">True</property>')
        self.cfgxml_data.append('                        <property name="can_focus">True</property>')
        self.cfgxml_data.append(f'                        <property name="label">{display_text}</property>')
        majorscale = (display_max - display_min) / 10
        self.cfgxml_data.append(f'                        <property name="majorscale">{majorscale}</property>')
        minorscale = (display_max - display_min) / 100
        self.cfgxml_data.append(f'                        <property name="minorscale">{minorscale}</property>')
        if display_unit:
            self.cfgxml_data.append(f'                        <property name="sublabel">{display_unit}</property>')
        self.cfgxml_data.append(f'                        <property name="min">{display_min}</property>')
        self.cfgxml_data.append(f'                        <property name="max">{display_max}</property>')
        if display_size:
            self.cfgxml_data.append(f'                        <property name="force_size">{display_size}</property>')

        if display_zone:
            for reg_n, zone in enumerate(display_zone[:3]):
                if len(zone) == 1:
                    color = zone[0]
                else:
                    color = zone[1]
                self.cfgxml_data.append(f'                        <property name="z{reg_n}_color">{color}</property>')
                if reg_n < 2:
                    self.cfgxml_data.append(f'                        <property name="z{reg_n}_border">{zone[0]}</property>')

        elif display_region:
            if float(display_region[0][0]) == float(display_min):
                for reg_n, region in enumerate(display_region[:3]):
                    if reg_n < 2:
                        self.cfgxml_data.append(f'                        <property name="z{reg_n}_border">{region[1]}</property>')
                        self.cfgxml_data.append(f'                        <property name="z{reg_n}_color">{region[2]}</property>')
                    else:
                        self.cfgxml_data.append(f'                        <property name="z{reg_n}_color">{region[2]}</property>')
                if len(display_region) < 3:
                    self.cfgxml_data.append('                        <property name="z2_color">green</property>')
            else:
                last_color = "green"
                for reg_n, region in enumerate(display_region[:3]):
                    if reg_n < 2:
                        self.cfgxml_data.append(f'                        <property name="z{reg_n}_border">{region[0]}</property>')
                        self.cfgxml_data.append(f'                        <property name="z{reg_n}_color">{last_color}</property>')
                    last_color = region[2]
                self.cfgxml_data.append(f'                        <property name="z2_color">{last_color}</property>')

        self.cfgxml_data.append("                      </object>")
        self.cfgxml_data.append("              <packing>")
        self.cfgxml_data.append('                <property name="expand">True</property>')
        self.cfgxml_data.append('                <property name="fill">True</property>')
        self.cfgxml_data.append('                <property name="position">1</property>')
        self.cfgxml_data.append("              </packing>")
        self.cfgxml_data.append("            </child>")
        return f"{self.prefix}.{halpin}"

    def draw_bar(self, name, halpin, setup={}, vmin=0, vmax=100):
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_text = setup.get("text", name)
        display_region = setup.get("region", [])
        display_zone = setup.get("zone")

        self.cfgxml_data.append("    <child>")
        self.cfgxml_data.append('      <object class="GtkHBox">')
        self.cfgxml_data.append('        <property name="visible">True</property>')
        self.cfgxml_data.append('        <property name="spacing">2</property>')
        self.draw_title(display_text)
        self.cfgxml_data.append("                    <child>")
        self.cfgxml_data.append(f'                      <object class="HAL_HBar" id="{halpin}">')
        self.cfgxml_data.append('                        <property name="visible">True</property>')
        self.cfgxml_data.append('                        <property name="can_focus">True</property>')
        self.cfgxml_data.append(f'                        <property name="min">{display_min}</property>')
        self.cfgxml_data.append(f'                        <property name="max">{display_max}</property>')
        self.cfgxml_data.append('                        <property name="force_height">27</property>')

        if display_zone:
            for reg_n, zone in enumerate(display_zone[:3]):
                if len(zone) == 1:
                    color = zone[0]
                else:
                    color = zone[1]
                self.cfgxml_data.append(f'                        <property name="z{reg_n}_color">{color}</property>')
                if reg_n < 2:
                    self.cfgxml_data.append(f'                        <property name="z{reg_n}_border">{zone[0]}</property>')

        elif display_region:
            if float(display_region[0][0]) == float(display_min):
                for reg_n, region in enumerate(display_region[:2]):
                    if reg_n < 1:
                        self.cfgxml_data.append(f'                        <property name="z{reg_n}_border">{region[1]}</property>')
                        self.cfgxml_data.append(f'                        <property name="z{reg_n}_color">{region[2]}</property>')
                    else:
                        self.cfgxml_data.append(f'                        <property name="z{reg_n}_color">{region[2]}</property>')
                if len(display_region) < 3:
                    self.cfgxml_data.append('                        <property name="z2_color">green</property>')
            else:
                last_color = "green"
                for reg_n, region in enumerate(display_region[:2]):
                    if reg_n < 1:
                        self.cfgxml_data.append(f'                        <property name="z{reg_n}_border">{region[0]}</property>')
                        self.cfgxml_data.append(f'                        <property name="z{reg_n}_color">{last_color}</property>')
                    last_color = region[2]
                self.cfgxml_data.append(f'                        <property name="z2_color">{last_color}</property>')

        self.cfgxml_data.append("                      </object>")
        self.cfgxml_data.append("                  <packing>")
        self.cfgxml_data.append('                    <property name="expand">True</property>')
        self.cfgxml_data.append('                    <property name="fill">True</property>')
        self.cfgxml_data.append('                    <property name="position">1</property>')
        self.cfgxml_data.append("                  </packing>")
        self.cfgxml_data.append("                    </child>")

        self.cfgxml_data.append("      </object>")
        self.cfgxml_data.append("    </child>")

        return f"{self.prefix}.{halpin}"

    def draw_number_u32(self, name, halpin, setup={}):
        return self.draw_number(name, halpin, hal_type="u32", setup=setup)

    def draw_number_s32(self, name, halpin, setup={}):
        return self.draw_number(name, halpin, hal_type="s32", setup=setup)

    def draw_graph(self, name, halpin, setup={}, hal_type="float"):
        return self.draw_bar(name, halpin, setup=setup)

    def draw_number(self, name, halpin, setup={}, hal_type="float"):
        if hal_type == "float":
            display_format = setup.get("format", "0.2f")
            label_pin_type = 1
        else:
            display_format = setup.get("format", "d")
            label_pin_type = 0
        title = setup.get("title", name)

        self.cfgxml_data.append("    <child>")
        self.cfgxml_data.append('      <object class="GtkHBox">')
        self.cfgxml_data.append('        <property name="visible">True</property>')
        self.cfgxml_data.append('        <property name="spacing">2</property>')
        self.draw_title(title)
        self.cfgxml_data.append("                    <child>")
        self.cfgxml_data.append(f'                      <object class="HAL_Label" id="{halpin}">')
        self.cfgxml_data.append('                        <property name="visible">True</property>')
        self.cfgxml_data.append('                        <property name="label" translatable="yes">label</property>')
        self.cfgxml_data.append(f'                        <property name="text_template">%{display_format}</property>')
        self.cfgxml_data.append("                        <attributes>")
        self.cfgxml_data.append('                          <attribute name="style" value="normal"/>')
        self.cfgxml_data.append('                          <attribute name="weight" value="bold"/>')
        self.cfgxml_data.append("                        </attributes>")
        self.cfgxml_data.append(f'                        <property name="label_pin_type">{label_pin_type}</property>')
        self.cfgxml_data.append("                      </object>")
        self.cfgxml_data.append("                  <packing>")
        self.cfgxml_data.append('                    <property name="expand">False</property>')
        self.cfgxml_data.append('                    <property name="fill">True</property>')
        self.cfgxml_data.append('                    <property name="position">1</property>')
        self.cfgxml_data.append("                  </packing>")
        self.cfgxml_data.append("                    </child>")
        self.cfgxml_data.append("      </object>")
        self.cfgxml_data.append("    </child>")

        return f"{self.prefix}.{halpin}"

    def draw_checkbutton(self, name, halpin, setup={}):
        display_initval = setup.get("initval", 0)
        self.inits.append(f"self.builder.get_object('{halpin}').set_active({display_initval})")
        self.cfgxml_data.append("    <child>")
        self.cfgxml_data.append('      <object class="GtkHBox">')
        self.cfgxml_data.append('        <property name="visible">True</property>')
        self.cfgxml_data.append('        <property name="spacing">2</property>')
        self.draw_title(name)
        self.cfgxml_data.append("                    <child>")
        self.cfgxml_data.append(f'                      <object class="HAL_CheckButton" id="{halpin}">')
        # self.cfgxml_data.append(f'                      <object class="HAL_ToggleButton" id="{halpin}">')
        self.cfgxml_data.append('                        <property name="label" translatable="yes"></property>')
        self.cfgxml_data.append('                        <property name="visible">True</property>')
        self.cfgxml_data.append('                        <property name="can_focus">True</property>')
        self.cfgxml_data.append('                        <property name="receives_default">False</property>')
        self.cfgxml_data.append('                        <property name="draw_indicator">True</property>')
        self.cfgxml_data.append("                      </object>")
        self.cfgxml_data.append("                  <packing>")
        self.cfgxml_data.append('                    <property name="expand">False</property>')
        self.cfgxml_data.append('                    <property name="fill">True</property>')
        self.cfgxml_data.append('                    <property name="position">1</property>')
        self.cfgxml_data.append("                  </packing>")
        self.cfgxml_data.append("                    </child>")

        self.cfgxml_data.append("      </object>")
        self.cfgxml_data.append("    </child>")
        return f"{self.prefix}.{halpin}"

    def draw_led(self, name, halpin, setup={}):
        title = setup.get("title", name)
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
        self.cfgxml_data.append("    <child>")
        self.cfgxml_data.append('      <object class="GtkHBox">')
        self.cfgxml_data.append('        <property name="visible">True</property>')
        self.cfgxml_data.append('        <property name="spacing">2</property>')
        self.draw_title(title)
        self.cfgxml_data.append("                    <child>")
        self.cfgxml_data.append(f'                      <object class="HAL_LED" id="{halpin}">')
        self.cfgxml_data.append('                        <property name="visible">True</property>')
        self.cfgxml_data.append('                        <property name="led-size">7</property>')
        self.cfgxml_data.append(f'                        <property name="pick_color_on">{self.colormapping[on_color]}</property>')
        self.cfgxml_data.append(f'                        <property name="pick_color_off">{self.colormapping[off_color]}</property>')
        self.cfgxml_data.append("                      </object>")
        self.cfgxml_data.append("                  <packing>")
        self.cfgxml_data.append('                    <property name="expand">False</property>')
        self.cfgxml_data.append('                    <property name="fill">True</property>')
        self.cfgxml_data.append('                    <property name="position">1</property>')
        self.cfgxml_data.append("                  </packing>")
        self.cfgxml_data.append("                    </child>")
        self.cfgxml_data.append("      </object>")
        self.cfgxml_data.append("    </child>")
        return f"{self.prefix}.{halpin}"

    def draw_rectled(self, name, halpin, setup={}):
        return self.draw_led(name, halpin, setup=setup)
