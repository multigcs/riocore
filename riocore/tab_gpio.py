import os
import sys
from functools import partial

if os.path.isfile(os.path.join("riocore", "__init__.py")):
    sys.path.insert(0, os.getcwd())
elif os.path.isfile(os.path.join(os.path.dirname(os.path.dirname(__file__)), "riocore", "__init__.py")):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import riocore

from riocore import gpios

from riocore.widgets import (
    ImageMap,
    PinButton,
)


from PyQt5.QtCore import QPoint, Qt, QRect
from PyQt5.QtGui import QPixmap, QPainter, QColor
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
        self.gui_components = parent.gui_components
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
        self.networks = {}
        linuxcnc_config = self.parent.config.get("linuxcnc", {})
        for net in linuxcnc_config.get("net", []):
            net_source = net.get("source")
            net_target = net.get("target")
            self.networks[net_source] = net_target
            self.networks[net_target] = net_source

        componentMapping = {}
        component_nums = {}
        for component in linuxcnc_config.get("components", []):
            comp_type = component.get("type")
            if comp_type not in component_nums:
                component_nums[comp_type] = 0
            component["num"] = component_nums[comp_type]
            for pin, halname in component.get("pins", {}).items():
                ctype = component["type"]
                cpin = f"{ctype}{component['num']}.{pin}"
                componentMapping[halname] = component
                self.networks[halname] = cpin
            component_nums[comp_type] += 1

        x_offset = 0
        pixmaps = []
        pins = {}
        self.inputs = []
        self.outputs = []
        gpio_ids = {}
        gpio_config = self.parent.config.get("gpios", [])
        for gpio in gpio_config:
            gtype = gpio.get("type")
            if gtype not in gpio_ids:
                gpio_ids[gtype] = 0
            if hasattr(gpios, f"gpio_{gtype}"):
                ginstance = getattr(gpios, f"gpio_{gtype}")(gpio_ids[gtype], gpio)
                self.inputs += ginstance.inputs
                self.outputs += ginstance.outputs
                pins.update(ginstance.slotpins(x_offset, self.networks))
                pixmap = QPixmap(ginstance.IMAGE)
                pixmaps.append(pixmap)
                x_offset += pixmap.width()

            gpio_ids[gtype] += 1

        if not pixmaps:
            pixmap = QPixmap(130, 600)
            pixmap.fill(QColor(255, 255, 255))
            pixmaps.append(pixmap)
            x_offset += pixmap.width()

        width = 0
        height = 0
        for pixmap in pixmaps:
            width += pixmap.width()
            height = max(height, pixmap.height())

        self.pinlayout_pixmap = QPixmap(width, height)
        self.pinlayout_pixmap.fill(QColor(255, 255, 255))
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

                if halname in componentMapping:
                    self.pinlabels[pkey].clicked.connect(partial(self.gui_components.edit_component, componentMapping.get(halname)))
                elif halname:
                    self.pinlabels[pkey].clicked.connect(partial(self.gui_components.add_component_or_net, pin_select=halname))
                else:
                    self.pinlabels[pkey].clicked.connect(partial(self.parent.gui_gpios.edit_gpio, pin_select=pin_id))

        pkey = "newgpio"
        self.pinlabels[pkey] = PinButton(self.boardimg, parent=self, pkey=pkey, bgcolor="red")
        self.pinlabels[pkey].setFixedWidth(100)
        self.pinlabels[pkey].setFixedHeight(15)
        self.pinlabels[pkey].setText("add gpio")
        self.pinlabels[pkey].move(QPoint(10, 10))
        self.pinlabels[pkey].setToolTip("adding a new gpio port")
        self.pinlabels[pkey].clicked.connect(self.parent.gui_gpios.add_gpio)

    def pinlayout_mark(self, pkey):
        slot_name = pkey.split(":")[0]
        infotext = [f"Slot: {slot_name}"]
        infotext.append("Pins:")
        networks = []
        infoline = 0
        ln = 0
        for key, label in self.pinlabels.items():
            if key == "newgpio":
                continue
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
