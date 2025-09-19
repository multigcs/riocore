from functools import partial


def startup(parent):
    # QRadioButton
    parent.rb_normal = False

    parent.rb_apply_style.clicked.connect(partial(create_stylesheet, parent))
    parent.rb_clear_style.clicked.connect(partial(clear_stylesheet, parent))

    parent.rb_disable.clicked.connect(partial(parent.disable, "radioButton_0"))

    parent.rb_min_width_normal.valueChanged.connect(parent.size)
    parent.rb_min_height_normal.valueChanged.connect(parent.size)
    parent.rb_max_width_normal.valueChanged.connect(parent.size)
    parent.rb_max_height_normal.valueChanged.connect(parent.size)

    border_types = ["none", "solid", "dashed", "dotted", "double", "groove", "ridge", "inset", "outset"]
    pseudo_states = ["normal", "hover", "pressed", "checked", "disabled"]

    for item in pseudo_states:
        # populate border combo boxes
        getattr(parent, f"rb_border_type_{item}").addItems(border_types)
        # setup variables
        setattr(parent, f"rb_{item}", False)  # build section flag
        setattr(parent, f"rb_fg_color_sel_{item}", False)
        setattr(parent, f"rb_bg_color_sel_{item}", False)
        setattr(parent, f"rb_border_color_sel_{item}", False)

    for state in pseudo_states:  # color dialog connections
        getattr(parent, f"rb_fg_color_{state}").clicked.connect(parent.color_dialog)
        getattr(parent, f"rb_bg_color_{state}").clicked.connect(parent.color_dialog)
        getattr(parent, f"rb_border_color_{state}").clicked.connect(parent.color_dialog)

    parent.rb_font_picker.clicked.connect(parent.font_dialog)
    parent.rb_font_family = False
    parent.rb_font_size = False
    parent.rb_font_weight = False
    parent.rb_font_style = False
    parent.rb_font_italic = False
    parent.rb_indicator = False

    parent.rb_padding_normal.valueChanged.connect(parent.padding)
    parent.rb_padding_left_normal.valueChanged.connect(parent.padding)
    parent.rb_padding_right_normal.valueChanged.connect(parent.padding)
    parent.rb_padding_top_normal.valueChanged.connect(parent.padding)
    parent.rb_padding_bottom_normal.valueChanged.connect(parent.padding)

    parent.rb_margin_normal.valueChanged.connect(parent.margin)
    parent.rb_margin_left_normal.valueChanged.connect(parent.margin)
    parent.rb_margin_right_normal.valueChanged.connect(parent.margin)
    parent.rb_margin_top_normal.valueChanged.connect(parent.margin)
    parent.rb_margin_bottom_normal.valueChanged.connect(parent.margin)

    parent.rb_indicator_width_normal.valueChanged.connect(parent.indicator)
    parent.rb_indicator_height_normal.valueChanged.connect(parent.indicator)


######### QRadioButton Stylesheet #########


