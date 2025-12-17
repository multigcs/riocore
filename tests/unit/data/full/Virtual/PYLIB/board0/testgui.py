#!/usr/bin/env python3
#
#

import sys
from functools import partial

from rio import RioWrapper

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
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
                    tab_layout.addWidget(QLabel(f"{plugin_config['title']}:"))
                    for variable in plugin_config["variables"]:
                        row_layout = self.draw_instance(plugin_name, plugin_config, variable, self.data_info[variable])
                        tab_layout.addLayout(row_layout)

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
        row_layout = QHBoxLayout()
        row_layout.addWidget(QLabel(f"    {signal_name}"), stretch=2)
        wid = f"widget_{variable}"
        if variable_info.get("type") == "bool":
            self.widgets[wid] = QCheckBox()
            self.widgets[wid].setChecked(False)
            row_layout.addWidget(self.widgets[wid], stretch=6)
        elif direction == "input":
            self.widgets[wid] = QLabel("---")
            row_layout.addWidget(self.widgets[wid], stretch=6)
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
            row_layout.addWidget(button, stretch=1)
        return row_layout

    def slider_reset(self, widget):
        widget.setValue(0)

    def runTimer(self):
        for plugin_name, plugin_config in self.rio.plugin_info().items():
            if plugin_config["variables"]:
                for variable in plugin_config["variables"]:
                    wid = f"widget_{variable}"
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
                                self.widgets[f"widget_out_{variable}"].setText(str(value))

        self.rio.rio_readwrite()

        for plugin_name, plugin_config in self.rio.plugin_info().items():
            if plugin_config["variables"]:
                for variable in plugin_config["variables"]:
                    wid = f"widget_{variable}"
                    direction = self.data_info[variable].get("direction")
                    if direction == "input":
                        if self.data_info[variable].get("type") == "bool":
                            self.widgets[wid].setChecked(self.rio.data_get(variable))
                        else:
                            self.widgets[wid].setText(str(self.rio.data_get(variable)))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = WinForm()
    form.show()
    sys.exit(app.exec_())
