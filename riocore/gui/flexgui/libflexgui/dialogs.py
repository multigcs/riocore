import os

from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel
from PyQt6.QtWidgets import QMessageBox, QPlainTextEdit
from PyQt6.QtWidgets import QSpinBox, QDoubleSpinBox
from PyQt6.QtGui import QPixmap, QTextCursor
from PyQt6.QtCore import Qt

import linuxcnc as emc
import hal

from libflexgui import number_pad
from libflexgui import gcode_pad
from libflexgui import keyboard_pad
from libflexgui import tool_change
from libflexgui import touchoff
from libflexgui import tool_touchoff
from libflexgui import utilities
from libflexgui import search


def spinbox_numbers(parent, obj):
    if obj.isEnabled():
        np = number_pad.number_pad()
        stylesheet = os.path.join(parent.lib_path, "touch.qss")
        with open(stylesheet, "r") as fh:
            np.setStyleSheet(fh.read())
        result = np.exec()
        if result:
            if isinstance(obj, QSpinBox):  # return an int
                obj.setValue(utilities.string_to_int(np.retval()))
            elif isinstance(obj, QDoubleSpinBox):  # return a float
                print(utilities.string_to_float(np.retval()))
                obj.setValue(utilities.string_to_float(np.retval()))


def numbers(parent, obj):
    np = number_pad.number_pad()
    stylesheet = os.path.join(parent.lib_path, "touch.qss")
    with open(stylesheet, "r") as fh:
        np.setStyleSheet(fh.read())
    result = np.exec()
    if result:
        obj.setText(np.retval())


def gcode(parent, obj):
    gp = gcode_pad.gcode_pad()
    stylesheet = os.path.join(parent.lib_path, "touch.qss")
    with open(stylesheet, "r") as fh:
        gp.setStyleSheet(fh.read())
    result = gp.exec()
    if result:
        obj.setText(gp.retval())


def manual_tool_change(parent):
    tc = tool_change.app()
    if parent.theme:  # use the theme
        stylesheet = os.path.join(parent.lib_path, f"{parent.theme}.qss")
    else:
        stylesheet = os.path.join(parent.lib_path, "touch.qss")
    with open(stylesheet, "r") as s:
        tc.setStyleSheet(s.read())
    result = tc.exec()
    if result:
        hal.set_p("iocontrol.0.tool-changed", "true")
        parent.tool_changed = True
    else:
        parent.command.abort()
        parent.command.wait_complete()


def touchoff_selected(parent):
    to = touchoff.app()
    if parent.theme:  # use the theme
        stylesheet = os.path.join(parent.lib_path, f"{parent.theme}.qss")
    else:
        stylesheet = os.path.join(parent.lib_path, "touch.qss")
    with open(stylesheet, "r") as s:
        to.setStyleSheet(s.read())
    axis = parent.axes_group.checkedButton().text()
    to.axis_lb.setText(f"Axis: {axis}")
    result = to.exec()
    if result == QDialog.DialogCode.Accepted:
        offset = to.coordinate_le.text()
        if not utilities.is_number(offset):
            msg = f"{offset} is not a number."
            warn_msg_ok(parent, msg, "Invalid Entry")
            return
        cs = to.coordinate_systems_cb.currentData()
        command = f"G10 L20 P{cs} {axis}{offset}"
        if utilities.ok_for_mdi(parent):
            parent.command.mode(emc.MODE_MDI)
            parent.command.wait_complete()  # wait until mode switch executed
            parent.command.mdi(command)
            parent.command.wait_complete()
            parent.command.mode(emc.MODE_MANUAL)


def tool_touchoff_selected(parent):
    tto = tool_touchoff.app()
    if parent.theme:  # use the theme
        stylesheet = os.path.join(parent.lib_path, f"{parent.theme}.qss")
    else:
        stylesheet = os.path.join(parent.lib_path, "touch.qss")
    with open(stylesheet, "r") as s:
        tto.setStyleSheet(s.read())
    axis = parent.axes_group.checkedButton().text()
    tto.axis_lb.setText(f"Axis: {axis}")
    result = tto.exec()
    if result == QDialog.DialogCode.Accepted:
        offset = tto.offset_le.text()
        if not utilities.is_number(offset):
            msg = f"{offset} is not a number."
            warn_msg_ok(parent, msg, "Invalid Entry")
            return
        command = f"G10 L11 P0 {axis}{offset}"
        if utilities.ok_for_mdi(parent):
            parent.command.mode(emc.MODE_MDI)
            parent.command.wait_complete()  # wait until mode switch executed
            parent.command.mdi(command)
            parent.command.wait_complete()
            parent.command.mode(emc.MODE_MANUAL)


