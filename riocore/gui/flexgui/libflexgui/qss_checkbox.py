from functools import partial


def startup(parent):
    # QCheckBox
    parent.cb_normal = False

    parent.cb_apply_style.clicked.connect(partial(create_stylesheet, parent))
    parent.cb_clear_style.clicked.connect(partial(clear_stylesheet, parent))

    parent.cb_disable.clicked.connect(partial(parent.disable, "checkBox"))

    parent.cb_min_width_normal.valueChanged.connect(parent.size)
    parent.cb_min_height_normal.valueChanged.connect(parent.size)
    parent.cb_max_width_normal.valueChanged.connect(parent.size)
    parent.cb_max_height_normal.valueChanged.connect(parent.size)

    border_types = ["none", "solid", "dashed", "dotted", "double", "groove", "ridge", "inset", "outset"]
    pseudo_states = ["normal", "hover", "pressed", "checked", "disabled"]

    for item in pseudo_states:
        # populate border combo boxes
        getattr(parent, f"cb_border_type_{item}").addItems(border_types)
        # setup variables
        setattr(parent, f"cb_{item}", False)  # build section flag
        setattr(parent, f"cb_fg_color_sel_{item}", False)
        setattr(parent, f"cb_bg_color_sel_{item}", False)
        setattr(parent, f"cb_border_color_sel_{item}", False)

    for state in pseudo_states:  # color dialog connections
        getattr(parent, f"cb_fg_color_{state}").clicked.connect(parent.color_dialog)
        getattr(parent, f"cb_bg_color_{state}").clicked.connect(parent.color_dialog)
        getattr(parent, f"cb_border_color_{state}").clicked.connect(parent.color_dialog)

    parent.cb_font_picker.clicked.connect(parent.font_dialog)
    parent.cb_font_family = False
    parent.cb_font_size = False
    parent.cb_font_weight = False
    parent.cb_font_style = False
    parent.cb_font_italic = False
    parent.cb_indicator = False

    parent.cb_padding_normal.valueChanged.connect(parent.padding)
    parent.cb_padding_left_normal.valueChanged.connect(parent.padding)
    parent.cb_padding_right_normal.valueChanged.connect(parent.padding)
    parent.cb_padding_top_normal.valueChanged.connect(parent.padding)
    parent.cb_padding_bottom_normal.valueChanged.connect(parent.padding)

    parent.cb_margin_normal.valueChanged.connect(parent.margin)
    parent.cb_margin_left_normal.valueChanged.connect(parent.margin)
    parent.cb_margin_right_normal.valueChanged.connect(parent.margin)
    parent.cb_margin_top_normal.valueChanged.connect(parent.margin)
    parent.cb_margin_bottom_normal.valueChanged.connect(parent.margin)

    parent.cb_indicator_width_normal.valueChanged.connect(parent.indicator)
    parent.cb_indicator_height_normal.valueChanged.connect(parent.indicator)


######### QCheckBox Stylesheet #########


