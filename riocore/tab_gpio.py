import os
import sys

if os.path.isfile(os.path.join("riocore", "__init__.py")):
    sys.path.insert(0, os.getcwd())
elif os.path.isfile(os.path.join(os.path.dirname(os.path.dirname(__file__)), "riocore", "__init__.py")):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import riocore

from riocore.widgets import (
    ImageMap,
    PinButton,
)


from PyQt5.QtCore import QPoint, Qt, QRect
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

riocore_path = os.path.dirname(riocore.__file__)


class TabGpios:
    scale = 1.0

    def __init__(self, parent=None):
        self.parent = parent
        self.img_container = QWidget()
        self.img_layout = QVBoxLayout(self.img_container)
        self.boardimg = QWidget()
        self.img_layout.addWidget(self.boardimg)

        self.pininfo = QLabel("")
        self.pininfo_timer = 0

        ipin_layout = QHBoxLayout()
        self.ipin_widget = QWidget()
        self.ipin_widget.setLayout(ipin_layout)
        ipin_layout.addWidget(self.img_container)
        ipin_layout.addWidget(self.pininfo)
        ipin_layout.addStretch()

        self.scroll_widget = QScrollArea()
        self.scroll_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_widget.setWidgetResizable(True)
        self.scroll_widget.setWidget(self.ipin_widget)

    def widget(self):
        return self.scroll_widget

    def timer(self):
        if self.pininfo_timer == 1:
            self.pininfo_timer = 0
            self.pininfo.setText("\n".join([""] * 10))
        elif self.pininfo_timer > 1:
            self.pininfo_timer -= 1

    def update(self):
        self.img_layout.removeWidget(self.boardimg)
        self.boardimg = QWidget()
        self.pinlabels = {}
        rpi_pinout = (
            "3V3",
            "5V",
            "GPIO2",
            "5V",
            "GPIO3",
            "GND",
            "GPIO4",
            "GPIO14",
            "GND",
            "GPIO15",
            "GPIO17",
            "GPIO18",
            "GPIO27",
            "GND",
            "GPIO22",
            "GPIO23",
            "3V3",
            "GPIO24",
            "GPIO10",
            "GND",
            "GPIO9",
            "GPIO25",
            "GPIO11",
            "GPIO8",
            "GND",
            "GPIO7",
            "GPIO0",
            "GPIO1",
            "GPIO5",
            "GND",
            "GPIO6",
            "GPIO12",
            "GPIO19",
            "GND",
            "GPIO19",
            "GPIO16",
            "GPIO26",
            "GPIO20",
            "GND",
            "GPIO21",
        )

        self.networks = {}
        linuxcnc_config = self.parent.config.get("linuxcnc", {})
        for net in linuxcnc_config.get("net", []):
            net_source = net.get("source")
            net_target = net.get("target")
            self.networks[net_source] = net_target
            self.networks[net_target] = net_source

        for component in linuxcnc_config.get("components", []):
            for pin, halname in component.get("pins", {}).items():
                ctype = component["type"]
                self.networks[halname] = f"{ctype}->{pin}"

        x_offset = 0
        pixmaps = []
        pins = {}
        self.inputs = []
        self.outputs = []
        parport_n = 0
        gpio_config = self.parent.config.get("gpios", [])
        for gpio in gpio_config:
            if gpio.get("type") == "parport":
                pp_mode = gpio.get("mode", "0 out")
                pinimage_path = riocore_path + "/files/db25.png"
                pixmap = QPixmap(pinimage_path)
                pixmaps.append(pixmap)

                mode_outputs = {
                    "in": [1, 14, 16, 17],
                    "out": [1, 2, 3, 4, 5, 6, 7, 8, 9, 14, 16, 17],
                    "epp": [1, 2, 3, 4, 5, 6, 7, 8, 9, 14, 16, 17],
                    "x": [2, 3, 4, 5, 6, 7, 8, 9],
                }
                outpins = mode_outputs.get(pp_mode.split()[-1])

                for pin_num in range(1, 18):
                    title = f"P{parport_n}.{pin_num}"
                    if pin_num in outpins:
                        direction = "output"
                    else:
                        direction = "input"
                    pin_name = f"parport.{parport_n}.pin-{pin_num:02d}-{direction.replace('put', '')}"
                    if pin_num in outpins:
                        self.outputs.append(pin_name)
                    else:
                        self.inputs.append(pin_name)
                    if pin_num < 14:
                        x_pos = x_offset + 20
                        y_pos = 97 + (pin_num - 1) * 32.4
                    else:
                        x_pos = x_offset + 110
                        y_pos = 97 + 15 + (pin_num - 14) * 32.4
                    pins[title] = {
                        "title": title,
                        "pin": pin_name,
                        "pos": [int(x_pos), int(y_pos)],
                        "direction": direction,
                        "slotname": f"parport.{parport_n}",
                        "net": self.networks.get(pin_name, ""),
                    }
                x_offset += pixmap.width()
                parport_n += 1

            elif gpio.get("type") == "rpi":
                pinimage_path = riocore_path + "/files/rpi-gpio.png"
                pixmap = QPixmap(pinimage_path)
                pixmaps.append(pixmap)
                rpi_pins = gpio.get("pins", [])
                self.inputs = rpi_pins.get("inputs", [])
                self.outputs = rpi_pins.get("outputs", [])
                rpi_pins.get("reset", [])
                direction = "all"
                for pin_num in range(0, 40):
                    pin_name = rpi_pinout[pin_num]
                    if pin_name.startswith("GPIO"):
                        x_pos = x_offset + 40 + (pin_num % 2) * 110
                        y_pos = x_offset + 60 + (pin_num // 2) * 20.5
                        pins[pin_name] = {
                            "title": pin_name,
                            "pin": pin_name,
                            "pos": [int(x_pos), int(y_pos)],
                            "direction": direction,
                            "slotname": "rpi_gpio",
                            "net": self.networks.get(pin_name, ""),
                        }
                x_offset += pixmap.width()

        if not pixmaps:
            return

        width = 0
        height = 0
        for pixmap in pixmaps:
            width += pixmap.width()
            height = max(height, pixmap.height())

        self.pinlayout_pixmap = QPixmap(width, height)
        painter = QPainter(self.pinlayout_pixmap)

        x_offset = 0
        for pixmap in pixmaps:
            rect = QRect(x_offset, 0, pixmap.width(), pixmap.height())
            painter.drawPixmap(rect, pixmap)
            x_offset += pixmap.width()

        self.boardimg.setFixedSize(self.pinlayout_pixmap.size())
        pinlayout_image = ImageMap(self)
        pinlayout_image.setAlignment(Qt.AlignRight | Qt.AlignTop)
        pinlayout_image.setFixedSize(self.pinlayout_pixmap.size())

        pinlayout_image.setPixmap(self.pinlayout_pixmap)

        self.img_layout.addWidget(self.boardimg)
        layout_box = QVBoxLayout(self.boardimg)
        layout_box.setContentsMargins(0, 0, 0, 0)
        layout_box.addWidget(pinlayout_image)

        for pin_id, pin in pins.items():
            slot_name = pin["slotname"]
            title = pin["title"]
            halname = pin["pin"]
            pkey = f"{slot_name}:{pin_id}"

            bgcolor = "darkgray"
            tooltip = f"{slot_name}:{pin_id} {pin['pin']} ({pin.get('direction', 'all')})"
            if halname in self.inputs:
                bgcolor = "blue"
            elif halname in self.outputs:
                bgcolor = "green"

            if "pos" in pin:
                self.pinlabels[pkey] = PinButton(self.boardimg, parent=self, pkey=pkey, bgcolor=bgcolor, pin=pin)
                if pin.get("rotate"):
                    if len(pin["pos"]) == 4:
                        self.pinlabels[pkey].setFixedWidth(int(pin["pos"][2]))
                        self.pinlabels[pkey].setFixedHeight(int(pin["pos"][3]))
                    else:
                        self.pinlabels[pkey].setFixedWidth(15)
                        self.pinlabels[pkey].setFixedHeight(len(pin_id * 15))
                    self.pinlabels[pkey].setText(title, True)
                else:
                    if len(pin["pos"]) == 4:
                        self.pinlabels[pkey].setFixedWidth(int(pin["pos"][2]))
                        self.pinlabels[pkey].setFixedHeight(int(pin["pos"][3]))
                    else:
                        self.pinlabels[pkey].setFixedWidth(len(pin_id * 10))
                        self.pinlabels[pkey].setFixedHeight(15)
                    self.pinlabels[pkey].setText(title)
                self.pinlabels[pkey].move(QPoint(int(pin["pos"][0]), int(pin["pos"][1])))
                self.pinlabels[pkey].setToolTip(tooltip)

                # self.pinlabels[pkey].clicked.connect(partial(self.parent.edit_plugin, plugin_instance, plugin_instance.plugin_id, None))

    def pinlayout_mark(self, pkey):
        slot_name = pkey.split(":")[0]
        infotext = [f"Slot: {slot_name}"]
        infotext.append("Pins:")
        networks = []
        infoline = 0
        ln = 0
        for key, label in self.pinlabels.items():
            splitted = key.split(":")
            if splitted[0] == slot_name:
                color = "darkCyan"
                label.mark(color)
                label.pin.get("direction") or "all"
                comment = label.pin.get("comment") or ""
                if comment:
                    comment = f" - {comment}"

                pinfo = ""
                net = label.pin.get("net")
                if net:
                    pinfo += net
                if key == pkey:
                    pinfo += " <-"
                    infoline = ln

                # infotext.append(f" {splitted[1]}: {label.pin.get('pin', {})} ({direction}{comment}) {pinfo}")
                infotext.append(f" {splitted[1]}: {label.pin.get('pin', {})} {pinfo}")
                ln += 1
            else:
                label.unmark()

        if len(infotext) > 2:
            if networks:
                infotext.append("Networks:")
                for net in networks:
                    infotext.append(f" {net}")

            ilen = 20
            off = ilen - 4
            start = 0
            end = ilen
            if infoline > off - 1:
                start = infoline - off
                end = start + ilen
            displayed = infotext[start:end]
            fill = ilen + 1 - len(displayed)
            displayed += [""] * fill
            self.pininfo.setText("\n".join(displayed))
            self.pininfo_timer = 0
        else:
            self.pininfo_timer = 3
