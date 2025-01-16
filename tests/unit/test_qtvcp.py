#!/usr/bin/env python3
#
#

import pytest

from lxml import etree

from riocore.generator.qtvcp import qtvcp


def test_qtvcp():
    expected = """
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
        <item>
          <widget class="QGroupBox" name="groupBox_rio">
            <property name="title">
              <string>RIO</string>
            </property>
            <property name="sizePolicy">
              <sizepolicy hsizetype="Minimum" vsizetype="Preferred">
                <horstretch>0</horstretch>
                <verstretch>0</verstretch>
              </sizepolicy>
            </property>
            <property name="minimumSize">
              <size>
                <width>200</width>
                <height>0</height>
              </size>
            </property>
            <property name="alignment">
              <set>Qt::AlignCenter</set>
            </property>
            <layout class="QVBoxLayout" name="verticalLayout_30">
              <property name="spacing">
                <number>6</number>
              </property>
              <property name="leftMargin">
                <number>2</number>
              </property>
              <property name="topMargin">
                <number>2</number>
              </property>
              <property name="rightMargin">
                <number>2</number>
              </property>
              <property name="bottomMargin">
                <number>2</number>
              </property>
              <item>
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
                        <layout class="QVBoxLayout">
                          <property name="leftMargin">
                            <number>5</number>
                          </property>
                          <property name="topMargin">
                            <number>5</number>
                          </property>
                          <property name="rightMargin">
                            <number>5</number>
                          </property>
                          <property name="bottomMargin">
                            <number>5</number>
                          </property>
                          <item>
                            <layout class="QHBoxLayout">
                              <property name="leftMargin">
                                <number>5</number>
                              </property>
                              <property name="topMargin">
                                <number>5</number>
                              </property>
                              <property name="rightMargin">
                                <number>5</number>
                              </property>
                              <property name="bottomMargin">
                                <number>5</number>
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
                                <widget class="LED" name="hal_led">
                                  <property name="sizePolicy">
                                    <sizepolicy hsizetype="Fixed" vsizetype="Fixed">
                                      <horstretch>0</horstretch>
                                      <verstretch>0</verstretch>
                                    </sizepolicy>
                                  </property>
                                  <property name="diameter">
                                    <number>16</number>
                                  </property>
                                  <property name="minimumSize">
                                    <size>
                                      <width>32</width>
                                      <height>32</height>
                                    </size>
                                  </property>
                                  <property name="color">
                                    <color>
                                      <red>85</red>
                                      <green>255</green>
                                      <blue>0</blue>
                                    </color>
                                  </property>
                                  <property name="maximumSize">
                                    <size>
                                      <width>32</width>
                                      <height>32</height>
                                    </size>
                                  </property>
                                </widget>
                              </item>
                            </layout>
                          </item>
                          <item>
                            <widget class="QWidget" native="true"/>
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
                        <layout class="QVBoxLayout">
                          <property name="leftMargin">
                            <number>5</number>
                          </property>
                          <property name="topMargin">
                            <number>5</number>
                          </property>
                          <property name="rightMargin">
                            <number>5</number>
                          </property>
                          <property name="bottomMargin">
                            <number>5</number>
                          </property>
                          <item>
                            <layout class="QHBoxLayout">
                              <property name="leftMargin">
                                <number>5</number>
                              </property>
                              <property name="topMargin">
                                <number>5</number>
                              </property>
                              <property name="rightMargin">
                                <number>5</number>
                              </property>
                              <property name="bottomMargin">
                                <number>5</number>
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
                                <widget class="PushButton" name="hal_check1">
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
                QLabel {
                    color: rgb(235, 235, 235);
                }
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
                            </layout>
                          </item>
                          <item>
                            <widget class="QWidget" native="true"/>
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
                        <layout class="QVBoxLayout">
                          <property name="leftMargin">
                            <number>5</number>
                          </property>
                          <property name="topMargin">
                            <number>5</number>
                          </property>
                          <property name="rightMargin">
                            <number>5</number>
                          </property>
                          <property name="bottomMargin">
                            <number>5</number>
                          </property>
                          <item>
                            <widget class="PushButton" name="hal_button1">
                              <property name="text">
                                <string>BUTTON11</string>
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
QLabel {
    color: rgb(235, 235, 235);
}
                 </string>
                              </property>
                            </widget>
                          </item>
                          <item>
                            <widget class="QWidget" native="true"/>
                          </item>
                        </layout>
                      </item>
                    </layout>
                  </widget>
                </widget>
              </item>
            </layout>
          </widget>
        </item>
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
</ui>
"""

    gui = qtvcp()

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
    # print(xml_string)

    parser = etree.XMLParser(ns_clean=True, remove_blank_text=True)
    root = etree.fromstring(xml_string.encode(), parser)
    formated = etree.tostring(root, pretty_print=True).decode()

    print(formated)

    assert formated.strip() == expected.strip()
