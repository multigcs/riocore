from lxml import etree
import os


class qtpyvcp:
    mode = "qtpyvcp"
    colormapping = {
        "white": "<red>255</red><green>255</green><blue>255</blue>",
        "black": "<red>0</red><green>0</green><blue>0</blue>",
        "yellow": "<red>255</red><green>255</green><blue>0</blue>",
        "red": "<red>255</red><green>0</green><blue>0</blue>",
        "green": "<red>0</red><green>255</green><blue>0</blue>",
        "blue": "<red>0</red><green>0</green><blue>255</blue>",
    }

    def __init__(self, prefix="rio-gui", vcp_pos=None, mode="qtvcp"):
        self.prefix = prefix
        self.vcp_pos = vcp_pos
        self.mode = mode

    def check(self, configuration_path):
        if self.mode != "tnc":
            return True
        return True
        ui_filename = os.path.join(configuration_path, "ui/window.ui")
        # read template
        xml_template = open(ui_filename, "rb").read()
        root = etree.fromstring(xml_template)
        # check
        for element in root.xpath("..//widget[@name='rioTab']"):
            return True
        print("ERROR: tncvcp: no 'QTabWidget' named 'rioTab' found")
        return False

    def draw_begin(self):
        self.cfgxml_data = []
        if self.mode != "tnc":
            if self.vcp_pos == "RIGHT":
                self.cfgxml_data.append("""<?xml version="1.0" encoding="UTF-8"?>
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
                self.cfgxml_data.append("""<?xml version="1.0" encoding="UTF-8"?>
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

    def draw_end(self):
        if self.mode != "tnc":
            self.cfgxml_data.append("""
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

    def xml(self):
        return "\n".join(self.cfgxml_data).strip()

    def save(self, configuration_path):
        if self.mode == "tnc":
            ui_filename = os.path.join(configuration_path, "ui/window.ui")

            # read rio xml-gui
            rio_items = etree.fromstring("\n".join(self.cfgxml_data).strip())
            # read template
            xml_template = open(ui_filename, "rb").read()
            root = etree.fromstring(xml_template)

            centralwidget = root.find("widget/widget[@name='centralwidget']")
            layout = root.find("widget/widget[@name='centralwidget']/layout")

            hlayout = etree.SubElement(centralwidget, "layout")
            hlayout.set("class", "QHBoxLayout")
            hlayout.set("name", "hLayout")

            item = etree.SubElement(hlayout, "item")
            item.append(layout)

            item = etree.SubElement(hlayout, "item")
            riotab = etree.SubElement(item, "widget")
            riotab.set("class", "QTabWidget")
            riotab.set("name", "rioTab")

            prop = etree.SubElement(riotab, "property", name="sizePolicy")
            sizepolicy = etree.SubElement(prop, "sizepolicy", hsizetype="Fixed", vsizetype="Expanding")
            etree.SubElement(sizepolicy, "horstretch").text = "0"
            etree.SubElement(sizepolicy, "verstretch").text = "0"

            prop = etree.SubElement(riotab, "property", name="minimumSize")
            size = etree.SubElement(prop, "size")
            etree.SubElement(size, "width").text = "300"
            etree.SubElement(size, "height").text = "0"

            customs = {
                "HalLabel": ("QLabel", "qtpyvcp.widgets.hal_widgets.hal_label"),
                "HalCheckBox": ("QCheckBox", "qtpyvcp.widgets.hal_widgets.hal_checkbox"),
                "HalSlider": ("QSlider", "qtpyvcp.widgets.hal_widgets.hal_slider"),
                "HalPlot": ("QWidget", "qtpyvcp.widgets.hal_widgets.hal_plot"),
            }

            customwidgets = root.find("customwidgets")
            for wclass, data in customs.items():
                customwidget = etree.SubElement(customwidgets, "customwidget")
                etree.SubElement(customwidget, "class").text = wclass
                etree.SubElement(customwidget, "extends").text = data[0]
                etree.SubElement(customwidget, "header").text = data[1]

            # fix currentIndex of main tab
            tab_current = root.find("widget/widget/layout/item/layout/item/widget/property[@name='currentIndex']/number")
            tab_current.text = "0"

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

        else:
            ui_filename = os.path.join(configuration_path, "user_tabs/rio/rio.ui")
            py_filename = os.path.join(configuration_path, "user_tabs/rio/rio.py")
            yml_filename = os.path.join(configuration_path, "custom_config.yml")

            custom_config = []
            custom_config.append("")
            custom_config.append("# example of a machine specific settings")
            custom_config.append("windows:")
            custom_config.append("  mainwindow:")
            custom_config.append("    kwargs:")
            custom_config.append("      confirm_exit: false")
            custom_config.append("")
            custom_config.append("data_plugins:")
            custom_config.append("  tooltable:")
            custom_config.append("    provider: qtpyvcp.plugins.tool_table:ToolTable")
            custom_config.append("    kwargs:")
            custom_config.append("      columns: TZDR")
            custom_config.append("")
            custom_config.append("  offsettable:")
            custom_config.append("    provider: qtpyvcp.plugins.offset_table:OffsetTable")
            custom_config.append("    kwargs:")
            custom_config.append('      columns: "XYZACR"')
            custom_config.append("")
            custom_config.append("settings:")
            custom_config.append("")
            custom_config.append("  # VTK backplot view settings")
            custom_config.append("")
            custom_config.append("  backplot.show-grid:")
            custom_config.append("    default_value: false")
            custom_config.append("")
            custom_config.append("  backplot.show-program-bounds:")
            custom_config.append("    default_value: false")
            custom_config.append("")
            custom_config.append("  backplot.show-program-labels:")
            custom_config.append("    default_value: false")
            custom_config.append("")
            custom_config.append("  backplot.show-program-ticks:")
            custom_config.append("    default_value: false")
            custom_config.append("")
            custom_config.append("  backplot.show-machine-bounds:")
            custom_config.append("    default_value: false")
            custom_config.append("")
            custom_config.append("  backplot.show-machine-labels:")
            custom_config.append("    default_value: false")
            custom_config.append("")
            custom_config.append("  backplot.show-machine-ticks:")
            custom_config.append("    default_value: false")
            custom_config.append("")
            custom_config.append("  backplot.perspective-view:")
            custom_config.append("    default_value: false")
            custom_config.append("")
            custom_config.append("  backplot.multitool-colors:")
            custom_config.append("    default_value: True")
            custom_config.append("")
            os.makedirs(os.path.join(configuration_path, "user_tabs", "rio"), exist_ok=True)
            os.makedirs(os.path.join(configuration_path, "user_buttons"), exist_ok=True)
            open(yml_filename, "w").write("\n".join(custom_config))

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
            print(ui_filename)
            open(ui_filename, "w").write("\n".join(self.cfgxml_data))

    def add_property(self, name, value, ptype="number"):
        self.cfgxml_data.append(f'      <property name="{name}">')
        self.cfgxml_data.append(f"       <{ptype}>{value}</{ptype}>")
        self.cfgxml_data.append("      </property>")

    def draw_tabs_begin(self, names):
        if self.mode == "tnc":
            self.cfgxml_data.append("    <rio_items>")
        else:
            self.cfgxml_data.append('   <item row="0" column="0">')
            self.cfgxml_data.append('    <widget class="QTabWidget" name="tabWidget_setup">')

    def draw_tabs_end(self):
        if self.mode == "tnc":
            self.cfgxml_data.append("    </rio_items>")
        else:
            self.cfgxml_data.append("    </widget>")
            self.cfgxml_data.append("   </item>")

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
        self.cfgxml_data.append('            <widget class="QWidget" name="widget" native="true"/>')
        self.cfgxml_data.append("           </item>")
        self.draw_vbox_end()
        self.cfgxml_data.append("        </layout>")
        self.cfgxml_data.append("      </widget>")

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
        self.cfgxml_data.append(f"          <string>{halpin}</string>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('         <property name="sizePolicy">')
        self.cfgxml_data.append('          <sizepolicy hsizetype="Minimum" vsizetype="Fixed">')
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
        title = setup.get("title", name)
        halpin = halpin.replace("_", "-")
        width = setup.get("width", 100)
        height = setup.get("height", 32)
        display_min = setup.get("min", vmin)
        display_max = setup.get("max", vmax)
        self.draw_hbox_begin()
        if title:
            self.draw_title(title)
        self.cfgxml_data.append("   <item>")
        self.cfgxml_data.append(f'       <widget class="HalBarIndicator" name="rio.{halpin}">')
        self.cfgxml_data.append('        <property name="pinBaseName" stdset="0">')
        self.cfgxml_data.append(f"          <string>{halpin}</string>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="sizePolicy">')
        self.cfgxml_data.append('         <sizepolicy hsizetype="Minimum" vsizetype="Fixed">')
        self.cfgxml_data.append("          <horstretch>0</horstretch>")
        self.cfgxml_data.append("          <verstretch>0</verstretch>")
        self.cfgxml_data.append("         </sizepolicy>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="minimumSize">')
        self.cfgxml_data.append("         <size>")
        self.cfgxml_data.append(f"          <width>{width}</width>")
        self.cfgxml_data.append(f"          <height>{height}</height>")
        self.cfgxml_data.append("         </size>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="maximumSize">')
        self.cfgxml_data.append("         <size>")
        self.cfgxml_data.append(f"          <width>{width}</width>")
        self.cfgxml_data.append(f"          <height>{height}</height>")
        self.cfgxml_data.append("         </size>")
        self.cfgxml_data.append("        </property>")
        self.add_property("minimum", int(display_min))
        self.add_property("maximum", int(display_max))
        self.cfgxml_data.append("       </widget>")
        self.cfgxml_data.append("   </item>")
        self.draw_hbox_end()
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
        title = setup.get("title", name)
        halpin = halpin.replace("_", "-")
        width = setup.get("width", 200)
        height = setup.get("height", 100)
        # display_min = setup.get("min", 0)
        # display_max = setup.get("max", 100)
        self.draw_hbox_begin()
        if title:
            self.draw_title(title)
        self.cfgxml_data.append("    <item>")
        self.cfgxml_data.append(f'     <widget class="HalPlot" name="rio.{halpin}">')
        self.cfgxml_data.append('        <property name="pinBaseName" stdset="0">')
        self.cfgxml_data.append(f"          <string>{halpin}</string>")
        self.cfgxml_data.append("        </property>")

        self.cfgxml_data.append('        <property name="sizePolicy">')
        self.cfgxml_data.append('         <sizepolicy hsizetype="Fixed" vsizetype="Fixed">')
        self.cfgxml_data.append("          <horstretch>0</horstretch>")
        self.cfgxml_data.append("          <verstretch>0</verstretch>")
        self.cfgxml_data.append("         </sizepolicy>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="minimumSize">')
        self.cfgxml_data.append("         <size>")
        self.cfgxml_data.append(f"          <width>{width}</width>")
        self.cfgxml_data.append(f"          <height>{height}</height>")
        self.cfgxml_data.append("         </size>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="maximumSize">')
        self.cfgxml_data.append("         <size>")
        self.cfgxml_data.append(f"          <width>{width}</width>")
        self.cfgxml_data.append(f"          <height>{height}</height>")
        self.cfgxml_data.append("         </size>")
        self.cfgxml_data.append("        </property>")

        # self.add_property("minimum", int(display_min))
        # self.add_property("maximum", int(display_max))

        self.cfgxml_data.append("     </widget>")
        self.cfgxml_data.append("    </item>")
        self.draw_hbox_end()
        return f"{self.prefix}.{halpin}.Series1"

    def draw_number(self, name, halpin, setup={}, hal_type="float"):
        halpin = halpin.replace("_", "-")
        self.draw_hbox_begin()
        self.draw_title(name)
        self.cfgxml_data.append("    <item>")
        self.cfgxml_data.append(f'     <widget class="HalLabel" name="rio.{halpin}">')
        self.cfgxml_data.append('        <property name="pinBaseName" stdset="0">')
        self.cfgxml_data.append(f"          <string>{halpin}</string>")
        self.cfgxml_data.append("        </property>")
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
        title = setup.get("title", name)
        halpin = halpin.replace("_", "-")
        width = setup.get("width", 16)
        height = setup.get("height", 16)
        self.draw_hbox_begin()
        if title:
            self.draw_title(title)
        self.cfgxml_data.append("    <item>")
        self.cfgxml_data.append(f'     <widget class="HalCheckBox" name="rio.{halpin}">')
        self.cfgxml_data.append('        <property name="pinBaseName" stdset="0">')
        self.cfgxml_data.append(f"          <string>{halpin}</string>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="sizePolicy">')
        self.cfgxml_data.append('         <sizepolicy hsizetype="Fixed" vsizetype="Fixed">')
        self.cfgxml_data.append("          <horstretch>0</horstretch>")
        self.cfgxml_data.append("          <verstretch>0</verstretch>")
        self.cfgxml_data.append("         </sizepolicy>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="minimumSize">')
        self.cfgxml_data.append("         <size>")
        self.cfgxml_data.append(f"          <width>{width}</width>")
        self.cfgxml_data.append(f"          <height>{height}</height>")
        self.cfgxml_data.append("         </size>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="maximumSize">')
        self.cfgxml_data.append("         <size>")
        self.cfgxml_data.append(f"          <width>{width}</width>")
        self.cfgxml_data.append(f"          <height>{height}</height>")
        self.cfgxml_data.append("         </size>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append("     </widget>")
        self.cfgxml_data.append("    </item>")
        self.draw_hbox_end()
        return f"{self.prefix}.{halpin}.checked"

    def draw_led(self, name, halpin, setup={}):
        title = setup.get("title", name)
        halpin = halpin.replace("_", "-")
        width = setup.get("width", 16)
        height = setup.get("height", 16)
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
        if title:
            self.draw_title(title)
        self.cfgxml_data.append("    <item>")
        self.cfgxml_data.append(f'     <widget class="HalLedIndicator" name="rio.{halpin}">')
        self.cfgxml_data.append('        <property name="pinBaseName" stdset="0">')
        self.cfgxml_data.append(f"          <string>{halpin}</string>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="sizePolicy">')
        self.cfgxml_data.append('         <sizepolicy hsizetype="Fixed" vsizetype="Fixed">')
        self.cfgxml_data.append("          <horstretch>0</horstretch>")
        self.cfgxml_data.append("          <verstretch>0</verstretch>")
        self.cfgxml_data.append("         </sizepolicy>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="minimumSize">')
        self.cfgxml_data.append("         <size>")
        self.cfgxml_data.append(f"          <width>{width}</width>")
        self.cfgxml_data.append(f"          <height>{height}</height>")
        self.cfgxml_data.append("         </size>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="maximumSize">')
        self.cfgxml_data.append("         <size>")
        self.cfgxml_data.append(f"          <width>{width}</width>")
        self.cfgxml_data.append(f"          <height>{height}</height>")
        self.cfgxml_data.append("         </size>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append('        <property name="color">')
        self.cfgxml_data.append("          <color>")
        self.cfgxml_data.append(f"            {self.colormapping[on_color]}")
        self.cfgxml_data.append("          </color>")
        self.cfgxml_data.append("        </property>")
        self.cfgxml_data.append("     </widget>")
        self.cfgxml_data.append("    </item>")
        self.draw_hbox_end()
        return f"{self.prefix}.{halpin}.on"

    def draw_rectled(self, name, halpin, setup={}):
        return self.draw_led(name, halpin, setup=setup)
