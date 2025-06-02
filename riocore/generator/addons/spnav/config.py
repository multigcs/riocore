from PyQt5.QtWidgets import (
    QPushButton,
)

from riocore.gui.widgets import MyStandardItem


def info():
    return {
        "title": "Spacemouse",
        "url": "",
        "comment": "spacemouse jogging",
    }


def load_tree(parent, tree_lcnc):
    def add_spnav(widget):
        if not parent.config["linuxcnc"].get("spnav"):
            parent.config["linuxcnc"]["spnav"] = {
                "enable": True,
            }
            parent.load_tree("/LinuxCNC/AddOn's/Spacemouse/")
            parent.display()

    bitem = MyStandardItem()
    tree_lcnc.appendRow(
        [
            MyStandardItem("Spacemouse", help_text="LinuxCNC Spacemouse-Setup"),
            bitem,
        ]
    )

    if not parent.config.get("linuxcnc", {}).get("spnav"):
        parent.config["linuxcnc"]["spnav"] = {}
        button = QPushButton("add")
        button.clicked.connect(add_spnav)
        button.setMaximumSize(button.sizeHint())
        parent.treeview.setIndexWidget(bitem.index(), button)

    tree_lcncspnav = tree_lcnc.child(tree_lcnc.rowCount() - 1)
    spnav_config = parent.config["linuxcnc"]["spnav"]
    if spnav_config:
        for key, var_setup in {
            "enable": {"type": bool, "default": True},
            "jointjog": {"type": bool, "default": False},
            "x-scale": {"type": float, "default": -0.2},
            "y-scale": {"type": float, "default": -0.2},
            "z-scale": {"type": float, "default": 0.2},
            "a-scale": {"type": float, "default": 0.0},
            "b-scale": {"type": float, "default": 0.0},
            "c-scale": {"type": float, "default": 0.02},
            "botton-0": {"type": str, "default": ""},
            "botton-1": {"type": str, "default": ""},
        }.items():
            aitem = MyStandardItem()
            tree_lcncspnav.appendRow(
                [
                    MyStandardItem(key.title()),
                    aitem,
                ]
            )
            parent.treeview.setIndexWidget(aitem.index(), parent.edit_item(spnav_config, key, var_setup))