def keyboard(parent, obj):
    kb = keyboard_pad.keyboard_pad()
    result = kb.exec()
    if result:
        obj.setText(kb.retval())


def find(parent):
    sr = search.FindDialog(parent)
    result = sr.exec()
    print(result)


def info_msg_ok(parent, msg, title=None):
    # dialogs.info_msg_ok(parent, msg, 'title'
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Information)
    msg_box.setWindowTitle(title)
    msg_box.setText(msg)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

    if parent.theme:  # use the theme
        stylesheet = os.path.join(parent.lib_path, f"{parent.theme}.qss")
    else:
        stylesheet = os.path.join(parent.lib_path, "touch.qss")
    with open(stylesheet, "r") as s:
        msg_box.setStyleSheet(s.read())

    returnValue = msg_box.exec()
    if returnValue == QMessageBox.StandardButton.Ok:
        return True
    else:
        return False


def error_msg_ok(parent, msg, title=None):  # plain error message
    # dialogs.error_msg_ok(parent, msg, 'title')
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setWindowTitle(title)
    msg_box.setText(msg)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

    returnValue = msg_box.exec()
    if returnValue == QMessageBox.StandardButton.Ok:
        return True
    else:
        return False


def warn_msg_ok(parent, msg, title=None):
    # dialogs.warn_msg_ok(parent, msg, 'title')
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setWindowTitle(title)
    msg_box.setText(msg)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

    if parent.theme:  # use the theme
        stylesheet = os.path.join(parent.lib_path, f"{parent.theme}.qss")
    else:
        stylesheet = os.path.join(parent.lib_path, "touch.qss")
    with open(stylesheet, "r") as s:
        msg_box.setStyleSheet(s.read())

    returnValue = msg_box.exec()
    if returnValue == QMessageBox.StandardButton.Ok:
        return True
    else:
        return False


def warn_msg_yes_no(parent, msg, title=None):
    # dialogs.warn_msg_yes_no(parent, msg, 'title')
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setWindowTitle(title)
    msg_box.setText(msg)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

    if parent.theme:  # use the theme
        stylesheet = os.path.join(parent.lib_path, f"{parent.theme}.qss")
    else:
        stylesheet = os.path.join(parent.lib_path, "touch.qss")
    with open(stylesheet, "r") as s:
        msg_box.setStyleSheet(s.read())

    returnValue = msg_box.exec()
    if returnValue == QMessageBox.StandardButton.Yes:
        return True
    else:
        return False


def critical_msg_ok(parent, msg, title=None):
    # dialogs.critical_msg_ok(parent, msg, 'title')
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(msg)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

    if parent.theme:  # use the theme
        stylesheet = os.path.join(parent.lib_path, f"{parent.theme}.qss")
    else:
        stylesheet = os.path.join(parent.lib_path, "touch.qss")
    with open(stylesheet, "r") as s:
        msg_box.setStyleSheet(s.read())

    returnValue = msg_box.exec()
    if returnValue == QMessageBox.StandardButton.Ok:
        return True
    else:
        return False


