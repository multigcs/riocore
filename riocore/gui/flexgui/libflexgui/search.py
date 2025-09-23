from PyQt5.QtWidgets import QDialog, QGridLayout
from PyQt5.QtWidgets import QLabel, QLineEdit, QCheckBox, QPushButton
from PyQt5.QtGui import QTextDocument


class FindDialog(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle("Find")
        layout = QGridLayout(self)
        label = QLabel("Find Text:")
        layout.addWidget(label, 0, 0)
        self.lineEdit = QLineEdit()
        layout.addWidget(self.lineEdit, 0, 1)
        self.caseSensitive = QCheckBox("Case Sensitive")
        layout.addWidget(self.caseSensitive, 1, 0)
        self.wholeWord = QCheckBox("Whole Word")
        layout.addWidget(self.wholeWord, 1, 1)
        self.wrap_around = QCheckBox("Wrap Around")
        layout.addWidget(self.wrap_around, 2, 0)
        self.closeButton = QPushButton("Close")
        layout.addWidget(self.closeButton, 2, 1)
        self.findForward = QPushButton("Find Forward")
        self.findForward.setObjectName("forward_search")
        layout.addWidget(self.findForward, 3, 1)
        self.findBackward = QPushButton("Find Backward")
        self.findBackward.setObjectName("backward_search")
        layout.addWidget(self.findBackward, 3, 0)

        self.findForward.clicked.connect(self.find_text)
        self.findBackward.clicked.connect(self.find_text)
        self.closeButton.clicked.connect(self.close)
        self.text_edit = parent.gcode_pte

    def find_text(self):
        senderName = self.sender().objectName()
        flags = False
        flagList = []
        if senderName == "backward_search":
            flagList.append("bs")
            flags = QTextDocument.FindFlag.FindBackward
        if self.caseSensitive.isChecked():
            flagList.append("cs")
            flags = QTextDocument.FindFlag.FindCaseSensitively
        if self.wholeWord.isChecked():
            flagList.append("ww")
            flags = QTextDocument.FindFlag.FindWholeWords

        match flagList:
            case ["bs", "cs", "ww"]:
                flags = QTextDocument.FindFlag.FindWholeWords | QTextDocument.FindFlag.FindCaseSensitively | QTextDocument.FindFlag.FindBackward
            case ["bs", "cs"]:
                flags = QTextDocument.FindFlag.FindCaseSensitively | QTextDocument.FindFlag.FindBackward
            case ["bs", "ww"]:
                flags = QTextDocument.FindFlag.FindWholeWords | QTextDocument.FindFlag.FindBackward
            case ["cs", "ww"]:
                flags = QTextDocument.FindFlag.FindWholeWords | QTextDocument.FindFlag.FindCaseSensitively

        text_to_find = self.lineEdit.text()
        if text_to_find:
            if flags:
                if self.text_edit.find(text_to_find, flags):
                    return
                else:
                    self.lineEdit.clear()
                    self.lineEdit.setPlaceholderText("Not found.")
            else:
                if self.text_edit.find(text_to_find):
                    return
                else:
                    self.lineEdit.clear()
                    self.lineEdit.setPlaceholderText("Not found.")
