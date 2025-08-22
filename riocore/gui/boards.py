import os

import riocore

from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
)

riocore_path = os.path.dirname(riocore.__file__)


class GuiBoards:
    def __init__(self, parent):
        self.parent = parent

    def edit_board(self):
        def update():
            pass

        def update_rotate(value):
            self.parent.board["rotate"] = int(value)
            self.parent.display()

        board_config = self.parent.board
        toolchain = self.parent.config.get("toolchain") or board_config.get("toolchain")
        toolchains = board_config.get("toolchains", [toolchain])
        protocol = self.parent.config.get("protocol") or "SPI"
        protocols = ["SPI", "UDP", "UART"]

        dialog = QDialog()
        dialog.setWindowTitle("edit board")
        if hasattr(self.parent, "STYLESHEET"):
            dialog.setStyleSheet(self.parent.STYLESHEET)

        dialog.layout = QVBoxLayout()
        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)

        dialog.layout.addWidget(QLabel("Name:"))
        dialog.layout.addWidget(self.parent.edit_item(self.parent.config, "name", {"type": str}, cb=None))

        dialog.layout.addWidget(QLabel("Description:"))
        dialog.layout.addWidget(self.parent.edit_item(self.parent.config, "description", {"type": str}, cb=None))

        dialog.layout.addWidget(QLabel("Toolchain:"))
        dialog.layout.addWidget(self.parent.edit_item(self.parent.config, "toolchain", {"type": "select", "options": toolchains, "default": toolchain}, cb=None))

        dialog.layout.addWidget(QLabel("Protocol:"))
        dialog.layout.addWidget(self.parent.edit_item(self.parent.config, "protocol", {"type": "select", "options": protocols, "default": protocol}, cb=None))

        dialog.mlabel = QLabel("")
        dialog.layout.addWidget(dialog.mlabel)
        update()

        dialog.layout.addWidget(dialog_buttonBox)
        dialog.setLayout(dialog.layout)

        if dialog.exec():
            pass