def create_stylesheet(parent):
    style = False

    # QRadioButton normal pseudo-state
    if parent.rb_normal:
        style = "QRadioButton {\n"

        # color
        if parent.rb_fg_color_sel_normal:
            style += f"\tcolor: {parent.rb_fg_color_sel_normal};\n"
        if parent.rb_bg_color_sel_normal:
            style += f"\tbackground-color: {parent.rb_bg_color_sel_normal};\n"

        # font
        if parent.rb_font_family:
            style += f"\tfont-family: {parent.rb_font_family};\n"
        if parent.rb_font_size:
            style += f"\tfont-size: {parent.rb_font_size}pt;\n"
        if parent.rb_font_weight:
            style += f"\tfont-weight: {parent.rb_font_weight};\n"

        # size
        if parent.rb_min_width_normal.value() > 0:
            style += f"\tmin-width: {parent.rb_min_width_normal.value()}px;\n"
        if parent.rb_min_height_normal.value() > 0:
            style += f"\tmin-height: {parent.rb_min_height_normal.value()}px;\n"
        if parent.rb_max_width_normal.value() > 0:
            style += f"\tmax-width: {parent.rb_max_width_normal.value()}px;\n"
        if parent.rb_max_height_normal.value() > 0:
            style += f"\tmax-height: {parent.rb_max_height_normal.value()}px;\n"

        # border
        border_type_normal = parent.rb_border_type_normal.currentText()
        if border_type_normal != "none":
            style += f"\tborder-style: {border_type_normal};\n"
        if parent.rb_border_color_sel_normal:
            style += f"\tborder-color: {parent.rb_border_color_sel_normal};\n"
        if parent.rb_border_width_normal.value() > 0:
            style += f"\tborder-width: {parent.rb_border_width_normal.value()}px;\n"
        if parent.rb_border_radius_normal.value() > 0:
            style += f"\tborder-radius: {parent.rb_border_radius_normal.value()}px;\n"

        # padding
        if parent.rb_padding_normal.value() > 0:
            style += f"\tpadding: {parent.rb_padding_normal.value()};\n"
        if parent.rb_padding_left_normal.value() > 0:
            style += f"\tpadding-left: {parent.rb_padding_left_normal.value()};\n"
        if parent.rb_padding_right_normal.value() > 0:
            style += f"\tpadding-right: {parent.rb_padding_right_normal.value()};\n"
        if parent.rb_padding_top_normal.value() > 0:
            style += f"\tpadding-top: {parent.rb_padding_top_normal.value()};\n"
        if parent.rb_padding_bottom_normal.value() > 0:
            style += f"\tpadding-bottom: {parent.rb_padding_bottom_normal.value()};\n"

        # margin
        if parent.rb_margin_normal.value() > 0:
            style += f"\tmargin: {parent.rb_margin_normal.value()};\n"
        if parent.rb_margin_left_normal.value() > 0:
            style += f"\tmargin-left: {parent.rb_margin_left_normal.value()};\n"
        if parent.rb_margin_right_normal.value() > 0:
            style += f"\tmargin-right: {parent.rb_margin_right_normal.value()};\n"
        if parent.rb_margin_top_normal.value() > 0:
            style += f"\tmargin-top: {parent.rb_margin_top_normal.value()};\n"
        if parent.rb_margin_bottom_normal.value() > 0:
            style += f"\tmargin-bottom: {parent.rb_margin_bottom_normal.value()};\n"

        style += "}"  # End of QRadioButton normal pseudo-state

        # QRadioButton indicator sub-control

    if parent.rb_indicator:
        if style:  # style is not False
            style += "\n\nQRadioButton::indicator {\n"
        else:
            style = "\tQRadioButton::indicator {\n"
        if parent.rb_indicator_width_normal.value() > 0:
            style += f"\twidth: {parent.rb_indicator_width_normal.value()}px;\n"
        if parent.rb_indicator_height_normal.value() > 0:
            style += f"\theight: {parent.rb_indicator_height_normal.value()}px;\n"

        style += "}"  # End of QRadioButton::indicator

    # QRadioButton hover pseudo-state
    if parent.rb_hover:
        # color
        if style:  # style is not False
            style += "\n\nQRadioButton:hover {"
        else:
            style = "\n\nQRadioButton:hover {"

        if parent.rb_fg_color_sel_hover:
            style += f"\tcolor: {parent.rb_fg_color_sel_hover};\n"
        if parent.rb_bg_color_sel_hover:
            style += f"\tbackground-color: {parent.rb_bg_color_sel_hover};\n"

        # border
        border_type_hover = parent.rb_border_type_hover.currentText()
        if border_type_hover != "none":
            style += f"\tborder-style: {border_type_hover};\n"
        if parent.rb_border_color_sel_hover:
            style += f"\tborder-color: {parent.rb_border_color_sel_hover};\n"
        if parent.rb_border_width_hover.value() > 0:
            style += f"\tborder-width: {parent.rb_border_width_hover.value()}px;\n"
        if parent.rb_border_radius_hover.value() > 0:
            style += f"\tborder-radius: {parent.rb_border_radius_hover.value()}px;\n"

        style += "}"  # End of QRadioButton hover pseudo-state

    # QRadioButton pressed pseudo-state
    # color
    if parent.rb_pressed:
        if style:  # style is not False
            style += "\n\nQRadioButton:pressed {"
        else:
            style = "\n\nQRadioButton:pressed {"

        if parent.rb_fg_color_sel_pressed:
            style += f"\tcolor: {parent.rb_fg_color_sel_pressed};\n"
        if parent.rb_bg_color_sel_pressed:
            style += f"\tbackground-color: {parent.rb_bg_color_sel_pressed};\n"

        # border
        border_type_pressed = parent.rb_border_type_pressed.currentText()
        if border_type_pressed != "none":
            style += f"\tborder-style: {border_type_pressed};\n"
        if parent.rb_border_color_sel_pressed:
            style += f"\tborder-color: {parent.rb_border_color_sel_pressed};\n"
        if parent.rb_border_width_pressed.value() > 0:
            style += f"\tborder-width: {parent.rb_border_width_pressed.value()}px;\n"
        if parent.rb_border_radius_pressed.value() > 0:
            style += f"\tborder-radius: {parent.rb_border_radius_pressed.value()}px;\n"

        style += "}"  # End of QRadioButton pressed pseudo-state

    # QRadioButton checked pseudo-state
    if parent.rb_checked:
        if style:  # style is not False
            style += "\n\nQRadioButton:checked {"
        else:
            style = "\n\nQRadioButton:checked {"

        # color
        if parent.rb_fg_color_sel_checked:
            style += f"\tcolor: {parent.rb_fg_color_sel_checked};\n"
        if parent.rb_bg_color_sel_checked:
            style += f"\tbackground-color: {parent.rb_bg_color_sel_checked};\n"

        # border
        border_type_checked = parent.rb_border_type_checked.currentText()
        if border_type_checked != "none":
            style += f"\tborder-style: {border_type_checked};\n"
        if parent.rb_border_color_sel_checked:
            style += f"\tborder-color: {parent.rb_border_color_sel_checked};\n"
        if parent.rb_border_width_checked.value() > 0:
            style += f"\tborder-width: {parent.rb_border_width_checked.value()}px;\n"
        if parent.rb_border_radius_checked.value() > 0:
            style += f"\tborder-radius: {parent.rb_border_radius_checked.value()}px;\n"

        style += "}"  # End of QRadioButton checked pseudo-state

    # QRadioButton disabled pseudo-state
    if parent.rb_disabled:
        if style:  # style is not False
            style += "\n\nQRadioButton:disabled {"
        else:
            style = "\n\nQRadioButton:disabled {"

        # color
        if parent.rb_fg_color_sel_disabled:
            style += f"\tcolor: {parent.rb_fg_color_sel_disabled};\n"
        if parent.rb_bg_color_sel_disabled:
            style += f"\tbackground-color: {parent.rb_bg_color_sel_disabled};\n"

        # border
        border_type_disabled = parent.rb_border_type_disabled.currentText()
        if border_type_disabled != "none":
            style += f"\tborder-style: {border_type_disabled};\n"
        if parent.rb_border_color_sel_disabled:
            style += f"\tborder-color: {parent.rb_border_color_sel_disabled};\n"
        if parent.rb_border_width_disabled.value() > 0:
            style += f"\tborder-width: {parent.rb_border_width_disabled.value()}px;\n"
        if parent.rb_border_radius_disabled.value() > 0:
            style += f"\tborder-radius: {parent.rb_border_radius_disabled.value()}px;\n"

        style += "\n}"  # End of QRadioButton disabled pseudo-state

    # QRadioButton build and apply the stylesheet
    parent.rb_stylesheet.clear()
    if style:
        lines = style.splitlines()
        for line in lines:
            parent.rb_stylesheet.appendPlainText(line)

        parent.radioButton_0.setStyleSheet(style)
        parent.radioButton_1.setStyleSheet(style)


