#!/usr/bin/env python3
#
#


from lxml import etree

from riocore.generator.gladevcp import gladevcp


def test_gladevcp():
    expected = """
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
        <child>
          <object class="GtkNotebook">
            <property name="visible">True</property>
            <property name="can-focus">True</property>
            <child>
              <object class="GtkBox" id="vbox_tab_tab1">
                <property name="margin">10</property>
                <property name="spacing">10</property>
                <property name="visible">True</property>
                <property name="can-focus">False</property>
                <property name="orientation">vertical</property>
                <child>
                  <object class="GtkHBox">
                    <property name="visible">True</property>
                    <property name="spacing">2</property>
                    <child>
                      <object class="GtkLabel">
                        <property name="visible">True</property>
                        <property name="can-focus">False</property>
                        <property name="label" translatable="yes">led1</property>
                        <property name="xpad">6</property>
                        <property name="xalign">0</property>
                      </object>
                      <packing>
                        <property name="expand">True</property>
                        <property name="fill">True</property>
                        <property name="position">1</property>
                      </packing>
                    </child>
                    <child>
                      <object class="HAL_LED" id="hal_led">
                        <property name="visible">True</property>
                        <property name="pick_color_on">#ffffb7b90b5c</property>
                        <property name="pick_color_off">#000000000000</property>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="position">1</property>
                      </packing>
                    </child>
                  </object>
                </child>
              </object>
            </child>
            <child type="tab">
              <object class="GtkLabel">
                <property name="visible">True</property>
                <property name="can-focus">False</property>
                <property name="label" translatable="yes">tab1</property>
              </object>
              <packing>
                <property name="tab-fill">False</property>
              </packing>
            </child>
            <child>
              <object class="GtkBox" id="vbox_tab_tab2">
                <property name="margin">10</property>
                <property name="spacing">10</property>
                <property name="visible">True</property>
                <property name="can-focus">False</property>
                <property name="orientation">vertical</property>
                <child>
                  <object class="GtkHBox">
                    <property name="visible">True</property>
                    <property name="spacing">2</property>
                    <child>
                      <object class="GtkLabel">
                        <property name="visible">True</property>
                        <property name="can-focus">False</property>
                        <property name="label" translatable="yes">check1</property>
                        <property name="xpad">6</property>
                        <property name="xalign">0</property>
                      </object>
                      <packing>
                        <property name="expand">True</property>
                        <property name="fill">True</property>
                        <property name="position">1</property>
                      </packing>
                    </child>
                    <child>
                      <object class="HAL_ToggleButton" id="hal_check1">
                        <property name="label" translatable="yes"/>
                        <property name="visible">True</property>
                        <property name="can_focus">True</property>
                        <property name="receives_default">False</property>
                        <property name="draw_indicator">True</property>
                      </object>
                      <packing>
                        <property name="expand">False</property>
                        <property name="fill">True</property>
                        <property name="position">1</property>
                      </packing>
                    </child>
                  </object>
                </child>
              </object>
            </child>
            <child type="tab">
              <object class="GtkLabel">
                <property name="visible">True</property>
                <property name="can-focus">False</property>
                <property name="label" translatable="yes">tab2</property>
              </object>
              <packing>
                <property name="tab-fill">False</property>
              </packing>
            </child>
            <child>
              <object class="GtkBox" id="vbox_tab_tab3">
                <property name="margin">10</property>
                <property name="spacing">10</property>
                <property name="visible">True</property>
                <property name="can-focus">False</property>
                <property name="orientation">vertical</property>
                <child>
                  <object class="HAL_Button" id="hal_button1">
                    <property name="label" translatable="yes">button11</property>
                    <property name="visible">True</property>
                    <property name="can-focus">True</property>
                    <property name="receives-default">True</property>
                  </object>
                  <packing>
                    <property name="expand">True</property>
                    <property name="fill">True</property>
                    <property name="position">1</property>
                  </packing>
                </child>
              </object>
            </child>
            <child type="tab">
              <object class="GtkLabel">
                <property name="visible">True</property>
                <property name="can-focus">False</property>
                <property name="label" translatable="yes">tab3</property>
              </object>
              <packing>
                <property name="tab-fill">False</property>
              </packing>
            </child>
          </object>
        </child>
      </object>
    </child>
  </object>
</interface>
"""

    gui = gladevcp()

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
