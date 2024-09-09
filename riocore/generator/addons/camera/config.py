from functools import partial
from PyQt5.QtWidgets import (
    QPushButton,
)

from riocore.widgets import MyStandardItem


def info():
    return {
        "title": "camera",
        "url": "",
        "comment": "camera support",
    }


def load_tree(parent, tree_lcnc):
    def add_camera(widget):
        if "camera" not in parent.config["linuxcnc"]:
            parent.config["linuxcnc"]["camera"] = []
        camera_config = parent.config["linuxcnc"]["camera"]
        camera_num = len(camera_config)
        camera_config.append(
            {
                "enable": False,
                "device": f"/dev/video{camera_num}",
                "tabname": f"Camera-{camera_num}",
            }
        )
        parent.load_tree("/LinuxCNC/AddOn's/Camera/")
        parent.display()

    def del_camera(camera_num, misc):
        parent.config["linuxcnc"]["camera"].pop(camera_num)
        parent.load_tree()
        parent.display()

    bitem = MyStandardItem()
    tree_lcnc.appendRow(
        [
            MyStandardItem("Camera", help_text="LinuxCNC Camera-Setup"),
            bitem,
        ]
    )

    button = QPushButton("add")
    button.clicked.connect(add_camera)
    button.setMaximumSize(button.sizeHint())
    parent.treeview.setIndexWidget(bitem.index(), button)

    tree_lcnccamera = tree_lcnc.child(tree_lcnc.rowCount() - 1)
    if "camera" not in parent.config["linuxcnc"]:
        parent.config["linuxcnc"]["camera"] = []
    camera_config = parent.config["linuxcnc"]["camera"]
    for camera_num, camera in enumerate(camera_config):
        bitem = MyStandardItem()
        tree_lcnccamera.appendRow(
            [
                MyStandardItem(f"Camera {camera_num}", help_text=f"Camera {camera_num} Setup"),
                bitem,
            ]
        )
        del_button = QPushButton("del camera")
        cb = partial(del_camera, camera_num)
        del_button.clicked.connect(cb)
        del_button.setMaximumSize(button.sizeHint())

        parent.treeview.setIndexWidget(bitem.index(), del_button)
        tree_lcnccamera_n = tree_lcnccamera.child(tree_lcnccamera.rowCount() - 1)

        for key, var_setup in {
            "enable": {"type": bool, "default": False},
            "device": {"type": "str", "default": f"/dev/video{camera_num}"},
            "tabname": {"type": str, "default": f"Camera-{camera_num}"},
        }.items():
            aitem = MyStandardItem()
            tree_lcnccamera_n.appendRow(
                [
                    MyStandardItem(key.title()),
                    aitem,
                ]
            )
            parent.treeview.setIndexWidget(aitem.index(), parent.edit_item(camera, key, var_setup))

        bitem = MyStandardItem()
        tree_lcnccamera_n.appendRow(
            [
                MyStandardItem("Offset", help_text="Camera offsets"),
                bitem,
            ]
        )
        tree_lcnccamera_n_offsets = tree_lcnccamera_n.child(tree_lcnccamera_n.rowCount() - 1)
        if "offset" not in camera:
            camera["offset"] = {}

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
            tree_lcnccamera_n_offsets.appendRow(
                [
                    MyStandardItem(offset_axis),
                    aitem,
                ]
            )
            parent.treeview.setIndexWidget(aitem.index(), parent.edit_item(camera["offset"], offset_axis, offset_var_setup))
