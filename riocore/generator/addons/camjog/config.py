from functools import partial
from PyQt5.QtWidgets import (
    QPushButton,
)

from riocore.widgets import MyStandardItem


def info():
    return {
        "title": "CamJog",
        "url": "",
        "comment": "camjog support",
    }


def load_tree(parent, tree_lcnc):
    def add_camjog(widget):
        if "camjog" not in parent.config["linuxcnc"]:
            parent.config["linuxcnc"]["camjog"] = []
        camjog_config = parent.config["linuxcnc"]["camjog"]
        camjog_num = len(camjog_config)
        camjog_config.append(
            {
                "enable": False,
                "device": f"/dev/video{camjog_num}",
                "tabname": f"camjog-{camjog_num}",
                "width": "640",
                "height": "480",
            }
        )
        parent.load_tree("/LinuxCNC/AddOn's/camjog/")
        parent.display()

    def del_camjog(camjog_num, misc):
        parent.config["linuxcnc"]["camjog"].pop(camjog_num)
        parent.load_tree()
        parent.display()

    bitem = MyStandardItem()
    tree_lcnc.appendRow(
        [
            MyStandardItem("camjog", help_text="LinuxCNC camjog-Setup"),
            bitem,
        ]
    )

    button = QPushButton("add")
    button.clicked.connect(add_camjog)
    button.setMaximumSize(button.sizeHint())
    parent.treeview.setIndexWidget(bitem.index(), button)

    tree_lcnccamjog = tree_lcnc.child(tree_lcnc.rowCount() - 1)
    if "camjog" not in parent.config["linuxcnc"]:
        parent.config["linuxcnc"]["camjog"] = []
    camjog_config = parent.config["linuxcnc"]["camjog"]
    for camjog_num, camjog in enumerate(camjog_config):
        bitem = MyStandardItem()
        tree_lcnccamjog.appendRow(
            [
                MyStandardItem(f"CamJog {camjog_num}", help_text=f"camjog {camjog_num} Setup"),
                bitem,
            ]
        )
        del_button = QPushButton("del camjog")
        cb = partial(del_camjog, camjog_num)
        del_button.clicked.connect(cb)
        del_button.setMaximumSize(button.sizeHint())

        parent.treeview.setIndexWidget(bitem.index(), del_button)
        tree_lcnccamjog_n = tree_lcnccamjog.child(tree_lcnccamjog.rowCount() - 1)

        for key, var_setup in {
            "enable": {"type": bool, "default": False},
            "device": {"type": "str", "default": f"/dev/video{camjog_num}"},
            "tabname": {"type": str, "default": f"camjog-{camjog_num}"},
            "width": {"type": int, "default": 640},
            "height": {"type": int, "default": 480},
            "scale": {"type": float, "default": 1.0},
        }.items():
            aitem = MyStandardItem()
            tree_lcnccamjog_n.appendRow(
                [
                    MyStandardItem(key.title()),
                    aitem,
                ]
            )
            parent.treeview.setIndexWidget(aitem.index(), parent.edit_item(camjog, key, var_setup))

        bitem = MyStandardItem()
        tree_lcnccamjog_n.appendRow(
            [
                MyStandardItem("Offset", help_text="camjog offsets"),
                bitem,
            ]
        )
        tree_lcnccamjog_n_offsets = tree_lcnccamjog_n.child(tree_lcnccamjog_n.rowCount() - 1)
        if "offset" not in camjog:
            camjog["offset"] = {}

        for offset_axis, offset_var_setup in {
            "X": {"type": int, "default": 0},
            "Y": {"type": int, "default": 0},
            "Z": {"type": int, "default": 0},
            "A": {"type": int, "default": 0},
            "B": {"type": int, "default": 0},
            "C": {"type": int, "default": 0},
            "U": {"type": int, "default": 0},
            "V": {"type": int, "default": 0},
            "W": {"type": int, "default": 0},
        }.items():
            aitem = MyStandardItem()
            tree_lcnccamjog_n_offsets.appendRow(
                [
                    MyStandardItem(offset_axis),
                    aitem,
                ]
            )
            parent.treeview.setIndexWidget(aitem.index(), parent.edit_item(camjog["offset"], offset_axis, offset_var_setup))
