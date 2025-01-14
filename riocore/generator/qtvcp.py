import os


class qtvcp:
    #
    # wget "https://raw.githubusercontent.com/LinuxCNC/linuxcnc/master/lib/python/qtvcp/designer/install_script"
    #

    def __init__(self, prefix="qtvcp.rio-gui", vcp_pos=None):
        self.prefix = prefix
        self.vcp_pos = vcp_pos

    def draw_begin(self):
        self.cfgxml_data = []

        self.cfgxml_data.append("""<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>350</width>
    <height>412</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>MainWindow</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <layout class="QVBoxLayout" name="verticalLayout">
""")
        self.cfgxml_data.append("")
        self.cfgxml_data.append("           <item>")
        self.cfgxml_data.append('            <widget class="QGroupBox" name="groupBox_rio">')
        self.cfgxml_data.append('             <property name="title">')
        self.cfgxml_data.append("              <string>RIO</string>")
        self.cfgxml_data.append("             </property>")
        self.cfgxml_data.append('           <property name="sizePolicy">')
        self.cfgxml_data.append('            <sizepolicy hsizetype="Minimum" vsizetype="Preferred">')
        self.cfgxml_data.append("             <horstretch>0</horstretch>")
        self.cfgxml_data.append("             <verstretch>0</verstretch>")
        self.cfgxml_data.append("            </sizepolicy>")
        self.cfgxml_data.append("           </property>")
        self.cfgxml_data.append('           <property name="minimumSize">')
        self.cfgxml_data.append("            <size>")
        self.cfgxml_data.append("             <width>200</width>")
        self.cfgxml_data.append("             <height>0</height>")
        self.cfgxml_data.append("            </size>")
        self.cfgxml_data.append("           </property>")
        self.cfgxml_data.append('             <property name="alignment">')
        self.cfgxml_data.append("              <set>Qt::AlignCenter</set>")
        self.cfgxml_data.append("             </property>")
        self.cfgxml_data.append('             <layout class="QVBoxLayout" name="verticalLayout_30">')
        self.cfgxml_data.append('              <property name="spacing">')
        self.cfgxml_data.append("               <number>6</number>")
        self.cfgxml_data.append("              </property>")
        self.cfgxml_data.append('              <property name="leftMargin">')
        self.cfgxml_data.append("               <number>2</number>")
        self.cfgxml_data.append("              </property>")
        self.cfgxml_data.append('              <property name="topMargin">')
        self.cfgxml_data.append("               <number>2</number>")
        self.cfgxml_data.append("              </property>")
        self.cfgxml_data.append('              <property name="rightMargin">')
        self.cfgxml_data.append("               <number>2</number>")
        self.cfgxml_data.append("              </property>")
        self.cfgxml_data.append('              <property name="bottomMargin">')
        self.cfgxml_data.append("               <number>2</number>")
        self.cfgxml_data.append("              </property>")

    def draw_end(self):
        self.cfgxml_data.append("             </layout>")
        self.cfgxml_data.append("            </widget>")
        self.cfgxml_data.append("           </item>")
        self.cfgxml_data.append("")
        self.cfgxml_data.append("""
   </layout>
  </widget>
  <widget class="QMenuBar" name="menubar">
   <property name="geometry">
    <rect>
     <x>0</x>
     <y>0</y>
     <width>350</width>
     <height>24</height>
    </rect>
   </property>
  </widget>
  <widget class="QStatusBar" name="statusbar"/>
 </widget>
 <customwidgets>
  <customwidget>
   <class>Gauge</class>
   <extends>QWidget</extends>
   <header>qtvcp.widgets.round_gauge</header>
  </customwidget>
  <customwidget>
   <class>CheckBox</class>
   <extends>QCheckBox</extends>
   <header>qtvcp.widgets.simple_widgets</header>
  </customwidget>
  <customwidget>
   <class>IndicatedPushButton</class>
   <extends>QPushButton</extends>
   <header>qtvcp.widgets.simple_widgets</header>
  </customwidget>
  <customwidget>
   <class>PushButton</class>
   <extends>IndicatedPushButton</extends>
   <header>qtvcp.widgets.simple_widgets</header>
  </customwidget>
  <customwidget>
   <class>LED</class>
   <extends>QWidget</extends>
   <header>qtvcp.widgets.led_widget</header>
  </customwidget>
  <customwidget>
   <class>HALLabel</class>
   <extends>QLabel</extends>
   <header>qtvcp.widgets.hal_label</header>
  </customwidget>
  <customwidget>
   <class>ScreenOptions</class>
   <extends>QWidget</extends>
   <header>qtvcp.widgets.screen_options</header>
   <container>1</container>
  </customwidget>
  <customwidget>
   <class>Slider</class>
   <extends>QSlider</extends>
   <header>qtvcp.widgets.simple_widgets</header>
  </customwidget>
 </customwidgets>
 <resources/>
 <slots>
  <slot>applyClicked()</slot>
  <slot>updateCombo()</slot>
 </slots>
</ui>""")

    def xml(self):
        return "\n".join(self.cfgxml_data)

    def save(self, configuration_path):
        ui_filename = os.path.join(configuration_path, "rio-gui.ui")
        py_filename = os.path.join(configuration_path, "rio-gui_handler.py")

        handler_py = []
        handler_py.append("")
        handler_py.append("from qtvcp.core import Status, Action")
        handler_py.append("from qtvcp import logger")
        handler_py.append("")
        handler_py.append("STATUS = Status()")
        handler_py.append("ACTION = Action()")
        handler_py.append("LOG = logger.getLogger(__name__)")
        handler_py.append("")
        handler_py.append("class HandlerClass:")
        handler_py.append("")
        handler_py.append("    def __init__(self, halcomp,widgets,paths):")
        handler_py.append("        self.hal = halcomp")
        handler_py.append("        self.w = widgets")
        handler_py.append("        self.PATHS = paths")
        handler_py.append("")
        handler_py.append("    def initialized__(self):")
        handler_py.append("        pass")
        handler_py.append("")
        handler_py.append("    def __getitem__(self, item):")
        handler_py.append("        return getattr(self, item)")
        handler_py.append("    def __setitem__(self, item, value):")
        handler_py.append("        return setattr(self, item, value)")
        handler_py.append("")
        handler_py.append("def get_handlers(halcomp,widgets,paths):")
        handler_py.append("     return [HandlerClass(halcomp,widgets,paths)]")
        handler_py.append("")
        open(py_filename, "w").write("\n".join(handler_py))
        open(ui_filename, "w").write("\n".join(self.cfgxml_data))

    def add_property(self, name, value, ptype="number"):
        self.cfgxml_data.append(f'      <property name="{name}">')
        self.cfgxml_data.append(f"       <{ptype}>{value}</{ptype}>")
        self.cfgxml_data.append("      </property>")

    def draw_tabs_begin(self, names):
        self.cfgxml_data.append("    <item>")
        self.cfgxml_data.append('     <widget class="QTabWidget" name="tabWidget_setup">')

    def draw_tabs_end(self):
        self.cfgxml_data.append("     </widget>")
        self.cfgxml_data.append("    </item>")

    def draw_tab_begin(self, name):
        self.cfgxml_data.append(f'      <widget class="QWidget" name="tab_{name}">')
        self.cfgxml_data.append('       <attribute name="title">')
        self.cfgxml_data.append(f"        <string>{name}</string>")
        self.cfgxml_data.append("       </attribute>")
        self.cfgxml_data.append('       <layout class="QVBoxLayout" name="layout_stat">')
        self.add_property("spacing", "0")
        self.add_property("leftMargin", "0")
        self.add_property("topMargin", "0")
        self.add_property("rightMargin", "0")
        self.add_property("bottomMargin", "0")
        self.draw_vbox_begin()

    def draw_tab_end(self):
        self.cfgxml_data.append("           <item>")
        self.cfgxml_data.append('            <widget class="QWidget" native="true"/>')
        self.cfgxml_data.append("           </item>")
        self.draw_vbox_end()
        self.cfgxml_data.append("        </layout>")
        self.cfgxml_data.append("      </widget>")

    def draw_frame_begin(self, name=None):
        if not name:
            name = "frame"
        self.cfgxml_data.append("""
    <item>
     <widget class="QFrame" name="frame">
      <property name="frameShape">
       <enum>QFrame::StyledPanel</enum>
      </property>
      <property name="frameShadow">
       <enum>QFrame::Sunken</enum>
      </property>
      <layout class="QVBoxLayout">
        """)

    def draw_frame_end(self):
        self.cfgxml_data.append("""
      </layout>
     </widget>
    </item>
        """)

    def draw_vbox_begin(self):
        self.cfgxml_data.append("     <item>")
        self.cfgxml_data.append('      <layout class="QVBoxLayout">')
        self.add_property("leftMargin", "5")
        self.add_property("topMargin", "5")
        self.add_property("rightMargin", "5")
        self.add_property("bottomMargin", "5")

    def draw_vbox_end(self):
        self.cfgxml_data.append("      </layout>")
        self.cfgxml_data.append("     </item>")

    def draw_hbox_begin(self):
        self.cfgxml_data.append("     <item>")
        self.cfgxml_data.append('      <layout class="QHBoxLayout">')
        self.add_property("leftMargin", "5")
        self.add_property("topMargin", "5")
        self.add_property("rightMargin", "5")
        self.add_property("bottomMargin", "5")

    def draw_hbox_end(self):
        self.cfgxml_data.append("      </layout>")
        self.cfgxml_data.append("     </item>")

    def draw_title(self, title):
        self.cfgxml_data.append("    <item>")
        self.cfgxml_data.append('     <widget class="QLabel">')
        self.add_property("text", title, ptype="string")
        self.add_property("indent", "4")
        self.cfgxml_data.append("     </widget>")
        self.cfgxml_data.append("    </item>")

    def draw_button(self, name, halpin, setup={}):
        self.cfgxml_data.append(f"""
              <item>
               <widget class="PushButton" name="{halpin}">
                <property name="text">
                 <string>{name.upper()}</string>
                </property>
                 <property name="minimumSize">
                  <size>
                   <width>70</width>
                   <height>50</height>
                  </size>
                 </property>
                 <property name="maximumSize">
                  <size>
                   <width>16777215</width>
                   <height>54</height>
                  </size>
                 </property>
                <property name="styleSheet">
                 <string notr="true">
QLabel {{
    color: rgb(235, 235, 235);
}}
                 </string>
                </property>
               </widget>
              </item>
        """)
        return f"{self.prefix}.{halpin}"

    def draw_scale(self, name, halpin, setup={}, vmin=0, vmax=100):
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        title = setup.get("title", name)
        self.draw_hbox_begin()
        self.draw_title(title)
        self.cfgxml_data.append("    <item>")
        self.cfgxml_data.append(f'     <widget class="Slider" name="{halpin}">')
        self.add_property("minimum", int(display_min))
        self.add_property("maximum", int(display_max))
        self.add_property("orientation", "Qt::Horizontal", ptype="enum")
        self.cfgxml_data.append("     </widget>")
        self.cfgxml_data.append("    </item>")
        self.draw_hbox_end()
        return f"{self.prefix}.{halpin}-f"

    def draw_meter(self, name, halpin, setup={}, vmin=0, vmax=100):
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_text = setup.get("text", name)
        display_threshold = setup.get("threshold")
        display_size = setup.get("size", "150")
        self.cfgxml_data.append("   <item>")
        self.cfgxml_data.append(f'       <widget class="Gauge" name="{halpin}">')
        self.cfgxml_data.append('        <property name="minimumSize">')
        self.cfgxml_data.append("         <size>")
        self.cfgxml_data.append(f"          <width>{display_size}</width>")
        self.cfgxml_data.append(f"          <height>{display_size}</height>")
        self.cfgxml_data.append("         </size>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="min_value" stdset="0">')
        self.cfgxml_data.append(f"         <number>{int(display_min)}</number>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="max_value" stdset="0">')
        self.cfgxml_data.append(f"         <number>{int(display_max)}</number>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="min_reading" stdset="0">')
        self.cfgxml_data.append(f"         <number>{int(display_min)}</number>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="max_reading" stdset="0">')
        self.cfgxml_data.append(f"         <number>{int(display_max)}</number>")
        self.cfgxml_data.append("        </property>")
        if display_threshold:
            self.cfgxml_data.append('        <property name="threshold" stdset="0">')
            self.cfgxml_data.append(f"         <number>{display_threshold}</number>")
            self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="num_ticks" stdset="0">')
        self.cfgxml_data.append("         <number>9</number>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="gauge_label" stdset="0">')
        self.cfgxml_data.append(f"         <string>{display_text}</string>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="zone1_color" stdset="0">')
        self.cfgxml_data.append("         <color>")
        self.cfgxml_data.append("          <red>0</red>")
        self.cfgxml_data.append("          <green>100</green>")
        self.cfgxml_data.append("          <blue>0</blue>")
        self.cfgxml_data.append("         </color>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="zone2_color" stdset="0">')
        self.cfgxml_data.append("         <color>")
        self.cfgxml_data.append("          <red>200</red>")
        self.cfgxml_data.append("          <green>0</green>")
        self.cfgxml_data.append("          <blue>0</blue>")
        self.cfgxml_data.append("         </color>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('      <property name="halpin_name" stdset="0">')
        self.cfgxml_data.append(f"       <string>{halpin}</string>")
        self.cfgxml_data.append("      </property>")
        self.cfgxml_data.append('      <property name="halpin_option" stdset="0">')
        self.cfgxml_data.append("       <bool>true</bool>")
        self.cfgxml_data.append("      </property>")
        self.cfgxml_data.append("       </widget>")
        self.cfgxml_data.append("   </item>")
        return f"{self.prefix}.{halpin}_value"

    def draw_bar(self, name, halpin, setup={}, vmin=0, vmax=100):
        return self.draw_number(name, halpin, setup)

    def draw_number_u32(self, name, halpin, setup={}):
        return self.draw_number(name, halpin, hal_type="u32", setup=setup)

    def draw_number_s32(self, name, halpin, setup={}):
        return self.draw_number(name, halpin, hal_type="s32", setup=setup)

    def draw_number(self, name, halpin, hal_type="float", setup={}):
        if hal_type == "float":
            display_format = setup.get("format", "0.2f")
        else:
            display_format = setup.get("format", "d")

        self.draw_hbox_begin()
        self.draw_title(name)
        self.cfgxml_data.append("    <item>")
        self.cfgxml_data.append(f'     <widget class="HALLabel" name="{halpin}">')
        self.cfgxml_data.append('      <property name="sizePolicy">')
        self.cfgxml_data.append('       <sizepolicy hsizetype="Minimum" vsizetype="Fixed">')
        self.cfgxml_data.append("        <horstretch>0</horstretch>")
        self.cfgxml_data.append("        <verstretch>0</verstretch>")
        self.cfgxml_data.append("       </sizepolicy>")
        self.cfgxml_data.append("      </property>")
        if display_format:
            self.cfgxml_data.append('      <property name="textTemplate" stdset="0">')
            self.cfgxml_data.append(f"       <string>%{display_format}</string>")
            self.cfgxml_data.append("      </property>")
        self.cfgxml_data.append('                 <property name="alignment">')
        self.cfgxml_data.append("                  <set>Qt::AlignRight|Qt::AlignTrailing|Qt::AlignVCenter</set>")
        self.cfgxml_data.append("                 </property>")
        self.cfgxml_data.append('      <property name="styleSheet">')
        self.cfgxml_data.append('       <string notr="true">font: 20pt &quot;Lato Heavy&quot;;</string>')
        self.cfgxml_data.append("      </property>")
        for ptype in ("s32", "u32", "float", "bin"):
            self.cfgxml_data.append(f'      <property name="{ptype}_pin_type" stdset="0">')
            if ptype == hal_type:
                self.cfgxml_data.append("       <bool>true</bool>")
            else:
                self.cfgxml_data.append("       <bool>false</bool>")
            self.cfgxml_data.append("      </property>")
        self.cfgxml_data.append("     </widget>")
        self.cfgxml_data.append("    </item>")
        self.draw_hbox_end()
        return f"{self.prefix}.{halpin}"

    def draw_checkbutton(self, name, halpin, setup={}):
        self.draw_hbox_begin()
        self.draw_title(name)
        self.cfgxml_data.append(f"""
          <item>
           <widget class="PushButton" name="{halpin}">
            <property name="minimumSize">
             <size>
              <width>30</width>
              <height>30</height>
             </size>
            </property>
            <property name="maximumSize">
             <size>
              <width>30</width>
              <height>30</height>
             </size>
            </property>
            <property name="styleSheet">
             <string notr="true">
                QLabel {{
                    color: rgb(235, 235, 235);
                }}
             </string>
            </property>
            <property name="text">
             <string>x</string>
            </property>
            <property name="checkable">
             <bool>true</bool>
            </property>
            <property name="checked">
             <bool>false</bool>
            </property>
           </widget>
          </item>
        """)
        self.draw_hbox_end()
        return f"{self.prefix}.{halpin}"

    def draw_led(self, name, halpin, setup={}):
        self.draw_hbox_begin()
        self.draw_title(name)
        self.cfgxml_data.append("    <item>")
        self.cfgxml_data.append(f'     <widget class="LED" name="{halpin}">')
        self.cfgxml_data.append('        <property name="sizePolicy">')
        self.cfgxml_data.append('         <sizepolicy hsizetype="Fixed" vsizetype="Fixed">')
        self.cfgxml_data.append("          <horstretch>0</horstretch>")
        self.cfgxml_data.append("          <verstretch>0</verstretch>")
        self.cfgxml_data.append("         </sizepolicy>")
        self.cfgxml_data.append("        </property>")
        self.add_property("diameter", "24")
        self.cfgxml_data.append('        <property name="minimumSize">')
        self.cfgxml_data.append("         <size>")
        self.cfgxml_data.append("          <width>32</width>")
        self.cfgxml_data.append("          <height>32</height>")
        self.cfgxml_data.append("         </size>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="color">')
        self.cfgxml_data.append("          <color>")
        if halpin.endswith(".B"):
            self.cfgxml_data.append("           <red>85</red>")
            self.cfgxml_data.append("           <green>0</green>")
            self.cfgxml_data.append("           <blue>255</blue>")
        elif halpin.endswith(".R"):
            self.cfgxml_data.append("           <red>255</red>")
            self.cfgxml_data.append("           <green>85</green>")
            self.cfgxml_data.append("           <blue>0</blue>")
        else:
            self.cfgxml_data.append("           <red>85</red>")
            self.cfgxml_data.append("           <green>255</green>")
            self.cfgxml_data.append("           <blue>0</blue>")
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
        return f"{self.prefix}.{halpin}"
