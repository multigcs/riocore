from PyQt5.QtWidgets import (
    QPushButton,
)

from riocore.widgets import MyStandardItem


def info():
    return {
        "title": "mxmpg",
        "url": "https://github.com/multigcs/linuxcnc-mpg",
        "comment": "mxmpg support",
    }


def load_tree(parent, tree_lcnc):
    def add_mxmpg(widget):
        if not parent.config["linuxcnc"].get("mxmpg"):
            parent.config["linuxcnc"]["mxmpg"] = {
                "enable": True,
            }
            parent.load_tree("/LinuxCNC/AddOn's/mxmpg/")
            parent.display()

    bitem = MyStandardItem()
    tree_lcnc.appendRow(
        [
            MyStandardItem("mxmpg", help_text="LinuxCNC MxMPG-Setup"),
            bitem,
        ]
    )

    if not parent.config.get("linuxcnc", {}).get("mxmpg"):
        parent.config["linuxcnc"]["mxmpg"] = {}
        button = QPushButton("add")
        button.clicked.connect(add_mxmpg)
        button.setMaximumSize(button.sizeHint())
        parent.treeview.setIndexWidget(bitem.index(), button)

    tree_lcncmxmpg = tree_lcnc.child(tree_lcnc.rowCount() - 1)
    mxmpg_config = parent.config["linuxcnc"]["mxmpg"]
    if mxmpg_config:
        for key, var_setup in {
            "enable": {"type": bool, "default": True},
            "device": {"type": str, "default": "/dev/ttyACM0"},
        }.items():
            aitem = MyStandardItem()
            tree_lcncmxmpg.appendRow(
                [
                    MyStandardItem(key.title()),
                    aitem,
                ]
            )
            parent.treeview.setIndexWidget(aitem.index(), parent.edit_item(mxmpg_config, key, var_setup))
