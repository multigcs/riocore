#!/usr/bin/env python3
#
#

import io
import sys
from functools import partial

from rio import RioWrapper

from PyQt5 import uic
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QGroupBox,
    QProxyStyle,
    QStyle,
    QScrollArea,
    QApplication,
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
    QTabWidget,
)


class SliderProxyStyle(QProxyStyle):
    def pixelMetric(self, metric, option, widget):
        if metric == QStyle.PM_SliderThickness:
            return 40
        elif metric == QStyle.PM_SliderLength:
            return 40
        return super().pixelMetric(metric, option, widget)


class PluginUI(QWidget):
    def __init__(self, template):
        super(PluginUI, self).__init__()
        f = io.StringIO(template)
        uic.loadUi(f, self)

    def widget(self, name):
        if hasattr(self, name):
            return getattr(self, name)
        return None


class WinForm(QWidget):
    def __init__(self, parent=None):
        super(WinForm, self).__init__(parent)

        self.rio = RioWrapper(sys.argv)
        self.data_info = self.rio.data_info()
        self.widgets = {}

        self.setWindowTitle("RIO - TestGui")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.listFile = QListWidget()
        layout = QGridLayout()
        self.setLayout(layout)
        self.tabwidget = QTabWidget()
        self.tabwidget.setMovable(True)
        layout.addWidget(self.tabwidget, 0, 0)
        plugin_types = []
        for plugin_name, plugin_config in self.rio.plugin_info().items():
            if plugin_config["variables"] and plugin_config["type"] not in plugin_types:
                plugin_types.append(plugin_config["type"])

        for plugin_type in plugin_types:
            tab_layout = self.add_tab(plugin_type)
            for plugin_name, plugin_config in self.rio.plugin_info().items():
                if plugin_config["variables"] and plugin_config["type"] == plugin_type:
                    # tab_layout.addWidget(QLabel(f"{plugin_config['title']}:"))
                    plugin_frame = QGroupBox()
                    plugin_frame.setTitle(f"{plugin_config['title']}:")
                    plugin_frame.setToolTip(plugin_name)
                    plugin_layout = QVBoxLayout()
                    plugin_frame.setLayout(plugin_layout)
                    tab_layout.addWidget(plugin_frame)

                    ptype = plugin_config.get("type")
                    if ptype == "wled":
                        for variable in plugin_config["variables"]:
                            variable_info = self.data_info[variable]
                            signal_name = variable_info.get("signal_name")
                            if signal_name.endswith("_green"):
                                num = signal_name.split("_")[0]
                                row_layout = QHBoxLayout()
                                row_layout.addWidget(QLabel(f"LED {num}"), stretch=0)
                                row_layout.addStretch()
                                for color in ("red", "green", "blue"):
                                    wid = f"widget_{variable.replace('GREEN', color.upper())}"
                                    self.widgets[wid] = QCheckBox()
                                    self.widgets[wid].setChecked(False)
                                    row_layout.addWidget(QLabel(color))
                                    row_layout.addWidget(self.widgets[wid], stretch=0)
                                plugin_layout.addLayout(row_layout)
                    else:
                        ui_xml = plugin_config.get("plugin_ui")
                        plugin_ui = None
                        if ui_xml:
                            plugin_ui = PluginUI(ui_xml)
                        if plugin_ui:
                            plugin_layout.addWidget(plugin_ui)
                            for variable in plugin_config["variables"]:
                                halname = self.data_info[variable]["halname"]
                                wname = halname.split(".")[-1]
                                wid = f"widget_{variable}"
                                self.widgets[wid] = plugin_ui.widget(wname)
                                if self.widgets[wid] is None:
                                    print(f"ERROR: widget not found in ui: {plugin_name} {wname}")
                                    sys.exit(1)
                                button = plugin_ui.widget(f"{wname}_zero")
                                if button:
                                    button.clicked.connect(partial(self.slider_reset, self.widgets[wid]))
                                value_out = plugin_ui.widget(f"{wname}_out")
                                if value_out:
                                    self.widgets[f"widget_out_{variable}"] = plugin_ui.widget(f"{wname}_out")
                        else:
                            for variable in plugin_config["variables"]:
                                row_layout = self.draw_instance(plugin_name, plugin_config, variable, self.data_info[variable])
                                plugin_layout.addLayout(row_layout)
            tab_layout.addStretch()
        self.errors = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.runTimer)
        self.timer.start(100)

    def add_tab(self, title):
        tab_widget = QWidget()
        scroll_widget = QScrollArea()
        scroll_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_widget.setWidgetResizable(True)
        scroll_widget.setWidget(tab_widget)
        self.tabwidget.addTab(scroll_widget, title)
        tab_layout1 = QHBoxLayout()
        tab_widget.setLayout(tab_layout1)
        tab_layout = QVBoxLayout()
        tab_layout1.addLayout(tab_layout, stretch=3)
        tab_layout_r = QVBoxLayout()
        tab_layout1.addLayout(tab_layout_r, stretch=0)
        return tab_layout

    def draw_instance(self, plugin_name, plugin_config, variable, variable_info):
        signal_name = variable_info.get("signal_name")
        direction = variable_info.get("direction")
        userconfig = variable_info.get("userconfig")
        unit = variable_info.get("unit") or ""

        wid = f"widget_{variable}"
        row_layout = QHBoxLayout()
        row_layout.addWidget(QLabel(signal_name), stretch=0)
        row_layout.addStretch()

        if variable_info.get("type") == "bool":
            self.widgets[wid] = QCheckBox()
            self.widgets[wid].setChecked(False)
            row_layout.addWidget(self.widgets[wid], stretch=0)
        elif direction == "input":
            self.widgets[wid] = QLabel("---")
            row_layout.addWidget(self.widgets[wid], stretch=0)
        else:
            vmin = 0
            vmax = 1000
            if plugin_config["is_joint"]:
                vmin = -100000
                vmax = 100000
            vmin = int(userconfig.get("display", {}).get("min", vmin))
            vmax = int(userconfig.get("display", {}).get("max", vmax))
            steps = int(vmax / 20)
            self.widgets[wid] = QSlider(Qt.Horizontal)
            self.widgets[wid].setMinimum(int(vmin))
            self.widgets[wid].setMaximum(int(vmax))
            self.widgets[wid].setSingleStep(1)
            self.widgets[wid].setPageStep(steps)
            self.widgets[wid].setTickPosition(QSlider.TicksBelow)
            self.widgets[wid].setMinimumWidth(200)
            self.widgets[wid].setValue(0)
            self.widgets[f"widget_out_{variable}"] = QLabel("0")
            self.widgets[f"widget_out_{variable}"].setMinimumWidth(50)
            row_layout.addWidget(self.widgets[f"widget_out_{variable}"])
            row_layout.addWidget(self.widgets[wid], stretch=6)
            button = QPushButton("0")
            button.clicked.connect(partial(self.slider_reset, self.widgets[wid]))
            row_layout.addWidget(button, stretch=0)

        unit_label = QLabel(unit)
        row_layout.addWidget(unit_label, stretch=0)

        return row_layout

    def slider_reset(self, widget):
        widget.setValue(0)

    def runTimer(self):
        for plugin_name, plugin_config in self.rio.plugin_info().items():
            if plugin_config["variables"]:
                for variable in plugin_config["variables"]:
                    wid = f"widget_{variable}"
                    if wid not in self.widgets:
                        continue
                    direction = self.data_info[variable].get("direction")
                    if direction == "output":
                        if self.data_info[variable].get("type") == "bool":
                            if self.widgets[wid].isChecked():
                                self.rio.data_set(variable, 1)
                            else:
                                self.rio.data_set(variable, 0)
                        else:
                            value = self.widgets[wid].value()
                            self.rio.data_set(variable, value)
                            if f"widget_out_{variable}" in self.widgets:
                                widget = self.widgets[f"widget_out_{variable}"]
                                if hasattr(widget, "setText"):
                                    widget.setText(str(value))
                                else:
                                    widget.setValue(value)

        self.rio.rio_readwrite()

        for plugin_name, plugin_config in self.rio.plugin_info().items():
            if plugin_config["variables"]:
                for variable in plugin_config["variables"]:
                    wid = f"widget_{variable}"
                    if wid not in self.widgets:
                        continue
                    direction = self.data_info[variable].get("direction")
                    if direction == "input":
                        if self.data_info[variable].get("type") == "bool":
                            self.widgets[wid].setChecked(self.rio.data_get(variable))
                        else:
                            if hasattr(self.widgets[wid], "setText"):
                                self.widgets[wid].setText(str(self.rio.data_get(variable)))
                            else:
                                self.widgets[wid].display(self.rio.data_get(variable))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = WinForm()
    form.show()
    sys.exit(app.exec_())
