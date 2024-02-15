
from PyQt5 import QtGui, QtSvg
from PyQt5.QtCore import QDateTime, QSize, Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTreeView,
    QVBoxLayout,
    QWidget,
)


class config():

    def __init__(self, instance):
        self.instance = instance
        print("blaa")

    def run(self):

        config = self.instance.plugin_setup.get("config", {})

        dialog = QDialog()
        dialog.setWindowTitle("add Plugin")
        dialog.setFixedWidth(500)
        dialog.setFixedHeight(400)

        dialog.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        dialog.buttonBox.accepted.connect(dialog.accept)

        dialog.layout = QVBoxLayout()

        hlayout = QHBoxLayout()

        vlayout_left = QVBoxLayout()

        message = QLabel("Plugin-Type:")
        vlayout_left.addWidget(message)
        combo = QComboBox()
        combo.addItem("test1")
        combo.addItem("test2")
        vlayout_left.addWidget(combo)
        vlayout_left.addStretch()

        vlayout = QVBoxLayout()
        info = QLabel("testme text")
        vlayout.addWidget(info)

        description = QPlainTextEdit()
        description.clear()
        description.insertPlainText(str(config))

        vlayout.addWidget(description)

        hlayout.addLayout(vlayout_left)
        hlayout.addLayout(vlayout)

        dialog.layout.addLayout(hlayout)

        dialog.layout.addWidget(dialog.buttonBox)
        dialog.setLayout(dialog.layout)

        if dialog.exec():
            self.instance.plugin_setup["config"] = {
                "testme": {
                    "direction": "output",
                    "address": 1,
                    "type": 3,
                    "values": 2,
                    "register": 0,
                    "unit": "",
                    "scale": 1.0,
                    "format": "d",
                }
            }
            return combo.currentText()

