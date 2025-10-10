import os
import glob
import json

import riocore

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (
    QHeaderView,
    QLineEdit,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

riocore_path = os.path.dirname(riocore.__file__)


class GuiBreakouts:
    def __init__(self, parent):
        self.parent = parent

    def edit_breakout(self, breakout_setup):
        def update():
            pass

        def update_rotate(value):
            breakout_setup["rotate"] = int(value)
            self.parent.display()

        dialog = QDialog()
        dialog.setWindowTitle("edit Breakout")
        if hasattr(self.parent, "STYLESHEET"):
            dialog.setStyleSheet(self.parent.STYLESHEET)

        dialog.layout = QVBoxLayout()
        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)

        slots = []
        for slot in self.parent.bnode.jdata["slots"]:
            slots.append(slot["name"])

        dialog.layout.addWidget(QLabel("Name:"))
        dialog.layout.addWidget(self.parent.edit_item(breakout_setup, "name", {"type": str}, cb=None))
        dialog.layout.addWidget(QLabel("Slot:"))
        dialog.layout.addWidget(self.parent.edit_item(breakout_setup, "slot", {"type": "select", "options": slots}, cb=None))
        dialog.layout.addWidget(QLabel("Rotate:"))
        dialog.layout.addWidget(self.parent.edit_item(breakout_setup, "rotate", {"type": "select", "options": ["0", "90", "180", "-90"]}, cb=update_rotate))

        dialog.mlabel = QLabel("")
        dialog.layout.addWidget(dialog.mlabel)
        update()

        dialog.layout.addWidget(dialog_buttonBox)
        dialog.setLayout(dialog.layout)

        if dialog.exec():
            pass

    def add_breakout(self, pin_id, slot_name=None):
        dialog = QDialog()
        dialog.setWindowTitle("select breakout")
        if hasattr(self.parent, "STYLESHEET"):
            dialog.setStyleSheet(self.parent.STYLESHEET)

        dialog.layout = QVBoxLayout()
        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)
        dialog_buttonBox.rejected.connect(dialog.reject)

        dialog.setLayout(dialog.layout)

        breakouts = []
        for breakout_path in sorted(glob.glob(os.path.join(riocore_path, "breakouts", "*", "breakout.json"))):
            breakout_name = os.path.basename(os.path.dirname(breakout_path))
            breakouts.append(breakout_name)

        def show_breakout_info(idx):
            if not breakout_table.item(idx, 1):
                return

            breakout_name = breakout_table.item(idx, 1).text()
            breakout_path = os.path.join(riocore_path, "breakouts", breakout_name)
            image_path = os.path.join(breakout_path, "breakout.png")
            json_path = os.path.join(breakout_path, "breakout.json")
            if os.path.isfile(image_path):
                pixmap = QPixmap(image_path)
                image_label.setPixmap(pixmap)
            else:
                image_label.clear()

            jdata = json.loads(open(json_path, "r").read())

            name_label.setText(breakout_name.replace("_", "-").title())
            info_label.setText(jdata.get("comment"))
            description = jdata.get("description") or "---"
            description_label.setText(description)
            dialog.selected = breakout_name

        def search(search_str):
            breakout_table.setRowCount(0)
            row = 0
            for breakout_name in breakouts:
                stext = f"{breakout_name}"
                if search_str.lower() not in stext.lower():
                    continue
                breakout_table.setRowCount(row + 1)
                breakout_table.setItem(row, 0, QTableWidgetItem(""))
                breakout_table.setItem(row, 1, QTableWidgetItem(breakout_name))
                breakout_path = os.path.join(riocore_path, "breakouts", breakout_name)
                image_path = os.path.join(breakout_path, "breakout.png")
                if os.path.isfile(image_path):
                    ilabel = QLabel()
                    ilabel.setFixedSize(24, 24)
                    pixmap = QPixmap(image_path)
                    ilabel.setPixmap(pixmap)
                    ilabel.setScaledContents(True)
                    breakout_table.setCellWidget(row, 0, ilabel)
                row += 1
            if row > 0:
                show_breakout_info(0)

        breakout_table = QTableWidget()
        breakout_table.setColumnCount(2)
        breakout_table.verticalHeader().setVisible(False)
        breakout_table.setHorizontalHeaderItem(0, QTableWidgetItem(""))
        breakout_table.setHorizontalHeaderItem(1, QTableWidgetItem("Name"))
        breakout_table.setRowCount(len(breakouts))
        for row, breakout_name in enumerate(breakouts):
            breakout_table.setItem(row, 0, QTableWidgetItem(""))
            breakout_table.setItem(row, 1, QTableWidgetItem(breakout_name))
            breakout_path = os.path.join(riocore_path, "breakouts", breakout_name)
            image_path = os.path.join(breakout_path, "image.png")
            if os.path.isfile(image_path):
                ilabel = QLabel()
                ilabel.setFixedSize(24, 24)
                pixmap = QPixmap(image_path)
                ilabel.setPixmap(pixmap)
                ilabel.setScaledContents(True)
                breakout_table.setCellWidget(row, 0, ilabel)

        breakout_table.setFixedWidth(200)
        breakout_table.cellClicked.connect(show_breakout_info)
        breakout_table.currentCellChanged.connect(show_breakout_info)
        header = breakout_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        mid_layout = QVBoxLayout()
        mid_widget = QWidget()
        mid_widget.setMinimumWidth(400)
        mid_widget.setLayout(mid_layout)
        name_label = QLabel("name")
        name_label_font = QFont()
        name_label_font.setBold(True)
        name_label.setFont(name_label_font)

        mid_layout.addWidget(name_label)
        info_label = QLabel("info")
        mid_layout.addWidget(info_label)
        description_label = QLabel("description")
        description_label.setAlignment(Qt.AlignTop)
        description_scroll = QScrollArea()
        description_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        description_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        description_scroll.setWidgetResizable(True)
        description_scroll.setWidget(description_label)
        mid_layout.addWidget(description_scroll, stretch=1)

        right_layout = QVBoxLayout()
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        image_label = QLabel()
        right_layout.addWidget(image_label)
        right_layout.addStretch()

        left_layout = QVBoxLayout()
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        breakout_search = QLineEdit("")
        breakout_search.textChanged.connect(search)
        left_layout.addWidget(breakout_search)
        left_layout.addWidget(breakout_table, stretch=1)

        infos = QHBoxLayout()
        infos.addWidget(left_widget, stretch=0)
        infos.addWidget(mid_widget, stretch=3)
        infos.addWidget(right_widget, stretch=0)

        dialog.layout.addLayout(infos)
        dialog.layout.addWidget(dialog_buttonBox)

        show_breakout_info(0)

        if dialog.exec():
            breakout_config = {"slot": slot_name, "breakout": dialog.selected, "name": "", "pos": [150.0, 120.0], "rotate": 0}

            uid_prefix = breakout_config["breakout"]
            unum = 0
            while f"{uid_prefix}{unum}" in self.parent.breakout_uids:
                unum += 1
            self.parent.breakout_uids.append(f"{uid_prefix}{unum}")

            if hasattr(self.parent, "insert_breakout"):
                breakout_config["name"] = f"{uid_prefix}{unum}"
                if "breakouts" not in self.parent.config:
                    self.parent.config["breakouts"] = []
                self.parent.config["breakouts"].append(breakout_config)
                self.parent.insert_breakout(breakout_config)
                self.parent.redraw()

            return dialog.selected
