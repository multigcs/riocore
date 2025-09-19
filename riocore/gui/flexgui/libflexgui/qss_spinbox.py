from functools import partial


def startup(parent):
    # QSpinBox
    parent.sb_normal = False

    parent.sb_apply_style.clicked.connect(partial(create_stylesheet, parent))
    parent.sb_clear_style.clicked.connect(partial(clear_stylesheet, parent))

    parent.sb_disable.clicked.connect(partial(parent.disable, "spinBox"))

    border_types = ["none", "solid", "dashed", "dotted", "double", "groove", "ridge", "inset", "outset"]
    pseudo_states = ["normal", "hover", "pressed", "disabled"]

    for state in pseudo_states:  # color dialog connections
        getattr(parent, f"sb_fg_color_{state}").clicked.connect(parent.color_dialog)
        getattr(parent, f"sb_bg_color_{state}").clicked.connect(parent.color_dialog)
        getattr(parent, f"sb_border_color_{state}").clicked.connect(parent.color_dialog)

    for item in pseudo_states:  # populate border combo boxes
        getattr(parent, f"sb_border_type_{item}").addItems(border_types)

    origins = ["none", "content", "padding", "border", "margin"]
    parent.sb_up_origin.addItems(origins)
    parent.sb_down_origin.addItems(origins)

    positions = ["none", "right", "left", "top", "bottom", "top left", "top right", "bottom left", "bottom right"]
    parent.sb_up_position.addItems(positions)
    parent.sb_down_position.addItems(positions)

    # setup enable variables
    for item in pseudo_states:
        setattr(parent, f"sb_{item}", False)
        setattr(parent, f"sb_fg_color_sel_{item}", False)
        setattr(parent, f"sb_bg_color_sel_{item}", False)
        setattr(parent, f"sb_border_color_sel_{item}", False)

    parent.sb_font_family = False
    parent.sb_font_size = False
    parent.sb_font_weight = False
    parent.sb_font_style = False
    parent.sb_font_italic = False
    parent.sb_up = False
    parent.sb_down = False

    parent.sb_min_width_normal.valueChanged.connect(parent.size)
    parent.sb_min_height_normal.valueChanged.connect(parent.size)
    parent.sb_max_width_normal.valueChanged.connect(parent.size)
    parent.sb_max_height_normal.valueChanged.connect(parent.size)

    parent.sb_padding_normal.valueChanged.connect(parent.padding)
    parent.sb_padding_left_normal.valueChanged.connect(parent.padding)
    parent.sb_padding_right_normal.valueChanged.connect(parent.padding)
    parent.sb_padding_top_normal.valueChanged.connect(parent.padding)
    parent.sb_padding_bottom_normal.valueChanged.connect(parent.padding)

    parent.sb_margin_normal.valueChanged.connect(parent.margin)
    parent.sb_margin_left_normal.valueChanged.connect(parent.margin)
    parent.sb_margin_right_normal.valueChanged.connect(parent.margin)
    parent.sb_margin_top_normal.valueChanged.connect(parent.margin)
    parent.sb_margin_bottom_normal.valueChanged.connect(parent.margin)

    parent.sb_font_picker.clicked.connect(parent.font_dialog)

    parent.sb_up_origin.currentIndexChanged.connect(partial(sub_controls, parent))
    parent.sb_up_position.currentIndexChanged.connect(partial(sub_controls, parent))
    parent.sb_up_hide.toggled.connect(partial(sub_controls, parent))
    parent.sb_up_padding.valueChanged.connect(partial(sub_controls, parent))

    parent.sb_down_origin.currentIndexChanged.connect(partial(sub_controls, parent))
    parent.sb_down_position.currentIndexChanged.connect(partial(sub_controls, parent))
    parent.sb_down_hide.toggled.connect(partial(sub_controls, parent))


######### QSpinBox Stylesheet #########


