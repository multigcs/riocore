#!/usr/bin/env python3
#
#

import argparse
import glob
import os
import sys
import time
import traceback
from functools import partial

import riocore
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QLineEdit,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
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

STYLESHEET = """
    background-color: #444444;
    color: white;
"""
STYLESHEET_CHECKBOX = """
    QCheckBox::indicator::unchecked {
        background-color: lightgray;
    }
"""

parser = argparse.ArgumentParser()
parser.add_argument("--debug", "-d", help="debug", default=False, action="store_true")
parser.add_argument("--interval", "-i", help="interval", type=int, default=50)
parser.add_argument("--vertical", "-v", help="vertical tabs", default=False, action="store_true")
parser.add_argument("--graphs", "-g", help="show graphs", default=False, action="store_true")
parser.add_argument("--buffer", "-b", help="buffer size for graphs", type=int, default=100)
parser.add_argument("config", help="config", nargs="?", type=str, default=None)
parser.add_argument("target", help="target", nargs="?", type=str, default="")
parser.add_argument("tab", help="tab", nargs="?", type=str, default="")
args = parser.parse_args()


riocore_path = os.path.dirname(riocore.__file__)


class WinForm(QWidget):
    def __init__(self, parent=None):
        super(WinForm, self).__init__(parent)
        self.setWindowTitle("LinuxCNC-RIO - TestGui")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.setStyleSheet(STYLESHEET)

        self.listFile = QListWidget()
        layout = QGridLayout()
        self.setLayout(layout)

        self.tabwidget = QTabWidget()
        self.tabwidget.setMovable(True)
        if args.vertical:
            self.tabwidget.setTabPosition(QTabWidget.West)
            self.tabwidget.setDocumentMode(True)

        layout.addWidget(self.tabwidget, 0, 0)

        if os.path.isfile(args.config):
            self.config_file = args.config
        elif os.path.isfile(f"{riocore_path}/configs/{args.config}"):
            self.config_file = f"{riocore_path}/configs/{args.config}"
        else:
            print(f"can not load: {args.config}")
            exit(1)
        if args.debug:
            print(f"loading: {self.config_file}")

        self.project = riocore.Project(self.config_file)

        target = args.target
        if not args.target:
            target = self.target_select()
        if not target:
            sys.exit(0)

        self.project.connect(target)

        self.haldata = self.project.haldata()

        plugin_types = set()
        for plugin_instance, haldata in self.haldata.items():
            if haldata.get("input") or haldata.get("output"):
                plugin_types.add(plugin_instance.NAME)

        self.ucount = 0
        if args.graphs:
            import pyqtgraph as pg

            self.time = list(range(args.buffer))
            pen = pg.mkPen(color=(255, 255, 255))

        for tab_num, plugin_type in enumerate(sorted(plugin_types)):
            tab_widget = QWidget()
            self.tabwidget.addTab(tab_widget, plugin_type.title())

            # tab_layout = QGridLayout()
            tab_layout1 = QHBoxLayout()
            tab_widget.setLayout(tab_layout1)

            tab_layout = QVBoxLayout()
            tab_layout1.addLayout(tab_layout, stretch=3)

            plugin_path = f"{riocore_path}/plugins/{plugin_type}"
            image_path = f"{plugin_path}/image.png"
            if os.path.isfile(image_path):
                ilabel = QLabel(self)
                pixmap = QPixmap(image_path)
                ilabel.setPixmap(pixmap)
                self.resize(pixmap.width(), pixmap.height())
                tab_layout1.addWidget(ilabel, stretch=1)

            for plugin_instance, haldata in self.haldata.items():
                if plugin_instance.NAME != plugin_type:
                    continue

                num_signals = len(plugin_instance.SIGNALS)
                if num_signals > 1:
                    row_layout = QHBoxLayout()
                    tab_layout.addLayout(row_layout)
                    row_layout.addWidget(QLabel(f"{plugin_instance.title} ({plugin_instance.NAME})"))

                for hdir in ("output", "input", "inout"):
                    for halname, signal in haldata.get(hdir, {}).items():
                        value = signal["value"]
                        userconfig = signal.get("userconfig", {})

                        halname_np = halname.split(".", 1)[-1]
                        halname_np = userconfig.get("display", {}).get("title", halname_np)

                        wid = f"widget_{plugin_instance.title}"
                        gid = f"graph_{plugin_instance.title}"
                        virtual = signal.get("virtual", False)
                        helper = signal.get("helper", False)
                        direction = signal.get("direction")

                        row_layout = QHBoxLayout()
                        tab_layout.addLayout(row_layout)
                        if num_signals == 1:
                            row_layout.addWidget(QLabel(f"{plugin_instance.title} ({plugin_instance.NAME})"), stretch=2)
                        if helper:
                            print(halname, helper)
                            row_layout.addWidget(QLabel(f"        {halname_np}"), stretch=2)
                        else:
                            row_layout.addWidget(QLabel(f"    {halname_np}"), stretch=2)

                        if virtual:
                            # swap direction vor virt signals
                            if direction == "input":
                                direction = "output"
                            else:
                                direction = "input"
                        if signal.get("bool"):
                            signal[wid] = QCheckBox()
                            signal[wid].setChecked(value)
                            signal[wid].setStyleSheet(STYLESHEET_CHECKBOX)
                            if args.graphs and direction == "input":
                                signal[f"graph_tab_{plugin_instance.title}"] = tab_num
                                signal[f"graph_minmax_{plugin_instance.title}"] = (0, 1)
                                plot_graph = pg.PlotWidget()
                                plot_graph.setBackground("black")
                                plot_graph.showGrid(x=True, y=True)
                                plot_graph.setYRange(0, 1)
                                signal[f"graphw_{plugin_instance.title}"] = plot_graph
                                signal[f"history_{plugin_instance.title}"] = [0 for _ in range(args.buffer)]
                                signal[gid] = plot_graph.plot(
                                    self.time,
                                    signal[f"history_{plugin_instance.title}"],
                                    name="Value",
                                    pen=pen,
                                )
                                row_layout.addWidget(plot_graph)
                            row_layout.addWidget(signal[wid], stretch=6)

                        elif direction == "input":
                            signal[wid] = QLabel("")
                            if args.graphs:
                                signal[f"graph_tab_{plugin_instance.title}"] = tab_num
                                signal[f"graph_minmax_{plugin_instance.title}"] = (0, 1)
                                plot_graph = pg.PlotWidget()
                                plot_graph.setBackground("black")
                                plot_graph.showGrid(x=True, y=True)
                                plot_graph.setYRange(0, 1)
                                signal[f"graphw_{plugin_instance.title}"] = plot_graph
                                signal[f"history_{plugin_instance.title}"] = [0 for _ in range(args.buffer)]
                                signal[gid] = plot_graph.plot(
                                    self.time,
                                    signal[f"history_{plugin_instance.title}"],
                                    name="Value",
                                    pen=pen,
                                )
                                row_layout.addWidget(plot_graph)
                            row_layout.addWidget(signal[wid], stretch=6)
                        else:
                            vmin = signal.get("userconfig", {}).get("min", signal.get("min", 0))
                            vmax = signal.get("userconfig", {}).get("max", signal.get("max", 100000))
                            signal[wid] = QSlider(Qt.Horizontal)
                            signal[wid].setMinimum(int(vmin))
                            signal[wid].setMaximum(int(vmax))
                            signal[wid].setSingleStep(1)
                            signal[wid].setPageStep(int((vmax - vmin) // 1000))
                            # signal[wid].setTickPosition(QSlider.TicksBelow)
                            signal[wid].setValue(value)
                            signal[f"widget_out_{plugin_instance.title}"] = QLabel("      ")
                            row_layout.addWidget(signal[f"widget_out_{plugin_instance.title}"])
                            button = QPushButton("0")
                            button.clicked.connect(partial(self.slider_reset, signal[wid]))
                            row_layout.addWidget(signal[wid], stretch=6)
                            row_layout.addWidget(button, stretch=1)

                if args.debug and plugin_instance.TYPE == "frameio":
                    row_layout = QHBoxLayout()
                    tab_layout.addLayout(row_layout)
                    row_layout.addWidget(QLabel("      >SEND"), stretch=2)
                    plugin_instance.frame_tx_overwride_widget = QLineEdit()
                    row_layout.addWidget(plugin_instance.frame_tx_overwride_widget, stretch=5)
                    button_set = QPushButton("SET")
                    row_layout.addWidget(button_set, stretch=1)
                    button_clear = QPushButton("CLEAR")
                    row_layout.addWidget(button_clear, stretch=1)

                    row_layout = QHBoxLayout()
                    tab_layout.addLayout(row_layout)
                    row_layout.addWidget(QLabel("      >TX"), stretch=1)
                    plugin_instance.frame_tx_id_widget = QLabel("LEN")
                    row_layout.addWidget(plugin_instance.frame_tx_id_widget, stretch=1)
                    plugin_instance.frame_tx_widget = QLineEdit("TX")
                    row_layout.addWidget(plugin_instance.frame_tx_widget, stretch=6)

                    button_set.clicked.connect(partial(self.framecopy, plugin_instance))
                    button_clear.clicked.connect(partial(self.frameclear, plugin_instance))

                    row_layout = QHBoxLayout()
                    tab_layout.addLayout(row_layout)
                    row_layout.addWidget(QLabel("      <RX"), stretch=1)
                    plugin_instance.frame_rx_id_widget = QLabel("LEN")
                    row_layout.addWidget(plugin_instance.frame_rx_id_widget, stretch=1)
                    plugin_instance.frame_rx_widget = QLineEdit("RX")
                    row_layout.addWidget(plugin_instance.frame_rx_widget, stretch=6)

                    if hasattr(plugin_instance, "testgui_frameio_init"):
                        plugin_instance.testgui_frameio_init(tab_layout)

            tab_layout.addStretch()

            if args.tab and args.tab.lower() == plugin_type.lower():
                self.tabwidget.setCurrentWidget(tab_widget)

        self.timer = QTimer()
        self.timer.timeout.connect(self.runTimer)
        self.timer.start(args.interval)

    def framecopy(self, plugin_instance, c):
        frame = plugin_instance.frame_tx_widget.text()
        if hasattr(plugin_instance, "testgui_frameio_clean"):
            frame = " ".join(plugin_instance.testgui_frameio_clean(frame.replace(",", " ").split()))
        plugin_instance.frame_tx_overwride_widget.setText(frame)

    def frameclear(self, plugin_instance, c):
        plugin_instance.frame_tx_overwride_widget.setText("")

    def target_select(self):
        def target_check(item):
            target = device.currentText()
            is_udp = target == "UDP"
            udp_ip.setEnabled(is_udp)
            udp_port.setEnabled(is_udp)

        dialog = QDialog()
        dialog.setWindowTitle("select target")
        dialog.setFixedWidth(500)
        dialog.setFixedHeight(400)
        dialog.setStyleSheet(STYLESHEET)

        dialog.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        dialog.buttonBox.accepted.connect(dialog.accept)

        dialog.layout = QVBoxLayout()
        hlayout = QHBoxLayout()
        vlayout_left = QVBoxLayout()

        message = QLabel("Device:")
        vlayout_left.addWidget(message)
        device = QComboBox(self)
        device.addItem("UDP")
        device.addItem("SPI")
        for path in glob.glob("/dev/ttyUSB*"):
            device.addItem(path)
        for path in glob.glob("/dev/ttyACM*"):
            device.addItem(path)
        for path in glob.glob("/dev/serial*"):
            device.addItem(path)
        device.activated.connect(target_check)

        ip = "192.168.10.194"
        port = 2390
        protocol = self.project.config["jdata"].get("protocol")
        if protocol:
            for n in range(0, device.count()):
                if device.itemText(n) == protocol:
                    device.setCurrentIndex(n)
                    break
                elif protocol == "UART" and device.itemText(n).startswith("/dev/tty"):
                    device.setCurrentIndex(n)
                    break

            if protocol == "UDP":
                for plugin_instance in self.project.plugin_instances:
                    if plugin_instance.TYPE == "interface":
                        if "ip" in plugin_instance.plugin_setup:
                            ip = plugin_instance.plugin_setup["ip"]
                        if "port" in plugin_instance.plugin_setup:
                            port = plugin_instance.plugin_setup["port"]

        vlayout_left.addWidget(device)
        vlayout_left.addStretch()

        vlayout_left.addWidget(QLabel("IP"))
        udp_ip = QLineEdit()
        udp_ip.setText(ip)
        vlayout_left.addWidget(udp_ip)
        vlayout_left.addWidget(QLabel("Port"))
        udp_port = QLineEdit()
        udp_port.setText(str(port))
        vlayout_left.addWidget(udp_port)

        vlayout_left.addStretch()
        hlayout.addLayout(vlayout_left)
        dialog.layout.addLayout(hlayout)
        dialog.layout.addWidget(dialog.buttonBox)
        dialog.setLayout(dialog.layout)
        target_check(0)

        if dialog.exec():
            target = device.currentText()
            if target == "UDP":
                target = f"{udp_ip.text()}:{udp_port.text()}"
            return target
        else:
            return None

    def slider_reset(self, widget):
        widget.setValue(0)

    def runTimer(self):
        try:
            if self.ucount > 10:
                self.ucount = 0
            else:
                self.ucount += 1

            for plugin_instance, haldata in self.haldata.items():
                for halname, signal in haldata.get("output", {}).items():
                    if signal.get("bool"):
                        if signal[f"widget_{plugin_instance.title}"].isChecked():
                            self.project.signal_value_set(halname, 1)
                        else:
                            self.project.signal_value_set(halname, 0)
                    else:
                        value = signal[f"widget_{plugin_instance.title}"].value()
                        signal[f"widget_out_{plugin_instance.title}"].setText(f"{value:05d}")
                        self.project.signal_value_set(halname, value)

                for halname, signal in haldata.get("inout", {}).items():
                    if signal.get("bool"):
                        if signal[f"widget_{plugin_instance.title}"].isChecked():
                            self.project.signal_value_set(halname, 1)
                        else:
                            self.project.signal_value_set(halname, 0)
                    else:
                        value = signal[f"widget_{plugin_instance.title}"].value()
                        signal[f"widget_out_{plugin_instance.title}"].setText(f"{value:05d}")
                        self.project.signal_value_set(halname, value)

                if hasattr(plugin_instance, "frame_tx_overwride_widget"):
                    overwrite = plugin_instance.frame_tx_overwride_widget.text()
                    if overwrite:
                        plugin_instance.frame_tx_overwride = []
                        parts = overwrite.replace(",", " ").split()
                        for inum in parts:
                            plugin_instance.frame_tx_overwride.append(int(inum))
                        if hasattr(plugin_instance, "testgui_frameio_send"):
                            plugin_instance.frame_tx_overwride = plugin_instance.testgui_frameio_send(plugin_instance.frame_tx_overwride)
                    else:
                        plugin_instance.frame_tx_overwride = None

            txdata = self.project.txdata_get()
            if args.debug:
                print(f"tx ({len(txdata*8)}): {txdata}")

            start = time.time()
            rxdata = self.project.transfare(txdata)
            stop = time.time()
            if args.debug:
                print("rx:", rxdata)
                print((stop - start) * 1000)

            if not args.debug:
                if len(rxdata) != self.project.buffer_bytes:
                    print(f"ERROR: reveived data have wrong size: {len(rxdata)} / {self.project.buffer_bytes}")
                    # return
                if rxdata[0] != 0x61 or rxdata[1] != 0x74 or rxdata[2] != 0x61 and rxdata[3] != 0x64:
                    print(f"ERROR: reveived data have wrong header: 0x{rxdata[0]:X} 0x{rxdata[1]:X} 0x{rxdata[2]:X} 0x{rxdata[3]:X}")
                    # return

            self.project.rxdata_set(rxdata)

            if args.graphs:
                self.time = self.time[1:]
                self.time.append(self.time[-1] + 1)

            for plugin_instance, haldata in self.haldata.items():
                if args.debug and plugin_instance.TYPE == "frameio":
                    txframe_raw = plugin_instance.INTERFACE["txdata"]["value"]
                    txframe = []
                    if args.debug:
                        print(f"{plugin_instance.title}: frame_tx: {plugin_instance.frame_tx}")

                    for p in txframe_raw:
                        txframe.append(str(int(p)))
                    frame_tx_id = int(txframe[0])
                    frame_tx_len = int(txframe[1])
                    plugin_instance.frame_tx_id_widget.setText(str(frame_tx_id))
                    plugin_instance.frame_tx_widget.setText(" ".join(txframe[2 : (frame_tx_len + 2)]))

                    if hasattr(plugin_instance, "testgui_frameio_update"):
                        plugin_instance.testgui_frameio_update(True, txframe)

                    rxframe_raw = plugin_instance.INTERFACE["rxdata"]["value"]
                    rxframe = []
                    for p in rxframe_raw:
                        rxframe.append(str(int(p)))
                    frame_rx_id = int(rxframe[1])
                    frame_rx_len = int(rxframe[2])
                    plugin_instance.frame_rx_id_widget.setText(str(frame_rx_id))
                    plugin_instance.frame_rx_widget.setText(" ".join(reversed(rxframe[3 : (frame_rx_len + 3)])))

                    if hasattr(plugin_instance, "testgui_frameio_update"):
                        plugin_instance.testgui_frameio_update(False, rxframe)

                for halname, signal in haldata.get("input", {}).items():
                    value = signal["value"]
                    value_format = signal.get("format", "d")
                    value_unit = signal.get("unit", "")
                    userconfig = signal.get("userconfig", {})
                    value_unit = userconfig.get("display", {}).get("unit", value_unit)
                    value_format = userconfig.get("display", {}).get("format", value_format)
                    value_offset = userconfig.get("offset", 0.0)
                    value_scale = userconfig.get("scale", 1.0)

                    if value_scale != 1.0 or value_offset:
                        value = (value + value_offset) / value_scale

                    value_str = f"%{value_format}" % (value,)
                    virtual = signal.get("virtual", False)
                    direction = signal.get("direction")
                    if virtual:
                        # swap direction vor virt signals
                        if direction == "input":
                            direction = "output"
                        else:
                            direction = "input"
                    if signal.get("bool"):
                        signal[f"widget_{plugin_instance.title}"].setChecked(int(value))
                        if args.graphs and direction == "input":
                            gmin, gmax = signal[f"graph_minmax_{plugin_instance.title}"]
                            mm_changed = False
                            if gmax < value:
                                gmax = value
                                mm_changed = True
                            if gmin > value:
                                gmin = value
                                mm_changed = True
                            if mm_changed:
                                signal[f"graph_minmax_{plugin_instance.title}"] = (gmin, gmax)
                                signal[f"graphw_{plugin_instance.title}"].setYRange(gmin, gmax)
                            signal[f"history_{plugin_instance.title}"] = signal[f"history_{plugin_instance.title}"][1:]
                            signal[f"history_{plugin_instance.title}"].append(value)
                            if self.ucount == 0:
                                signal[f"graph_{plugin_instance.title}"].setData(self.time, signal[f"history_{plugin_instance.title}"])
                    elif direction == "input":
                        signal[f"widget_{plugin_instance.title}"].setText(f"{value_str} {value_unit}")
                        if args.graphs:
                            gmin, gmax = signal[f"graph_minmax_{plugin_instance.title}"]
                            mm_changed = False
                            if gmax < value:
                                gmax = value
                                mm_changed = True
                            if gmin > value:
                                gmin = value
                                mm_changed = True
                            if mm_changed:
                                signal[f"graph_minmax_{plugin_instance.title}"] = (gmin, gmax)
                                signal[f"graphw_{plugin_instance.title}"].setYRange(gmin, gmax)
                            signal[f"history_{plugin_instance.title}"] = signal[f"history_{plugin_instance.title}"][1:]
                            signal[f"history_{plugin_instance.title}"].append(value)
                            if self.ucount == 0:
                                signal[f"graph_{plugin_instance.title}"].setData(self.time, signal[f"history_{plugin_instance.title}"])
                    else:
                        signal[f"widget_{plugin_instance.title}"].setValue(value)
            if args.debug:
                print("")
        except Exception as e:
            print("ERROR", e)
            print(traceback.format_exc())


def main():
    app = QApplication(sys.argv)
    form = WinForm()
    form.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