def create_stylesheet(parent):
    style = False

    # QCheckBox normal pseudo-state
    if parent.cb_normal:
        style = "QCheckBox {\n"

        # color
        if parent.cb_fg_color_sel_normal:
            style += f"\tcolor: {parent.cb_fg_color_sel_normal};\n"
        if parent.cb_bg_color_sel_normal:
            style += f"\tbackground-color: {parent.cb_bg_color_sel_normal};\n"

        # font
        if parent.cb_font_family:
            style += f"\tfont-family: {parent.cb_font_family};\n"
        if parent.cb_font_size:
            style += f"\tfont-size: {parent.cb_font_size}pt;\n"
        if parent.cb_font_weight:
            style += f"\tfont-weight: {parent.cb_font_weight};\n"

        # size
        if parent.cb_min_width_normal.value() > 0:
            style += f"\tmin-width: {parent.cb_min_width_normal.value()}px;\n"
        if parent.cb_min_height_normal.value() > 0:
            style += f"\tmin-height: {parent.cb_min_height_normal.value()}px;\n"
        if parent.cb_max_width_normal.value() > 0:
            style += f"\tmax-width: {parent.cb_max_width_normal.value()}px;\n"
        if parent.cb_max_height_normal.value() > 0:
            style += f"\tmax-height: {parent.cb_max_height_normal.value()}px;\n"

        # border
        border_type_normal = parent.cb_border_type_normal.currentText()
        if border_type_normal != "none":
            style += f"\tborder-style: {border_type_normal};\n"
        if parent.cb_border_color_sel_normal:
            style += f"\tborder-color: {parent.cb_border_color_sel_normal};\n"
        if parent.cb_border_width_normal.value() > 0:
            style += f"\tborder-width: {parent.cb_border_width_normal.value()}px;\n"
        if parent.cb_border_radius_normal.value() > 0:
            style += f"\tborder-radius: {parent.cb_border_radius_normal.value()}px;\n"

        # padding
        if parent.cb_padding_normal.value() > 0:
            style += f"\tpadding: {parent.cb_padding_normal.value()};\n"
        if parent.cb_padding_left_normal.value() > 0:
            style += f"\tpadding-left: {parent.cb_padding_left_normal.value()};\n"
        if parent.cb_padding_right_normal.value() > 0:
            style += f"\tpadding-right: {parent.cb_padding_right_normal.value()};\n"
        if parent.cb_padding_top_normal.value() > 0:
            style += f"\tpadding-top: {parent.cb_padding_top_normal.value()};\n"
        if parent.cb_padding_bottom_normal.value() > 0:
            style += f"\tpadding-bottom: {parent.cb_padding_bottom_normal.value()};\n"

        # margin
        if parent.cb_margin_normal.value() > 0:
            style += f"\tmargin: {parent.cb_margin_normal.value()};\n"
        if parent.cb_margin_left_normal.value() > 0:
            style += f"\tmargin-left: {parent.cb_margin_left_normal.value()};\n"
        if parent.cb_margin_right_normal.value() > 0:
            style += f"\tmargin-right: {parent.cb_margin_right_normal.value()};\n"
        if parent.cb_margin_top_normal.value() > 0:
            style += f"\tmargin-top: {parent.cb_margin_top_normal.value()};\n"
        if parent.cb_margin_bottom_normal.value() > 0:
            style += f"\tmargin-bottom: {parent.cb_margin_bottom_normal.value()};\n"

        style += "}"  # End of QCheckBox normal pseudo-state

        # QCheckBox indicator sub-control

    if parent.cb_indicator:
        if style:  # style is not False
            style += "\n\nQCheckBox::indicator {\n"
        else:
            style = "\tQCheckBox::indicator {\n"
        if parent.cb_indicator_width_normal.value() > 0:
            style += f"\twidth: {parent.cb_indicator_width_normal.value()}px;\n"
        if parent.cb_indicator_height_normal.value() > 0:
            style += f"\theight: {parent.cb_indicator_height_normal.value()}px;\n"

        style += "}"  # End of QCheckBox::indicator

    # QCheckBox hover pseudo-state
    if parent.cb_hover:
        # color
        if style:  # style is not False
            style += "\n\nQCheckBox:hover {"
        else:
            style = "\n\nQCheckBox:hover {"

        if parent.cb_fg_color_sel_hover:
            style += f"\tcolor: {parent.cb_fg_color_sel_hover};\n"
        if parent.cb_bg_color_sel_hover:
            style += f"\tbackground-color: {parent.cb_bg_color_sel_hover};\n"

        # border
        border_type_hover = parent.cb_border_type_hover.currentText()
        if border_type_hover != "none":
            style += f"\tborder-style: {border_type_hover};\n"
        if parent.cb_border_color_sel_hover:
            style += f"\tborder-color: {parent.cb_border_color_sel_hover};\n"
        if parent.cb_border_width_hover.value() > 0:
            style += f"\tborder-width: {parent.cb_border_width_hover.value()}px;\n"
        if parent.cb_border_radius_hover.value() > 0:
            style += f"\tborder-radius: {parent.cb_border_radius_hover.value()}px;\n"

        style += "}"  # End of QCheckBox hover pseudo-state

    # QCheckBox pressed pseudo-state
    # color
    if parent.cb_pressed:
        if style:  # style is not False
            style += "\n\nQCheckBox:pressed {"
        else:
            style = "\n\nQCheckBox:pressed {"

        if parent.cb_fg_color_sel_pressed:
            style += f"\tcolor: {parent.cb_fg_color_sel_pressed};\n"
        if parent.cb_bg_color_sel_pressed:
            style += f"\tbackground-color: {parent.cb_bg_color_sel_pressed};\n"

        # border
        border_type_pressed = parent.cb_border_type_pressed.currentText()
        if border_type_pressed != "none":
            style += f"\tborder-style: {border_type_pressed};\n"
        if parent.cb_border_color_sel_pressed:
            style += f"\tborder-color: {parent.cb_border_color_sel_pressed};\n"
        if parent.cb_border_width_pressed.value() > 0:
            style += f"\tborder-width: {parent.cb_border_width_pressed.value()}px;\n"
        if parent.cb_border_radius_pressed.value() > 0:
            style += f"\tborder-radius: {parent.cb_border_radius_pressed.value()}px;\n"

        style += "}"  # End of QCheckBox pressed pseudo-state

    # QCheckBox checked pseudo-state
    if parent.cb_checked:
        if style:  # style is not False
            style += "\n\nQCheckBox:checked {"
        else:
            style = "\n\nQCheckBox:checked {"

        # color
        if parent.cb_fg_color_sel_checked:
            style += f"\tcolor: {parent.cb_fg_color_sel_checked};\n"
        if parent.cb_bg_color_sel_checked:
            style += f"\tbackground-color: {parent.cb_bg_color_sel_checked};\n"

        # border
        border_type_checked = parent.cb_border_type_checked.currentText()
        if border_type_checked != "none":
            style += f"\tborder-style: {border_type_checked};\n"
        if parent.cb_border_color_sel_checked:
            style += f"\tborder-color: {parent.cb_border_color_sel_checked};\n"
        if parent.cb_border_width_checked.value() > 0:
            style += f"\tborder-width: {parent.cb_border_width_checked.value()}px;\n"
        if parent.cb_border_radius_checked.value() > 0:
            style += f"\tborder-radius: {parent.cb_border_radius_checked.value()}px;\n"

        style += "}"  # End of QCheckBox checked pseudo-state

    # QCheckBox disabled pseudo-state
    if parent.cb_disabled:
        if style:  # style is not False
            style += "\n\nQCheckBox:disabled {"
        else:
            style = "\n\nQCheckBox:disabled {"

        # color
        if parent.cb_fg_color_sel_disabled:
            style += f"\tcolor: {parent.cb_fg_color_sel_disabled};\n"
        if parent.cb_bg_color_sel_disabled:
            style += f"\tbackground-color: {parent.cb_bg_color_sel_disabled};\n"

        # border
        border_type_disabled = parent.cb_border_type_disabled.currentText()
        if border_type_disabled != "none":
            style += f"\tborder-style: {border_type_disabled};\n"
        if parent.cb_border_color_sel_disabled:
            style += f"\tborder-color: {parent.cb_border_color_sel_disabled};\n"
        if parent.cb_border_width_disabled.value() > 0:
            style += f"\tborder-width: {parent.cb_border_width_disabled.value()}px;\n"
        if parent.cb_border_radius_disabled.value() > 0:
            style += f"\tborder-radius: {parent.cb_border_radius_disabled.value()}px;\n"

        style += "\n}"  # End of QCheckBox disabled pseudo-state

    # QCheckBox build and apply the stylesheet
    parent.cb_stylesheet.clear()
    if style:
        lines = style.splitlines()
        for line in lines:
            parent.cb_stylesheet.appendPlainText(line)

        parent.checkBox.setStyleSheet(style)


