from functools import partial

from libflexgui import qss_toolbar


def startup(parent):
    # QToolButton
    parent.tb_normal = False

    parent.tb_apply_style.clicked.connect(partial(create_stylesheet, parent))
    parent.tb_clear_style.clicked.connect(partial(clear_stylesheet, parent))

    parent.tb_min_width_normal.valueChanged.connect(parent.size)
    parent.tb_min_height_normal.valueChanged.connect(parent.size)
    parent.tb_max_width_normal.valueChanged.connect(parent.size)
    parent.tb_max_height_normal.valueChanged.connect(parent.size)

    border_types = ["none", "solid", "dashed", "dotted", "double", "groove", "ridge", "inset", "outset"]
    pseudo_states = ["normal", "hover", "pressed", "checked", "disabled"]

    for item in pseudo_states:
        # populate border combo boxes
        getattr(parent, f"tb_border_type_{item}").addItems(border_types)
        # setup variables
        setattr(parent, f"tb_{item}", False)  # build section flag
        setattr(parent, f"tb_fg_color_sel_{item}", False)
        setattr(parent, f"tb_bg_color_sel_{item}", False)
        setattr(parent, f"tb_border_color_sel_{item}", False)

    for state in pseudo_states:  # color dialog connections
        getattr(parent, f"tb_fg_color_{state}").clicked.connect(parent.color_dialog)
        getattr(parent, f"tb_bg_color_{state}").clicked.connect(parent.color_dialog)
        getattr(parent, f"tb_border_color_{state}").clicked.connect(parent.color_dialog)

    parent.tb_font_picker.clicked.connect(parent.font_dialog)
    parent.tb_font_family = False
    parent.tb_font_size = False
    parent.tb_font_weight = False
    parent.tb_font_style = False
    parent.tb_font_italic = False

    parent.tb_padding_normal.valueChanged.connect(parent.padding)
    parent.tb_padding_left_normal.valueChanged.connect(parent.padding)
    parent.tb_padding_right_normal.valueChanged.connect(parent.padding)
    parent.tb_padding_top_normal.valueChanged.connect(parent.padding)
    parent.tb_padding_bottom_normal.valueChanged.connect(parent.padding)

    parent.tb_margin_normal.valueChanged.connect(parent.margin)
    parent.tb_margin_left_normal.valueChanged.connect(parent.margin)
    parent.tb_margin_right_normal.valueChanged.connect(parent.margin)
    parent.tb_margin_top_normal.valueChanged.connect(parent.margin)
    parent.tb_margin_bottom_normal.valueChanged.connect(parent.margin)


######### QToolButton Stylesheet #########


