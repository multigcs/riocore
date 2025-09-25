from lxml import etree
import os


class tncvcp:
    colormapping = {
        "white": "<red>255</red><green>255</green><blue>255</blue>",
        "black": "<red>0</red><green>0</green><blue>0</blue>",
        "yellow": "<red>255</red><green>255</green><blue>0</blue>",
        "red": "<red>255</red><green>0</green><blue>0</blue>",
        "green": "<red>0</red><green>255</green><blue>0</blue>",
        "blue": "<red>0</red><green>0</green><blue>255</blue>",
    }

    def __init__(self, prefix="rio-gui", vcp_pos=None):
        self.prefix = prefix
        self.vcp_pos = vcp_pos

    def draw_begin(self):
        self.tmp = []
        self.cfgxml_data = []
        self.cfgxml_data.append("")

    def draw_end(self):
        pass

    def xml(self):
        return "\n".join(self.cfgxml_data).strip()

    def check(self, configuration_path):
        ui_filename = os.path.join(configuration_path, "libtnc/ui/window.ui")
        # read template
        xml_template = open(ui_filename, "rb").read()
        root = etree.fromstring(xml_template)
        # check
        for element in root.xpath("..//widget[@name='rioTab']"):
            return True
        print("ERROR: tncvcp: no 'QTabWidget' named 'rioTab' found")
        return False

    def save(self, configuration_path):
        ui_filename = os.path.join(configuration_path, "libtnc/ui/window.ui")

        # read rio xml-gui
        rio_items = etree.fromstring("\n".join(self.cfgxml_data).strip())
        # read template
        xml_template = open(ui_filename, "rb").read()
        root = etree.fromstring(xml_template)
        # merge
        for element in root.xpath("..//widget[@name='rioTab']"):
            # remove old sub elements
            for child in element:
                if child.tag == "property":
                    continue
                keep = False
                for sub in child:
                    if sub.tag in {"widget", "layout"}:
                        keep = True
                        break
                if not keep:
                    element.remove(child)
            # adding new sub elements
            for child in rio_items:
                element.append(child)
        self.formated = etree.tostring(root, pretty_print=True).decode()
        open(ui_filename, "w").write(self.formated)

    def add_property(self, name, value, ptype="number"):
        self.cfgxml_data.append(f'      <property name="{name}">')
        self.cfgxml_data.append(f"       <{ptype}>{value}</{ptype}>")
        self.cfgxml_data.append("      </property>")

    def draw_tabs_begin(self, names):
        self.cfgxml_data.append("    <rio_items>")

    def draw_tabs_end(self):
        self.cfgxml_data.append("    </rio_items>")

    def draw_tab_begin(self, name):
        self.tab_name = name
        self.tmp = self.cfgxml_data
        self.cfgxml_data = []

    def draw_tab_end(self):
        # remove empty tabs
        if self.cfgxml_data:
            tabdata = self.cfgxml_data
            self.cfgxml_data = []
            self.cfgxml_data.append(f'      <widget class="QWidget" name="tab_{self.tab_name}">')
            self.cfgxml_data.append('       <attribute name="title">')
            self.cfgxml_data.append(f"        <string>{self.tab_name}</string>")
            self.cfgxml_data.append("       </attribute>")
            self.cfgxml_data.append('       <layout class="QVBoxLayout" name="layout_stat">')
            self.add_property("spacing", "0")
            self.add_property("leftMargin", "0")
            self.add_property("topMargin", "0")
            self.add_property("rightMargin", "0")
            self.add_property("bottomMargin", "0")
            self.draw_vbox_begin()
            self.cfgxml_data += tabdata
            self.cfgxml_data.append("           <item>")
            self.cfgxml_data.append('            <widget class="QWidget" name="widget" native="true"/>')
            self.cfgxml_data.append("           </item>")
            self.draw_vbox_end()
            self.cfgxml_data.append("        </layout>")
            self.cfgxml_data.append("      </widget>")
        self.cfgxml_data = self.tmp + self.cfgxml_data
        self.tmp = []

    def draw_frame_begin(self, name=None):
        self.cfgxml_data.append("     <item>")
        self.cfgxml_data.append('   <widget class="QGroupBox" name="groupBox_7">')
        self.cfgxml_data.append('    <property name="sizePolicy">')
        self.cfgxml_data.append('     <sizepolicy hsizetype="Minimum" vsizetype="Fixed">')
        self.cfgxml_data.append("      <horstretch>0</horstretch>")
        self.cfgxml_data.append("      <verstretch>0</verstretch>")
        self.cfgxml_data.append("     </sizepolicy>")
        self.cfgxml_data.append("    </property>")
        if name:
            self.cfgxml_data.append('    <property name="title">')
            self.cfgxml_data.append(f"     <string>{name}</string>")
            self.cfgxml_data.append("    </property>")

        self.cfgxml_data.append('      <layout class="QVBoxLayout" name="verticalLayout_5">')
        self.add_property("leftMargin", "2")
        self.add_property("topMargin", "2")
        self.add_property("rightMargin", "2")
        self.add_property("bottomMargin", "2")

    def draw_frame_end(self):
        self.cfgxml_data.append("      </layout>")
        self.cfgxml_data.append("   </widget>")
        self.cfgxml_data.append("     </item>")

    def draw_vbox_begin(self):
        self.cfgxml_data.append("     <item>")
        self.cfgxml_data.append('      <layout class="QVBoxLayout" name="verticalLayout_5">')
        self.add_property("leftMargin", "5")
        self.add_property("topMargin", "10")
        self.add_property("rightMargin", "5")
        self.add_property("bottomMargin", "10")

    def draw_vbox_end(self):
        self.cfgxml_data.append("      </layout>")
        self.cfgxml_data.append("     </item>")

    def draw_hbox_begin(self):
        self.cfgxml_data.append("     <item>")
        self.cfgxml_data.append('      <layout class="QHBoxLayout" name="hosizontalLayout_3">')
        self.add_property("leftMargin", "5")
        self.add_property("topMargin", "0")
        self.add_property("rightMargin", "5")
        self.add_property("bottomMargin", "0")

    def draw_hbox_end(self):
        self.cfgxml_data.append("      </layout>")
        self.cfgxml_data.append("     </item>")

    def draw_button(self, name, halpin, setup={}):
        halpin = halpin.replace("_", "-")
        self.cfgxml_data.append(f"""
              <item>
               <widget class="HalButton" name="rio.{halpin}">
                <property name="pinBaseName" stdset="0">
                  <string>{halpin}</string>
                </property>
                <property name="text">
                 <string>{name}</string>
                </property>
               </widget>
              </item>
        """)
        return f"{self.prefix}.{halpin}.out"

    def draw_title(self, title):
        self.cfgxml_data.append("    <item>")
        self.cfgxml_data.append('     <widget class="QLabel">')
        self.add_property("text", title, ptype="string")
        self.add_property("indent", "4")
        if self.vcp_pos == "RIGHT":
            self.cfgxml_data.append('             <property name="styleSheet">')
            self.cfgxml_data.append('              <string notr="true">QLabel {')
            self.cfgxml_data.append("    color: rgb(235, 235, 235);")
            self.cfgxml_data.append("}</string>")
            self.cfgxml_data.append("             </property>")
        self.cfgxml_data.append("     </widget>")
        self.cfgxml_data.append("    </item>")

    def draw_scale(self, name, halpin, setup={}, vmin=0, vmax=100):
        halpin = halpin.replace("_", "-")
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        title = setup.get("title", name)
        self.draw_hbox_begin()
        self.draw_title(title)
        self.cfgxml_data.append("    <item>")
        self.cfgxml_data.append(f'     <widget class="HalSlider" name="rio.{halpin}">')
        self.cfgxml_data.append('        <property name="pinBaseName" stdset="0">')
        self.cfgxml_data.append(f'          <string>{halpin}</string>')
        self.cfgxml_data.append('        </property>')
        self.cfgxml_data.append('         <property name="sizePolicy">')
        self.cfgxml_data.append('          <sizepolicy hsizetype="Preferred" vsizetype="Minimum">')
        self.cfgxml_data.append("           <horstretch>0</horstretch>")
        self.cfgxml_data.append("           <verstretch>0</verstretch>")
        self.cfgxml_data.append("          </sizepolicy>")
        self.cfgxml_data.append("         </property>")
        self.add_property("minimum", int(int(display_min) * 100.0))
        self.add_property("maximum", int(int(display_max) * 100.0))
        self.add_property("orientation", "Qt::Horizontal", ptype="enum")
        self.cfgxml_data.append("     </widget>")
        self.cfgxml_data.append("    </item>")
        self.draw_hbox_end()
        return f"{self.prefix}.{halpin}.out-f"

    def draw_meter(self, name, halpin, setup={}, vmin=0, vmax=100):
        halpin = halpin.replace("_", "-")
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        # display_text = setup.get("text", name)
        # display_threshold = setup.get("threshold")
        # display_size = setup.get("size", "150")
        self.cfgxml_data.append("   <item>")
        self.cfgxml_data.append(f'       <widget class="HalBarIndicator" name="rio.{halpin}">')
        self.cfgxml_data.append('        <property name="pinBaseName" stdset="0">')
        self.cfgxml_data.append(f'          <string>{halpin}</string>')
        self.cfgxml_data.append('        </property>')
        self.add_property("minimum", int(display_min))
        self.add_property("maximum", int(display_max))
        self.cfgxml_data.append("       </widget>")
        self.cfgxml_data.append("   </item>")
        return f"{self.prefix}.{halpin}.in-f"

    def draw_bar(self, name, halpin, setup={}, vmin=0, vmax=100):
        halpin = halpin.replace("_", "-")
        return self.draw_number(name, halpin, setup)

    def draw_number_u32(self, name, halpin, setup={}):
        halpin = halpin.replace("_", "-")
        return self.draw_number(name, halpin, hal_type="u32", setup=setup)

    def draw_number_s32(self, name, halpin, setup={}):
        halpin = halpin.replace("_", "-")
        return self.draw_number(name, halpin, hal_type="s32", setup=setup)

    def draw_graph(self, name, halpin, setup={}, hal_type="float"):
        return self.draw_bar(name, halpin, setup=setup)

    def draw_number(self, name, halpin, setup={}, hal_type="float"):
        halpin = halpin.replace("_", "-")
        self.draw_hbox_begin()
        self.draw_title(name)
        self.cfgxml_data.append("    <item>")
        self.cfgxml_data.append(f'     <widget class="HalLabel" name="rio.{halpin}">')
        self.cfgxml_data.append('        <property name="pinBaseName" stdset="0">')
        self.cfgxml_data.append(f'          <string>{halpin}</string>')
        self.cfgxml_data.append('        </property>')
        self.cfgxml_data.append('      <property name="sizePolicy">')
        self.cfgxml_data.append('       <sizepolicy hsizetype="Minimum" vsizetype="Fixed">')
        self.cfgxml_data.append("        <horstretch>0</horstretch>")
        self.cfgxml_data.append("        <verstretch>0</verstretch>")
        self.cfgxml_data.append("       </sizepolicy>")
        self.cfgxml_data.append("      </property>")
        self.add_property("alignment", "Qt::AlignRight|Qt::AlignTrailing|Qt::AlignVCenter", ptype="set")
        self.cfgxml_data.append('      <property name="styleSheet">')
        self.cfgxml_data.append('       <string notr="true">font: 20pt &quot;Lato Heavy&quot;;</string>')
        self.cfgxml_data.append("      </property>")
        if self.vcp_pos == "RIGHT":
            self.cfgxml_data.append('             <property name="styleSheet">')
            self.cfgxml_data.append('              <string notr="true">QLabel {')
            self.cfgxml_data.append("    color: rgb(235, 235, 235);")
            self.cfgxml_data.append("}</string>")
            self.cfgxml_data.append("             </property>")
        self.cfgxml_data.append("     </widget>")
        self.cfgxml_data.append("    </item>")
        self.draw_hbox_end()
        return f"{self.prefix}.{halpin}.in"

    def draw_checkbutton(self, name, halpin, setup={}):
        halpin = halpin.replace("_", "-")
        self.draw_hbox_begin()
        self.draw_title(name)
        self.cfgxml_data.append("    <item>")
        self.cfgxml_data.append(f'     <widget class="HalCheckBox" name="rio.{halpin}">')
        self.cfgxml_data.append('        <property name="pinBaseName" stdset="0">')
        self.cfgxml_data.append(f'          <string>{halpin}</string>')
        self.cfgxml_data.append('        </property>')
        self.cfgxml_data.append(' <property name="sizePolicy">')
        self.cfgxml_data.append('  <sizepolicy hsizetype="Fixed" vsizetype="Fixed">')
        self.cfgxml_data.append("   <horstretch>0</horstretch>")
        self.cfgxml_data.append("   <verstretch>0</verstretch>")
        self.cfgxml_data.append("  </sizepolicy>")
        self.cfgxml_data.append(" </property>")
        self.cfgxml_data.append(' <property name="minimumSize">')
        self.cfgxml_data.append("  <size>")
        self.cfgxml_data.append("   <width>32</width>")
        self.cfgxml_data.append("   <height>32</height>")
        self.cfgxml_data.append("  </size>")
        self.cfgxml_data.append(" </property>")
        self.cfgxml_data.append("     </widget>")
        self.cfgxml_data.append("    </item>")
        self.draw_hbox_end()
        return f"{self.prefix}.{halpin}.checked"

    def draw_led(self, name, halpin, setup={}):
        title = setup.get("title", name)
        halpin = halpin.replace("_", "-")
        color = setup.get("color")
        on_color = "yellow"
        # off_color = "red"
        if color:
            on_color = color
            # off_color = setup.get("off_color", "black")
        elif halpin.endswith(".R"):
            on_color = "red"
            # off_color = setup.get("off_color", "black")
        elif halpin.endswith(".G"):
            on_color = "green"
            # off_color = setup.get("off_color", "black")
        elif halpin.endswith(".B"):
            on_color = "blue"
            # off_color = setup.get("off_color", "black")
        self.draw_hbox_begin()
        self.draw_title(title)
        self.cfgxml_data.append("    <item>")
        self.cfgxml_data.append(f'     <widget class="HalLedIndicator" name="rio.{halpin}">')
        self.cfgxml_data.append('        <property name="pinBaseName" stdset="0">')
        self.cfgxml_data.append(f'          <string>{halpin}</string>')
        self.cfgxml_data.append('        </property>')
        self.cfgxml_data.append('        <property name="sizePolicy">')
        self.cfgxml_data.append('         <sizepolicy hsizetype="Fixed" vsizetype="Fixed">')
        self.cfgxml_data.append("          <horstretch>0</horstretch>")
        self.cfgxml_data.append("          <verstretch>0</verstretch>")
        self.cfgxml_data.append("         </sizepolicy>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="minimumSize">')
        self.cfgxml_data.append("         <size>")
        self.cfgxml_data.append("          <width>32</width>")
        self.cfgxml_data.append("          <height>32</height>")
        self.cfgxml_data.append("         </size>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="color">')
        self.cfgxml_data.append("          <color>")
        self.cfgxml_data.append(f"            {self.colormapping[on_color]}")
        self.cfgxml_data.append("          </color>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="maximumSize">')
        self.cfgxml_data.append("         <size>")
        self.cfgxml_data.append("          <width>32</width>")
        self.cfgxml_data.append("          <height>32</height>")
        self.cfgxml_data.append("         </size>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append("     </widget>")
        self.cfgxml_data.append("    </item>")
        self.draw_hbox_end()
        return f"{self.prefix}.{halpin}.on"

    def draw_rectled(self, name, halpin, setup={}):
        return self.draw_led(name, halpin, setup=setup)
