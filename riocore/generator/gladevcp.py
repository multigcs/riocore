import os


class gladevcp:
    def draw_begin(self, configuration_path, prefix="gladevcp", vcp_pos=None):
        self.configuration_path = configuration_path
        self.prefix = prefix
        self.adjustment = []
        cfgxml_data = []
        cfgxml_data.append("""<?xml version="1.0"?>
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
        return cfgxml_data

    def draw_end(self):
        cfgxml_data = []
        cfgxml_data.append("""

      </object>
    </child>

  </object>
  <object class="EMC_Action_MDI" id="hal_action_mdi1">
    <property name="command">G53 G0  X0 Y0 Z0</property>
  </object>
  <object class="EMC_Action_MDI" id="hal_action_mdi2">
    <property name="command">g0 X0 Y0 Z0</property>
  </object>
  <object class="EMC_ToggleAction_MDI" id="hal_toggleaction_mdi1">
    <property name="command"> O&lt;oword&gt; call [${spin-f}] [${check}] [${toggle}] [${scale}] [${spin-f}]  [${combo-s}]</property>
  </object>
        """)

        cfgxml_data += self.adjustment
        cfgxml_data.append("</interface>")
        return cfgxml_data

    def save(self, cfgxml_data):
        ui_filename = os.path.join(self.configuration_path, "rio-gui.ui")
        gvcp_filename = os.path.join(self.configuration_path, "rio-gui.py")

        handler_py = []
        handler_py.append("""
import hal
import glib
import time

class HandlerClass:
    def __init__(self, halcomp,builder,useropts):
        self.halcomp = halcomp
        self.builder = builder
        self.nhits = 0

def get_handlers(halcomp,builder,useropts):
    return [HandlerClass(halcomp,builder,useropts)]

""")
        open(gvcp_filename, "w").write("\n".join(handler_py))
        open(ui_filename, "w").write("\n".join(cfgxml_data))

    def draw_tabs_begin(self, names):
        cfgxml_data = []
        cfgxml_data.append("""
            <child>
              <object class="GtkNotebook">
                <property name="visible">True</property>
                <property name="can-focus">True</property>

        """)

        return cfgxml_data

    def draw_tabs_end(self):
        cfgxml_data = []

        cfgxml_data.append("""
              </object>
            </child>
        """)

        return cfgxml_data

    def draw_tab_begin(self, name):
        self.tabname = name
        cfgxml_data = []
        cfgxml_data.append(f"""

    <child>
      <object class="GtkBox" id="vbox_tab_{name}">
        <property name="margin">10</property>
        <property name="spacing">10</property>
        <property name="visible">True</property>
        <property name="can-focus">False</property>
        <property name="orientation">vertical</property>


        """)
        return cfgxml_data

    def draw_tab_end(self):
        cfgxml_data = []

        cfgxml_data.append(f"""
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
        return cfgxml_data

    def draw_frame_begin(self, name=None):
        cfgxml_data = []

        cfgxml_data.append(f"""
           <child>

            <object class="GtkFrame">
            <property name="visible">True</property>
            <property name="label_xalign">0.5</property>

            <child type="label">
              <object class="GtkLabel" id="label1text">
                <property name="visible">True</property>
                <property name="label" translatable="yes">{name}</property>
                <property name="use_markup">True</property>
              </object>
            </child>

        """)

        cfgxml_data += self.draw_vbox_begin()
        return cfgxml_data

    def draw_frame_end(self):
        cfgxml_data = []

        cfgxml_data += self.draw_vbox_end()

        cfgxml_data.append("""
            </object>
           </child>
        """)
        return cfgxml_data

    def draw_vbox_begin(self):
        cfgxml_data = []

        cfgxml_data.append("""

    <child>
      <object class="GtkBox">
        <property name="margin">10</property>
        <property name="spacing">10</property>
        <property name="visible">True</property>
        <property name="can-focus">False</property>
        <property name="orientation">vertical</property>

        """)
        return cfgxml_data

    def draw_vbox_end(self):
        cfgxml_data = []
        cfgxml_data.append("              </object>")
        cfgxml_data.append("            </child>")
        return cfgxml_data

    def draw_hbox_begin(self):
        cfgxml_data = []
        cfgxml_data.append("""

    <child>
      <object class="GtkBox">
        <property name="margin">10</property>
        <property name="spacing">10</property>
        <property name="visible">True</property>
        <property name="can-focus">False</property>
        <property name="orientation">horizontal</property>

        """)
        return cfgxml_data

    def draw_hbox_end(self):
        cfgxml_data = []
        cfgxml_data.append("              </object>")
        cfgxml_data.append("            </child>")
        return cfgxml_data

    def draw_button(self, name, halpin, setup={}):
        cfgxml_data = []

        cfgxml_data.append("            <child>")
        cfgxml_data.append(f'              <object class="HAL_Button" id="{halpin}">')
        cfgxml_data.append(f'                <property name="label" translatable="yes">{name}</property>')
        cfgxml_data.append('                <property name="visible">True</property>')
        cfgxml_data.append('                <property name="can-focus">True</property>')
        cfgxml_data.append('                <property name="receives-default">True</property>')
        cfgxml_data.append("              </object>")
        cfgxml_data.append("            </child>")

        return (f"{self.prefix}.{halpin}", cfgxml_data)

    def draw_spinbox(self, name, halpin, setup={}, vmin=0, vmax=100):
        title = setup.get("title", name)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_initval = setup.get("initval", 0.0)
        resolution = setup.get("resolution", 0.1)
        cfgxml_data = []

        cfgxml_data.append("    <child>")
        cfgxml_data.append('      <object class="GtkHBox">')
        cfgxml_data.append('        <property name="visible">True</property>')
        cfgxml_data.append('        <property name="spacing">2</property>')

        cfgxml_data.append("                <child>")
        cfgxml_data.append('                  <object class="GtkLabel">')
        cfgxml_data.append('                    <property name="visible">True</property>')
        cfgxml_data.append('                    <property name="can-focus">False</property>')
        cfgxml_data.append(f'                    <property name="label" translatable="yes">{name}</property>')
        cfgxml_data.append('                     <property name="xpad">6</property>')
        cfgxml_data.append('                     <property name="xalign">0</property>')
        cfgxml_data.append("                  </object>")
        cfgxml_data.append("                  <packing>")
        cfgxml_data.append('                    <property name="expand">True</property>')
        cfgxml_data.append('                    <property name="fill">True</property>')
        cfgxml_data.append('                    <property name="position">1</property>')
        cfgxml_data.append("                  </packing>")
        cfgxml_data.append("                </child>")

        cfgxml_data.append("                    <child>")
        cfgxml_data.append(f'                      <object class="HAL_SpinButton" id="{halpin}">')
        cfgxml_data.append('                        <property name="visible">True</property>')
        cfgxml_data.append('                        <property name="can_focus">True</property>')
        cfgxml_data.append('                        <property name="digits">2</property>')
        cfgxml_data.append(f'                        <property name="adjustment">adj_{halpin}</property>')
        cfgxml_data.append("                      </object>")
        cfgxml_data.append("                  <packing>")
        cfgxml_data.append('                    <property name="expand">True</property>')
        cfgxml_data.append('                    <property name="fill">True</property>')
        cfgxml_data.append('                    <property name="position">1</property>')
        cfgxml_data.append("                  </packing>")
        cfgxml_data.append("                    </child>")
        cfgxml_data.append("      </object>")
        cfgxml_data.append("    </child>")

        self.adjustment.append(f'  <object class="GtkAdjustment" id="adj_{halpin}">')
        self.adjustment.append(f'    <property name="lower">{display_min}</property>')
        self.adjustment.append(f'    <property name="upper">{display_max}</property>')
        self.adjustment.append(f'    <property name="step_increment">{resolution}</property>')
        self.adjustment.append("  </object>")

        return (f"{self.prefix}.{halpin}-f", cfgxml_data)

    def draw_scale(self, name, halpin, setup={}, vmin=0, vmax=100):
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        title = setup.get("title", name)
        cfgxml_data = []

        cfgxml_data.append("    <child>")
        cfgxml_data.append('      <object class="GtkHBox">')
        cfgxml_data.append('        <property name="visible">True</property>')
        cfgxml_data.append('        <property name="spacing">2</property>')

        cfgxml_data.append("                <child>")
        cfgxml_data.append('                  <object class="GtkLabel">')
        cfgxml_data.append('                    <property name="visible">True</property>')
        cfgxml_data.append('                    <property name="can-focus">False</property>')
        cfgxml_data.append(f'                    <property name="label" translatable="yes">{name}</property>')
        cfgxml_data.append('                     <property name="xpad">6</property>')
        cfgxml_data.append('                     <property name="xalign">0</property>')
        cfgxml_data.append("                  </object>")
        cfgxml_data.append("                  <packing>")
        cfgxml_data.append('                    <property name="expand">True</property>')
        cfgxml_data.append('                    <property name="fill">True</property>')
        cfgxml_data.append('                    <property name="position">1</property>')
        cfgxml_data.append("                  </packing>")
        cfgxml_data.append("                </child>")

        cfgxml_data.append("                    <child>")
        cfgxml_data.append(f'                      <object class="HAL_HScale" id="{halpin}">')
        cfgxml_data.append('                        <property name="visible">True</property>')
        cfgxml_data.append('                        <property name="can_focus">True</property>')
        cfgxml_data.append(f'                        <property name="adjustment">adj_{halpin}</property>')
        cfgxml_data.append("                      </object>")
        cfgxml_data.append("                  <packing>")
        cfgxml_data.append('                    <property name="expand">True</property>')
        cfgxml_data.append('                    <property name="fill">True</property>')
        cfgxml_data.append('                    <property name="position">1</property>')
        cfgxml_data.append("                  </packing>")
        cfgxml_data.append("                    </child>")
        cfgxml_data.append("      </object>")
        cfgxml_data.append("    </child>")

        self.adjustment.append(f'  <object class="GtkAdjustment" id="adj_{halpin}">')
        self.adjustment.append(f'    <property name="lower">{display_min}</property>')
        self.adjustment.append(f'    <property name="upper">{display_max}</property>')
        self.adjustment.append("  </object>")

        # -s for s32
        return (f"{self.prefix}.{halpin}", cfgxml_data)

    def draw_meter(self, name, halpin, setup={}, vmin=0, vmax=100):
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_text = setup.get("text", name)
        display_region = setup.get("region", [])
        display_zone = setup.get("zone")
        display_size = setup.get("size", "150")
        cfgxml_data = []

        cfgxml_data.append("                    <child>")
        cfgxml_data.append(f'                      <object class="HAL_Meter" id="{halpin}">')
        cfgxml_data.append('                        <property name="visible">True</property>')
        cfgxml_data.append('                        <property name="can_focus">True</property>')
        cfgxml_data.append(f'                        <property name="label">{display_text}</property>')
        if name != display_text:
            cfgxml_data.append(f'                        <property name="sublabel">{name}</property>')
        cfgxml_data.append(f'                        <property name="min">{display_min}</property>')
        cfgxml_data.append(f'                        <property name="max">{display_max}</property>')
        if display_size:
            cfgxml_data.append(f'                        <property name="force_size">{display_size}</property>')

        if display_zone:
            for reg_n, zone in enumerate(display_zone[:3]):
                if len(zone) == 1:
                    color = zone[0]
                else:
                    color = zone[1]
                cfgxml_data.append(f'                        <property name="z{reg_n}_color">{color}</property>')
                if reg_n < 2:
                    cfgxml_data.append(f'                        <property name="z{reg_n}_border">{zone[0]}</property>')

        elif display_region:
            if float(display_region[0][0]) == float(display_min):
                for reg_n, region in enumerate(display_region[:3]):
                    if reg_n < 2:
                        cfgxml_data.append(f'                        <property name="z{reg_n}_border">{region[1]}</property>')
                        cfgxml_data.append(f'                        <property name="z{reg_n}_color">{region[2]}</property>')
                    else:
                        cfgxml_data.append(f'                        <property name="z{reg_n}_color">{region[2]}</property>')
                if len(display_region) < 3:
                    cfgxml_data.append('                        <property name="z2_color">green</property>')
            else:
                last_color = "green"
                for reg_n, region in enumerate(display_region[:3]):
                    if reg_n < 2:
                        cfgxml_data.append(f'                        <property name="z{reg_n}_border">{region[0]}</property>')
                        cfgxml_data.append(f'                        <property name="z{reg_n}_color">{last_color}</property>')
                    last_color = region[2]
                cfgxml_data.append(f'                        <property name="z2_color">{last_color}</property>')

        cfgxml_data.append("                      </object>")
        cfgxml_data.append("                    </child>")
        return (f"{self.prefix}.{halpin}", cfgxml_data)

    def draw_bar(self, name, halpin, setup={}, vmin=0, vmax=100):
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_text = setup.get("text", name)
        display_region = setup.get("region", [])
        display_zone = setup.get("zone")
        cfgxml_data = []

        cfgxml_data.append("    <child>")
        cfgxml_data.append('      <object class="GtkHBox">')
        cfgxml_data.append('        <property name="visible">True</property>')
        cfgxml_data.append('        <property name="spacing">2</property>')

        cfgxml_data.append("                <child>")
        cfgxml_data.append('                  <object class="GtkLabel">')
        cfgxml_data.append('                    <property name="visible">True</property>')
        cfgxml_data.append('                    <property name="can-focus">False</property>')
        cfgxml_data.append(f'                    <property name="label" translatable="yes">{name}</property>')
        cfgxml_data.append('                     <property name="xpad">6</property>')
        cfgxml_data.append('                     <property name="xalign">0</property>')
        cfgxml_data.append("                  </object>")
        cfgxml_data.append("                  <packing>")
        cfgxml_data.append('                    <property name="expand">True</property>')
        cfgxml_data.append('                    <property name="fill">True</property>')
        cfgxml_data.append('                    <property name="position">1</property>')
        cfgxml_data.append("                  </packing>")
        cfgxml_data.append("                </child>")

        cfgxml_data.append("                    <child>")
        cfgxml_data.append(f'                      <object class="HAL_HBar" id="{halpin}">')
        cfgxml_data.append('                        <property name="visible">True</property>')
        cfgxml_data.append('                        <property name="can_focus">True</property>')
        cfgxml_data.append(f'                        <property name="min">{display_min}</property>')
        cfgxml_data.append(f'                        <property name="max">{display_max}</property>')
        cfgxml_data.append('                        <property name="force_height">27</property>')

        if display_zone:
            for reg_n, zone in enumerate(display_zone[:3]):
                if len(zone) == 1:
                    color = zone[0]
                else:
                    color = zone[1]
                cfgxml_data.append(f'                        <property name="z{reg_n}_color">{color}</property>')
                if reg_n < 2:
                    cfgxml_data.append(f'                        <property name="z{reg_n}_border">{zone[0]}</property>')

        elif display_region:
            if float(display_region[0][0]) == float(display_min):
                for reg_n, region in enumerate(display_region[:2]):
                    if reg_n < 1:
                        cfgxml_data.append(f'                        <property name="z{reg_n}_border">{region[1]}</property>')
                        cfgxml_data.append(f'                        <property name="z{reg_n}_color">{region[2]}</property>')
                    else:
                        cfgxml_data.append(f'                        <property name="z{reg_n}_color">{region[2]}</property>')
                if len(display_region) < 3:
                    cfgxml_data.append('                        <property name="z2_color">green</property>')
            else:
                last_color = "green"
                for reg_n, region in enumerate(display_region[:2]):
                    if reg_n < 1:
                        cfgxml_data.append(f'                        <property name="z{reg_n}_border">{region[0]}</property>')
                        cfgxml_data.append(f'                        <property name="z{reg_n}_color">{last_color}</property>')
                    last_color = region[2]
                cfgxml_data.append(f'                        <property name="z2_color">{last_color}</property>')

        cfgxml_data.append("                      </object>")
        cfgxml_data.append("                  <packing>")
        cfgxml_data.append('                    <property name="expand">True</property>')
        cfgxml_data.append('                    <property name="fill">True</property>')
        cfgxml_data.append('                    <property name="position">1</property>')
        cfgxml_data.append("                  </packing>")
        cfgxml_data.append("                    </child>")

        cfgxml_data.append("      </object>")
        cfgxml_data.append("    </child>")

        return (f"{self.prefix}.{halpin}", cfgxml_data)

    def draw_number_u32(self, name, halpin, setup={}):
        return self.draw_number(name, halpin, hal_type="u32", setup=setup)

    def draw_number_s32(self, name, halpin, setup={}):
        return self.draw_number(name, halpin, hal_type="s32", setup=setup)

    def draw_number(self, name, halpin, hal_type="float", setup={}):
        if hal_type == "float":
            display_format = setup.get("format", "0.2f")
            label_pin_type = 1
        else:
            display_format = setup.get("format", "d")
            label_pin_type = 0

        cfgxml_data = []
        cfgxml_data.append("    <child>")
        cfgxml_data.append('      <object class="GtkHBox">')
        cfgxml_data.append('        <property name="visible">True</property>')
        cfgxml_data.append('        <property name="spacing">2</property>')

        cfgxml_data.append("                <child>")
        cfgxml_data.append('                  <object class="GtkLabel">')
        cfgxml_data.append('                    <property name="visible">True</property>')
        cfgxml_data.append('                    <property name="can-focus">False</property>')
        cfgxml_data.append(f'                    <property name="label" translatable="yes">{name}</property>')
        cfgxml_data.append('                     <property name="xpad">6</property>')
        cfgxml_data.append('                     <property name="xalign">0</property>')
        cfgxml_data.append("                  </object>")
        cfgxml_data.append("                  <packing>")
        cfgxml_data.append('                    <property name="expand">True</property>')
        cfgxml_data.append('                    <property name="fill">True</property>')
        cfgxml_data.append('                    <property name="position">1</property>')
        cfgxml_data.append("                  </packing>")
        cfgxml_data.append("                </child>")

        cfgxml_data.append("                    <child>")
        cfgxml_data.append(f'                      <object class="HAL_Label" id="{halpin}">')
        cfgxml_data.append('                        <property name="visible">True</property>')
        cfgxml_data.append('                        <property name="label" translatable="yes">label</property>')
        cfgxml_data.append(f'                        <property name="text_template">%{display_format}</property>')
        cfgxml_data.append("                        <attributes>")
        cfgxml_data.append('                          <attribute name="style" value="normal"/>')
        cfgxml_data.append('                          <attribute name="weight" value="bold"/>')
        cfgxml_data.append("                        </attributes>")
        cfgxml_data.append(f'                        <property name="label_pin_type">{label_pin_type}</property>')
        cfgxml_data.append("                      </object>")
        cfgxml_data.append("                  <packing>")
        cfgxml_data.append('                    <property name="expand">False</property>')
        cfgxml_data.append('                    <property name="fill">True</property>')
        cfgxml_data.append('                    <property name="position">1</property>')
        cfgxml_data.append("                  </packing>")
        cfgxml_data.append("                    </child>")
        cfgxml_data.append("      </object>")
        cfgxml_data.append("    </child>")

        return (f"{self.prefix}.{halpin}", cfgxml_data)

    def draw_checkbutton(self, name, halpin, setup={}):
        cfgxml_data = []
        cfgxml_data.append("    <child>")
        cfgxml_data.append('      <object class="GtkHBox">')
        cfgxml_data.append('        <property name="visible">True</property>')
        cfgxml_data.append('        <property name="spacing">2</property>')

        cfgxml_data.append("                <child>")
        cfgxml_data.append('                  <object class="GtkLabel">')
        cfgxml_data.append('                    <property name="visible">True</property>')
        cfgxml_data.append('                    <property name="can-focus">False</property>')
        cfgxml_data.append(f'                    <property name="label" translatable="yes">{name}</property>')
        cfgxml_data.append('                     <property name="xpad">6</property>')
        cfgxml_data.append('                     <property name="xalign">0</property>')
        cfgxml_data.append("                  </object>")
        cfgxml_data.append("                  <packing>")
        cfgxml_data.append('                    <property name="expand">True</property>')
        cfgxml_data.append('                    <property name="fill">True</property>')
        cfgxml_data.append('                    <property name="position">1</property>')
        cfgxml_data.append("                  </packing>")

        cfgxml_data.append("                </child>")

        cfgxml_data.append("                    <child>")
        # cfgxml_data.append(f'                      <object class="HAL_CheckButton" id="{halpin}">')
        cfgxml_data.append(f'                      <object class="HAL_ToggleButton" id="{halpin}">')
        cfgxml_data.append('                        <property name="label" translatable="yes"></property>')
        cfgxml_data.append('                        <property name="visible">True</property>')
        cfgxml_data.append('                        <property name="can_focus">True</property>')
        cfgxml_data.append('                        <property name="receives_default">False</property>')
        cfgxml_data.append('                        <property name="draw_indicator">True</property>')
        cfgxml_data.append("                      </object>")
        cfgxml_data.append("                  <packing>")
        cfgxml_data.append('                    <property name="expand">False</property>')
        cfgxml_data.append('                    <property name="fill">True</property>')
        cfgxml_data.append('                    <property name="position">1</property>')
        cfgxml_data.append("                  </packing>")
        cfgxml_data.append("                    </child>")

        cfgxml_data.append("      </object>")
        cfgxml_data.append("    </child>")
        return (f"{self.prefix}.{halpin}", cfgxml_data)

    def draw_led(self, name, halpin, setup={}):
        cfgxml_data = []
        cfgxml_data.append("    <child>")
        cfgxml_data.append('      <object class="GtkHBox">')
        cfgxml_data.append('        <property name="visible">True</property>')
        cfgxml_data.append('        <property name="spacing">2</property>')

        cfgxml_data.append("                <child>")
        cfgxml_data.append('                  <object class="GtkLabel">')
        cfgxml_data.append('                    <property name="visible">True</property>')
        cfgxml_data.append('                    <property name="can-focus">False</property>')
        cfgxml_data.append(f'                    <property name="label" translatable="yes">{name}</property>')
        cfgxml_data.append('                     <property name="xpad">6</property>')
        cfgxml_data.append('                     <property name="xalign">0</property>')
        cfgxml_data.append("                  </object>")
        cfgxml_data.append("                  <packing>")
        cfgxml_data.append('                    <property name="expand">True</property>')
        cfgxml_data.append('                    <property name="fill">True</property>')
        cfgxml_data.append('                    <property name="position">1</property>')
        cfgxml_data.append("                  </packing>")
        cfgxml_data.append("                </child>")

        cfgxml_data.append("                    <child>")
        cfgxml_data.append(f'                      <object class="HAL_LED" id="{halpin}">')
        cfgxml_data.append('                        <property name="visible">True</property>')
        cfgxml_data.append('                        <property name="pick_color_on">#ffffb7b90b5c</property>')
        cfgxml_data.append('                        <property name="pick_color_off">#000000000000</property>')
        cfgxml_data.append("                      </object>")
        cfgxml_data.append("                  <packing>")
        cfgxml_data.append('                    <property name="expand">False</property>')
        cfgxml_data.append('                    <property name="fill">True</property>')
        cfgxml_data.append('                    <property name="position">1</property>')
        cfgxml_data.append("                  </packing>")
        cfgxml_data.append("                    </child>")

        cfgxml_data.append("      </object>")
        cfgxml_data.append("    </child>")
        return (f"{self.prefix}.{halpin}", cfgxml_data)
