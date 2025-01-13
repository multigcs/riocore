#!/usr/bin/env python3
#
#

import pytest

from lxml import etree

from riocore.generator.pyvcp import pyvcp


def test_pyvcp():
    expected = """
<pyvcp>
  <tabs>
    <names>['tab1', 'tab2', 'tab3']</names>
    <vbox>
      <hbox>
        <relief>RAISED</relief>
        <bd>2</bd>
        <label>
          <text>"led1      "</text>
          <font>("Helvetica",9)</font>
          <width>13</width>
        </label>
        <led>
          <halpin>"hal_led"</halpin>
          <size>16</size>
          <on_color>"yellow"</on_color>
          <off_color>"red"</off_color>
        </led>
      </hbox>
    </vbox>
    <vbox>
      <hbox>
        <relief>RAISED</relief>
        <bd>2</bd>
        <label>
          <text>"check1    "</text>
          <font>("Helvetica",9)</font>
          <width>13</width>
        </label>
        <checkbutton>
          <halpin>"hal_check1"</halpin>
        </checkbutton>
      </hbox>
    </vbox>
    <vbox>
      <button>
        <relief>RAISED</relief>
        <bd>3</bd>
        <halpin>"hal_button1"</halpin>
        <text>"button11"</text>
        <font>("Helvetica", 12)</font>
      </button>
    </vbox>
  </tabs>
  <label>
    <text>""</text>
    <width>30</width>
  </label>
</pyvcp>
"""

    gui = pyvcp()

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
