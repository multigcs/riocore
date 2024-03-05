

from riocore.widgets import MyStandardItem

def load_tree(parent, tree_lcnc):
    bitem = MyStandardItem()
    tree_lcnc.appendRow(
        [
            MyStandardItem("Joypad", help_text="LinuxCNC Joypad-Setup"),
            bitem,
        ]
    )
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

