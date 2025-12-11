import json
import os

from PyQt5 import QtGui, QtSvg
from PyQt5.QtCore import QRect, QSize, Qt, pyqtSignal, QSortFilterProxyModel
from PyQt5.QtGui import QFont, QPixmap, QStandardItem
from PyQt5.QtWidgets import (
    QCompleter,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)

import riocore

riocore_path = os.path.dirname(riocore.__file__)

STYLESHEET = """
    background-color: #444444;
    color: white;
"""
STYLESHEET_CHECKBOX = """
    QCheckBox::indicator::unchecked {
        background-color: darkgray;
    }
"""
STYLESHEET_CHECKBOX_BIG = """
    QCheckBox::indicator {
        width: 40px;
        height: 40px;
    }
"""
STYLESHEET_BUTTON = """
    QPushButton::disabled {
        background-color: black;
    }
"""
STYLESHEET_CHECKBOX_GREEN_RED = """
    QCheckBox::indicator::checked {
        background-color: green;
    }
    QCheckBox::indicator::unchecked {
        background-color: red;
    }
"""

# MacOS tabs default to white backgrounds, making them unreadable without more styling.
STYLESHEET_TABBAR = """
    QTabWidget::tab-bar {
        left: 0;
    }

    QTabBar::tab {
        background-color: #333333;
        border: 1px solid #222222;
        color: white;
        padding: 5px 10px;
    }

    QTabBar::tab:selected {
        background-color: #444444;
        border-bottom-color: #444444;
    }

    QTabWidget::pane {
        top: -1px;
        margin-top: 0;
        padding: 10px;
        border: 1px solid black;
    }
"""