def create_stylesheet(parent):
    style = False

    # QAbstractSpinBox normal pseudo-state
    if parent.sb_normal:
        style = "\nQAbstractSpinBox {\n"

        # color
        if parent.sb_fg_color_sel_normal:
            style += f"\tcolor: {parent.sb_fg_color_sel_normal};\n"
        if parent.sb_bg_color_sel_normal:
            style += f"\tbackground-color: {parent.sb_bg_color_sel_normal};\n"

        # font
        if parent.sb_font_family:
            style += f"\tfont-family: {parent.sb_font_family};\n"
        if parent.sb_font_size:
            style += f"\tfont-size: {parent.sb_font_size}pt;\n"
        if parent.sb_font_weight:
            style += f"\tfont-weight: {parent.sb_font_weight};\n"

        # size
        if parent.sb_min_width_normal.value() > 0:
            style += f"\tmin-width: {parent.sb_min_width_normal.value()}px;\n"
        if parent.sb_min_height_normal.value() > 0:
            style += f"\tmin-height: {parent.sb_min_height_normal.value()}px;\n"
        if parent.sb_max_width_normal.value() > 0:
            style += f"\tmax-width: {parent.sb_max_width_normal.value()}px;\n"
        if parent.sb_max_height_normal.value() > 0:
            style += f"\tmax-height: {parent.sb_max_height_normal.value()}px;\n"

        # border
        border_type_normal = parent.sb_border_type_normal.currentText()
        if border_type_normal != "none":
            style += f"\tborder-style: {border_type_normal};\n"
        if parent.sb_border_color_sel_normal:
            style += f"\tborder-color: {parent.sb_border_color_sel_normal};\n"
        if parent.sb_border_width_normal.value() > 0:
            style += f"\tborder-width: {parent.sb_border_width_normal.value()}px;\n"
        if parent.sb_border_radius_normal.value() > 0:
            style += f"\tborder-radius: {parent.sb_border_radius_normal.value()}px;\n"

        # padding
        if parent.sb_padding_normal.value() > 0:
            style += f"\tpadding: {parent.sb_padding_normal.value()};\n"
        if parent.sb_padding_left_normal.value() > 0:
            style += f"\tpadding-left: {parent.sb_padding_left_normal.value()};\n"
        if parent.sb_padding_right_normal.value() > 0:
            style += f"\tpadding-right: {parent.sb_padding_right_normal.value()};\n"
        if parent.sb_padding_top_normal.value() > 0:
            style += f"\tpadding-top: {parent.sb_padding_top_normal.value()};\n"
        if parent.sb_padding_bottom_normal.value() > 0:
            style += f"\tpadding-bottom: {parent.sb_padding_bottom_normal.value()};\n"

        # margin
        if parent.sb_margin_normal.value() > 0:
            style += f"\tmargin: {parent.sb_margin_normal.value()};\n"
        if parent.sb_margin_left_normal.value() > 0:
            style += f"\tmargin-left: {parent.sb_margin_left_normal.value()};\n"
        if parent.sb_margin_right_normal.value() > 0:
            style += f"\tmargin-right: {parent.sb_margin_right_normal.value()};\n"
        if parent.sb_margin_top_normal.value() > 0:
            style += f"\tmargin-top: {parent.sb_margin_top_normal.value()};\n"
        if parent.sb_margin_bottom_normal.value() > 0:
            style += f"\tmargin-bottom: {parent.sb_margin_bottom_normal.value()};\n"

        style += "}"  # End of QAbstractSpinBox normal pseudo-state

    # QAbstractSpinBox up-button
    if parent.sb_up:
        if style:  # style is not False
            style += "\nQAbstractSpinBox::up-button {\n"
        else:
            style = "\nQAbstractSpinBox::up-button {\n"
        if parent.sb_up_origin.currentText() != "none":
            style += f"\tsubcontrol-origin: {parent.sb_up_origin.currentText()};\n"
        if parent.sb_up_position.currentText() != "none":
            style += f"\tsubcontrol-position: {parent.sb_up_position.currentText()};\n"
        width = parent.sb_up_width.value()
        if width > 0:
            style += f"\twidth: {parent.sb_up_width.value()}px;\n"
        height = parent.sb_up_height.value()
        if height > 0:
            style += f"\theight: {parent.sb_up_height.value()}px;\n"
        if width == 0 and height == 0 and parent.sb_up_hide.isChecked():
            style += "\twidth: 0px;\n"
            style += "\theight: 0px;\n"
        if parent.sb_up_padding.value() > 0:
            style += f"\tpadding: {parent.sb_up_padding.value()}px;\n"

        style += "}"  # End of QAbstractSpinBox up-button

    # QAbstractSpinBox down-button
    if parent.sb_down:
        if style:  # style is not False
            style += "\nQAbstractSpinBox::down-button {\n"
        else:
            style = "\nQAbstractSpinBox::down-button {\n"
        if parent.sb_down_origin.currentText() != "none":
            style += f"\tsubcontrol-origin: {parent.sb_down_origin.currentText()};\n"
        if parent.sb_down_position.currentText() != "none":
            style += f"\tsubcontrol-position: {parent.sb_down_position.currentText()};\n"
        width = parent.sb_down_width.value()
        if width > 0:
            style += f"\twidth: {parent.sb_down_width.value()}px;\n"
        height = parent.sb_down_height.value()
        if height > 0:
            style += f"\theight: {parent.sb_down_height.value()}px;\n"
        if width == 0 and height == 0 and parent.sb_down_hide.isChecked():
            style += "\twidth: 0px;\n"
            style += "\theight: 0px;\n"

        style += "}"  # End of QAbstractSpinBox down-button

    # QAbstractSpinBox hover pseudo-state
    if parent.sb_hover:
        # color
        if style:  # style is not False
            style += "\nQAbstractSpinBox:hover {\n"
        else:
            style = "\nQAbstractSpinBox:hover {\n"

        if parent.sb_fg_color_sel_hover:
            style += f"\tcolor: {parent.sb_fg_color_sel_hover};\n"
        if parent.sb_bg_color_sel_hover:
            style += f"\tbackground-color: {parent.sb_bg_color_sel_hover};\n"

        # border
        border_type_hover = parent.sb_border_type_hover.currentText()
        if border_type_hover != "none":
            style += f"\tborder-style: {border_type_hover};\n"
        if parent.sb_border_color_sel_hover:
            style += f"\tborder-color: {parent.sb_border_color_sel_hover};\n"
        if parent.sb_border_width_hover.value() > 0:
            style += f"\tborder-width: {parent.sb_border_width_hover.value()}px;\n"
        if parent.sb_border_radius_hover.value() > 0:
            style += f"\tborder-radius: {parent.sb_border_radius_hover.value()}px;\n"

        style += "}"  # End of QAbstractSpinBox hover pseudo-state

    # QAbstractSpinBox disabled pseudo-state
    if parent.sb_disabled:
        if style:  # style is not False
            style += "\n\nQAbstractSpinBox:disabled {"
        else:
            style = "\n\nQAbstractSpinBox:disabled {"

        # color
        if parent.sb_fg_color_sel_disabled:
            style += f"\tcolor: {parent.sb_fg_color_sel_disabled};\n"
        if parent.sb_bg_color_sel_disabled:
            style += f"\tbackground-color: {parent.sb_bg_color_sel_disabled};\n"

        # border
        border_type_disabled = parent.sb_border_type_disabled.currentText()
        if border_type_disabled != "none":
            style += f"\tborder-style: {border_type_disabled};\n"
        if parent.sb_border_color_sel_disabled:
            style += f"\tborder-color: {parent.sb_border_color_sel_disabled};\n"
        if parent.sb_border_width_disabled.value() > 0:
            style += f"\tborder-width: {parent.sb_border_width_disabled.value()}px;\n"
        if parent.sb_border_radius_disabled.value() > 0:
            style += f"\tborder-radius: {parent.sb_border_radius_disabled.value()}px;\n"

        style += "\n}"  # End of QAbstractSpinBox disabled pseudo-state
    """
	style = 'QSpinBox::edit {\n'
	style += '\tbackground-color: white;\n'
	style += '\tborder: 1px solid gray;\n'
	style += '\tpadding: 2px;\n'
	style += '}\n'
	"""

    # QAbstractSpinBox build and apply the stylesheet
    parent.sb_stylesheet.clear()
    if style:
        lines = style.splitlines()
        for line in lines:
            parent.sb_stylesheet.appendPlainText(line)
        parent.spinBox.setStyleSheet(style)


