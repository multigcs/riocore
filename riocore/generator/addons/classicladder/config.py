from PyQt5.QtWidgets import (
    QPushButton,
)

from riocore.widgets import MyStandardItem


def load_tree(parent, tree_lcnc):
    def add_classicladder(widget):
        if not parent.config["linuxcnc"].get("classicladder"):
            parent.config["linuxcnc"]["classicladder"] = {
                "enable": False,
            }
            parent.load_tree()
            parent.display()

    bitem = MyStandardItem()
    tree_lcnc.appendRow(
        [
            MyStandardItem("classicladder", help_text="LinuxCNC classicladder-Setup"),
            bitem,
        ]
    )

    button = QPushButton("add classicladder")
    button.clicked.connect(add_classicladder)
    button.setMaximumSize(button.sizeHint())
    parent.treeview.setIndexWidget(bitem.index(), button)

    tree_lcncclassicladder = tree_lcnc.child(tree_lcnc.rowCount() - 1)
    if "classicladder" not in parent.config["linuxcnc"]:
        parent.config["linuxcnc"]["classicladder"] = {}
    classicladder_config = parent.config["linuxcnc"]["classicladder"]
    if classicladder_config:
        for key, var_setup in {
            "enable": {"type": bool, "default": False},
        }.items():
            aitem = MyStandardItem()
            tree_lcncclassicladder.appendRow(
                [
                    MyStandardItem(key.title()),
                    aitem,
                ]
            )
            parent.treeview.setIndexWidget(aitem.index(), parent.edit_item(classicladder_config, key, var_setup))
