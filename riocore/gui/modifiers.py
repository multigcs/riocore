from functools import partial

from riocore.modifiers import Modifiers

from riocore.gui.widgets import (
    STYLESHEET,
)


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QHeaderView,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


class GuiModifiers:
    def __init__(self, parent):
        self.parent = parent

    def add_modifier(self, parent, pin_setup):
        if "modifier" not in pin_setup:
            pin_setup["modifier"] = []
        modifier_id = len(pin_setup.get("modifier", []))
        pin_setup["modifier"].append({"type": "invert"})
        modifier = pin_setup["modifier"][-1]
        self.parent.tree_add_modifier(parent, pin_setup, modifier_id, modifier)
        self.parent.display()

    def edit_modifier(self, modifier_list, modifier_id, parent_layout=None):
        def update():
            mods = []
            for modifier_id, modifier in enumerate(modifier_list):
                modifier_type = modifier.get("type", "???")
                if dialog.modifier_id == modifier_id:
                    mods.append(modifier_type.upper())
                else:
                    mods.append(modifier_type)
            dialog.mlabel.setText(f"Chain: {'>'.join(mods)}")

        def remove_modifier():
            modifier_list.pop(dialog.modifier_id)
            if parent_layout:
                self.modifier_list_update(parent_layout, modifier_list)
            dialog.close()

        def move_left():
            if dialog.modifier_id > 0:
                modifier_list[dialog.modifier_id - 1], modifier_list[dialog.modifier_id] = modifier_list[dialog.modifier_id], modifier_list[dialog.modifier_id - 1]
                if parent_layout:
                    self.modifier_list_update(parent_layout, modifier_list)
                dialog.modifier_id -= 1
                update()

        def move_right():
            if dialog.modifier_id < len(modifier_list) - 1:
                modifier_list[dialog.modifier_id + 1], modifier_list[dialog.modifier_id] = modifier_list[dialog.modifier_id], modifier_list[dialog.modifier_id + 1]
                if parent_layout:
                    self.modifier_list_update(parent_layout, modifier_list)
                dialog.modifier_id += 1
                update()

        dialog = QDialog()
        dialog.setWindowTitle("edit Modifier")
        dialog.setStyleSheet(STYLESHEET)
        dialog.modifier_id = modifier_id
        modifier_config = modifier_list[dialog.modifier_id]
        modifier_type = modifier_config.get("type", "???")

        dialog.layout = QVBoxLayout()
        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)

        remove_button = QPushButton(self.parent.tr("Remove"))
        remove_button.clicked.connect(remove_modifier)
        dialog_buttonBox.addButton(remove_button, QDialogButtonBox.ActionRole)

        if len(modifier_list) > 1:
            move_button = QPushButton(self.parent.tr("<<"))
            move_button.clicked.connect(move_left)
            dialog_buttonBox.addButton(move_button, QDialogButtonBox.ActionRole)

            move_button = QPushButton(self.parent.tr(">>"))
            move_button.clicked.connect(move_right)
            dialog_buttonBox.addButton(move_button, QDialogButtonBox.ActionRole)

        dialog.layout.addWidget(QLabel(f"Type: {modifier_type}"))

        moptions = Modifiers().info()
        if modifier_type in moptions:
            for key, option in moptions[modifier_type].get("options", {}).items():
                dialog.layout.addWidget(QLabel(option.get("title", key.title())))
                dialog.layout.addWidget(self.parent.edit_item(modifier_config, key, option, cb=None))

        dialog.mlabel = QLabel("")
        dialog.layout.addWidget(dialog.mlabel)
        update()

        dialog.layout.addWidget(dialog_buttonBox)
        dialog.setLayout(dialog.layout)

        if dialog.exec():
            modifier_list[dialog.modifier_id] = modifier_config

    def modifier_list_add(self, parent_layout, modifier_list):
        modifiers = Modifiers()
        dialog = QDialog()
        dialog.setWindowTitle("add Modifier")
        dialog.setStyleSheet(STYLESHEET)
        dialog_buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        dialog_buttonBox.accepted.connect(dialog.accept)

        def show_modifier_info(row):
            modifier_type = modifier_table.item(row, 0).text()
            info = modifiers.info().get(modifier_type)
            infotext = info.get("info", "")
            options = info.get("options", "")
            title = info.get("title", modifier_type.title())
            dialog.label.setText(f"Modifier: {title}")
            textlines = ["", infotext, ""]

            if options:
                textlines.append("Options:")
                for key, option in options.items():
                    title = option.get("title", key.title())
                    default = option.get("default", "")
                    oinfo = option.get("help_text", "")
                    textlines.append(f" {title}: {oinfo} (default: {default})")

            dialog.info.setText("\n".join(textlines))

        dialog.layout = QHBoxLayout()
        modifier_table = QTableWidget()
        modifier_table.setColumnCount(1)
        modifier_table.setHorizontalHeaderItem(0, QTableWidgetItem("Modifier"))
        header = modifier_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        modifier_n = 0
        for modifier_name in modifiers.pin_modifier_list():
            modifier_table.setRowCount(modifier_n + 1)
            pitem = QTableWidgetItem(modifier_name)
            modifier_table.setItem(modifier_n, 0, pitem)
            modifier_n += 1

        modifier_table.currentCellChanged.connect(show_modifier_info)
        modifier_table.setFixedWidth(200)
        dialog.layout.addWidget(modifier_table, stretch=1)

        dialog.vlayout = QVBoxLayout()
        dialog.label = QLabel("Modifier-Info:")
        dialog.vlayout.addWidget(dialog.label, stretch=0)
        dialog.info = QLabel("...")
        dialog.info.setWordWrap(True)
        dialog.info.setFixedWidth(300)
        dialog.info.setAlignment(Qt.AlignTop)
        dialog.vlayout.addWidget(dialog.info, stretch=1)
        dialog.layout.addLayout(dialog.vlayout)
        dialog.vlayout.addWidget(dialog_buttonBox)
        dialog.setLayout(dialog.layout)

        if dialog.exec():
            row = modifier_table.currentRow()
            modifier_type = modifier_table.item(row, 0).text()
            modifier_list.append({"type": modifier_type})
            self.modifier_list_update(parent_layout, modifier_list)
            if modifier_type != "invert":
                self.edit_modifier(modifier_list, len(modifier_list) - 1, parent_layout)

    def modifier_list_update(self, parent_layout, modifier_list):
        pc = parent_layout.count()
        for i in reversed(range(pc)):
            parent_layout.itemAt(i).widget().setParent(None)

        for modifier_id, modifier in enumerate(modifier_list):
            modifier_type = modifier.get("type", "???")
            modifier_button = QPushButton(modifier_type)
            modifier_button.clicked.connect(partial(self.edit_modifier, modifier_list, modifier_id, parent_layout))
            modifier_button.setFixedWidth(len(modifier_type) * 9 + 10)
            parent_layout.addWidget(modifier_button, stretch=1)