class MyQLabel(QLabel):
    def __init__(self, parent):
        super(QLabel, self).__init__()
        self.parent = parent
        self.pixmap = QPixmap()
        self.png_data = None
        self.scale = 1.0

    def mousePressEvent(self, event):
        x = int(event.pos().x() / self.scale)
        y = int(event.pos().y() / self.scale)
        self.parent.on_click(x, y)

    def mouseReleaseEvent(self, event):
        if hasattr(self.parent, "on_release"):
            x = int(event.pos().x() / self.scale)
            y = int(event.pos().y() / self.scale)
            self.parent.on_release(x, y)

    def mouseMoveEvent(self, event):
        if hasattr(self.parent, "on_move"):
            x = int(event.pos().x() / self.scale)
            y = int(event.pos().y() / self.scale)
            self.parent.on_move(x, y)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        delta = event.angleDelta()
        if delta.y() < 0:
            if self.scale > 0.1:
                self.scale -= 0.1
        elif self.scale < 10.0:
            self.scale += 0.1
        self.load(None)

    def load(self, png_data):
        if png_data:
            self.png_data = png_data
        if self.png_data:
            self.pixmap.loadFromData(self.png_data, "png")
            w = int(self.pixmap.size().width() * self.scale)
            h = int(self.pixmap.size().height() * self.scale)
            pixmap = self.pixmap.scaled(QSize(w, h), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setAlignment(Qt.AlignRight | Qt.AlignTop)
            self.setFixedSize(pixmap.size())
            self.setPixmap(pixmap)


class MyQSvgWidget(QtSvg.QSvgWidget):
    def mousePressEvent(self, event):
        self.old_x = event.pos().x()
        self.old_y = event.pos().y()

    def mouseMoveEvent(self, event):
        mp_x = event.pos().x()
        mp_y = event.pos().y()
        diff_x = self.old_x - mp_x
        diff_y = self.old_y - mp_y
        self.old_x = mp_x
        self.old_y = mp_y
        viewbox = self.renderer().viewBox()
        x = int(viewbox.x()) + diff_x
        y = int(viewbox.y()) + diff_y
        width = int(viewbox.width())
        height = int(viewbox.height())
        self.renderer().setViewBox(QRect(int(x), int(y), int(width), int(height)))
        self.repaint()

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        delta = event.angleDelta()
        mp_x = event.pos().x()
        mp_y = event.pos().y()
        if delta.y() < 0:
            scale = 1.1
            diff_x = -mp_x / 10
            diff_y = -mp_y / 10
        else:
            scale = 0.9
            diff_x = mp_x / 10
            diff_y = mp_y / 10
        viewbox = self.renderer().viewBox()
        x = int(viewbox.x()) + diff_x
        y = int(viewbox.y()) + diff_y
        width = int(viewbox.width()) * scale
        height = int(viewbox.height()) * scale
        self.renderer().setViewBox(QRect(int(x), int(y), int(width), int(height)))
        self.repaint()


class MyStandardItem(QStandardItem):
    def __init__(self, txt="", font_size=12, set_bold=False, key=None, help_text=None):
        super().__init__()
        self.key = key
        if help_text:
            self.setToolTip(help_text)
        else:
            self.setToolTip(txt)
        self.setEditable(False)
        self.setText(txt)


class edit_float(QDoubleSpinBox):
    def __init__(self, win, obj, key, vmin=None, vmax=None, cb=None, help_text=None, default=None, decimals=None):
        super().__init__()
        self.win = win
        self.cb = cb
        self.obj = obj
        self.key = key
        self.default = default
        self.no_update = False
        if help_text:
            self.setToolTip(help_text)
        if decimals is None:
            decimals = 5
        self.setDecimals(decimals)
        steps = 1.0
        # if decimals > 1:
        #    for dn in range(decimals - 1):
        #        steps /= 10.0
        self.setSingleStep(steps)
        if vmin:
            self.setMinimum(vmin)
        else:
            self.setMinimum(-99999999)
        if vmax:
            self.setMaximum(vmax)
        else:
            self.setMaximum(99999999)
        if key in obj:
            self.setValue(float(obj[key]))
        elif default is not None:
            self.setValue(float(default))
        self.valueChanged.connect(self.change)
        self.editingFinished.connect(self.change)
        self.setFocusPolicy(Qt.StrongFocus)

    def update(self, obj=None):
        if obj is not None:
            self.obj = obj
        self.no_update = True
        if self.key in self.obj:
            self.setValue(float(self.obj[self.key]))
        elif self.default is not None:
            self.setValue(float(self.default))
        self.no_update = False

    def wheelEvent(self, *args, **kwargs):
        if self.hasFocus():
            return QSpinBox.wheelEvent(self, *args, **kwargs)

    def change(self):
        if self.no_update:
            return
        if self.value() != self.default:
            self.obj[self.key] = self.value()
        elif self.key in self.obj:
            del self.obj[self.key]
        if self.cb:
            self.cb(self.value())
        else:
            self.win.display()


class edit_int(QSpinBox):
    def __init__(self, win, obj, key, vmin=None, vmax=None, cb=None, help_text=None, default=None):
        super().__init__()
        self.win = win
        self.cb = cb
        self.obj = obj
        self.key = key
        self.default = default
        self.no_update = False
        if help_text:
            self.setToolTip(help_text)
        if vmin is not None:
            self.setMinimum(vmin)
        else:
            self.setMinimum(-99999999)
        if vmax is not None:
            self.setMaximum(vmax)
        else:
            self.setMaximum(99999999)
        if key in obj:
            self.setValue(int(obj[key]))
        elif default is not None:
            self.setValue(int(default))
        self.valueChanged.connect(self.change)
        self.editingFinished.connect(self.change)
        self.setFocusPolicy(Qt.StrongFocus)

    def update(self, obj=None):
        if obj is not None:
            self.obj = obj
        self.no_update = True
        if self.key in self.obj:
            self.setValue(int(self.obj[self.key]))
        elif self.default is not None:
            self.setValue(int(self.default))
        self.no_update = False

    def wheelEvent(self, *args, **kwargs):
        if self.hasFocus():
            return QSpinBox.wheelEvent(self, *args, **kwargs)

    def change(self):
        if self.no_update:
            return
        if self.value() != self.default:
            self.obj[self.key] = self.value()
        elif self.key in self.obj:
            del self.obj[self.key]
        if self.cb:
            self.cb(self.value())
        else:
            self.win.display()


class edit_avgfilter(QSpinBox):
    def __init__(self, win, obj, key, vmin=None, vmax=None, cb=None, help_text=None, default=None):
        super().__init__()
        self.win = win
        self.cb = cb
        self.obj = obj
        self.key = key
        self.default = default
        self.no_update = False
        self.setValue(0)
        if help_text:
            self.setToolTip(help_text)
        if vmin:
            self.setMinimum(vmin)
        else:
            self.setMinimum(-99999999)
        if vmax:
            self.setMaximum(vmax)
        else:
            self.setMaximum(99999999)
        if key in obj:
            if obj[key]:
                self.setValue(obj[key][0].get("depth", 0))

        self.valueChanged.connect(self.change)
        self.editingFinished.connect(self.change)
        self.setFocusPolicy(Qt.StrongFocus)

    def update(self, obj=None):
        if obj is not None:
            self.obj = obj
        self.no_update = True
        if self.key in self.obj:
            if self.obj[self.key]:
                self.setValue(self.obj[self.key][0].get("depth", 0))
        self.no_update = False

    def wheelEvent(self, *args, **kwargs):
        if self.hasFocus():
            return QSpinBox.wheelEvent(self, *args, **kwargs)

    def change(self):
        if self.no_update:
            return
        if self.value() != self.default:
            if self.key not in self.obj:
                self.obj[self.key] = []
            fpos = -1
            for pn, part in enumerate(self.obj[self.key]):
                if part.get("type") == "avg":
                    fpos = pn
                    break
            if fpos != -1:
                self.obj[self.key][fpos]["depth"] = self.value()
            else:
                self.obj[self.key].append({"type": "avg", "depth": self.value()})

        elif self.key in self.obj:
            if self.key not in self.obj:
                self.obj[self.key] = []
            fpos = -1
            for pn, part in enumerate(self.obj[self.key]):
                if part.get("type") == "avg":
                    fpos = pn
                    break
            if fpos != -1:
                self.obj[self.key].pop(fpos)
        if self.cb:
            self.cb(self.value())
        else:
            self.win.display()


class edit_text(QLineEdit):
    def __init__(self, win, obj, key, cb=None, help_text=None, default=None):
        super().__init__()
        # self.setMaxLength(150)
        self.win = win
        self.cb = cb
        self.obj = obj
        self.key = key
        self.default = default
        self.no_update = False
        if help_text:
            self.setToolTip(help_text)
        if key in obj:
            self.setText(str(obj[key]))
        elif default is not None:
            self.setText(str(default))
        self.textChanged.connect(self.change)

    def update(self, obj=None):
        if obj is not None:
            self.obj = obj
        self.no_update = True
        if self.key in self.obj:
            self.setText(str(self.obj[self.key]))
        elif self.default is not None:
            self.setText(str(self.default))
        self.no_update = False

    def change(self):
        if self.no_update:
            return
        if self.text() != self.default:
            self.obj[self.key] = self.text()
        elif self.key in self.obj:
            del self.obj[self.key]
        if self.cb:
            self.cb(self.text())
        else:
            self.win.display()


class edit_multiline(QTextEdit):
    def __init__(self, win, obj, key, cb=None, help_text=None, default=None, mul=0):
        super().__init__()
        self.setFont(QFont("Monospace"))
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.win = win
        self.cb = cb
        self.obj = obj
        self.key = key
        self.default = default
        self.no_update = False
        if help_text:
            self.setToolTip(help_text)
        if key in obj:
            self.setText(str(obj[key]))
        elif default is not None:
            self.setText(str(default))
        self.textChanged.connect(self.change)

    def update(self, obj=None):
        if obj is not None:
            self.obj = obj
        self.no_update = True
        if self.key in self.obj:
            self.setText(str(self.obj[self.key]))
        elif self.default is not None:
            self.setText(str(self.default))
        self.no_update = False

    def change(self):
        if self.no_update:
            return
        if self.toPlainText() != self.default:
            self.obj[self.key] = self.toPlainText()
        elif self.key in self.obj:
            del self.obj[self.key]
        if self.cb:
            self.cb(self.toPlainText())
        else:
            self.win.display()


class edit_file(QLineEdit):
    clicked = pyqtSignal()

    def __init__(self, win, obj, key, cb=None, help_text=None, default=None):
        super().__init__()
        self.setMaxLength(150)
        self.win = win
        self.cb = cb
        self.obj = obj
        self.key = key
        self.default = default
        self.no_update = False
        if help_text:
            self.setToolTip(help_text)
        if key in obj:
            self.setText(str(obj[key]))
        elif default is not None:
            self.setText(str(default))
        self.textChanged.connect(self.change)

    def mousePressEvent(self, event):
        self.clicked.emit()
        file_dialog = QFileDialog(self)
        suffix_list = ["*.json"]
        folder = os.path.join(riocore_path, "configs")
        text = self.text()
        if text:
            folder = os.path.dirname(text)
        name = file_dialog.getOpenFileName(
            self,
            "Load File",
            folder,
            f"json ( {' '.join(suffix_list)} )Load File",
            "",
        )
        if name[0]:
            self.setText(name[0])

    def change(self):
        if self.no_update:
            return
        if self.text() != self.default:
            self.obj[self.key] = self.text()
        elif self.key in self.obj:
            del self.obj[self.key]
        if self.cb:
            self.cb(self.text())
        else:
            self.win.display()


class edit_bool(QCheckBox):
    def __init__(self, win, obj, key, cb=None, help_text=None, default=None):
        super().__init__()
        self.win = win
        self.cb = cb
        self.obj = obj
        self.key = key
        self.default = default
        self.no_update = False
        self.setStyleSheet(STYLESHEET_CHECKBOX)
        if help_text:
            self.setToolTip(help_text)
        if key in obj:
            self.setChecked(obj[key])
        elif default is not None:
            self.setChecked(default)
        self.stateChanged.connect(self.change)

    def update(self, obj=None):
        if obj is not None:
            self.obj = obj
        self.no_update = True
        if self.key in self.obj:
            self.setChecked(self.obj[self.key])
        elif self.default is not None:
            self.setChecked(self.default)
        self.no_update = False

    def change(self):
        if self.no_update:
            return
        if self.isChecked() != self.default:
            self.obj[self.key] = self.isChecked()
        elif self.key in self.obj:
            del self.obj[self.key]
        if self.cb:
            self.cb(self.text())
        else:
            self.win.display()


class edit_combobox(QComboBox):
    def __init__(self, win, obj, key, options, cb=None, help_text=None, default=None, need_enter=False):
        super().__init__()
        self.win = win
        self.cb = cb
        self.obj = obj
        self.key = key
        self.default = default
        self.no_update = False
        self.options = options.copy()
        self.options_clean = []
        for opt in self.options:
            if opt:
                self.options_clean.append(opt.split("|")[0])
            else:
                self.options_clean.append(opt)
        if help_text:
            self.setToolTip(help_text)
        if key in obj:
            if str(obj[key]) not in self.options_clean:
                self.options.append(str(obj[key]))
                self.options_clean.append(str(obj[key]))
        else:
            self.options.append("")
            self.options_clean.append("")
        for option in self.options:
            self.addItem(option)

        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.pFilterModel = QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())
        self.completer = QCompleter(self.pFilterModel, self)
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(self.completer)
        self.lineEdit().textEdited[str].connect(self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.on_completer_activated)

        if key in obj:
            if str(obj[key]) in self.options_clean:
                self.setCurrentIndex(self.options_clean.index(str(obj[key])))
            else:
                print(f"ERROR: {obj[key]} is not a option")
        elif default is not None:
            if str(default) in self.options_clean:
                self.setCurrentIndex(self.options_clean.index(str(default)))
            else:
                print(f"ERROR: {default} is not a option")
        else:
            self.setCurrentIndex(self.options_clean.index(""))
        if need_enter:
            self.currentIndexChanged.connect(self.change)
            self.textActivated.connect(self.change)
        else:
            self.editTextChanged.connect(self.change)
        self.setFocusPolicy(Qt.StrongFocus)

    def on_completer_activated(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            self.activated[str].emit(self.itemText(index))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.change()
        else:
            QComboBox.keyPressEvent(self, event)

    def update(self, obj=None):
        if obj is not None:
            self.obj = obj
        self.no_update = True
        if self.key in self.obj:
            if str(self.obj[self.key]) in self.options_clean:
                self.setCurrentIndex(self.options_clean.index(str(self.obj[self.key])))
            else:
                print(f"ERROR: {self.obj[self.key]} is not a option")
        elif self.default is not None:
            if str(self.default) in self.options_clean:
                self.setCurrentIndex(self.options_clean.index(str(self.default)))
            else:
                print(f"ERROR: {self.default} is not a option")
        else:
            self.setCurrentIndex(self.options_clean.index(""))
        self.no_update = False

    def wheelEvent(self, *args, **kwargs):
        if self.hasFocus():
            return QComboBox.wheelEvent(self, *args, **kwargs)

    def change(self):
        if self.no_update:
            return
        new_value = self.currentText().split("|")[0]
        if new_value != self.default:
            self.obj[str(self.key)] = new_value
        elif str(self.key) in self.obj:
            del self.obj[str(self.key)]
        if self.cb:
            self.cb(new_value)
        else:
            self.win.display()


class modifier_selector(QComboBox):
    def __init__(self, win, pin_setup, modifier_id, modifier_view, help_text=None):
        super().__init__()
        self.win = win
        self.pin_setup = pin_setup
        self.modifier_id = modifier_id
        self.modifier_view = modifier_view
        self.entrys = list(set(riocore.plugins.Modifiers().pin_modifier_list()))
        self.entrys.append("--delete--")
        if help_text:
            self.setToolTip(help_text)
        for entry in self.entrys:
            self.addItem(entry)
        active = pin_setup["modifier"][self.modifier_id]["type"]
        self.setCurrentIndex(self.entrys.index(active))
        self.setEditable(False)
        self.activated.connect(self.change)
        self.setFocusPolicy(Qt.StrongFocus)

    def wheelEvent(self, *args, **kwargs):
        if self.hasFocus():
            return QComboBox.wheelEvent(self, *args, **kwargs)

    def change(self):
        selected = self.currentText()
        if selected == "--delete--":
            del self.pin_setup["modifier"][self.modifier_id]
            parent = self.modifier_view.parent()
            while parent.rowCount() > 0:
                parent.removeRow(0)
            for modifier_id, modifier in enumerate(self.pin_setup.get("modifier", [])):
                self.win.tree_add_modifier(parent, self.pin_setup, modifier_id, modifier)
        else:
            self.pin_setup["modifier"][self.modifier_id]["type"] = selected
        self.win.display()


class ImageMap(QLabel):
    last_x = -1
    last_y = -1
    last_action = 0
    moved = 0

    def __init__(self, parent):
        super(QLabel, self).__init__(parent.parent)
        self.parent = parent

    def mousePressEvent(self, event):
        x = int(event.pos().x() / self.parent.scale)
        y = int(event.pos().y() / self.parent.scale)
        self.last_x = x
        self.last_y = y
        self.last_action = 1
        self.moved = 0
        if event.button() == Qt.RightButton:
            self.setPin(event.pos())

    def mouseReleaseEvent(self, event):
        int(event.pos().x() / self.parent.scale)
        int(event.pos().y() / self.parent.scale)
        self.last_action = 0
        self.moved = 0

    def mouseMoveEvent(self, event):
        x = int(event.pos().x() / self.parent.scale)
        y = int(event.pos().y() / self.parent.scale)
        if self.last_action == 1:
            xs = self.parent.scroll_widget.horizontalScrollBar()
            ys = self.parent.scroll_widget.verticalScrollBar()
            xs_last = xs.value()
            ys_last = ys.value()
            diff_x = x - self.last_x
            diff_y = y - self.last_y
            if abs(diff_x) > 4 or abs(diff_y) > 4:
                self.moved = 1
            xs.setValue(xs_last - diff_x)
            ys.setValue(ys_last - diff_y)

    """
    def wheelEvent(self, event):
        delta = event.angleDelta()
        if delta.y() < 0:
            if self.parent.scale > 0.1:
                self.parent.scale -= 0.1
        else:
            if self.parent.scale < 10.0:
                self.parent.scale += 0.1
    """

    def setPin(self, pos):
        grid = 5
        pos_x = pos.x() / self.parent.scale
        pos_y = pos.y() / self.parent.scale
        used_pos_x = set()
        used_pos_y = set()
        used_pins = []
        for slot in self.parent.parent.slots:
            for pin_name, pin_data in slot["pins"].items():
                if isinstance(pin_data, str):
                    used_pins.append(pin_data)
                else:
                    used_pins.append(pin_data["pin"])
                    if "pos" in pin_data:
                        used_pos_x.add(pin_data["pos"][0])
                        used_pos_y.add(pin_data["pos"][1])

        # align to other positions +-grid size
        for pos in used_pos_x:
            if abs(pos - pos_x) <= grid:
                pos_x = pos
                break
        for pos in used_pos_y:
            if abs(pos - pos_y) <= grid:
                pos_y = pos
                break

        pin_name_default = "P1"
        if self.parent.parent.slots:
            last_slot = self.parent.parent.slots[-1]
            pin_name_num = 1
            found = True
            while found:
                found = False
                for pin_name in last_slot["pins"]:
                    if f"P{pin_name_num}" == pin_name:
                        pin_name_num += 1
                        found = True
            pin_name_default = f"P{pin_name_num}"

        dialog = QDialog()
        dialog.setWindowTitle("set pin")
        dialog.setStyleSheet(STYLESHEET)
        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)
        dialog.layout = QVBoxLayout()

        message = QLabel("Slot:")
        dialog.layout.addWidget(message)
        slot_select = QComboBox()
        slot_select.setEditable(True)
        for slot in reversed(self.parent.parent.slots):
            slot_select.addItem(slot["name"])
        dialog.layout.addWidget(slot_select)

        message = QLabel("Pin-Name:")
        dialog.layout.addWidget(message)
        pin_name = QLineEdit(pin_name_default)
        dialog.layout.addWidget(pin_name)

        message = QLabel("FPGA-Pin:")
        dialog.layout.addWidget(message)
        pin_select = QComboBox()
        pin_select.setEditable(True)
        for pin in self.parent.parent.pinlist:
            if ":" not in pin and pin not in used_pins:
                pin_select.addItem(pin)
        dialog.layout.addWidget(pin_select)

        message = QLabel("Direction:")
        dialog.layout.addWidget(message)
        direction = QComboBox()
        direction.addItem("all")
        direction.addItem("output")
        direction.addItem("input")
        dialog.layout.addWidget(direction)

        message = QLabel("PosX:")
        dialog.layout.addWidget(message)
        posx = QComboBox()
        posx.setEditable(True)
        posx.addItem(str(pos_x))
        for pos in used_pos_x:
            posx.addItem(str(pos))
        dialog.layout.addWidget(posx)

        message = QLabel("PosY:")
        dialog.layout.addWidget(message)
        posy = QComboBox()
        posy.setEditable(True)
        posy.addItem(str(pos_y))
        for pos in used_pos_y:
            posy.addItem(str(pos))
        dialog.layout.addWidget(posy)

        dialog.layout.addWidget(dialog_buttonBox)
        dialog.setLayout(dialog.layout)

        if dialog.exec():
            slot_name = slot_select.currentText()
            name = pin_name.text()
            pin = pin_select.currentText()
            direction_str = direction.currentText()
            pos_x = posx.currentText()
            pos_y = posy.currentText()
            if direction_str == "":
                direction_str = "all"

            if slot_name and name and pin:
                pin_cfg = {"pin": pin, "pos": [int(float(pos_x)), int(float(pos_y))], "direction": direction_str}

                slot_n = -1
                for sn, slot in enumerate(self.parent.parent.slots):
                    if slot["name"] == slot_name:
                        slot_n = sn
                        break

                if slot_n == -1:
                    self.parent.parent.slots.append(
                        {
                            "name": slot_name,
                            "comment": "",
                            "default": "",
                            "pins": {name: pin_cfg},
                        }
                    )
                else:
                    self.parent.parent.slots[slot_n]["pins"][name] = pin_cfg

                print(json.dumps(self.parent.parent.slots, indent=4))
                self.parent.parent.request_pin_table_load = 1
            else:
                print("ERROR: missing informations")


class PinButton(QPushButton):
    def __init__(self, widget, parent=None, pkey=None, bgcolor=None, pin=None):
        super(QPushButton, self).__init__(widget)
        self.parent = parent
        self.pkey = pkey
        self.bgcolor = bgcolor
        if not pin:
            pin = {}
        self.pin = pin
        if self.parent and self.bgcolor:
            self.setStyleSheet(f"background-color: {self.bgcolor}; font-size:12px;")

    def setText(self, text, rotate=False):
        if rotate:
            text = "\n".join(text)
        QPushButton.setText(self, text)

    def enterEvent(self, event):
        if self.parent and self.pkey:
            self.parent.pinlayout_mark(self.pkey)

    def leaveEvent(self, event):
        if self.parent and self.pkey:
            self.parent.pinlayout_mark(":")

    def mark(self, color):
        if self.parent and color:
            self.setStyleSheet(f"background-color: {color}; font-size:12px;")

    def unmark(self):
        if self.parent and self.bgcolor:
            self.setStyleSheet(f"background-color: {self.bgcolor}; font-size:12px;")