def create_stylesheet(parent):
    style = False

    # check for toolbar style set
    if parent.sender().objectName() == "tb_apply_style":
        if parent.tbar_normal:
            style = qss_toolbar.tbar_create_stylesheet(parent)

    # QToolButton normal pseudo-state
    if parent.tb_normal:
        if style:  # style is not False
            style += "QToolBar QToolButton {\n"
        else:
            style = "QToolBar QToolButton {\n"

        # color
        if parent.tb_fg_color_sel_normal:
            style += f"\tcolor: {parent.tb_fg_color_sel_normal};\n"
        if parent.tb_bg_color_sel_normal:
            style += f"\tbackground-color: {parent.tb_bg_color_sel_normal};\n"

        # size
        if parent.tb_min_width_normal.value() > 0:
            style += f"\tmin-width: {parent.tb_min_width_normal.value()}px;\n"
        if parent.tb_min_height_normal.value() > 0:
            style += f"\tmin-height: {parent.tb_min_height_normal.value()}px;\n"
        if parent.tb_max_width_normal.value() > 0:
            style += f"\tmax-width: {parent.tb_max_width_normal.value()}px;\n"
        if parent.tb_max_height_normal.value() > 0:
            style += f"\tmax-height: {parent.tb_max_height_normal.value()}px;\n"

        # border
        border_type_normal = parent.tb_border_type_normal.currentText()
        if border_type_normal != "none":
            style += f"\tborder-style: {border_type_normal};\n"
        if parent.tb_border_color_sel_normal:
            style += f"\tborder-color: {parent.tb_border_color_sel_normal};\n"
        if parent.tb_border_width_normal.value() > 0:
            style += f"\tborder-width: {parent.tb_border_width_normal.value()}px;\n"
        if parent.tb_border_radius_normal.value() > 0:
            style += f"\tborder-radius: {parent.tb_border_radius_normal.value()}px;\n"

        # font
        if parent.tb_font_family:
            style += f"\tfont-family: {parent.tb_font_family};\n"
        if parent.tb_font_size:
            style += f"\tfont-size: {parent.tb_font_size}pt;\n"
        if parent.tb_font_weight:
            style += f"\tfont-weight: {parent.tb_font_weight};\n"

        # padding
        if parent.tb_padding_normal.value() > 0:
            style += f"\tpadding: {parent.tb_padding_normal.value()};\n"
        if parent.tb_padding_left_normal.value() > 0:
            style += f"\tpadding-left: {parent.tb_padding_left_normal.value()};\n"
        if parent.tb_padding_right_normal.value() > 0:
            style += f"\tpadding-right: {parent.tb_padding_right_normal.value()};\n"
        if parent.tb_padding_top_normal.value() > 0:
            style += f"\tpadding-top: {parent.tb_padding_top_normal.value()};\n"
        if parent.tb_padding_bottom_normal.value() > 0:
            style += f"\tpadding-bottom: {parent.tb_padding_bottom_normal.value()};\n"

        # margin
        if parent.tb_margin_normal.value() > 0:
            style += f"\tmargin: {parent.tb_margin_normal.value()};\n"
        if parent.tb_margin_left_normal.value() > 0:
            style += f"\tmargin-left: {parent.tb_margin_left_normal.value()};\n"
        if parent.tb_margin_right_normal.value() > 0:
            style += f"\tmargin-right: {parent.tb_margin_right_normal.value()};\n"
        if parent.tb_margin_top_normal.value() > 0:
            style += f"\tmargin-top: {parent.tb_margin_top_normal.value()};\n"
        if parent.tb_margin_bottom_normal.value() > 0:
            style += f"\tmargin-bottom: {parent.tb_margin_bottom_normal.value()};\n"

        style += "}\n"  # End of QToolButton normal pseudo-state

    # QToolBar QToolButton hover pseudo-state
    if parent.tb_hover:
        # color
        if style:  # style is not False
            style += "\nQToolBar QToolButton:hover {\n"
        else:
            style = "\nQToolBar QToolButton:hover {\n"

        if parent.tb_fg_color_sel_hover:
            style += f"\tcolor: {parent.tb_fg_color_sel_hover};\n"
        if parent.tb_bg_color_sel_hover:
            style += f"\tbackground-color: {parent.tb_bg_color_sel_hover};\n"

        # border
        border_type_hover = parent.tb_border_type_hover.currentText()
        if border_type_hover != "none":
            style += f"\tborder-style: {border_type_hover};\n"
        if parent.tb_border_color_sel_hover:
            style += f"\tborder-color: {parent.tb_border_color_sel_hover};\n"
        if parent.tb_border_width_hover.value() > 0:
            style += f"\tborder-width: {parent.tb_border_width_hover.value()}px;\n"
        if parent.tb_border_radius_hover.value() > 0:
            style += f"\tborder-radius: {parent.tb_border_radius_hover.value()}px;\n"

        style += "}\n"  # End of QToolBar QToolButton hover pseudo-state

    # QToolBar QToolButton pressed pseudo-state
    # color
    if parent.tb_pressed:
        if style:  # style is not False
            style += "\n\nQToolBar QToolButton:pressed {\n"
        else:
            style = "\n\nQToolBar QToolButton:pressed {\n"

        if parent.tb_fg_color_sel_pressed:
            style += f"\tcolor: {parent.tb_fg_color_sel_pressed};\n"
        if parent.tb_bg_color_sel_pressed:
            style += f"\tbackground-color: {parent.tb_bg_color_sel_pressed};\n"

        # border
        border_type_pressed = parent.tb_border_type_pressed.currentText()
        if border_type_pressed != "none":
            style += f"\tborder-style: {border_type_pressed};\n"
        if parent.tb_border_color_sel_pressed:
            style += f"\tborder-color: {parent.tb_border_color_sel_pressed};\n"
        if parent.tb_border_width_pressed.value() > 0:
            style += f"\tborder-width: {parent.tb_border_width_pressed.value()}px;\n"
        if parent.tb_border_radius_pressed.value() > 0:
            style += f"\tborder-radius: {parent.tb_border_radius_pressed.value()}px;\n"

        style += "}\n"  # End of QToolBar QToolButton pressed pseudo-state

    # QToolBar QToolButton checked pseudo-state
    if parent.tb_checked:
        if style:  # style is not False
            style += "\n\nQToolBar QToolButton:checked {\n"
        else:
            style = "\n\nQToolBar QToolButton:checked {\n"

        # color
        if parent.tb_fg_color_sel_checked:
            style += f"\tcolor: {parent.tb_fg_color_sel_checked};\n"
        if parent.tb_bg_color_sel_checked:
            style += f"\tbackground-color: {parent.tb_bg_color_sel_checked};\n"

        # border
        border_type_checked = parent.tb_border_type_checked.currentText()
        if border_type_checked != "none":
            style += f"\tborder-style: {border_type_checked};\n"
        if parent.tb_border_color_sel_checked:
            style += f"\tborder-color: {parent.tb_border_color_sel_checked};\n"
        if parent.tb_border_width_checked.value() > 0:
            style += f"\tborder-width: {parent.tb_border_width_checked.value()}px;\n"
        if parent.tb_border_radius_checked.value() > 0:
            style += f"\tborder-radius: {parent.tb_border_radius_checked.value()}px;\n"

        style += "}\n"  # End of QToolBar QToolButton checked pseudo-state

    # QToolBar QToolButton disabled pseudo-state
    if parent.tb_disabled:
        if style:  # style is not False
            style += "\n\nQToolBar QToolButton:disabled {\n"
        else:
            style = "\n\nQToolBar QToolButton:disabled {\n"

        # color
        if parent.tb_fg_color_sel_disabled:
            style += f"\tcolor: {parent.tb_fg_color_sel_disabled};\n"
        if parent.tb_bg_color_sel_disabled:
            style += f"\tbackground-color: {parent.tb_bg_color_sel_disabled};\n"

        # border
        border_type_disabled = parent.tb_border_type_disabled.currentText()
        if border_type_disabled != "none":
            style += f"\tborder-style: {border_type_disabled};\n"
        if parent.tb_border_color_sel_disabled:
            style += f"\tborder-color: {parent.tb_border_color_sel_disabled};\n"
        if parent.tb_border_width_disabled.value() > 0:
            style += f"\tborder-width: {parent.tb_border_width_disabled.value()}px;\n"
        if parent.tb_border_radius_disabled.value() > 0:
            style += f"\tborder-radius: {parent.tb_border_radius_disabled.value()}px;\n"

        style += "}"  # End of QToolBar QToolButton disabled pseudo-state

    parent.tb_stylesheet.clear()
    if style:
        lines = style.splitlines()
        for line in lines:
            parent.tb_stylesheet.appendPlainText(line)

        parent.toolBar.setStyleSheet(style)

    if parent.sender().objectName() == "tbar_apply_style":
        return style


