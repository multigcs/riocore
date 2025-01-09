class gladevcp:
    def draw_begin(self):
        cfgxml_data = []
        cfgxml_data.append("""<?xml version="1.0"?>
<interface>
  <!-- interface-requires gladevcp 0.0 -->
  <requires lib="gtk+" version="2.16"/>
  <!-- interface-naming-policy project-wide -->
  <object class="GtkWindow" id="window1">

    <child>
      <object class="GtkBox" id="vbox_tab_{name}">
        <property name="spacing">5</property>
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
  <object class="GtkAdjustment" id="adjustment1">
    <property name="upper">100</property>
    <property name="step_increment">1</property>
  </object>
  <object class="GtkAdjustment" id="adjustment2">
    <property name="upper">10</property>
    <property name="step_increment">.1</property>
  </object>
  <object class="GtkListStore" id="offset-list">
    <columns>
      <!-- column-name System -->
      <column type="gchararray"/>
      <!-- column-name Number -->
      <column type="gint"/>
    </columns>
    <data>
      <row>
        <col id="0" translatable="yes">G54</col>
        <col id="1">0</col>
      </row>
      <row>
        <col id="0" translatable="yes">G55</col>
        <col id="1">1</col>
      </row>
      <row>
        <col id="0" translatable="yes">G56</col>
        <col id="1">2</col>
      </row>
      <row>
        <col id="0" translatable="yes">G57</col>
        <col id="1">3</col>
      </row>
      <row>
        <col id="0" translatable="yes">G58</col>
        <col id="1">4</col>
      </row>
      <row>
        <col id="0" translatable="yes">G59</col>
        <col id="1">5</col>
      </row>
      <row>
        <col id="0" translatable="yes">G59.1</col>
        <col id="1">6</col>
      </row>
      <row>
        <col id="0" translatable="yes">G59.2</col>
        <col id="1">7</col>
      </row>
      <row>
        <col id="0" translatable="yes">G59.3</col>
        <col id="1">8</col>
      </row>
    </data>
  </object>
</interface>""")
        return cfgxml_data

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
        <property name="spacing">5</property>
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

    def draw_button(self, name, halpin, setup={}):
        cfgxml_data = []
        return (f"gladevcp.{halpin}-f", cfgxml_data)

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
        cfgxml_data.append('                        <property name="adjustment">adjustment1</property>')
        cfgxml_data.append("                      </object>")
        cfgxml_data.append("                  <packing>")
        cfgxml_data.append('                    <property name="expand">True</property>')
        cfgxml_data.append('                    <property name="fill">True</property>')
        cfgxml_data.append('                    <property name="position">1</property>')
        cfgxml_data.append("                  </packing>")
        cfgxml_data.append("                    </child>")
        cfgxml_data.append("      </object>")
        cfgxml_data.append("    </child>")

        return (f"gladevcp.{halpin}", cfgxml_data)

    def draw_meter(self, name, halpin, setup={}, vmin=0, vmax=100):
        display_max = setup.get("max", vmax)
        display_text = setup.get("text", name)
        display_threshold = setup.get("threshold")
        display_size = setup.get("size", "150")
        cfgxml_data = []
        cfgxml_data.append("                    <child>")
        cfgxml_data.append(f'                      <object class="HAL_HScale" id="{halpin}">')
        cfgxml_data.append('                        <property name="visible">True</property>')
        cfgxml_data.append('                        <property name="can_focus">True</property>')
        cfgxml_data.append('                        <property name="adjustment">adjustment1</property>')
        cfgxml_data.append("                      </object>")
        cfgxml_data.append("                      <packing>")
        cfgxml_data.append('                        <property name="left_attach">1</property>')
        cfgxml_data.append('                        <property name="right_attach">2</property>')
        cfgxml_data.append('                        <property name="top_attach">1</property>')
        cfgxml_data.append('                        <property name="bottom_attach">2</property>')
        cfgxml_data.append("                      </packing>")
        cfgxml_data.append("                    </child>")
        return (f"gladevcp.{halpin}", cfgxml_data)

    def draw_bar(self, name, halpin, setup={}, vmin=0, vmax=100):
        return self.draw_number(name, halpin, setup)

    def draw_number(self, name, halpin, hal_type="float", setup={}):
        display_format = setup.get("format", "0.2f")
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
        cfgxml_data.append('                        <property name="label_pin_type">1</property>')
        cfgxml_data.append("                      </object>")
        cfgxml_data.append("                  <packing>")
        cfgxml_data.append('                    <property name="expand">False</property>')
        cfgxml_data.append('                    <property name="fill">True</property>')
        cfgxml_data.append('                    <property name="position">1</property>')
        cfgxml_data.append("                  </packing>")
        cfgxml_data.append("                    </child>")
        cfgxml_data.append("      </object>")
        cfgxml_data.append("    </child>")

        return (f"gladevcp.{halpin}", cfgxml_data)

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
        cfgxml_data.append(f'                      <object class="HAL_CheckButton" id="{halpin}">')
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
        return (f"gladevcp.{halpin}", cfgxml_data)

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
        return (f"gladevcp.{halpin}", cfgxml_data)