def clear_stylesheet(parent):
    parent.cb_normal = False

    pseudo_states = ["normal", "hover", "pressed", "checked", "disabled"]

    # set all the variables to False
    for item in pseudo_states:
        setattr(parent, f"cb_{item}", False)  # build section flag
        setattr(parent, f"cb_fg_color_sel_{item}", False)
        setattr(parent, f"cb_bg_color_sel_{item}", False)
        setattr(parent, f"cb_border_color_sel_{item}", False)

    # clear all the colors
    for item in pseudo_states:
        label = getattr(parent, f"cb_fg_color_{item}").property("label")
        getattr(parent, label).setStyleSheet("background-color: none;")
        label = getattr(parent, f"cb_bg_color_{item}").property("label")
        getattr(parent, label).setStyleSheet("background-color: none;")
        label = getattr(parent, f"cb_border_color_{item}").property("label")
        getattr(parent, label).setStyleSheet("background-color: none;")

    # set border to none and 0
    for item in pseudo_states:
        getattr(parent, f"cb_border_type_{item}").setCurrentIndex(0)
        getattr(parent, f"cb_border_width_{item}").setValue(0)
        getattr(parent, f"cb_border_radius_{item}").setValue(0)

    # clear the font variables
    parent.cb_font_family = False
    parent.cb_font_size = False
    parent.cb_font_weight = False
    parent.cb_font_style = False
    parent.cb_font_italic = False

    parent.cb_min_width_normal.setValue(0)
    parent.cb_min_height_normal.setValue(0)
    parent.cb_max_width_normal.setValue(0)
    parent.cb_max_height_normal.setValue(0)
    parent.cb_padding_normal.setValue(0)
    parent.cb_padding_left_normal.setValue(0)
    parent.cb_padding_right_normal.setValue(0)
    parent.cb_padding_top_normal.setValue(0)
    parent.cb_padding_top_normal.setValue(0)
    parent.cb_margin_normal.setValue(0)
    parent.cb_margin_left_normal.setValue(0)
    parent.cb_margin_right_normal.setValue(0)
    parent.cb_margin_top_normal.setValue(0)
    parent.cb_margin_top_normal.setValue(0)

    parent.cb_stylesheet.clear()
    parent.checkBox.setStyleSheet("")
