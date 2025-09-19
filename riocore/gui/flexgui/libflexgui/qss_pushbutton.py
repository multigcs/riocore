from functools import partial


def startup(parent):
    # QPushButton
    parent.pb_normal = False

    parent.pb_apply_style.clicked.connect(partial(create_stylesheet, parent))
    parent.pb_clear_style.clicked.connect(partial(clear_stylesheet, parent))

    parent.pb_set_checkable.released.connect(parent.set_checkable)
    parent.pb_disable.clicked.connect(partial(parent.disable, "pushButton"))

    parent.pb_min_width_normal.valueChanged.connect(parent.size)
    parent.pb_min_height_normal.valueChanged.connect(parent.size)
    parent.pb_max_width_normal.valueChanged.connect(parent.size)
    parent.pb_max_height_normal.valueChanged.connect(parent.size)

    border_types = ["none", "solid", "dashed", "dotted", "double", "groove", "ridge", "inset", "outset"]
    pseudo_states = ["normal", "hover", "pressed", "checked", "disabled"]

    for item in pseudo_states:
        # populate border combo boxes
        getattr(parent, f"pb_border_type_{item}").addItems(border_types)
        # setup variables
        setattr(parent, f"pb_{item}", False)  # build section flag
        setattr(parent, f"pb_fg_color_sel_{item}", False)
        setattr(parent, f"pb_bg_color_sel_{item}", False)
        setattr(parent, f"pb_border_color_sel_{item}", False)

    for state in pseudo_states:  # color dialog connections
        getattr(parent, f"pb_fg_color_{state}").clicked.connect(parent.color_dialog)
        getattr(parent, f"pb_bg_color_{state}").clicked.connect(parent.color_dialog)
        getattr(parent, f"pb_border_color_{state}").clicked.connect(parent.color_dialog)

    parent.pb_font_picker.clicked.connect(parent.font_dialog)
    parent.pb_font_family = False
    parent.pb_font_size = False
    parent.pb_font_weight = False
    parent.pb_font_style = False
    parent.pb_font_italic = False

    parent.pb_padding_normal.valueChanged.connect(parent.padding)
    parent.pb_padding_left_normal.valueChanged.connect(parent.padding)
    parent.pb_padding_right_normal.valueChanged.connect(parent.padding)
    parent.pb_padding_top_normal.valueChanged.connect(parent.padding)
    parent.pb_padding_bottom_normal.valueChanged.connect(parent.padding)

    parent.pb_margin_normal.valueChanged.connect(parent.margin)
    parent.pb_margin_left_normal.valueChanged.connect(parent.margin)
    parent.pb_margin_right_normal.valueChanged.connect(parent.margin)
    parent.pb_margin_top_normal.valueChanged.connect(parent.margin)
    parent.pb_margin_bottom_normal.valueChanged.connect(parent.margin)


######### QPushButton Stylesheet #########


