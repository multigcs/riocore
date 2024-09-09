from PyQt5.QtWidgets import (
    QPushButton,
)

from riocore.widgets import MyStandardItem


def info():
    return {
        "title": "hy_vfd",
        "url": "",
        "comment": "hy_vfd support",
    }


def load_tree(parent, tree_lcnc):
    def add_hy_vfd(widget):
        if not parent.config["linuxcnc"].get("hy_vfd"):
            parent.config["linuxcnc"]["hy_vfd"] = {
                "enable": False,
                "address": 1,
                "device": "/dev/ttyUSB0",
            }
            parent.load_tree("/LinuxCNC/AddOn's/hy_vfd/")
            parent.display()

    bitem = MyStandardItem()
    tree_lcnc.appendRow(
        [
            MyStandardItem("hy_vfd", help_text="LinuxCNC hy_vfd-Setup"),
            bitem,
        ]
    )

    if not parent.config.get("linuxcnc", {}).get("hy_vfd"):
        parent.config["linuxcnc"]["hy_vfd"] = {}
        button = QPushButton("add")
        button.clicked.connect(add_hy_vfd)
        button.setMaximumSize(button.sizeHint())
        parent.treeview.setIndexWidget(bitem.index(), button)

    tree_lcnchy_vfd = tree_lcnc.child(tree_lcnc.rowCount() - 1)
    hy_vfd_config = parent.config["linuxcnc"]["hy_vfd"]
    if hy_vfd_config:
        for key, var_setup in {
            "enable": {"type": bool, "default": False},
            "address": {"type": int, "default": 1, "min": 0, "max": 255},
            "baud": {"type": str, "default": "9600"},
            "device": {"type": "select", "options": ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0", "/dev/ttyACM1"]},
        }.items():
            aitem = MyStandardItem()
            tree_lcnchy_vfd.appendRow(
                [
                    MyStandardItem(key.title()),
                    aitem,
                ]
            )
            parent.treeview.setIndexWidget(aitem.index(), parent.edit_item(hy_vfd_config, key, var_setup))
