import os
from functools import partial


from riocore.gui.widgets import (
    ImageMap,
    PinButton,
)


from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class TabBoard:
    scale = 1.0

    def __init__(self, parent=None):
        self.parent = parent
        self.img_container = QWidget()
        self.img_layout = QVBoxLayout(self.img_container)
        self.boardimg = QWidget()
        self.img_layout.setAlignment(Qt.AlignRight | Qt.AlignTop)
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

        pinimage = self.parent.board.get("pinimage", "board.png")
        pinimage_path = os.path.join(self.parent.boardcfg_path, pinimage)
        if not pinimage or not os.path.isfile(pinimage_path):
            if self.parent.tabwidget.tabText(0) == "Board":
                self.parent.tabwidget.removeTab(0)
            return

        pinlayout_pixmap = QPixmap(pinimage_path)
        self.boardimg.setFixedSize(pinlayout_pixmap.size())

        pinlayout_image = ImageMap(self)
        pinlayout_image.setAlignment(Qt.AlignRight | Qt.AlignTop)
        pinlayout_image.setFixedSize(pinlayout_pixmap.size())
        pinlayout_image.setPixmap(pinlayout_pixmap)

        self.img_layout.addWidget(self.boardimg)

        layout_box = QVBoxLayout(self.boardimg)
        layout_box.setContentsMargins(0, 0, 0, 0)
        layout_box.addWidget(pinlayout_image)

        for slot in self.parent.slots:
            slot_name = slot["name"]
            module_name = self.parent.get_module_by_slot(slot_name)

            if "rect" in slot:
                pkey = f"{slot_name}:"
                w = int(slot["rect"][2])
                h = int(slot["rect"][3])
                tooltip = f"slot:{slot_name}"
                bgcolor = "lightblue"
                if module_name:
                    bgcolor = "lightgreen"
                    tooltip += f"\nmodule: {module_name}"
                self.pinlabels[pkey] = PinButton(self.boardimg, parent=self, pkey=pkey, bgcolor=bgcolor)
                self.pinlabels[pkey].setFixedWidth(w)
                self.pinlabels[pkey].setFixedHeight(h)
                self.pinlabels[pkey].setText(pkey)
                self.pinlabels[pkey].move(QPoint(int(slot["rect"][0]), int(slot["rect"][1])))
                self.pinlabels[pkey].setToolTip(tooltip)
                if module_name:
                    self.pinlabels[pkey].clicked.connect(partial(self.parent.gui_modules.remove_module, slot_name))
                else:
                    self.pinlabels[pkey].clicked.connect(partial(self.parent.gui_modules.add_module, slot_name=slot_name, slot_select=False))

            for pin_id, pin in slot["pins"].items():
                if isinstance(pin, dict):
                    # check if pin is allready used
                    pkey = f"{slot_name}:{pin_id}"

                    bgcolor = "blue"
                    if "pos" in pin:
                        tooltip = f"{slot_name}:{pin_id} {pin['pin']} ({pin.get('direction', 'all')})"
                    else:
                        tooltip = f"{slot_name}"

                    plugin_instance, pin_name = self.parent.get_plugin_by_pin(pin["pin"])
                    if module_name:
                        bgcolor = "green"
                        tooltip += f"\nmodule: {module_name}"
                    elif plugin_instance:
                        bgcolor = "green"
                        tooltip += f"\n{plugin_instance.title} ({plugin_instance.NAME}) : {pin_name}"

                    if "pos" in pin:
                        self.pinlabels[pkey] = PinButton(self.boardimg, parent=self, pkey=pkey, bgcolor=bgcolor, pin=pin)
                        if pin.get("rotate"):
                            if len(pin["pos"]) == 4:
                                self.pinlabels[pkey].setFixedWidth(int(pin["pos"][2]))
                                self.pinlabels[pkey].setFixedHeight(int(pin["pos"][3]))
                            else:
                                self.pinlabels[pkey].setFixedWidth(15)
                                self.pinlabels[pkey].setFixedHeight(len(pin_id * 15))
                            self.pinlabels[pkey].setText(pin_id, True)
                        else:
                            if len(pin["pos"]) == 4:
                                self.pinlabels[pkey].setFixedWidth(int(pin["pos"][2]))
                                self.pinlabels[pkey].setFixedHeight(int(pin["pos"][3]))
                            else:
                                self.pinlabels[pkey].setFixedWidth(len(pin_id * 10))
                                self.pinlabels[pkey].setFixedHeight(15)
                            self.pinlabels[pkey].setText(pin_id)
                        self.pinlabels[pkey].move(QPoint(int(pin["pos"][0]), int(pin["pos"][1])))
                        self.pinlabels[pkey].setToolTip(tooltip)

                        if module_name:
                            self.pinlabels[pkey].clicked.connect(partial(self.parent.gui_modules.remove_module, slot_name))
                        elif plugin_instance:
                            self.pinlabels[pkey].clicked.connect(partial(self.parent.gui_plugins.edit_plugin, plugin_instance, plugin_instance.plugin_id, None))
                        else:
                            self.pinlabels[pkey].clicked.connect(partial(self.parent.gui_plugins.add_plugin, pin_id, slot_name=slot_name))

                    elif "pos" in slot:
                        self.pinlabels[pkey] = PinButton(self.boardimg, parent=self, pkey=pkey, bgcolor=bgcolor, pin=pin)
                        self.pinlabels[pkey].setFixedWidth(len(slot_name * 10))
                        self.pinlabels[pkey].setFixedHeight(15)
                        self.pinlabels[pkey].setText(slot_name)
                        self.pinlabels[pkey].move(QPoint(int(slot["pos"][0]), int(slot["pos"][1])))
                        self.pinlabels[pkey].setToolTip(tooltip)

                        if module_name:
                            self.pinlabels[pkey].clicked.connect(partial(self.parent.gui_modules.remove_module, slot_name))
                        elif plugin_instance:
                            self.pinlabels[pkey].clicked.connect(partial(self.parent.gui_plugins.edit_plugin, plugin_instance))
                        else:
                            self.pinlabels[pkey].clicked.connect(partial(self.parent.gui_plugins.add_plugin, pin_id, slot_name=slot_name))

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
                direction = label.pin.get("direction") or "all"
                comment = label.pin.get("comment") or ""
                if comment:
                    comment = f" - {comment}"

                plugin_instance, pin_name = self.parent.get_plugin_by_pin(label.pin.get("pin", {}))
                pinfo = ""
                if plugin_instance:
                    pinfo = f"-> {plugin_instance.title} ({plugin_instance.NAME}) : {pin_name}"

                    for signal_name, signal_config in plugin_instance.signals().items():
                        if "userconfig" not in signal_config:
                            signal_config["userconfig"] = {}
                        userconfig = signal_config["userconfig"]
                        net = userconfig.get("net")
                        if net:
                            networks.append(net)

                if key == pkey:
                    pinfo += " <-"
                    infoline = ln

                infotext.append(f" {splitted[1]}: {label.pin.get('pin', {})} ({direction}{comment}) {pinfo}")
                ln += 1
            else:
                label.unmark()

        if len(infotext) > 2:
            if networks:
                infotext.append("Networks:")
                for net in networks:
                    infotext.append(f" {net}")

            ilen = 30
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