def create_stylesheet(parent):
    style = False

    # QPushButton normal pseudo-state
    if parent.pb_normal:
        style = "QPushButton {\n"

        # color
        if parent.pb_fg_color_sel_normal:
            style += f"\tcolor: {parent.pb_fg_color_sel_normal};\n"
        if parent.pb_bg_color_sel_normal:
            style += f"\tbackground-color: {parent.pb_bg_color_sel_normal};\n"

        # font
        if parent.pb_font_family:
            style += f"\tfont-family: {parent.pb_font_family};\n"
        if parent.pb_font_size:
            style += f"\tfont-size: {parent.pb_font_size}pt;\n"
        if parent.pb_font_weight:
            style += f"\tfont-weight: {parent.pb_font_weight};\n"

        # size
        if parent.pb_min_width_normal.value() > 0:
            style += f"\tmin-width: {parent.pb_min_width_normal.value()}px;\n"
        if parent.pb_min_height_normal.value() > 0:
            style += f"\tmin-height: {parent.pb_min_height_normal.value()}px;\n"
        if parent.pb_max_width_normal.value() > 0:
            style += f"\tmax-width: {parent.pb_max_width_normal.value()}px;\n"
        if parent.pb_max_height_normal.value() > 0:
            style += f"\tmax-height: {parent.pb_max_height_normal.value()}px;\n"

        # border
        border_type_normal = parent.pb_border_type_normal.currentText()
        if border_type_normal != "none":
            style += f"\tborder-style: {border_type_normal};\n"
        if parent.pb_border_color_sel_normal:
            style += f"\tborder-color: {parent.pb_border_color_sel_normal};\n"
        if parent.pb_border_width_normal.value() > 0:
            style += f"\tborder-width: {parent.pb_border_width_normal.value()}px;\n"
        if parent.pb_border_radius_normal.value() > 0:
            style += f"\tborder-radius: {parent.pb_border_radius_normal.value()}px;\n"

        # padding
        if parent.pb_padding_normal.value() > 0:
            style += f"\tpadding: {parent.pb_padding_normal.value()};\n"
        if parent.pb_padding_left_normal.value() > 0:
            style += f"\tpadding-left: {parent.pb_padding_left_normal.value()};\n"
        if parent.pb_padding_right_normal.value() > 0:
            style += f"\tpadding-right: {parent.pb_padding_right_normal.value()};\n"
        if parent.pb_padding_top_normal.value() > 0:
            style += f"\tpadding-top: {parent.pb_padding_top_normal.value()};\n"
        if parent.pb_padding_bottom_normal.value() > 0:
            style += f"\tpadding-bottom: {parent.pb_padding_bottom_normal.value()};\n"

        # margin
        if parent.pb_margin_normal.value() > 0:
            style += f"\tmargin: {parent.pb_margin_normal.value()};\n"
        if parent.pb_margin_left_normal.value() > 0:
            style += f"\tmargin-left: {parent.pb_margin_left_normal.value()};\n"
        if parent.pb_margin_right_normal.value() > 0:
            style += f"\tmargin-right: {parent.pb_margin_right_normal.value()};\n"
        if parent.pb_margin_top_normal.value() > 0:
            style += f"\tmargin-top: {parent.pb_margin_top_normal.value()};\n"
        if parent.pb_margin_bottom_normal.value() > 0:
            style += f"\tmargin-bottom: {parent.pb_margin_bottom_normal.value()};\n"

        style += "}"  # End of QPushButton normal pseudo-state

    # QPushButton hover pseudo-state
    if parent.pb_hover:
        # color
        if style:  # style is not False
            style += "\n\nQPushButton:hover {"
        else:
            style = "\n\nQPushButton:hover {"

        if parent.pb_fg_color_sel_hover:
            style += f"\tcolor: {parent.pb_fg_color_sel_hover};\n"
        if parent.pb_bg_color_sel_hover:
            style += f"\tbackground-color: {parent.pb_bg_color_sel_hover};\n"

        # border
        border_type_hover = parent.pb_border_type_hover.currentText()
        if border_type_hover != "none":
            style += f"\tborder-style: {border_type_hover};\n"
        if parent.pb_border_color_sel_hover:
            style += f"\tborder-color: {parent.pb_border_color_sel_hover};\n"
        if parent.pb_border_width_hover.value() > 0:
            style += f"\tborder-width: {parent.pb_border_width_hover.value()}px;\n"
        if parent.pb_border_radius_hover.value() > 0:
            style += f"\tborder-radius: {parent.pb_border_radius_hover.value()}px;\n"

        style += "}"  # End of QPushButton hover pseudo-state

    # QPushButton pressed pseudo-state
    # color
    if parent.pb_pressed:
        if style:  # style is not False
            style += "\n\nQPushButton:pressed {"
        else:
            style = "\n\nQPushButton:pressed {"

        if parent.pb_fg_color_sel_pressed:
            style += f"\tcolor: {parent.pb_fg_color_sel_pressed};\n"
        if parent.pb_bg_color_sel_pressed:
            style += f"\tbackground-color: {parent.pb_bg_color_sel_pressed};\n"

        # border
        border_type_pressed = parent.pb_border_type_pressed.currentText()
        if border_type_pressed != "none":
            style += f"\tborder-style: {border_type_pressed};\n"
        if parent.pb_border_color_sel_pressed:
            style += f"\tborder-color: {parent.pb_border_color_sel_pressed};\n"
        if parent.pb_border_width_pressed.value() > 0:
            style += f"\tborder-width: {parent.pb_border_width_pressed.value()}px;\n"
        if parent.pb_border_radius_pressed.value() > 0:
            style += f"\tborder-radius: {parent.pb_border_radius_pressed.value()}px;\n"

        style += "}"  # End of QPushButton pressed pseudo-state

    # QPushButton checked pseudo-state
    if parent.pb_checked:
        if style:  # style is not False
            style += "\n\nQPushButton:checked {"
        else:
            style = "\n\nQPushButton:checked {"

        # color
        if parent.pb_fg_color_sel_checked:
            style += f"\tcolor: {parent.pb_fg_color_sel_checked};\n"
        if parent.pb_bg_color_sel_checked:
            style += f"\tbackground-color: {parent.pb_bg_color_sel_checked};\n"

        # border
        border_type_checked = parent.pb_border_type_checked.currentText()
        if border_type_checked != "none":
            style += f"\tborder-style: {border_type_checked};\n"
        if parent.pb_border_color_sel_checked:
            style += f"\tborder-color: {parent.pb_border_color_sel_checked};\n"
        if parent.pb_border_width_checked.value() > 0:
            style += f"\tborder-width: {parent.pb_border_width_checked.value()}px;\n"
        if parent.pb_border_radius_checked.value() > 0:
            style += f"\tborder-radius: {parent.pb_border_radius_checked.value()}px;\n"

        style += "}"  # End of QPushButton checked pseudo-state

    # QPushButton disabled pseudo-state
    if parent.pb_disabled:
        if style:  # style is not False
            style += "\n\nQPushButton:disabled {"
        else:
            style = "\n\nQPushButton:disabled {"

        # color
        if parent.pb_fg_color_sel_disabled:
            style += f"\tcolor: {parent.pb_fg_color_sel_disabled};\n"
        if parent.pb_bg_color_sel_disabled:
            style += f"\tbackground-color: {parent.pb_bg_color_sel_disabled};\n"

        # border
        border_type_disabled = parent.pb_border_type_disabled.currentText()
        if border_type_disabled != "none":
            style += f"\tborder-style: {border_type_disabled};\n"
        if parent.pb_border_color_sel_disabled:
            style += f"\tborder-color: {parent.pb_border_color_sel_disabled};\n"
        if parent.pb_border_width_disabled.value() > 0:
            style += f"\tborder-width: {parent.pb_border_width_disabled.value()}px;\n"
        if parent.pb_border_radius_disabled.value() > 0:
            style += f"\tborder-radius: {parent.pb_border_radius_disabled.value()}px;\n"

        style += "\n}"  # End of QPushButton disabled pseudo-state

    # QPushButton build and apply the stylesheet
    parent.pb_stylesheet.clear()
    if style:
        lines = style.splitlines()
        for line in lines:
            parent.pb_stylesheet.appendPlainText(line)

        parent.pushButton.setStyleSheet(style)