def about_dialog(parent):
    dialog_box = QDialog()
    dialog_box.setMinimumSize(300, 300)
    dialog_box.setWindowTitle("About")

    layout = QVBoxLayout(dialog_box)

    titleLabel = QLabel()
    titleLabel.setText("FlexGUI")
    titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(titleLabel)

    imageLabel = QLabel()
    imageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

    image_path = os.path.join(parent.lib_path, "flexgui.jpg")
    pixmap = QPixmap(image_path)
    pixmap = pixmap.scaled(256, 256, Qt.AspectRatioMode.KeepAspectRatio)
    imageLabel.setPixmap(pixmap)
    layout.addWidget(imageLabel)

    authorLabel = QLabel()
    authorLabel.setText("Author: John Thornton")
    authorLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(authorLabel)

    versionLabel = QLabel()
    versionLabel.setText(f"Version: {parent.flex_version}")
    versionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(versionLabel)

    aboutLabel = QLabel()
    aboutLabel.setText("Flexible Graphical User Interface\nfor LinuxCNC")
    aboutLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(aboutLabel)

    websiteLabel = QLabel()
    websiteLabel.setText("<a href='https://gnipsel.com/'>Authors Website</a>")
    websiteLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    websiteLabel.setOpenExternalLinks(True)
    layout.addWidget(websiteLabel)

    docsLabel = QLabel()
    docsLabel.setText("<a href='https://gnipsel.com/linuxcnc/flexgui/index.html'>Documents</a>")
    docsLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    docsLabel.setOpenExternalLinks(True)
    layout.addWidget(docsLabel)

    repoLabel = QLabel()
    repoLabel.setText("<a href='https://github.com/jethornton/flexgui'>Code Website</a>")
    repoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    repoLabel.setOpenExternalLinks(True)
    layout.addWidget(repoLabel)

    videoLabel = QLabel()
    videoLabel.setText("<a href='https://www.youtube.com/@Gnipsel/videos'>Youtube Videos</a>")
    videoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    videoLabel.setOpenExternalLinks(True)
    layout.addWidget(videoLabel)

    from datetime import datetime

    year = datetime.today().year
    copyrightLabel = QLabel()
    copyrightLabel.setText(f"Copyright © 1953-{year} John Thornton")
    copyrightLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(copyrightLabel)

    layout.addStretch()

    buttonBox = QDialogButtonBox()
    buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)
    buttonBox.setCenterButtons(True)
    buttonBox.accepted.connect(dialog_box.close)
    layout.addWidget(buttonBox)

    dialog_box.exec()


def quick_reference_dialog(parent):
    dialog_box = QDialog()
    dialog_box.setMinimumSize(300, 300)
    dialog_box.setWindowTitle("Keyboard Shortcuts")

    layout = QVBoxLayout(dialog_box)

    titleLabel = QLabel()
    titleLabel.setText("FlexGUI")
    titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(titleLabel)

    shortcutsLabel = QLabel()
    if len(parent.shortcuts) > 0:
        shortcutsLabel.setText("  \n".join(parent.shortcuts))
    else:
        shortcutsLabel.setText("No Keyboard Shortcuts Found")
    layout.addWidget(shortcutsLabel)

    layout.addStretch()

    buttonBox = QDialogButtonBox()
    buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)
    buttonBox.setCenterButtons(True)
    buttonBox.accepted.connect(dialog_box.close)
    layout.addWidget(buttonBox)

    dialog_box.exec()


def help_dialog(parent):
    if parent.help_dialog is not None:
        if not parent.help_dialog.isVisible():
            parent.help_dialog = None
    if parent.help_dialog is None:
        btn = parent.sender()
        file_name = btn.property("file")
        help_file = os.path.join(parent.config_path, file_name)
        width = btn.property("horz_size") or 250
        if isinstance(width, str):
            width = int(width)
        height = btn.property("vert_size") or 250
        if isinstance(height, str):
            height = int(height)
        x_pos = btn.property("x_pos") or 100
        if isinstance(x_pos, str):
            x_pos = int(x_pos)
        y_pos = btn.property("y_pos") or 100
        if isinstance(y_pos, str):
            y_pos = int(y_pos)

        if os.path.isfile(help_file):
            parent.help_dialog = QDialog()
            parent.help_dialog.setWindowTitle(btn.property("topic"))
            parent.help_dialog.setGeometry(x_pos, y_pos, width, height)
            layout = QVBoxLayout(parent.help_dialog)
            text_edit = QPlainTextEdit()
            layout.addWidget(text_edit)
            with open(help_file) as f:
                lines = f.readlines()
            for line in lines:
                text_edit.appendPlainText(line.rstrip())

            # Create a cursor object
            cursor = text_edit.textCursor()
            # Move the cursor to the beginning of the document
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            # Set the cursor back to the text edit
            text_edit.setTextCursor(cursor)

            parent.help_dialog.show()
        else:
            msg = f"The help file {file_name}\nwas not found in the configuration directory\n{parent.config_path}"
            warn_msg_ok(parent, msg, "Missing File")
