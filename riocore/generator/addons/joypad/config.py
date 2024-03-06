from PyQt5.QtWidgets import (
    QPushButton,
)

from riocore.widgets import MyStandardItem


def load_tree(parent, tree_lcnc):
    def add_joypad(widget):
        if not parent.config["linuxcnc"].get("joypad"):
            parent.config["linuxcnc"]["joypad"] = {
                "enable": False,
                "name": "Joypad",
                "btn_slow": "btn-base",
                "btn_medium": "btn-base2",
                "btn_fast": "btn-top",
            }
            parent.load_tree()
            parent.display()

    bitem = MyStandardItem()
    tree_lcnc.appendRow(
        [
            MyStandardItem("Joypad", help_text="LinuxCNC Joypad-Setup"),
            bitem,
        ]
    )

    button = QPushButton("add joypad")
    button.clicked.connect(add_joypad)
    button.setMaximumSize(button.sizeHint())
    parent.treeview.setIndexWidget(bitem.index(), button)

    tree_lcncjoypad = tree_lcnc.child(tree_lcnc.rowCount() - 1)
    if "joypad" not in parent.config["linuxcnc"]:
        parent.config["linuxcnc"]["joypad"] = {}
    joypad_config = parent.config["linuxcnc"]["joypad"]
    if joypad_config:
        joypad_buttons = ["btn-base", "btn-base2", "btn-top", "btn-top2"]
        for key, var_setup in {
            "enable": {"type": bool, "default": False},
            "name": {"type": str},
            "btn_slow": {"type": "select", "options": joypad_buttons},
            "btn_medium": {"type": "select", "options": joypad_buttons},
            "btn_fast": {"type": "select", "options": joypad_buttons},
        }.items():
            aitem = MyStandardItem()
            tree_lcncjoypad.appendRow(
                [
                    MyStandardItem(key.title()),
                    aitem,
                ]
            )
            parent.treeview.setIndexWidget(aitem.index(), parent.edit_item(joypad_config, key, var_setup))
