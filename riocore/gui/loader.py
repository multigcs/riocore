import os
import glob
import json

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QStyle,
    QFileDialog,
    QDialogButtonBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QDialog,
)

import riocore

riocore_path = os.path.dirname(riocore.__file__)


class ConfigLoader:
    def __init__(self, parent):
        self.parent = parent

    def select(self):
        dialog = QDialog()
        dialog.setWindowTitle("rio-flow")
        if hasattr(self.parent, "STYLESHEET"):
            dialog.setStyleSheet(self.parent.STYLESHEET)
        dialog.layout = QVBoxLayout()
        dialog.setLayout(dialog.layout)

        def select_config():
            self.parent.config_file = self.select_config()
            if self.parent.config_file is None:
                exit(1)
            dialog.accept()

        def select_empty():
            self.parent.config = {
                "name": "Empty",
                "plugins": [],
            }
            dialog.accept()

        def select_file():
            self.load_config_from()
            dialog.accept()

        def select_exit():
            exit(1)

        button_empty = QPushButton(" Empty Config")
        button_empty.setIcon(self.parent.style().standardIcon(QStyle.SP_FileIcon))
        button_empty.setIconSize(QSize(48, 48))
        button_empty.setFixedSize(300, 100)
        button_empty.setStyleSheet("QPushButton{border: 1px solid; font-size:18px;}")
        button_empty.clicked.connect(select_empty)
        dialog.layout.addWidget(button_empty)

        button_config = QPushButton(" Select Config")
        button_config.setIcon(self.parent.style().standardIcon(QStyle.SP_ComputerIcon))
        button_config.setIconSize(QSize(48, 48))
        button_config.setFixedSize(300, 100)
        button_config.setStyleSheet("QPushButton{border: 1px solid; font-size:18px;}")
        button_config.clicked.connect(select_config)
        dialog.layout.addWidget(button_config)

        button_file = QPushButton(" Open config file from...")
        button_file.setIcon(self.parent.style().standardIcon(QStyle.SP_DirIcon))
        button_file.setIconSize(QSize(48, 48))
        button_file.setFixedSize(300, 100)
        button_file.setStyleSheet("QPushButton{border: 1px solid; font-size:18px;}")
        button_file.clicked.connect(select_file)
        dialog.layout.addWidget(button_file)

        dialog.layout.addStretch()

        button_exit = QPushButton("Exit")
        button_exit.setIcon(self.parent.style().standardIcon(QStyle.SP_DialogCancelButton))
        button_exit.clicked.connect(select_exit)
        dialog.layout.addWidget(button_exit)

        if dialog.exec():
            return True
        return False

    def load_config_from(self):
        file_dialog = QFileDialog(self.parent)
        suffix_list = ["*.json"]
        name = file_dialog.getOpenFileName(
            self.parent,
            "Load Config",
            os.path.join(riocore_path, "configs"),
            f"config ( {' '.join(suffix_list)} )Load Config",
            "",
        )
        if name[0]:
            self.parent.config_file = name[0]

    def select_config(self):
        def show_config_info(idx):
            config_path = config_list[idx]
            config_name = config_path.split(os.sep)[-1]
            config_raw = open(config_path, "r").read()
            config_config = json.loads(config_raw)

            image_label.clear()

            name_label.setText(config_name)
            description = []
            for key in ("name", "description"):
                value = config_config.get(key)
                description.append(f"{key.title()}: {value}")
            description_label.setText("\n".join(description))
            dialog.selected = config_path

        dialog = QDialog()
        dialog.setWindowTitle("load config")
        if hasattr(self.parent, "STYLESHEET"):
            dialog.setStyleSheet(self.parent.STYLESHEET)
        # dialog.setMinimumWidth(800)
        dialog.setMinimumHeight(480)

        dialog.layout = QVBoxLayout()
        dialog.setLayout(dialog.layout)

        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)
        dialog_buttonBox.rejected.connect(dialog.reject)

        config_table = QTableWidget()
        config_table.setColumnCount(1)
        config_table.setHorizontalHeaderItem(0, QTableWidgetItem("configs"))
        header = config_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        config_list = []
        config_n = 0
        for path in sorted(glob.glob(os.path.join(riocore_path, "configs", "*", "*.json"))):
            if path.endswith(".json"):
                config_name = path.split(os.sep)[-2] + "/" + path.split(os.sep)[-1]
            else:
                continue
            config_table.setRowCount(config_n + 1)
            config_list.append(path)
            pitem = QTableWidgetItem(config_name)
            config_table.setItem(config_n, 0, pitem)
            config_n += 1

        config_table.setFixedWidth(300)
        config_table.cellClicked.connect(show_config_info)
        config_table.currentCellChanged.connect(show_config_info)

        mid_layout = QVBoxLayout()
        mid_widget = QWidget()
        mid_widget.setFixedWidth(400)
        mid_widget.setLayout(mid_layout)
        name_label = QLabel("name")
        name_label_font = QFont()
        name_label_font.setBold(True)
        name_label.setFont(name_label_font)

        mid_layout.addWidget(name_label)
        description_label = QLabel("description")
        mid_layout.addWidget(description_label)
        mid_layout.addStretch()

        right_layout = QVBoxLayout()
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        image_label = QLabel()
        right_layout.addWidget(image_label)
        right_layout.addStretch()

        infos = QHBoxLayout()
        infos.addWidget(config_table, stretch=1)
        infos.addWidget(mid_widget, stretch=3)
        infos.addWidget(right_widget, stretch=1)

        dialog.layout.addLayout(infos)
        dialog.layout.addWidget(dialog_buttonBox)

        show_config_info(0)

        if dialog.exec():
            return dialog.selected
