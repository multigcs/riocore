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
      <vbox>
        <relief>RIDGE</relief>
        <bd>2</bd>
        <hbox>
          <relief>RAISED</relief>
          <bd>2</bd>
          <label>
            <text>"led1      "</text>
            <font>("Helvetica",9)</font>
            <width>13</width>
          </label>
          <led>
            <halpin>"hal_led1"</halpin>
            <size>16</size>
            <on_color>"yellow"</on_color>
            <off_color>"red"</off_color>
          </led>
        </hbox>
        <hbox>
          <relief>RAISED</relief>
          <bd>2</bd>
          <label>
            <text>"led2      "</text>
            <font>("Helvetica",9)</font>
            <width>13</width>
          </label>
          <led>
            <halpin>"hal_led2"</halpin>
            <size>16</size>
            <on_color>"yellow"</on_color>
            <off_color>"red"</off_color>
          </led>
        </hbox>
        <hbox>
          <relief>RAISED</relief>
          <bd>2</bd>
          <label>
            <text>"name      "</text>
            <font>("Helvetica",9)</font>
            <width>13</width>
          </label>
          <scale>
            <halpin>"halpin1"</halpin>
            <resolution>0.1</resolution>
            <orient>HORIZONTAL</orient>
            <initval>0</initval>
            <param_pin>1</param_pin>
          </scale>
        </hbox>
        <vbox>
          <relief>RAISED</relief>
          <bd>2</bd>
          <labelframe text="name">
            <multilabel>
              <legends>['v0', 'v1']</legends>
              <halpin>"halpin2"</halpin>
              <font>("Helvetica", 12)</font>
              <bg>"black"</bg>
              <fg>"yellow"</fg>
            </multilabel>
            <scale>
              <halpin>"halpin2"</halpin>
              <resolution>1</resolution>
              <orient>HORIZONTAL</orient>
              <initval>0</initval>
              <param_pin>1</param_pin>
            </scale>
          </labelframe>
        </vbox>
      </vbox>
      <labelframe text="myframe">
        <relief>RIDGE</relief>
        <font>("Helvetica", 10)</font>
        <hbox>
          <relief>RAISED</relief>
          <bd>2</bd>
          <label>
            <text>"name      "</text>
            <font>("Helvetica",9)</font>
            <width>13</width>
          </label>
          <spinbox>
            <halpin>"halpin3"</halpin>
            <resolution>0.1</resolution>
            <initval>0</initval>
            <param_pin>1</param_pin>
          </spinbox>
        </hbox>
        <jogwheel>
          <halpin>"halpin4"</halpin>
          <text>"name"</text>
          <size>200</size>
          <cpr>50</cpr>
          <resolution>0.1</resolution>
          <initval>0</initval>
          <param_pin>1</param_pin>
        </jogwheel>
      </labelframe>
    </vbox>
    <vbox>
      <hbox>
        <relief>RIDGE</relief>
        <bd>2</bd>
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
        <hbox>
          <relief>RAISED</relief>
          <bd>2</bd>
          <label>
            <text>"check2    "</text>
            <font>("Helvetica",9)</font>
            <width>13</width>
          </label>
          <checkbutton>
            <halpin>"hal_check2"</halpin>
          </checkbutton>
        </hbox>
        <dial>
          <halpin>"halpin5"</halpin>
          <text>"name"</text>
          <size>200</size>
          <cpr>50</cpr>
          <resolution>0.1</resolution>
          <dialcolor>"yellow"</dialcolor>
          <edgecolor>"green"</edgecolor>
          <dotcolor>"black"</dotcolor>
          <initval>0</initval>
          <param_pin>1</param_pin>
        </dial>
        <hbox>
          <relief>RAISED</relief>
          <bd>2</bd>
          <meter>
            <halpin>"halpin6"</halpin>
            <text>"name"</text>
            <subtext>""</subtext>
            <size>150</size>
            <initval>0</initval>
            <size>150</size>
            <param_pin>1</param_pin>
          </meter>
        </hbox>
        <hbox>
          <relief>RAISED</relief>
          <bd>2</bd>
          <label>
            <text>"name      "</text>
            <font>("Helvetica",9)</font>
            <width>13</width>
          </label>
          <bar>
            <halpin>"halpin7"</halpin>
            <initval>0</initval>
            <format>"05d"</format>
            <bgcolor>"grey"</bgcolor>
            <fillcolor>"red"</fillcolor>
            <param_pin>1</param_pin>
          </bar>
        </hbox>
        <hbox>
          <relief>RAISED</relief>
          <bd>2</bd>
          <label>
            <text>"name      "</text>
            <font>("Helvetica",9)</font>
            <width>13</width>
          </label>
          <u32>
            <halpin>"halpin8"</halpin>
            <font>("Helvetica",14)</font>
            <format>"d"</format>
            <justify>LEFT</justify>
          </u32>
        </hbox>
        <hbox>
          <relief>RAISED</relief>
          <bd>2</bd>
          <label>
            <text>"name      "</text>
            <font>("Helvetica",9)</font>
            <width>13</width>
          </label>
          <s32>
            <halpin>"halpin9"</halpin>
            <font>("Helvetica",14)</font>
            <format>"d"</format>
            <justify>LEFT</justify>
          </s32>
        </hbox>
      </hbox>
    </vbox>
    <vbox>
      <hbox>
        <relief>RAISED</relief>
        <bd>2</bd>
        <label>
          <text>"name      "</text>
          <font>("Helvetica",9)</font>
          <width>13</width>
        </label>
        <number>
          <halpin>"halpin10"</halpin>
          <font>("Helvetica",14)</font>
          <format>"07.2f"</format>
          <justify>LEFT</justify>
        </number>
      </hbox>
      <hbox>
        <relief>RAISED</relief>
        <bd>2</bd>
        <label>
          <text>"name      "</text>
          <font>("Helvetica",9)</font>
          <width>13</width>
        </label>
        <checkbutton>
          <halpin>"halpin11"</halpin>
        </checkbutton>
      </hbox>
      <hbox>
        <relief>RAISED</relief>
        <bd>2</bd>
        <label>
          <text>"name      "</text>
          <font>("Helvetica",9)</font>
          <width>13</width>
        </label>
        <checkbutton>
          <halpin>"halpin_g"</halpin>
          <text>"G"</text>
        </checkbutton>
        <checkbutton>
          <halpin>"halpin_b"</halpin>
          <text>"B"</text>
        </checkbutton>
        <checkbutton>
          <halpin>"halpin_r"</halpin>
          <text>"R"</text>
        </checkbutton>
      </hbox>
      <hbox>
        <relief>RAISED</relief>
        <bd>2</bd>
        <label>
          <text>"name      "</text>
          <font>("Helvetica",9)</font>
          <width>13</width>
        </label>
        <led>
          <halpin>"halpin12"</halpin>
          <size>16</size>
          <on_color>"yellow"</on_color>
          <off_color>"red"</off_color>
        </led>
      </hbox>
      <hbox>
        <relief>RAISED</relief>
        <bd>2</bd>
        <label>
          <text>"name      "</text>
          <font>("Helvetica",9)</font>
          <width>13</width>
        </label>
        <led>
          <halpin>"halpin13"</halpin>
          <width>16</width>
          <height>16</height>
          <on_color>"red"</on_color>
          <off_color>"yellow"</off_color>
        </led>
      </hbox>
      <button>
        <relief>RAISED</relief>
        <bd>3</bd>
        <halpin>"halpin14"</halpin>
        <text>"name"</text>
        <font>("Helvetica", 12)</font>
      </button>
      <multilabel>
        <legends>['LABEL1', 'LABEL2', 'LABEL3', 'LABEL4']</legends>
        <halpin>"halpin15"</halpin>
        <font>("Helvetica", 12)</font>
        <bg>"black"</bg>
        <fg>"yellow"</fg>
      </multilabel>
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
    gui.draw_vbox_begin()
    gui.draw_led("led1", "hal_led1")
    gui.draw_led("led2", "hal_led2")
    gui.draw_scale("name", "halpin1")
    gui.draw_fselect("name", "halpin2")
    gui.draw_vbox_end()
    gui.draw_frame_begin("myframe")
    gui.draw_spinbox("name", "halpin3")
    gui.draw_jogwheel("name", "halpin4")
    gui.draw_frame_end()
    gui.draw_tab_end()

    gui.draw_tab_begin("tab2")
    gui.draw_hbox_begin()
    gui.draw_checkbutton("check1", "hal_check1")
    gui.draw_checkbutton("check2", "hal_check2")
    gui.draw_dial("name", "halpin5")
    gui.draw_meter("name", "halpin6")
    gui.draw_bar("name", "halpin7")
    gui.draw_number_u32("name", "halpin8")
    gui.draw_number_s32("name", "halpin9")
    gui.draw_hbox_end()
    gui.draw_tab_end()

    gui.draw_tab_begin("tab3")
    gui.draw_number("name", "halpin10")
    gui.draw_checkbutton("name", "halpin11")
    gui.draw_checkbutton_rgb("name", "halpin_g", "halpin_b", "halpin_r")
    gui.draw_led("name", "halpin12")
    gui.draw_rectled("name", "halpin13")
    gui.draw_button("name", "halpin14")
    gui.draw_multilabel("name", "halpin15")
    gui.draw_tab_end()

    gui.draw_tabs_end()
    gui.draw_end()

    xml_string = gui.xml()

    assert xml_string.strip() == expected.strip()
