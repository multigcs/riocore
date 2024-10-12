from PyQt5.QtWidgets import (
    QPushButton,
)

from riocore.widgets import MyStandardItem


def info():
    return {
        "title": "robojog",
        "url": "https://github.com/multigcs/linuxcnc-mpg",
        "comment": "robojog support",
    }


def load_tree(parent, tree_lcnc):
    def add_robojog(widget):
        if not parent.config["linuxcnc"].get("robojog"):
            parent.config["linuxcnc"]["robojog"] = {
                "enable": True,
            }
            parent.load_tree("/LinuxCNC/AddOn's/robojog/")
            parent.display()

    bitem = MyStandardItem()
    tree_lcnc.appendRow(
        [
            MyStandardItem("RoboJog", help_text="LinuxCNC robojog-Setup"),
            bitem,
        ]
    )

    if not parent.config.get("linuxcnc", {}).get("robojog"):
        parent.config["linuxcnc"]["robojog"] = {}
        button = QPushButton("add")
        button.clicked.connect(add_robojog)
        button.setMaximumSize(button.sizeHint())
        parent.treeview.setIndexWidget(bitem.index(), button)

    tree_lcncrobojog = tree_lcnc.child(tree_lcnc.rowCount() - 1)
    robojog_config = parent.config["linuxcnc"]["robojog"]
    if robojog_config:
        for key, var_setup in {
            "enable": {"type": bool, "default": False},
            "tabname": {"type": str, "default": "RoboJog"},
        }.items():
            aitem = MyStandardItem()
            tree_lcncrobojog.appendRow(
                [
                    MyStandardItem(key.title()),
                    aitem,
                ]
            )
            parent.treeview.setIndexWidget(aitem.index(), parent.edit_item(robojog_config, key, var_setup))
