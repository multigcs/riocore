import os


class qtvcp:
    #
    # wget "https://raw.githubusercontent.com/LinuxCNC/linuxcnc/master/lib/python/qtvcp/designer/install_script"
    #

    def draw_begin(self, configuration_path, prefix="qtvcp.rio-gui", vcp_pos=None):
        self.configuration_path = configuration_path
        self.prefix = prefix
        cfgxml_data = []
        cfgxml_data.append("""<?xml version="1.0" encoding="UTF-8"?>
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
        cfgxml_data.append("")
        cfgxml_data.append("           <item>")
        cfgxml_data.append('            <widget class="QGroupBox" name="groupBox_rio">')
        cfgxml_data.append('             <property name="title">')
        cfgxml_data.append("              <string>RIO</string>")
        cfgxml_data.append("             </property>")
        cfgxml_data.append('           <property name="sizePolicy">')
        cfgxml_data.append('            <sizepolicy hsizetype="Minimum" vsizetype="Preferred">')
        cfgxml_data.append("             <horstretch>0</horstretch>")
        cfgxml_data.append("             <verstretch>0</verstretch>")
        cfgxml_data.append("            </sizepolicy>")
        cfgxml_data.append("           </property>")
        cfgxml_data.append('           <property name="minimumSize">')
        cfgxml_data.append("            <size>")
        cfgxml_data.append("             <width>200</width>")
        cfgxml_data.append("             <height>0</height>")
        cfgxml_data.append("            </size>")
        cfgxml_data.append("           </property>")
        cfgxml_data.append('             <property name="alignment">')
        cfgxml_data.append("              <set>Qt::AlignCenter</set>")
        cfgxml_data.append("             </property>")
        cfgxml_data.append('             <layout class="QVBoxLayout" name="verticalLayout_30">')
        cfgxml_data.append('              <property name="spacing">')
        cfgxml_data.append("               <number>6</number>")
        cfgxml_data.append("              </property>")
        cfgxml_data.append('              <property name="leftMargin">')
        cfgxml_data.append("               <number>2</number>")
        cfgxml_data.append("              </property>")
        cfgxml_data.append('              <property name="topMargin">')
        cfgxml_data.append("               <number>2</number>")
        cfgxml_data.append("              </property>")
        cfgxml_data.append('              <property name="rightMargin">')
        cfgxml_data.append("               <number>2</number>")
        cfgxml_data.append("              </property>")
        cfgxml_data.append('              <property name="bottomMargin">')
        cfgxml_data.append("               <number>2</number>")
        cfgxml_data.append("              </property>")
        return cfgxml_data

    def draw_end(self):
        cfgxml_data = []
        cfgxml_data.append("             </layout>")
        cfgxml_data.append("            </widget>")
        cfgxml_data.append("           </item>")
        cfgxml_data.append("")
        cfgxml_data.append("""
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
        return cfgxml_data

    def save(self, cfgxml_data):
        ui_filename = os.path.join(self.configuration_path, "rio-gui.ui")
        py_filename = os.path.join(self.configuration_path, "rio-gui_handler.py")

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
        open(ui_filename, "w").write("\n".join(cfgxml_data))

    def draw_tabs_begin(self, names):
        cfgxml_data = []
        cfgxml_data.append("                    <item>")
        cfgxml_data.append('                     <widget class="QTabWidget" name="tabWidget_setup">')
        cfgxml_data.append('                      <property name="geometry">')
        cfgxml_data.append("                       <rect>")
        cfgxml_data.append("                        <x>0</x>")
        cfgxml_data.append("                        <y>0</y>")
        cfgxml_data.append("                        <width>400</width>")
        cfgxml_data.append("                        <height>300</height>")
        cfgxml_data.append("                       </rect>")
        cfgxml_data.append("                      </property>")
        cfgxml_data.append('                      <property name="sizePolicy">')
        cfgxml_data.append('                       <sizepolicy hsizetype="Expanding" vsizetype="Preferred">')
        cfgxml_data.append("                        <horstretch>1</horstretch>")
        cfgxml_data.append("                        <verstretch>0</verstretch>")
        cfgxml_data.append("                       </sizepolicy>")
        cfgxml_data.append("                      </property>")
        cfgxml_data.append('                      <property name="currentIndex">')
        cfgxml_data.append("                       <number>0</number>")
        cfgxml_data.append("                      </property>")
        return cfgxml_data

    def draw_tabs_end(self):
        cfgxml_data = []
        cfgxml_data.append("                     </widget>")
        cfgxml_data.append("                    </item>")
        return cfgxml_data

    def draw_tab_begin(self, name):
        cfgxml_data = []
        cfgxml_data.append(f'                      <widget class="QWidget" name="tab_{name}">')
        cfgxml_data.append('                       <attribute name="title">')
        cfgxml_data.append(f"                        <string>{name}</string>")
        cfgxml_data.append("                       </attribute>")
        cfgxml_data.append('                       <layout class="QVBoxLayout" name="layout_stat">')
        cfgxml_data.append('                        <property name="spacing">')
        cfgxml_data.append("                         <number>0</number>")
        cfgxml_data.append("                        </property>")
        cfgxml_data.append('                        <property name="leftMargin">')
        cfgxml_data.append("                         <number>0</number>")
        cfgxml_data.append("                        </property>")
        cfgxml_data.append('                        <property name="topMargin">')
        cfgxml_data.append("                         <number>0</number>")
        cfgxml_data.append("                        </property>")
        cfgxml_data.append('                        <property name="rightMargin">')
        cfgxml_data.append("                         <number>0</number>")
        cfgxml_data.append("                        </property>")
        cfgxml_data.append('                        <property name="bottomMargin">')
        cfgxml_data.append("                         <number>0</number>")
        cfgxml_data.append("                        </property>")
        cfgxml_data.append("                         <item>")
        cfgxml_data.append('                          <layout class="QVBoxLayout" name="verticalLayout_58">')
        return cfgxml_data

    def draw_tab_end(self):
        cfgxml_data = []
        cfgxml_data.append("                          </layout>")
        cfgxml_data.append("                         </item>")
        cfgxml_data.append("                        </layout>")
        cfgxml_data.append("                      </widget>")
        return cfgxml_data

    def draw_frame_begin(self, name=None):
        if not name:
            name = "frame"
        cfgxml_data = []
        return cfgxml_data

    def draw_frame_end(self):
        cfgxml_data = []
        return cfgxml_data

    def draw_vbox_begin(self):
        cfgxml_data = []
        cfgxml_data.append("                         <item>")
        cfgxml_data.append('                          <layout class="QVBoxLayout" name="verticalLayout_5">')
        return cfgxml_data

    def draw_vbox_end(self):
        cfgxml_data = []
        cfgxml_data.append("                          </layout>")
        cfgxml_data.append("                         </item>")
        return cfgxml_data

    def draw_hbox_begin(self):
        cfgxml_data = []
        cfgxml_data.append("                         <item>")
        cfgxml_data.append('                          <layout class="QHBoxLayout" name="hosizontalLayout_3">')
        return cfgxml_data

    def draw_hbox_end(self):
        cfgxml_data = []
        cfgxml_data.append("                          </layout>")
        cfgxml_data.append("                         </item>")
        return cfgxml_data

    def draw_button(self, name, halpin, setup={}):
        cfgxml_data = []
        cfgxml_data.append(f"""
              <item>
               <widget class="PushButton" name="{halpin}">
                <property name="text">
                 <string>{name}</string>
                </property>
               </widget>
              </item>
        """)
        return (f"{self.prefix}.{halpin}", cfgxml_data)

    def draw_scale(self, name, halpin, setup={}, vmin=0, vmax=100):
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        title = setup.get("title", name)
        cfgxml_data = []
        cfgxml_data.append("  <item>")
        cfgxml_data.append(f'   <layout class="QHBoxLayout" name="layl_{halpin}">')
        cfgxml_data.append("    <item>")
        cfgxml_data.append('     <widget class="QLabel" name="label_22">')
        cfgxml_data.append('      <property name="text">')
        cfgxml_data.append(f"       <string>{title}</string>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append('      <property name="indent">')
        cfgxml_data.append("       <number>4</number>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append("     </widget>")
        cfgxml_data.append("    </item>")
        cfgxml_data.append("    <item>")
        cfgxml_data.append(f'     <widget class="Slider" name="{halpin}">')
        cfgxml_data.append('      <property name="minimum">')
        cfgxml_data.append(f"       <number>{display_min}</number>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append('      <property name="maximum">')
        cfgxml_data.append(f"       <number>{display_max}</number>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append('      <property name="orientation">')
        cfgxml_data.append("       <enum>Qt::Horizontal</enum>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append("     </widget>")
        cfgxml_data.append("    </item>")
        cfgxml_data.append("   </layout>")
        cfgxml_data.append("  </item>")
        return (f"{self.prefix}.{halpin}-f", cfgxml_data)

    def draw_meter(self, name, halpin, setup={}, vmin=0, vmax=100):
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_text = setup.get("text", name)
        display_threshold = setup.get("threshold")
        display_size = setup.get("size", "150")
        cfgxml_data = []
        cfgxml_data.append("   <item>")
        cfgxml_data.append(f'       <widget class="Gauge" name="{halpin}">')
        cfgxml_data.append('        <property name="minimumSize">')
        cfgxml_data.append("         <size>")
        cfgxml_data.append(f"          <width>{display_size}</width>")
        cfgxml_data.append(f"          <height>{display_size}</height>")
        cfgxml_data.append("         </size>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="min_value" stdset="0">')
        cfgxml_data.append(f"         <number>{int(display_min)}</number>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="max_value" stdset="0">')
        cfgxml_data.append(f"         <number>{int(display_max)}</number>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="max_reading" stdset="0">')
        cfgxml_data.append(f"         <number>{int(display_max)}</number>")
        cfgxml_data.append("        </property>")
        if display_threshold:
            cfgxml_data.append('        <property name="threshold" stdset="0">')
            cfgxml_data.append(f"         <number>{display_threshold}</number>")
            cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="num_ticks" stdset="0">')
        cfgxml_data.append("         <number>9</number>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="gauge_label" stdset="0">')
        cfgxml_data.append(f"         <string>{display_text}</string>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="zone1_color" stdset="0">')
        cfgxml_data.append("         <color>")
        cfgxml_data.append("          <red>0</red>")
        cfgxml_data.append("          <green>100</green>")
        cfgxml_data.append("          <blue>0</blue>")
        cfgxml_data.append("         </color>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="zone2_color" stdset="0">')
        cfgxml_data.append("         <color>")
        cfgxml_data.append("          <red>200</red>")
        cfgxml_data.append("          <green>0</green>")
        cfgxml_data.append("          <blue>0</blue>")
        cfgxml_data.append("         </color>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('      <property name="halpin_name" stdset="0">')
        cfgxml_data.append(f"       <string>{halpin}</string>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append('      <property name="halpin_option" stdset="0">')
        cfgxml_data.append("       <bool>true</bool>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append("       </widget>")
        cfgxml_data.append("   </item>")
        return (f"{self.prefix}.{halpin}_value", cfgxml_data)

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

        cfgxml_data = []
        cfgxml_data.append("  <item>")
        cfgxml_data.append(f'   <layout class="QHBoxLayout" name="layl_{halpin}">')
        cfgxml_data.append("    <item>")
        cfgxml_data.append('     <widget class="QLabel" name="label_22">')
        cfgxml_data.append('      <property name="text">')
        cfgxml_data.append(f"       <string>{name}</string>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append('      <property name="indent">')
        cfgxml_data.append("       <number>4</number>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append("     </widget>")
        cfgxml_data.append("    </item>")
        cfgxml_data.append("    <item>")
        cfgxml_data.append(f'     <widget class="HALLabel" name="{halpin}">')
        cfgxml_data.append('      <property name="sizePolicy">')
        cfgxml_data.append('       <sizepolicy hsizetype="Minimum" vsizetype="Fixed">')
        cfgxml_data.append("        <horstretch>0</horstretch>")
        cfgxml_data.append("        <verstretch>0</verstretch>")
        cfgxml_data.append("       </sizepolicy>")
        cfgxml_data.append("      </property>")
        if display_format:
            cfgxml_data.append('      <property name="textTemplate" stdset="0">')
            cfgxml_data.append(f"       <string>%{display_format}</string>")
            cfgxml_data.append("      </property>")
        cfgxml_data.append('                 <property name="alignment">')
        cfgxml_data.append("                  <set>Qt::AlignRight|Qt::AlignTrailing|Qt::AlignVCenter</set>")
        cfgxml_data.append("                 </property>")
        cfgxml_data.append('      <property name="styleSheet">')
        cfgxml_data.append('       <string notr="true">font: 20pt &quot;Lato Heavy&quot;;</string>')
        cfgxml_data.append("      </property>")

        for ptype in ("s32", "u32", "float", "bin"):
            cfgxml_data.append(f'      <property name="{ptype}_pin_type" stdset="0">')
            if ptype == hal_type:
                cfgxml_data.append("       <bool>true</bool>")
            else:
                cfgxml_data.append("       <bool>false</bool>")
            cfgxml_data.append("      </property>")

        cfgxml_data.append("     </widget>")
        cfgxml_data.append("    </item>")
        cfgxml_data.append("   </layout>")
        cfgxml_data.append("  </item>")
        return (f"{self.prefix}.{halpin}", cfgxml_data)

    def draw_checkbutton(self, name, halpin, setup={}):
        cfgxml_data = []
        cfgxml_data.append("  <item>")
        cfgxml_data.append(f'   <layout class="QHBoxLayout" name="layl_{halpin}">')
        cfgxml_data.append("    <item>")
        cfgxml_data.append('     <widget class="QLabel" name="label_22">')
        cfgxml_data.append('      <property name="text">')
        cfgxml_data.append(f"       <string>{name}</string>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append('      <property name="indent">')
        cfgxml_data.append("       <number>4</number>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append("     </widget>")
        cfgxml_data.append("    </item>")
        cfgxml_data.append("    <item>")
        cfgxml_data.append(f'     <widget class="CheckBox" name="{halpin}">')
        cfgxml_data.append('                 <property name="sizePolicy">')
        cfgxml_data.append('                  <sizepolicy hsizetype="Fixed" vsizetype="Fixed">')
        cfgxml_data.append("                   <horstretch>0</horstretch>")
        cfgxml_data.append("                   <verstretch>0</verstretch>")
        cfgxml_data.append("                  </sizepolicy>")
        cfgxml_data.append("                 </property>")
        cfgxml_data.append('                 <property name="minimumSize">')
        cfgxml_data.append("                  <size>")
        cfgxml_data.append("                   <width>32</width>")
        cfgxml_data.append("                   <height>32</height>")
        cfgxml_data.append("                  </size>")
        cfgxml_data.append("                 </property>")
        cfgxml_data.append('                 <property name="text">')
        cfgxml_data.append("                  <string/>")
        cfgxml_data.append("                 </property>")
        cfgxml_data.append("     </widget>")
        cfgxml_data.append("    </item>")
        cfgxml_data.append("   </layout>")
        cfgxml_data.append("  </item>")
        return (f"{self.prefix}.{halpin}", cfgxml_data)

    def draw_led(self, name, halpin, setup={}):
        cfgxml_data = []
        cfgxml_data.append("  <item>")
        cfgxml_data.append(f'   <layout class="QHBoxLayout" name="layl_{halpin}">')
        cfgxml_data.append("    <item>")
        cfgxml_data.append('     <widget class="QLabel" name="label_22">')
        cfgxml_data.append('      <property name="text">')
        cfgxml_data.append(f"       <string>{name}</string>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append('      <property name="indent">')
        cfgxml_data.append("       <number>4</number>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append("     </widget>")
        cfgxml_data.append("    </item>")
        cfgxml_data.append("    <item>")
        cfgxml_data.append(f'     <widget class="LED" name="{halpin}">')
        cfgxml_data.append('        <property name="sizePolicy">')
        cfgxml_data.append('         <sizepolicy hsizetype="Fixed" vsizetype="Fixed">')
        cfgxml_data.append("          <horstretch>0</horstretch>")
        cfgxml_data.append("          <verstretch>0</verstretch>")
        cfgxml_data.append("         </sizepolicy>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="minimumSize">')
        cfgxml_data.append("         <size>")
        cfgxml_data.append("          <width>32</width>")
        cfgxml_data.append("          <height>32</height>")
        cfgxml_data.append("         </size>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="color">')
        cfgxml_data.append("          <color>")
        if halpin.endswith(".B"):
            cfgxml_data.append("           <red>85</red>")
            cfgxml_data.append("           <green>0</green>")
            cfgxml_data.append("           <blue>255</blue>")
        elif halpin.endswith(".R"):
            cfgxml_data.append("           <red>255</red>")
            cfgxml_data.append("           <green>85</green>")
            cfgxml_data.append("           <blue>0</blue>")
        else:
            cfgxml_data.append("           <red>85</red>")
            cfgxml_data.append("           <green>255</green>")
            cfgxml_data.append("           <blue>0</blue>")

        cfgxml_data.append("          </color>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="maximumSize">')
        cfgxml_data.append("         <size>")
        cfgxml_data.append("          <width>32</width>")
        cfgxml_data.append("          <height>32</height>")
        cfgxml_data.append("         </size>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append("     </widget>")
        cfgxml_data.append("    </item>")
        cfgxml_data.append("   </layout>")
        cfgxml_data.append("  </item>")
        return (f"{self.prefix}.{halpin}", cfgxml_data)
