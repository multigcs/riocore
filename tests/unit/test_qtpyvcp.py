#!/usr/bin/env python3
#
#


from lxml import etree

from riocore.generator.qtpyvcp import qtpyvcp


def test_qtpyvcp():
    expected = """
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
      <item row="0" column="0">
        <widget class="QTabWidget" name="tabWidget_setup">
          <widget class="QWidget" name="tab_tab1">
            <attribute name="title">
              <string>tab1</string>
            </attribute>
            <layout class="QVBoxLayout" name="layout_stat">
              <property name="spacing">
                <number>0</number>
              </property>
              <property name="leftMargin">
                <number>0</number>
              </property>
              <property name="topMargin">
                <number>0</number>
              </property>
              <property name="rightMargin">
                <number>0</number>
              </property>
              <property name="bottomMargin">
                <number>0</number>
              </property>
              <item>
                <layout class="QVBoxLayout" name="verticalLayout_5">
                  <property name="leftMargin">
                    <number>5</number>
                  </property>
                  <property name="topMargin">
                    <number>10</number>
                  </property>
                  <property name="rightMargin">
                    <number>5</number>
                  </property>
                  <property name="bottomMargin">
                    <number>10</number>
                  </property>
                  <item>
                    <layout class="QHBoxLayout" name="hosizontalLayout_3">
                      <property name="leftMargin">
                        <number>5</number>
                      </property>
                      <property name="topMargin">
                        <number>0</number>
                      </property>
                      <property name="rightMargin">
                        <number>5</number>
                      </property>
                      <property name="bottomMargin">
                        <number>0</number>
                      </property>
                      <item>
                        <widget class="QLabel">
                          <property name="text">
                            <string>led1</string>
                          </property>
                          <property name="indent">
                            <number>4</number>
                          </property>
                        </widget>
                      </item>
                      <item>
                        <widget class="HalLedIndicator" name="rio.hal-led">
                          <property name="pinBaseName" stdset="0">
                            <string>hal-led</string>
                          </property>
                          <property name="sizePolicy">
                            <sizepolicy hsizetype="Fixed" vsizetype="Fixed">
                              <horstretch>0</horstretch>
                              <verstretch>0</verstretch>
                            </sizepolicy>
                          </property>
                          <property name="minimumSize">
                            <size>
                              <width>16</width>
                              <height>16</height>
                            </size>
                          </property>
                          <property name="maximumSize">
                            <size>
                              <width>16</width>
                              <height>16</height>
                            </size>
                          </property>
                          <property name="color">
                            <color>
                              <red>255</red>
                              <green>255</green>
                              <blue>0</blue>
                            </color>
                          </property>
                        </widget>
                      </item>
                    </layout>
                  </item>
                  <item>
                    <widget class="QWidget" name="widget" native="true"/>
                  </item>
                </layout>
              </item>
            </layout>
          </widget>
          <widget class="QWidget" name="tab_tab2">
            <attribute name="title">
              <string>tab2</string>
            </attribute>
            <layout class="QVBoxLayout" name="layout_stat">
              <property name="spacing">
                <number>0</number>
              </property>
              <property name="leftMargin">
                <number>0</number>
              </property>
              <property name="topMargin">
                <number>0</number>
              </property>
              <property name="rightMargin">
                <number>0</number>
              </property>
              <property name="bottomMargin">
                <number>0</number>
              </property>
              <item>
                <layout class="QVBoxLayout" name="verticalLayout_5">
                  <property name="leftMargin">
                    <number>5</number>
                  </property>
                  <property name="topMargin">
                    <number>10</number>
                  </property>
                  <property name="rightMargin">
                    <number>5</number>
                  </property>
                  <property name="bottomMargin">
                    <number>10</number>
                  </property>
                  <item>
                    <layout class="QHBoxLayout" name="hosizontalLayout_3">
                      <property name="leftMargin">
                        <number>5</number>
                      </property>
                      <property name="topMargin">
                        <number>0</number>
                      </property>
                      <property name="rightMargin">
                        <number>5</number>
                      </property>
                      <property name="bottomMargin">
                        <number>0</number>
                      </property>
                      <item>
                        <widget class="QLabel">
                          <property name="text">
                            <string>check1</string>
                          </property>
                          <property name="indent">
                            <number>4</number>
                          </property>
                        </widget>
                      </item>
                      <item>
                        <widget class="HalCheckBox" name="rio.hal-check1">
                          <property name="checked">
                            <number>0</number>
                          </property>
                          <property name="pinBaseName" stdset="0">
                            <string>hal-check1</string>
                          </property>
                          <property name="sizePolicy">
                            <sizepolicy hsizetype="Fixed" vsizetype="Fixed">
                              <horstretch>0</horstretch>
                              <verstretch>0</verstretch>
                            </sizepolicy>
                          </property>
                          <property name="minimumSize">
                            <size>
                              <width>16</width>
                              <height>16</height>
                            </size>
                          </property>
                          <property name="maximumSize">
                            <size>
                              <width>16</width>
                              <height>16</height>
                            </size>
                          </property>
                        </widget>
                      </item>
                    </layout>
                  </item>
                  <item>
                    <widget class="QWidget" name="widget" native="true"/>
                  </item>
                </layout>
              </item>
            </layout>
          </widget>
          <widget class="QWidget" name="tab_tab3">
            <attribute name="title">
              <string>tab3</string>
            </attribute>
            <layout class="QVBoxLayout" name="layout_stat">
              <property name="spacing">
                <number>0</number>
              </property>
              <property name="leftMargin">
                <number>0</number>
              </property>
              <property name="topMargin">
                <number>0</number>
              </property>
              <property name="rightMargin">
                <number>0</number>
              </property>
              <property name="bottomMargin">
                <number>0</number>
              </property>
              <item>
                <layout class="QVBoxLayout" name="verticalLayout_5">
                  <property name="leftMargin">
                    <number>5</number>
                  </property>
                  <property name="topMargin">
                    <number>10</number>
                  </property>
                  <property name="rightMargin">
                    <number>5</number>
                  </property>
                  <property name="bottomMargin">
                    <number>10</number>
                  </property>
                  <item>
                    <widget class="HalButton" name="rio.hal-button1">
                      <property name="pinBaseName" stdset="0">
                        <string>hal-button1</string>
                      </property>
                      <property name="text">
                        <string>button11</string>
                      </property>
                    </widget>
                  </item>
                  <item>
                    <widget class="QWidget" name="widget" native="true"/>
                  </item>
                </layout>
              </item>
            </layout>
          </widget>
        </widget>
      </item>
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
"""

    gui = qtpyvcp()

    gui.draw_begin()
    gui.draw_tabs_begin(["tab1", "tab2", "tab3"])

    gui.draw_tab_begin("tab1")
    gui.draw_led("led1", "hal_led")
    gui.draw_tab_end()

    gui.draw_tab_begin("tab2")
    gui.draw_checkbutton("check1", "hal_check1")
    gui.draw_tab_end()

    gui.draw_tab_begin("tab3")
    gui.draw_button("button11", "hal_button1")
    gui.draw_tab_end()

    gui.draw_tabs_end()
    gui.draw_end()

    xml_string = gui.xml()
    parser = etree.XMLParser(ns_clean=True, remove_blank_text=True)
    root = etree.fromstring(xml_string.encode(), parser)
    formated = etree.tostring(root, pretty_print=True).decode()

    print(formated)

    assert formated.strip() == expected.strip()