def clear_stylesheet(parent):
    parent.tb_normal = False

    pseudo_states = ["normal", "hover", "pressed", "checked", "disabled"]

    # set all the variables to False
    for item in pseudo_states:
        setattr(parent, f"tb_{item}", False)  # build section flag
        setattr(parent, f"tb_fg_color_sel_{item}", False)
        setattr(parent, f"tb_bg_color_sel_{item}", False)
        setattr(parent, f"tb_border_color_sel_{item}", False)

    # clear all the colors
    for item in pseudo_states:
        label = getattr(parent, f"tb_fg_color_{item}").property("label")
        getattr(parent, label).setStyleSheet("background-color: none;")
        label = getattr(parent, f"tb_bg_color_{item}").property("label")
        getattr(parent, label).setStyleSheet("background-color: none;")
        label = getattr(parent, f"tb_border_color_{item}").property("label")
        getattr(parent, label).setStyleSheet("background-color: none;")

    # set border to none and 0
    for item in pseudo_states:
        getattr(parent, f"tb_border_type_{item}").setCurrentIndex(0)
        getattr(parent, f"tb_border_width_{item}").setValue(0)
        getattr(parent, f"tb_border_radius_{item}").setValue(0)

    # clear the font variables
    parent.tb_font_family = False
    parent.tb_font_size = False
    parent.tb_font_weight = False
    parent.tb_font_style = False
    parent.tb_font_italic = False

    parent.tb_min_width_normal.setValue(0)
    parent.tb_min_height_normal.setValue(0)
    parent.tb_max_width_normal.setValue(0)
    parent.tb_max_height_normal.setValue(0)
    parent.tb_padding_normal.setValue(0)
    parent.tb_padding_left_normal.setValue(0)
    parent.tb_padding_right_normal.setValue(0)
    parent.tb_padding_top_normal.setValue(0)
    parent.tb_padding_top_normal.setValue(0)
    parent.tb_margin_normal.setValue(0)
    parent.tb_margin_left_normal.setValue(0)
    parent.tb_margin_right_normal.setValue(0)
    parent.tb_margin_top_normal.setValue(0)
    parent.tb_margin_top_normal.setValue(0)

    parent.tb_stylesheet.clear()
    parent.toolBar.setStyleSheet("")
