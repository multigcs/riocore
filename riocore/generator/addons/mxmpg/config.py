from PyQt5.QtWidgets import (
    QPushButton,
)

from riocore.gui.widgets import MyStandardItem

BUTTON_FUNCS = (
    "short",
    "long",
    "toggle",
    "toggle-on",
    "toggle-off",
    "long-toggle",
    "long-toggle-on",
    "long-toggle-off",
    "short-not",
    "long-not",
    "toggle-not",
    "long-toggle-not",
)

BUTTON_NAMES = (
    "01",
    "01b",
    "02",
    "03",
    "04",
    "05",
    #    "06", # internal used for scale
    #    "06b",
    "enc01",
    "enc02",
    "enc03",
    "estop",
    #    "sel01", # internal used for axis selection
    #    "sel02",
    #    "sel03",
    #    "sel04",
    #    "sel05",
    #    "sel06",
)

DEFAULTS = {
    "01-short": "halui.program.stop",
    "01-long": "halui.program.run",
    "01b-short": "halui.program.pause",
    "01b-long": "halui.program.resume",
    "02-short": "halui.spindle.0.stop",
    "02-long": "halui.spindle.0.start",
    "estop-short-not": "iocontrol.0.emc-enable-in",
}


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
        options = {
            "enable": {"type": bool, "default": True},
            "device": {"type": str, "default": "/dev/ttyACM0"},
        }
        for key, var_setup in options.items():
            aitem = MyStandardItem()
            tree_lcncmxmpg.appendRow(
                [
                    MyStandardItem(key.title()),
                    aitem,
                ]
            )
            parent.treeview.setIndexWidget(aitem.index(), parent.edit_item(mxmpg_config, key, var_setup))

        bitem = MyStandardItem()
        tree_lcncmxmpg.appendRow(
            [
                MyStandardItem("Buttons", help_text="buttons"),
                bitem,
            ]
        )
        tree_buttons = tree_lcncmxmpg.child(tree_lcncmxmpg.rowCount() - 1)
        if "buttons" not in parent.config["linuxcnc"]["mxmpg"]:
            parent.config["linuxcnc"]["mxmpg"]["buttons"] = {}
        mxmpg_buttons = parent.config["linuxcnc"]["mxmpg"]["buttons"]

        for button in BUTTON_NAMES:
            bitem = MyStandardItem()
            tree_buttons.appendRow(
                [
                    MyStandardItem(button, help_text=f"button {button}"),
                    bitem,
                ]
            )
            tree_button = tree_buttons.child(tree_buttons.rowCount() - 1)

            if button not in parent.config["linuxcnc"]["mxmpg"]["buttons"]:
                parent.config["linuxcnc"]["mxmpg"]["buttons"][button] = {}

            for bfunc in BUTTON_FUNCS:
                aitem = MyStandardItem()
                tree_button.appendRow(
                    [
                        MyStandardItem(bfunc),
                        aitem,
                    ]
                )
                options = {"type": str, "default": DEFAULTS.get(f"{button}-{bfunc}", "")}
                parent.treeview.setIndexWidget(aitem.index(), parent.edit_item(mxmpg_buttons[button], bfunc, options))
