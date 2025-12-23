
import os
import ctypes

class RioData(ctypes.Structure):
    _fields_ = [
      ("sys_enable", ctypes.POINTER(ctypes.c_bool)),
      ("sys_enable_request", ctypes.POINTER(ctypes.c_bool)),
      ("sys_status", ctypes.POINTER(ctypes.c_bool)),
      ("machine_on", ctypes.POINTER(ctypes.c_bool)),
      ("sys_simulation", ctypes.POINTER(ctypes.c_bool)),
      ("fpga_timestamp", ctypes.POINTER(ctypes.c_int)),
      ("duration", ctypes.POINTER(ctypes.c_float)),
      # signals
      ("SIGOUT_BOARD0_BOARD0_WLED_0_GREEN", ctypes.POINTER(ctypes.c_bool)),
      ("SIGOUT_BOARD0_BOARD0_WLED_0_BLUE", ctypes.POINTER(ctypes.c_bool)),
      ("SIGOUT_BOARD0_BOARD0_WLED_0_RED", ctypes.POINTER(ctypes.c_bool)),
      ("SIGOUT_BOARD0_STEPDIR0_VELOCITY", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_BOARD0_STEPDIR0_VELOCITY_SCALE", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_BOARD0_STEPDIR0_VELOCITY_OFFSET", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR0_POSITION", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR0_POSITION_ABS", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR0_POSITION_S32", ctypes.POINTER(ctypes.c_int32)),
      ("SIGIN_BOARD0_STEPDIR0_POSITION_U32_ABS", ctypes.POINTER(ctypes.c_uint32)),
      ("SIGIN_BOARD0_STEPDIR0_POSITION_SCALE", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR0_POSITION_OFFSET", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_BOARD0_STEPDIR0_ENABLE", ctypes.POINTER(ctypes.c_bool)),
      ("SIGOUT_BOARD0_STEPDIR1_VELOCITY", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_BOARD0_STEPDIR1_VELOCITY_SCALE", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_BOARD0_STEPDIR1_VELOCITY_OFFSET", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR1_POSITION", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR1_POSITION_ABS", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR1_POSITION_S32", ctypes.POINTER(ctypes.c_int32)),
      ("SIGIN_BOARD0_STEPDIR1_POSITION_U32_ABS", ctypes.POINTER(ctypes.c_uint32)),
      ("SIGIN_BOARD0_STEPDIR1_POSITION_SCALE", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR1_POSITION_OFFSET", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_BOARD0_STEPDIR1_ENABLE", ctypes.POINTER(ctypes.c_bool)),
      ("SIGOUT_BOARD0_STEPDIR2_VELOCITY", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_BOARD0_STEPDIR2_VELOCITY_SCALE", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_BOARD0_STEPDIR2_VELOCITY_OFFSET", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR2_POSITION", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR2_POSITION_ABS", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR2_POSITION_S32", ctypes.POINTER(ctypes.c_int32)),
      ("SIGIN_BOARD0_STEPDIR2_POSITION_U32_ABS", ctypes.POINTER(ctypes.c_uint32)),
      ("SIGIN_BOARD0_STEPDIR2_POSITION_SCALE", ctypes.POINTER(ctypes.c_float)),
      ("SIGIN_BOARD0_STEPDIR2_POSITION_OFFSET", ctypes.POINTER(ctypes.c_float)),
      ("SIGOUT_BOARD0_STEPDIR2_ENABLE", ctypes.POINTER(ctypes.c_bool)),
      # raw variables
      ("VAROUT32_STEPDIR0_VELOCITY", ctypes.c_uint32),
      ("VARIN32_STEPDIR0_POSITION", ctypes.c_uint32),
      ("VAROUT32_STEPDIR1_VELOCITY", ctypes.c_uint32),
      ("VARIN32_STEPDIR1_POSITION", ctypes.c_uint32),
      ("VAROUT32_STEPDIR2_VELOCITY", ctypes.c_uint32),
      ("VARIN32_STEPDIR2_POSITION", ctypes.c_uint32),
      ("VAROUT1_BOARD0_WLED_0_GREEN", ctypes.c_bool),
      ("VAROUT1_BOARD0_WLED_0_BLUE", ctypes.c_bool),
      ("VAROUT1_BOARD0_WLED_0_RED", ctypes.c_bool),
      ("VAROUT1_STEPDIR0_ENABLE", ctypes.c_bool),
      ("VAROUT1_STEPDIR1_ENABLE", ctypes.c_bool),
      ("VAROUT1_STEPDIR2_ENABLE", ctypes.c_bool),
    ]

class RioWrapper():
    def __init__(self, argv=[]):
        libname = os.path.join(os.path.dirname(__file__), "librio.so")
        self.rio = ctypes.CDLL(libname)
        self.rio.init.restype = ctypes.POINTER(RioData)
        p_args = list((arg.encode() for arg in argv))
        args = (ctypes.c_char_p * len(p_args))(*p_args)
        self.rio_data = self.rio.init(len(args), args)

    def rio_readwrite(self):
     self.rio.rio_readwrite(None, 0)

    def data_get(self, name):
        var = getattr(self.rio_data.contents, name)
        if hasattr(var, "contents"):
            return var.contents.value
        return var

    def data_set(self, name, value):
        var = getattr(self.rio_data.contents, name)
        if hasattr(var, "contents"):
            var.contents.value = value
        var = value

    def plugin_info(self):
        return {
            "board0": {
                "type": "fpga",
                "title": "board0",
                "is_joint": False,
                "variables": [
                ],
            },
            "board0_w5500": {
                "type": "w5500",
                "title": "board0_w5500",
                "is_joint": False,
                "variables": [
                ],
            },
            "board0_wled": {
                "type": "wled",
                "title": "board0_wled",
                "is_joint": False,
                "variables": [
                    "SIGOUT_BOARD0_BOARD0_WLED_0_GREEN",
                    "SIGOUT_BOARD0_BOARD0_WLED_0_BLUE",
                    "SIGOUT_BOARD0_BOARD0_WLED_0_RED",
                ],
            },
            "stepdir0": {
                "type": "stepdir",
                "title": "stepdir0",
                "plugin_ui": """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>Form</class>
 <widget class="QWidget" name="Form">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>418</width>
    <height>138</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Form</string>
  </property>
  <layout class="QGridLayout" name="gridLayout_2">
   <item row="0" column="0">
    <layout class="QVBoxLayout" name="verticalLayout">
     <item>
      <layout class="QHBoxLayout" name="horizontalLayout">
       <item>
        <widget class="QLabel" name="position_label">
         <property name="sizePolicy">
          <sizepolicy hsizetype="Fixed" vsizetype="Preferred">
           <horstretch>0</horstretch>
           <verstretch>0</verstretch>
          </sizepolicy>
         </property>
         <property name="font">
          <font>
           <pointsize>17</pointsize>
          </font>
         </property>
         <property name="text">
          <string>Position:</string>
         </property>
        </widget>
       </item>
       <item>
        <widget class="QLabel" name="position">
         <property name="font">
          <font>
           <pointsize>18</pointsize>
          </font>
         </property>
        </widget>
       </item>
       <item>
        <widget class="QLabel" name="unit">
         <property name="sizePolicy">
          <sizepolicy hsizetype="Preferred" vsizetype="Preferred">
           <horstretch>1</horstretch>
           <verstretch>0</verstretch>
          </sizepolicy>
         </property>
         <property name="text">
          <string>units</string>
         </property>
        </widget>
       </item>
       <item>
        <widget class="QPushButton" name="velocity_zero">
         <property name="sizePolicy">
          <sizepolicy hsizetype="Maximum" vsizetype="Minimum">
           <horstretch>0</horstretch>
           <verstretch>0</verstretch>
          </sizepolicy>
         </property>
         <property name="text">
          <string>Stop</string>
         </property>
        </widget>
       </item>
      </layout>
     </item>
    </layout>
   </item>
   <item row="3" column="0">
    <widget class="QScrollBar" name="velocity">
     <property name="minimumSize">
      <size>
       <width>0</width>
       <height>20</height>
      </size>
     </property>
     <property name="minimum">
      <number>-100000</number>
     </property>
     <property name="maximum">
      <number>100000</number>
     </property>
     <property name="pageStep">
      <number>100</number>
     </property>
     <property name="orientation">
      <enum>Qt::Horizontal</enum>
     </property>
    </widget>
   </item>
   <item row="1" column="0">
    <layout class="QHBoxLayout" name="horizontalLayout_2">
     <item>
      <widget class="QLabel" name="velocity_label">
       <property name="sizePolicy">
        <sizepolicy hsizetype="Fixed" vsizetype="Preferred">
         <horstretch>0</horstretch>
         <verstretch>0</verstretch>
        </sizepolicy>
       </property>
       <property name="text">
        <string>Velocity:</string>
       </property>
      </widget>
     </item>
     <item>
      <widget class="QLabel" name="velocity_out">
       <property name="sizePolicy">
        <sizepolicy hsizetype="Fixed" vsizetype="Preferred">
         <horstretch>0</horstretch>
         <verstretch>0</verstretch>
        </sizepolicy>
       </property>
       <property name="text">
        <string>TextLabel</string>
       </property>
      </widget>
     </item>
     <item>
      <widget class="QLabel" name="unit_out">
       <property name="sizePolicy">
        <sizepolicy hsizetype="Preferred" vsizetype="Fixed">
         <horstretch>1</horstretch>
         <verstretch>0</verstretch>
        </sizepolicy>
       </property>
       <property name="text">
        <string>Hz</string>
       </property>
      </widget>
     </item>
     <item>
      <widget class="QLabel" name="enable_lbael">
       <property name="sizePolicy">
        <sizepolicy hsizetype="Fixed" vsizetype="Preferred">
         <horstretch>0</horstretch>
         <verstretch>0</verstretch>
        </sizepolicy>
       </property>
       <property name="text">
        <string>Enable</string>
       </property>
      </widget>
     </item>
     <item>
      <widget class="QCheckBox" name="enable">
       <property name="sizePolicy">
        <sizepolicy hsizetype="Maximum" vsizetype="Minimum">
         <horstretch>0</horstretch>
         <verstretch>0</verstretch>
        </sizepolicy>
       </property>
       <property name="text">
        <string/>
       </property>
      </widget>
     </item>
    </layout>
   </item>
  </layout>
 </widget>
 <resources/>
 <connections/>
</ui>
""",
                "is_joint": True,
                "variables": [
                    "SIGOUT_BOARD0_STEPDIR0_VELOCITY",
                    "SIGIN_BOARD0_STEPDIR0_POSITION",
                    "SIGOUT_BOARD0_STEPDIR0_ENABLE",
                ],
            },
            "stepdir1": {
                "type": "stepdir",
                "title": "stepdir1",
                "plugin_ui": """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>Form</class>
 <widget class="QWidget" name="Form">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>418</width>
    <height>138</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Form</string>
  </property>
  <layout class="QGridLayout" name="gridLayout_2">
   <item row="0" column="0">
    <layout class="QVBoxLayout" name="verticalLayout">
     <item>
      <layout class="QHBoxLayout" name="horizontalLayout">
       <item>
        <widget class="QLabel" name="position_label">
         <property name="sizePolicy">
          <sizepolicy hsizetype="Fixed" vsizetype="Preferred">
           <horstretch>0</horstretch>
           <verstretch>0</verstretch>
          </sizepolicy>
         </property>
         <property name="font">
          <font>
           <pointsize>17</pointsize>
          </font>
         </property>
         <property name="text">
          <string>Position:</string>
         </property>
        </widget>
       </item>
       <item>
        <widget class="QLabel" name="position">
         <property name="font">
          <font>
           <pointsize>18</pointsize>
          </font>
         </property>
        </widget>
       </item>
       <item>
        <widget class="QLabel" name="unit">
         <property name="sizePolicy">
          <sizepolicy hsizetype="Preferred" vsizetype="Preferred">
           <horstretch>1</horstretch>
           <verstretch>0</verstretch>
          </sizepolicy>
         </property>
         <property name="text">
          <string>units</string>
         </property>
        </widget>
       </item>
       <item>
        <widget class="QPushButton" name="velocity_zero">
         <property name="sizePolicy">
          <sizepolicy hsizetype="Maximum" vsizetype="Minimum">
           <horstretch>0</horstretch>
           <verstretch>0</verstretch>
          </sizepolicy>
         </property>
         <property name="text">
          <string>Stop</string>
         </property>
        </widget>
       </item>
      </layout>
     </item>
    </layout>
   </item>
   <item row="3" column="0">
    <widget class="QScrollBar" name="velocity">
     <property name="minimumSize">
      <size>
       <width>0</width>
       <height>20</height>
      </size>
     </property>
     <property name="minimum">
      <number>-100000</number>
     </property>
     <property name="maximum">
      <number>100000</number>
     </property>
     <property name="pageStep">
      <number>100</number>
     </property>
     <property name="orientation">
      <enum>Qt::Horizontal</enum>
     </property>
    </widget>
   </item>
   <item row="1" column="0">
    <layout class="QHBoxLayout" name="horizontalLayout_2">
     <item>
      <widget class="QLabel" name="velocity_label">
       <property name="sizePolicy">
        <sizepolicy hsizetype="Fixed" vsizetype="Preferred">
         <horstretch>0</horstretch>
         <verstretch>0</verstretch>
        </sizepolicy>
       </property>
       <property name="text">
        <string>Velocity:</string>
       </property>
      </widget>
     </item>
     <item>
      <widget class="QLabel" name="velocity_out">
       <property name="sizePolicy">
        <sizepolicy hsizetype="Fixed" vsizetype="Preferred">
         <horstretch>0</horstretch>
         <verstretch>0</verstretch>
        </sizepolicy>
       </property>
       <property name="text">
        <string>TextLabel</string>
       </property>
      </widget>
     </item>
     <item>
      <widget class="QLabel" name="unit_out">
       <property name="sizePolicy">
        <sizepolicy hsizetype="Preferred" vsizetype="Fixed">
         <horstretch>1</horstretch>
         <verstretch>0</verstretch>
        </sizepolicy>
       </property>
       <property name="text">
        <string>Hz</string>
       </property>
      </widget>
     </item>
     <item>
      <widget class="QLabel" name="enable_lbael">
       <property name="sizePolicy">
        <sizepolicy hsizetype="Fixed" vsizetype="Preferred">
         <horstretch>0</horstretch>
         <verstretch>0</verstretch>
        </sizepolicy>
       </property>
       <property name="text">
        <string>Enable</string>
       </property>
      </widget>
     </item>
     <item>
      <widget class="QCheckBox" name="enable">
       <property name="sizePolicy">
        <sizepolicy hsizetype="Maximum" vsizetype="Minimum">
         <horstretch>0</horstretch>
         <verstretch>0</verstretch>
        </sizepolicy>
       </property>
       <property name="text">
        <string/>
       </property>
      </widget>
     </item>
    </layout>
   </item>
  </layout>
 </widget>
 <resources/>
 <connections/>
</ui>
""",
                "is_joint": True,
                "variables": [
                    "SIGOUT_BOARD0_STEPDIR1_VELOCITY",
                    "SIGIN_BOARD0_STEPDIR1_POSITION",
                    "SIGOUT_BOARD0_STEPDIR1_ENABLE",
                ],
            },
            "stepdir2": {
                "type": "stepdir",
                "title": "stepdir2",
                "plugin_ui": """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>Form</class>
 <widget class="QWidget" name="Form">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>418</width>
    <height>138</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Form</string>
  </property>
  <layout class="QGridLayout" name="gridLayout_2">
   <item row="0" column="0">
    <layout class="QVBoxLayout" name="verticalLayout">
     <item>
      <layout class="QHBoxLayout" name="horizontalLayout">
       <item>
        <widget class="QLabel" name="position_label">
         <property name="sizePolicy">
          <sizepolicy hsizetype="Fixed" vsizetype="Preferred">
           <horstretch>0</horstretch>
           <verstretch>0</verstretch>
          </sizepolicy>
         </property>
         <property name="font">
          <font>
           <pointsize>17</pointsize>
          </font>
         </property>
         <property name="text">
          <string>Position:</string>
         </property>
        </widget>
       </item>
       <item>
        <widget class="QLabel" name="position">
         <property name="font">
          <font>
           <pointsize>18</pointsize>
          </font>
         </property>
        </widget>
       </item>
       <item>
        <widget class="QLabel" name="unit">
         <property name="sizePolicy">
          <sizepolicy hsizetype="Preferred" vsizetype="Preferred">
           <horstretch>1</horstretch>
           <verstretch>0</verstretch>
          </sizepolicy>
         </property>
         <property name="text">
          <string>units</string>
         </property>
        </widget>
       </item>
       <item>
        <widget class="QPushButton" name="velocity_zero">
         <property name="sizePolicy">
          <sizepolicy hsizetype="Maximum" vsizetype="Minimum">
           <horstretch>0</horstretch>
           <verstretch>0</verstretch>
          </sizepolicy>
         </property>
         <property name="text">
          <string>Stop</string>
         </property>
        </widget>
       </item>
      </layout>
     </item>
    </layout>
   </item>
   <item row="3" column="0">
    <widget class="QScrollBar" name="velocity">
     <property name="minimumSize">
      <size>
       <width>0</width>
       <height>20</height>
      </size>
     </property>
     <property name="minimum">
      <number>-100000</number>
     </property>
     <property name="maximum">
      <number>100000</number>
     </property>
     <property name="pageStep">
      <number>100</number>
     </property>
     <property name="orientation">
      <enum>Qt::Horizontal</enum>
     </property>
    </widget>
   </item>
   <item row="1" column="0">
    <layout class="QHBoxLayout" name="horizontalLayout_2">
     <item>
      <widget class="QLabel" name="velocity_label">
       <property name="sizePolicy">
        <sizepolicy hsizetype="Fixed" vsizetype="Preferred">
         <horstretch>0</horstretch>
         <verstretch>0</verstretch>
        </sizepolicy>
       </property>
       <property name="text">
        <string>Velocity:</string>
       </property>
      </widget>
     </item>
     <item>
      <widget class="QLabel" name="velocity_out">
       <property name="sizePolicy">
        <sizepolicy hsizetype="Fixed" vsizetype="Preferred">
         <horstretch>0</horstretch>
         <verstretch>0</verstretch>
        </sizepolicy>
       </property>
       <property name="text">
        <string>TextLabel</string>
       </property>
      </widget>
     </item>
     <item>
      <widget class="QLabel" name="unit_out">
       <property name="sizePolicy">
        <sizepolicy hsizetype="Preferred" vsizetype="Fixed">
         <horstretch>1</horstretch>
         <verstretch>0</verstretch>
        </sizepolicy>
       </property>
       <property name="text">
        <string>Hz</string>
       </property>
      </widget>
     </item>
     <item>
      <widget class="QLabel" name="enable_lbael">
       <property name="sizePolicy">
        <sizepolicy hsizetype="Fixed" vsizetype="Preferred">
         <horstretch>0</horstretch>
         <verstretch>0</verstretch>
        </sizepolicy>
       </property>
       <property name="text">
        <string>Enable</string>
       </property>
      </widget>
     </item>
     <item>
      <widget class="QCheckBox" name="enable">
       <property name="sizePolicy">
        <sizepolicy hsizetype="Maximum" vsizetype="Minimum">
         <horstretch>0</horstretch>
         <verstretch>0</verstretch>
        </sizepolicy>
       </property>
       <property name="text">
        <string/>
       </property>
      </widget>
     </item>
    </layout>
   </item>
  </layout>
 </widget>
 <resources/>
 <connections/>
</ui>
""",
                "is_joint": True,
                "variables": [
                    "SIGOUT_BOARD0_STEPDIR2_VELOCITY",
                    "SIGIN_BOARD0_STEPDIR2_POSITION",
                    "SIGOUT_BOARD0_STEPDIR2_ENABLE",
                ],
            },
        }

    def data_info(self):
        return {
            "SIGOUT_BOARD0_BOARD0_WLED_0_GREEN": {
                "plugin": "board0_wled",
                "direction": "output",
                "signal_name": "0_green",
                "userconfig": {},
                "unit": "",
                "halname": "board0.board0_wled.0_green",
                "netname": "",
                "type": "bool",
                "subs": {
                },
            },
            "SIGOUT_BOARD0_BOARD0_WLED_0_BLUE": {
                "plugin": "board0_wled",
                "direction": "output",
                "signal_name": "0_blue",
                "userconfig": {},
                "unit": "",
                "halname": "board0.board0_wled.0_blue",
                "netname": "",
                "type": "bool",
                "subs": {
                },
            },
            "SIGOUT_BOARD0_BOARD0_WLED_0_RED": {
                "plugin": "board0_wled",
                "direction": "output",
                "signal_name": "0_red",
                "userconfig": {},
                "unit": "",
                "halname": "board0.board0_wled.0_red",
                "netname": "",
                "type": "bool",
                "subs": {
                },
            },
            "SIGOUT_BOARD0_STEPDIR0_VELOCITY": {
                "plugin": "stepdir0",
                "direction": "output",
                "signal_name": "velocity",
                "userconfig": {},
                "unit": "Hz",
                "halname": "board0.stepdir0.velocity",
                "netname": "",
                "type": "float",
                "subs": {
                    "SIGOUT_BOARD0_STEPDIR0_VELOCITY_SCALE": {"type": "float"},
                    "SIGOUT_BOARD0_STEPDIR0_VELOCITY_OFFSET": {"type": "float"},
                },
            },
            "SIGIN_BOARD0_STEPDIR0_POSITION": {
                "plugin": "stepdir0",
                "direction": "input",
                "signal_name": "position",
                "userconfig": {},
                "unit": "steps",
                "halname": "board0.stepdir0.position",
                "netname": "",
                "type": "float",
                "subs": {
                    "SIGIN_BOARD0_STEPDIR0_POSITION_ABS": {"type": "float"},
                    "SIGIN_BOARD0_STEPDIR0_POSITION_S32": {"type": "int32"},
                    "SIGIN_BOARD0_STEPDIR0_POSITION_U32_ABS": {"type": "uint32"},
                    "SIGIN_BOARD0_STEPDIR0_POSITION_SCALE": {"type": "float"},
                    "SIGIN_BOARD0_STEPDIR0_POSITION_OFFSET": {"type": "float"},
                },
            },
            "SIGOUT_BOARD0_STEPDIR0_ENABLE": {
                "plugin": "stepdir0",
                "direction": "output",
                "signal_name": "enable",
                "userconfig": {},
                "unit": "",
                "halname": "board0.stepdir0.enable",
                "netname": "",
                "type": "bool",
                "subs": {
                },
            },
            "SIGOUT_BOARD0_STEPDIR1_VELOCITY": {
                "plugin": "stepdir1",
                "direction": "output",
                "signal_name": "velocity",
                "userconfig": {},
                "unit": "Hz",
                "halname": "board0.stepdir1.velocity",
                "netname": "",
                "type": "float",
                "subs": {
                    "SIGOUT_BOARD0_STEPDIR1_VELOCITY_SCALE": {"type": "float"},
                    "SIGOUT_BOARD0_STEPDIR1_VELOCITY_OFFSET": {"type": "float"},
                },
            },
            "SIGIN_BOARD0_STEPDIR1_POSITION": {
                "plugin": "stepdir1",
                "direction": "input",
                "signal_name": "position",
                "userconfig": {},
                "unit": "steps",
                "halname": "board0.stepdir1.position",
                "netname": "",
                "type": "float",
                "subs": {
                    "SIGIN_BOARD0_STEPDIR1_POSITION_ABS": {"type": "float"},
                    "SIGIN_BOARD0_STEPDIR1_POSITION_S32": {"type": "int32"},
                    "SIGIN_BOARD0_STEPDIR1_POSITION_U32_ABS": {"type": "uint32"},
                    "SIGIN_BOARD0_STEPDIR1_POSITION_SCALE": {"type": "float"},
                    "SIGIN_BOARD0_STEPDIR1_POSITION_OFFSET": {"type": "float"},
                },
            },
            "SIGOUT_BOARD0_STEPDIR1_ENABLE": {
                "plugin": "stepdir1",
                "direction": "output",
                "signal_name": "enable",
                "userconfig": {},
                "unit": "",
                "halname": "board0.stepdir1.enable",
                "netname": "",
                "type": "bool",
                "subs": {
                },
            },
            "SIGOUT_BOARD0_STEPDIR2_VELOCITY": {
                "plugin": "stepdir2",
                "direction": "output",
                "signal_name": "velocity",
                "userconfig": {},
                "unit": "Hz",
                "halname": "board0.stepdir2.velocity",
                "netname": "",
                "type": "float",
                "subs": {
                    "SIGOUT_BOARD0_STEPDIR2_VELOCITY_SCALE": {"type": "float"},
                    "SIGOUT_BOARD0_STEPDIR2_VELOCITY_OFFSET": {"type": "float"},
                },
            },
            "SIGIN_BOARD0_STEPDIR2_POSITION": {
                "plugin": "stepdir2",
                "direction": "input",
                "signal_name": "position",
                "userconfig": {},
                "unit": "steps",
                "halname": "board0.stepdir2.position",
                "netname": "",
                "type": "float",
                "subs": {
                    "SIGIN_BOARD0_STEPDIR2_POSITION_ABS": {"type": "float"},
                    "SIGIN_BOARD0_STEPDIR2_POSITION_S32": {"type": "int32"},
                    "SIGIN_BOARD0_STEPDIR2_POSITION_U32_ABS": {"type": "uint32"},
                    "SIGIN_BOARD0_STEPDIR2_POSITION_SCALE": {"type": "float"},
                    "SIGIN_BOARD0_STEPDIR2_POSITION_OFFSET": {"type": "float"},
                },
            },
            "SIGOUT_BOARD0_STEPDIR2_ENABLE": {
                "plugin": "stepdir2",
                "direction": "output",
                "signal_name": "enable",
                "userconfig": {},
                "unit": "",
                "halname": "board0.stepdir2.enable",
                "netname": "",
                "type": "bool",
                "subs": {
                },
            },
        }