def clear_stylesheet(parent):
    parent.pb_normal = False

    pseudo_states = ["normal", "hover", "pressed", "checked", "disabled"]

    # set all the variables to False
    for item in pseudo_states:
        setattr(parent, f"pb_{item}", False)  # build section flag
        setattr(parent, f"pb_fg_color_sel_{item}", False)
        setattr(parent, f"pb_bg_color_sel_{item}", False)
        setattr(parent, f"pb_border_color_sel_{item}", False)

    # clear all the colors
    for item in pseudo_states:
        label = getattr(parent, f"pb_fg_color_{item}").property("label")
        getattr(parent, label).setStyleSheet("background-color: none;")
        label = getattr(parent, f"pb_bg_color_{item}").property("label")
        getattr(parent, label).setStyleSheet("background-color: none;")
        label = getattr(parent, f"pb_border_color_{item}").property("label")
        getattr(parent, label).setStyleSheet("background-color: none;")

    # set border to none and 0
    for item in pseudo_states:
        getattr(parent, f"pb_border_type_{item}").setCurrentIndex(0)
        getattr(parent, f"pb_border_width_{item}").setValue(0)
        getattr(parent, f"pb_border_radius_{item}").setValue(0)

    # clear the font variables
    parent.pb_font_family = False
    parent.pb_font_size = False
    parent.pb_font_weight = False
    parent.pb_font_style = False
    parent.pb_font_italic = False

    parent.pb_min_width_normal.setValue(0)
    parent.pb_min_height_normal.setValue(0)
    parent.pb_max_width_normal.setValue(0)
    parent.pb_max_height_normal.setValue(0)
    parent.pb_padding_normal.setValue(0)
    parent.pb_padding_left_normal.setValue(0)
    parent.pb_padding_right_normal.setValue(0)
    parent.pb_padding_top_normal.setValue(0)
    parent.pb_padding_top_normal.setValue(0)
    parent.pb_margin_normal.setValue(0)
    parent.pb_margin_left_normal.setValue(0)
    parent.pb_margin_right_normal.setValue(0)
    parent.pb_margin_top_normal.setValue(0)
    parent.pb_margin_top_normal.setValue(0)

    parent.pb_stylesheet.clear()
    parent.pushButton.setStyleSheet("")
