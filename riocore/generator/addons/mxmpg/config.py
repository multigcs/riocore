from PyQt5.QtWidgets import (
    QPushButton,
)

from riocore.widgets import MyStandardItem


def load_tree(parent, tree_lcnc):
    def add_mxmpg(widget):
        if not parent.config["linuxcnc"].get("mxmpg"):
            parent.config["linuxcnc"]["mxmpg"] = {
                "enable": False,
            }
            parent.load_tree()
            parent.display()

    bitem = MyStandardItem()
    tree_lcnc.appendRow(
        [
            MyStandardItem("mxmpg", help_text="LinuxCNC MxMPG-Setup"),
            bitem,
        ]
    )

    if "mxmpg" not in parent.config["linuxcnc"]:
        parent.config["linuxcnc"]["mxmpg"] = {}
        button = QPushButton("add")
        button.clicked.connect(add_mxmpg)
        button.setMaximumSize(button.sizeHint())
        parent.treeview.setIndexWidget(bitem.index(), button)

    tree_lcncmxmpg = tree_lcnc.child(tree_lcnc.rowCount() - 1)
    mxmpg_config = parent.config["linuxcnc"]["mxmpg"]
    if mxmpg_config:
        for key, var_setup in {
            "enable": {"type": bool, "default": False},
        }.items():
            aitem = MyStandardItem()
            tree_lcncmxmpg.appendRow(
                [
                    MyStandardItem(key.title()),
                    aitem,
                ]
            )
            parent.treeview.setIndexWidget(aitem.index(), parent.edit_item(mxmpg_config, key, var_setup))
