import os


class qtpyvcp:
    def draw_begin(self, configuration_path, prefix="qtpyvcp.rio-gui", vcp_pos=None):
        self.vcp_pos = vcp_pos
        self.configuration_path = configuration_path
        self.prefix = prefix
        cfgxml_data = []
        if vcp_pos == "RIGHT":
            cfgxml_data.append("""<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>USER</class>
 <widget class="QWidget" name="RIO">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>179</width>
    <height>511</height>
   </rect>
  </property>
  <property name="maximumSize">
   <size>
    <width>1645</width>
    <height>619</height>
   </size>
  </property>
  <property name="windowTitle">
   <string>USER MAIN</string>
  </property>
  <property name="sidebar" stdset="0">
   <bool>true</bool>
  </property>
  <layout class="QGridLayout" name="gridLayout">
""")
        else:
            cfgxml_data.append("""<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>USER</class>
 <widget class="QWidget" name="RIO">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>1645</width>
    <height>619</height>
   </rect>
  </property>
  <property name="maximumSize">
   <size>
    <width>1645</width>
    <height>619</height>
   </size>
  </property>
  <property name="windowTitle">
   <string>USER MAIN</string>
  </property>
  <property name="sidebar" stdset="0">
   <bool>false</bool>
  </property>
  <layout class="QGridLayout" name="gridLayout">
""")

        return cfgxml_data

    def draw_end(self):
        cfgxml_data = []
        cfgxml_data.append("""
  </layout>
 </widget>
 <customwidgets>
  <customwidget>
   <class>VCPMainWindow</class>
   <extends>QMainWindow</extends>
   <header>qtpyvcp.widgets.form_widgets.main_window</header>
   <container>1</container>
  </customwidget>
  <customwidget>
   <class>HalLedIndicator</class>
   <extends>QWidget</extends>
   <header>qtpyvcp.widgets.hal_widgets.hal_led</header>
  </customwidget>
  <customwidget>
   <class>HalCheckBox</class>
   <extends>QCheckBox</extends>
   <header>qtpyvcp.widgets.hal_widgets.hal_checkbox</header>
  </customwidget>
  <customwidget>
   <class>HalLabel</class>
   <extends>QLabel</extends>
   <header>qtpyvcp.widgets.hal_widgets.hal_label</header>
  </customwidget>
  <customwidget>
   <class>HalButton</class>
   <extends>QPushButton</extends>
   <header>qtpyvcp.widgets.hal_widgets.hal_button</header>
  </customwidget>
  <customwidget>
   <class>HALLEDButton</class>
   <extends>QPushButton</extends>
   <header>qtpyvcp.widgets.hal_widgets.hal_led_button</header>
  </customwidget>
  <customwidget>
   <class>HalSlider</class>
   <extends>QSlider</extends>
   <header>qtpyvcp.widgets.hal_widgets.hal_slider</header>
  </customwidget>
  <customwidget>
   <class>HalBarIndicator</class>
   <extends>QWidget</extends>
   <header>qtpyvcp.widgets.hal_widgets.hal_bar_indicator</header>
  </customwidget>
 </customwidgets>
 <resources/>
 <connections/>
</ui>
""")
        return cfgxml_data

    def save(self, cfgxml_data):
        ui_filename = os.path.join(self.configuration_path, "user_tabs/rio/rio.ui")
        py_filename = os.path.join(self.configuration_path, "user_tabs/rio/rio.py")

        handler_py = []
        handler_py.append("""
import os
import linuxcnc

from qtpy import uic
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget

from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities import logger

LOG = logger.getLogger(__name__)
STATUS = getPlugin('status')
TOOL_TABLE = getPlugin('tooltable')
INI_FILE = linuxcnc.ini(os.getenv('INI_FILE_NAME'))

class UserTab(QWidget):
    def __init__(self, parent=None):
        super(UserTab, self).__init__(parent)
        ui_file = os.path.splitext(os.path.basename(__file__))[0] + ".ui"
        uic.loadUi(os.path.join(os.path.dirname(__file__), ui_file), self)
""")
        open(py_filename, "w").write("\n".join(handler_py))
        open(ui_filename, "w").write("\n".join(cfgxml_data))

    def draw_tabs_begin(self, names):
        cfgxml_data = []
        cfgxml_data.append('    <item row="0" column="0">')
        cfgxml_data.append('     <widget class="QTabWidget" name="tabWidget_setup">')
        return cfgxml_data

    def draw_tabs_end(self):
        cfgxml_data = []
        cfgxml_data.append("     </widget>")
        cfgxml_data.append("    </item>")
        return cfgxml_data

    def draw_tab_begin(self, name):
        cfgxml_data = []
        cfgxml_data.append(f'      <widget class="QWidget" name="tab_{name}">')
        cfgxml_data.append('       <attribute name="title">')
        cfgxml_data.append(f"        <string>{name}</string>")
        cfgxml_data.append("       </attribute>")
        cfgxml_data.append('       <layout class="QVBoxLayout" name="layout_stat">')
        cfgxml_data.append('        <property name="spacing">')
        cfgxml_data.append("         <number>0</number>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="leftMargin">')
        cfgxml_data.append("         <number>0</number>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="topMargin">')
        cfgxml_data.append("         <number>0</number>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="rightMargin">')
        cfgxml_data.append("         <number>0</number>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="bottomMargin">')
        cfgxml_data.append("         <number>0</number>")
        cfgxml_data.append("        </property>")

        cfgxml_data += self.draw_vbox_begin()

        return cfgxml_data

    def draw_tab_end(self):
        cfgxml_data = []
        cfgxml_data.append("           <item>")
        cfgxml_data.append('            <widget class="QWidget" name="widget" native="true"/>')
        cfgxml_data.append("           </item>")

        cfgxml_data += self.draw_vbox_end()

        cfgxml_data.append("        </layout>")
        cfgxml_data.append("      </widget>")
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
        cfgxml_data.append("     <item>")
        cfgxml_data.append('      <layout class="QVBoxLayout" name="verticalLayout_5">')
        cfgxml_data.append('           <property name="leftMargin">')
        cfgxml_data.append("            <number>5</number>")
        cfgxml_data.append("           </property>")
        cfgxml_data.append('           <property name="topMargin">')
        cfgxml_data.append("            <number>5</number>")
        cfgxml_data.append("           </property>")
        cfgxml_data.append('           <property name="rightMargin">')
        cfgxml_data.append("            <number>5</number>")
        cfgxml_data.append("           </property>")
        cfgxml_data.append('           <property name="bottomMargin">')
        cfgxml_data.append("            <number>5</number>")
        cfgxml_data.append("           </property>")
        return cfgxml_data

    def draw_vbox_end(self):
        cfgxml_data = []
        cfgxml_data.append("      </layout>")
        cfgxml_data.append("     </item>")
        return cfgxml_data

    def draw_hbox_begin(self):
        cfgxml_data = []
        cfgxml_data.append("     <item>")
        cfgxml_data.append('      <layout class="QHBoxLayout" name="hosizontalLayout_3">')
        cfgxml_data.append('           <property name="leftMargin">')
        cfgxml_data.append("            <number>5</number>")
        cfgxml_data.append("           </property>")
        cfgxml_data.append('           <property name="topMargin">')
        cfgxml_data.append("            <number>5</number>")
        cfgxml_data.append("           </property>")
        cfgxml_data.append('           <property name="rightMargin">')
        cfgxml_data.append("            <number>5</number>")
        cfgxml_data.append("           </property>")
        cfgxml_data.append('           <property name="bottomMargin">')
        cfgxml_data.append("            <number>5</number>")
        cfgxml_data.append("           </property>")

        return cfgxml_data

    def draw_hbox_end(self):
        cfgxml_data = []
        cfgxml_data.append("      </layout>")
        cfgxml_data.append("     </item>")
        return cfgxml_data

    def draw_button(self, name, halpin, setup={}):
        halpin = halpin.replace("_", "-")
        cfgxml_data = []
        cfgxml_data.append(f"""
              <item>
               <widget class="HalButton" name="rio.{halpin}">
                <property name="text">
                 <string>{name}</string>
                </property>
               </widget>
              </item>
        """)
        return (f"{self.prefix}.{halpin}.out", cfgxml_data)

    def draw_title(self, title):
        cfgxml_data = []
        cfgxml_data.append("    <item>")
        cfgxml_data.append('     <widget class="QLabel">')
        cfgxml_data.append('      <property name="text">')
        cfgxml_data.append(f"       <string>{title}</string>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append('      <property name="indent">')
        cfgxml_data.append("       <number>4</number>")
        cfgxml_data.append("      </property>")

        if self.vcp_pos == "RIGHT":
            cfgxml_data.append('             <property name="styleSheet">')
            cfgxml_data.append('              <string notr="true">QLabel {')
            cfgxml_data.append("    color: rgb(235, 235, 235);")
            cfgxml_data.append("}</string>")
            cfgxml_data.append("             </property>")

        cfgxml_data.append("     </widget>")
        cfgxml_data.append("    </item>")
        return cfgxml_data

    def draw_scale(self, name, halpin, setup={}, vmin=0, vmax=100):
        halpin = halpin.replace("_", "-")
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        title = setup.get("title", name)
        cfgxml_data = []

        cfgxml_data += self.draw_hbox_begin()

        cfgxml_data += self.draw_title(title)

        cfgxml_data.append("    <item>")
        cfgxml_data.append(f'     <widget class="HalSlider" name="rio.{halpin}">')
        cfgxml_data.append('         <property name="sizePolicy">')
        cfgxml_data.append('          <sizepolicy hsizetype="Preferred" vsizetype="Minimum">')
        cfgxml_data.append("           <horstretch>0</horstretch>")
        cfgxml_data.append("           <verstretch>0</verstretch>")
        cfgxml_data.append("          </sizepolicy>")
        cfgxml_data.append("         </property>")
        cfgxml_data.append('      <property name="minimum">')
        cfgxml_data.append(f"       <number>{int(int(display_min) * 100.0)}</number>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append('      <property name="maximum">')
        cfgxml_data.append(f"       <number>{int(int(display_max) * 100.0)}</number>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append('      <property name="orientation">')
        cfgxml_data.append("       <enum>Qt::Horizontal</enum>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append("     </widget>")
        cfgxml_data.append("    </item>")

        cfgxml_data += self.draw_hbox_end()

        return (f"{self.prefix}.{halpin}.out-f", cfgxml_data)

    def draw_meter(self, name, halpin, setup={}, vmin=0, vmax=100):
        halpin = halpin.replace("_", "-")
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        display_text = setup.get("text", name)
        display_threshold = setup.get("threshold")
        display_size = setup.get("size", "150")
        cfgxml_data = []
        cfgxml_data.append("   <item>")
        cfgxml_data.append(f'       <widget class="HalBarIndicator" name="rio.{halpin}">')
        cfgxml_data.append('        <property name="minimum" stdset="0">')
        cfgxml_data.append(f"         <number>{int(display_min)}</number>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append('        <property name="maximum" stdset="0">')
        cfgxml_data.append(f"         <number>{int(display_max)}</number>")
        cfgxml_data.append("        </property>")
        cfgxml_data.append("       </widget>")
        cfgxml_data.append("   </item>")

        return (f"{self.prefix}.{halpin}.in-f", cfgxml_data)

    def draw_bar(self, name, halpin, setup={}, vmin=0, vmax=100):
        halpin = halpin.replace("_", "-")
        return self.draw_number(name, halpin, setup)

    def draw_number_u32(self, name, halpin, setup={}):
        halpin = halpin.replace("_", "-")
        return self.draw_number(name, halpin, hal_type="u32", setup=setup)

    def draw_number_s32(self, name, halpin, setup={}):
        halpin = halpin.replace("_", "-")
        return self.draw_number(name, halpin, hal_type="s32", setup=setup)

    def draw_number(self, name, halpin, hal_type="float", setup={}):
        halpin = halpin.replace("_", "-")
        if hal_type == "float":
            display_format = setup.get("format", "0.2f")
        else:
            display_format = setup.get("format", "d")

        cfgxml_data = []
        cfgxml_data += self.draw_hbox_begin()

        cfgxml_data += self.draw_title(name)

        cfgxml_data.append("    <item>")
        cfgxml_data.append(f'     <widget class="HalLabel" name="rio.{halpin}">')
        cfgxml_data.append(' <property name="pinType" stdset="0">')
        cfgxml_data.append("  <enum>HalLabel::float</enum>")
        cfgxml_data.append(" </property>")
        cfgxml_data.append('      <property name="sizePolicy">')
        cfgxml_data.append('       <sizepolicy hsizetype="Minimum" vsizetype="Fixed">')
        cfgxml_data.append("        <horstretch>0</horstretch>")
        cfgxml_data.append("        <verstretch>0</verstretch>")
        cfgxml_data.append("       </sizepolicy>")
        cfgxml_data.append("      </property>")
        cfgxml_data.append(' <property name="alignment">')
        cfgxml_data.append("  <set>Qt::AlignRight|Qt::AlignTrailing|Qt::AlignVCenter</set>")
        cfgxml_data.append(" </property>")
        cfgxml_data.append('      <property name="styleSheet">')
        cfgxml_data.append('       <string notr="true">font: 20pt &quot;Lato Heavy&quot;;</string>')
        cfgxml_data.append("      </property>")
        cfgxml_data.append("     </widget>")
        cfgxml_data.append("    </item>")

        cfgxml_data += self.draw_hbox_end()

        return (f"{self.prefix}.{halpin}-in", cfgxml_data)

    def draw_checkbutton(self, name, halpin, setup={}):
        halpin = halpin.replace("_", "-")
        cfgxml_data = []

        cfgxml_data += self.draw_hbox_begin()

        cfgxml_data += self.draw_title(name)

        cfgxml_data.append("    <item>")
        cfgxml_data.append(f'     <widget class="HalCheckBox" name="rio.{halpin}">')
        cfgxml_data.append(' <property name="sizePolicy">')
        cfgxml_data.append('  <sizepolicy hsizetype="Fixed" vsizetype="Fixed">')
        cfgxml_data.append("   <horstretch>0</horstretch>")
        cfgxml_data.append("   <verstretch>0</verstretch>")
        cfgxml_data.append("  </sizepolicy>")
        cfgxml_data.append(" </property>")
        cfgxml_data.append(' <property name="minimumSize">')
        cfgxml_data.append("  <size>")
        cfgxml_data.append("   <width>32</width>")
        cfgxml_data.append("   <height>32</height>")
        cfgxml_data.append("  </size>")
        cfgxml_data.append(" </property>")
        cfgxml_data.append(' <property name="text">')
        cfgxml_data.append("  <string/>")
        cfgxml_data.append(" </property>")
        cfgxml_data.append("     </widget>")
        cfgxml_data.append("    </item>")

        cfgxml_data += self.draw_hbox_end()

        return (f"{self.prefix}.{halpin}.checked", cfgxml_data)

    def draw_led(self, name, halpin, setup={}):
        halpin = halpin.replace("_", "-")
        cfgxml_data = []

        cfgxml_data += self.draw_hbox_begin()

        cfgxml_data += self.draw_title(name)

        cfgxml_data.append("    <item>")
        cfgxml_data.append(f'     <widget class="HalLedIndicator" name="rio.{halpin}">')
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

        cfgxml_data += self.draw_hbox_end()

        return (f"{self.prefix}.{halpin}.on", cfgxml_data)
