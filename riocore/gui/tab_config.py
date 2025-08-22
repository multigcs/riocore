import os

import riocore

from PyQt5.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)

riocore_path = os.path.dirname(riocore.__file__)


class TabConfig:
    def __init__(self, parent=None):
        def update(value):
            self.parent.display()

        self.parent = parent
        self.gui_widget = QWidget()

        self.layout = QVBoxLayout()
        self.gui_widget.setLayout(self.layout)

        self.layout.addWidget(QLabel("Name:"))
        self.name_widget = self.parent.edit_item(self.parent.config, "name", {"type": str}, cb=update)
        self.layout.addWidget(self.name_widget)

        self.layout.addWidget(QLabel("Description:"))
        self.description_widget = self.parent.edit_item(self.parent.config, "description", {"type": str}, cb=update)
        self.layout.addWidget(self.description_widget)

        self.layout.addWidget(QLabel("Toolchain:"))
        self.toolchain_widget = self.parent.edit_item(self.parent.config, "toolchain", {"type": "select", "options": []}, cb=update)
        self.layout.addWidget(self.toolchain_widget)

        self.layout.addWidget(QLabel("Protocol:"))
        self.protocol_widget = self.parent.edit_item(self.parent.config, "protocol", {"type": "select", "options": []}, cb=update)
        self.layout.addWidget(self.protocol_widget)

        self.layout.addStretch()

    def widget(self):
        return self.gui_widget

    def timer(self):
        pass

    def update(self):
        self.name_widget.no_update = True
        self.description_widget.no_update = True
        self.toolchain_widget.no_update = True
        self.protocol_widget.no_update = True

        self.name_widget.obj = self.parent.config
        self.description_widget.obj = self.parent.config
        self.toolchain_widget.obj = self.parent.config
        self.protocol_widget.obj = self.parent.config

        board_config = self.parent.board
        config_name = self.parent.config["name"]
        config_description = self.parent.config.get("description")
        toolchain = self.parent.config.get("toolchain") or board_config.get("toolchain")
        toolchains = board_config.get("toolchains", [toolchain])
        protocol = self.parent.config.get("protocol") or "UDP"
        protocols = ("SPI", "UDP", "UART")

        if "toolchain" not in self.parent.config:
            self.parent.config["toolchain"] = toolchain
        if "protocol" not in self.parent.config:
            self.parent.config["protocol"] = "SPI"
        if "description" not in self.parent.config:
            self.parent.config["description"] = ""

        self.name_widget.setText(config_name)
        self.description_widget.setText(config_description)

        self.toolchain_widget.clear()
        for option in toolchains:
            self.toolchain_widget.addItem(option)
        self.toolchain_widget.setCurrentIndex(toolchains.index(toolchain))

        self.protocol_widget.clear()
        for option in protocols:
            self.protocol_widget.addItem(option)
        self.protocol_widget.setCurrentIndex(protocols.index(protocol))

        self.name_widget.no_update = False
        self.description_widget.no_update = False
        self.toolchain_widget.no_update = False
        self.protocol_widget.no_update = False
