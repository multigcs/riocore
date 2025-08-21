import json
import difflib

from PyQt5.QtGui import QColor, QTextCursor
from PyQt5.QtWidgets import (
    QPlainTextEdit,
)


class TabJson:
    def __init__(self, parent=None, diff_only=True, line_numbers=True):
        self.parent = parent
        self.jsondiff = QPlainTextEdit()
        self.jsondiff.clear()
        self.jsondiff.insertPlainText("...")
        self.diff_only = diff_only
        self.line_numbers = line_numbers

    def widget(self):
        return self.jsondiff

    def timer(self):
        pass

    def update(self):
        config = json.dumps(self.parent.clean_config(self.parent.config), indent=4)
        config_original = json.dumps(self.parent.clean_config(self.parent.config_original), indent=4)
        self.jsondiff.clear()
        differ = difflib.Differ()
        color_format = self.jsondiff.currentCharFormat()
        default_color = color_format.foreground()
        last_lines = []
        show_next = 0
        diffs = False
        for line_n, line in enumerate(differ.compare(config_original.split("\n"), config.split("\n"))):
            marker = line[0]
            show = True
            if marker == "-":
                color = QColor(155, 0, 0)
                cursor = self.jsondiff.textCursor()
                cursor.movePosition(QTextCursor.End)
                self.jsondiff.setTextCursor(cursor)
                diffs = True
            elif marker == "+":
                color = QColor(0, 155, 0)
                cursor = self.jsondiff.textCursor()
                cursor.movePosition(QTextCursor.End)
                self.jsondiff.setTextCursor(cursor)
                diffs = True
            elif marker == "?":
                continue
            else:
                color = default_color
                if self.diff_only:
                    show = False
            if show:
                if last_lines:
                    for lline in last_lines[-3:]:
                        self.jsondiff.insertPlainText(lline)
                    last_lines = []
                    show_next = 3
                color_format.setForeground(color)
                self.jsondiff.setCurrentCharFormat(color_format)
                if self.line_numbers:
                    self.jsondiff.insertPlainText(f"{line_n} ")
                self.jsondiff.insertPlainText(f"{line}\n")
            else:
                color_format.setForeground(color)
                self.jsondiff.setCurrentCharFormat(color_format)
                if show_next:
                    if self.line_numbers:
                        self.jsondiff.insertPlainText(f"{line_n} ")
                    self.jsondiff.insertPlainText(f"{line}\n")
                    show_next -= 1
                    if show_next == 0:
                        self.jsondiff.insertPlainText("-----------\n")
                if self.line_numbers:
                    last_lines.append(f"{line_n} {line}\n")
                else:
                    last_lines.append(f"{line}\n")
        if self.diff_only and not diffs:
            self.jsondiff.insertPlainText("--- NO CHANGES ---\n")