def clear_stylesheet(parent):
    parent.rb_normal = False

    pseudo_states = ["normal", "hover", "pressed", "checked", "disabled"]

    # set all the variables to False
    for item in pseudo_states:
        setattr(parent, f"rb_{item}", False)  # build section flag
        setattr(parent, f"rb_fg_color_sel_{item}", False)
        setattr(parent, f"rb_bg_color_sel_{item}", False)
        setattr(parent, f"rb_border_color_sel_{item}", False)

    # clear all the colors
    for item in pseudo_states:
        label = getattr(parent, f"rb_fg_color_{item}").property("label")
        getattr(parent, label).setStyleSheet("background-color: none;")
        label = getattr(parent, f"rb_bg_color_{item}").property("label")
        getattr(parent, label).setStyleSheet("background-color: none;")
        label = getattr(parent, f"rb_border_color_{item}").property("label")
        getattr(parent, label).setStyleSheet("background-color: none;")

    # set border to none and 0
    for item in pseudo_states:
        getattr(parent, f"rb_border_type_{item}").setCurrentIndex(0)
        getattr(parent, f"rb_border_width_{item}").setValue(0)
        getattr(parent, f"rb_border_radius_{item}").setValue(0)

    # clear the font variables
    parent.rb_font_family = False
    parent.rb_font_size = False
    parent.rb_font_weight = False
    parent.rb_font_style = False
    parent.rb_font_italic = False

    parent.rb_min_width_normal.setValue(0)
    parent.rb_min_height_normal.setValue(0)
    parent.rb_max_width_normal.setValue(0)
    parent.rb_max_height_normal.setValue(0)
    parent.rb_padding_normal.setValue(0)
    parent.rb_padding_left_normal.setValue(0)
    parent.rb_padding_right_normal.setValue(0)
    parent.rb_padding_top_normal.setValue(0)
    parent.rb_padding_top_normal.setValue(0)
    parent.rb_margin_normal.setValue(0)
    parent.rb_margin_left_normal.setValue(0)
    parent.rb_margin_right_normal.setValue(0)
    parent.rb_margin_top_normal.setValue(0)
    parent.rb_margin_top_normal.setValue(0)

    parent.rb_stylesheet.clear()
    parent.radioButton_0.setStyleSheet("")
    parent.radioButton_1.setStyleSheet("")