def sub_controls(parent):
    up_origin = False if parent.sb_up_origin.currentText() == "none" else True
    up_position = False if parent.sb_up_position.currentText() == "none" else True
    up_hide = True if parent.sb_up_hide.isChecked() else False
    up_padding = True if parent.sb_up_padding.value() > 0 else False
    if up_origin or up_position or up_hide or up_padding:
        parent.sb_up = True
    else:
        parent.sb_up = False

    down_origin = False if parent.sb_down_origin.currentText() == "none" else True
    down_position = False if parent.sb_down_position.currentText() == "none" else True
    down_hide = True if parent.sb_down_hide.isChecked() else False
    if down_origin or down_position or down_hide:
        parent.sb_down = True
    else:
        parent.sb_down = False


def clear_stylesheet(parent):
    parent.sb_normal = False

    pseudo_states = ["normal", "hover", "pressed", "disabled"]

    # set all the variables to False
    for item in pseudo_states:
        setattr(parent, f"sb_{item}", False)  # build section flag
        setattr(parent, f"sb_fg_color_sel_{item}", False)
        setattr(parent, f"sb_bg_color_sel_{item}", False)
        setattr(parent, f"sb_border_color_sel_{item}", False)

    # clear all the colors
    for item in pseudo_states:
        label = getattr(parent, f"sb_fg_color_{item}").property("label")
        getattr(parent, label).setStyleSheet("background-color: none;")
        label = getattr(parent, f"sb_bg_color_{item}").property("label")
        getattr(parent, label).setStyleSheet("background-color: none;")
        label = getattr(parent, f"sb_border_color_{item}").property("label")
        getattr(parent, label).setStyleSheet("background-color: none;")

    # set border to none and 0
    for item in pseudo_states:
        getattr(parent, f"sb_border_type_{item}").setCurrentIndex(0)
        getattr(parent, f"sb_border_width_{item}").setValue(0)
        getattr(parent, f"sb_border_radius_{item}").setValue(0)

    # clear the font variables
    parent.sb_font_family = False
    parent.sb_font_size = False
    parent.sb_font_weight = False
    parent.sb_font_style = False
    parent.sb_font_italic = False

    parent.sb_min_width_normal.setValue(0)
    parent.sb_min_height_normal.setValue(0)
    parent.sb_max_width_normal.setValue(0)
    parent.sb_max_height_normal.setValue(0)
    parent.sb_padding_normal.setValue(0)
    parent.sb_padding_left_normal.setValue(0)
    parent.sb_padding_right_normal.setValue(0)
    parent.sb_padding_top_normal.setValue(0)
    parent.sb_padding_top_normal.setValue(0)
    parent.sb_margin_normal.setValue(0)
    parent.sb_margin_left_normal.setValue(0)
    parent.sb_margin_right_normal.setValue(0)
    parent.sb_margin_top_normal.setValue(0)
    parent.sb_margin_top_normal.setValue(0)

    parent.sb_stylesheet.clear()
    parent.spinBox.setStyleSheet("")
