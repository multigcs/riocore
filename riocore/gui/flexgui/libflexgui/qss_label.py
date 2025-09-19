from functools import partial


def startup(parent):
    # QLabel
    parent.lb_normal = False

    parent.lb_apply_style.clicked.connect(partial(create_stylesheet, parent))
    parent.lb_clear_style.clicked.connect(partial(clear_stylesheet, parent))

    parent.lb_disable.clicked.connect(partial(parent.disable, "label"))

    border_types = ["none", "solid", "dashed", "dotted", "double", "groove", "ridge", "inset", "outset"]
    pseudo_states = ["normal", "hover", "disabled"]

    for state in pseudo_states:  # color dialog connections
        getattr(parent, f"lb_fg_color_{state}").clicked.connect(parent.color_dialog)
        getattr(parent, f"lb_bg_color_{state}").clicked.connect(parent.color_dialog)
        getattr(parent, f"lb_border_color_{state}").clicked.connect(parent.color_dialog)

    for item in pseudo_states:  # populate border combo boxes
        getattr(parent, f"lb_border_type_{item}").addItems(border_types)

    # setup enable variables
    for item in pseudo_states:
        setattr(parent, f"lb_{item}", False)
        setattr(parent, f"lb_fg_color_sel_{item}", False)
        setattr(parent, f"lb_bg_color_sel_{item}", False)
        setattr(parent, f"lb_border_color_sel_{item}", False)

    parent.lb_font_family = False
    parent.lb_font_size = False
    parent.lb_font_weight = False
    parent.lb_font_style = False
    parent.lb_font_italic = False

    parent.lb_min_width_normal.valueChanged.connect(parent.size)
    parent.lb_min_height_normal.valueChanged.connect(parent.size)
    parent.lb_max_width_normal.valueChanged.connect(parent.size)
    parent.lb_max_height_normal.valueChanged.connect(parent.size)

    parent.lb_padding_normal.valueChanged.connect(parent.padding)
    parent.lb_padding_left_normal.valueChanged.connect(parent.padding)
    parent.lb_padding_right_normal.valueChanged.connect(parent.padding)
    parent.lb_padding_top_normal.valueChanged.connect(parent.padding)
    parent.lb_padding_bottom_normal.valueChanged.connect(parent.padding)

    parent.lb_margin_normal.valueChanged.connect(parent.margin)
    parent.lb_margin_left_normal.valueChanged.connect(parent.margin)
    parent.lb_margin_right_normal.valueChanged.connect(parent.margin)
    parent.lb_margin_top_normal.valueChanged.connect(parent.margin)
    parent.lb_margin_bottom_normal.valueChanged.connect(parent.margin)

    parent.lb_font_picker.clicked.connect(parent.font_dialog)


######### QLabel Stylesheet #########


def create_stylesheet(parent):
    style = False

    # QLabel normal pseudo-state
    if parent.lb_normal:
        style = "QLabel {\n"

        # color
        if parent.lb_fg_color_sel_normal:
            style += f"\tcolor: {parent.lb_fg_color_sel_normal};\n"
        if parent.lb_bg_color_sel_normal:
            style += f"\tbackground-color: {parent.lb_bg_color_sel_normal};\n"

        # font
        if parent.lb_font_family:
            style += f"\tfont-family: {parent.lb_font_family};\n"
        if parent.lb_font_size:
            style += f"\tfont-size: {parent.lb_font_size}pt;\n"
        if parent.lb_font_weight:
            style += f"\tfont-weight: {parent.lb_font_weight};\n"

        # size
        if parent.lb_min_width_normal.value() > 0:
            style += f"\tmin-width: {parent.lb_min_width_normal.value()}px;\n"
        if parent.lb_min_height_normal.value() > 0:
            style += f"\tmin-height: {parent.lb_min_height_normal.value()}px;\n"
        if parent.lb_max_width_normal.value() > 0:
            style += f"\tmax-width: {parent.lb_max_width_normal.value()}px;\n"
        if parent.lb_max_height_normal.value() > 0:
            style += f"\tmax-height: {parent.lb_max_height_normal.value()}px;\n"

        # border
        border_type_normal = parent.lb_border_type_normal.currentText()
        if border_type_normal != "none":
            style += f"\tborder-style: {border_type_normal};\n"
        if parent.lb_border_color_sel_normal:
            style += f"\tborder-color: {parent.lb_border_color_sel_normal};\n"
        if parent.lb_border_width_normal.value() > 0:
            style += f"\tborder-width: {parent.lb_border_width_normal.value()}px;\n"
        if parent.lb_border_radius_normal.value() > 0:
            style += f"\tborder-radius: {parent.lb_border_radius_normal.value()}px;\n"

        # padding
        if parent.lb_padding_normal.value() > 0:
            style += f"\tpadding: {parent.lb_padding_normal.value()};\n"
        if parent.lb_padding_left_normal.value() > 0:
            style += f"\tpadding-left: {parent.lb_padding_left_normal.value()};\n"
        if parent.lb_padding_right_normal.value() > 0:
            style += f"\tpadding-right: {parent.lb_padding_right_normal.value()};\n"
        if parent.lb_padding_top_normal.value() > 0:
            style += f"\tpadding-top: {parent.lb_padding_top_normal.value()};\n"
        if parent.lb_padding_bottom_normal.value() > 0:
            style += f"\tpadding-bottom: {parent.lb_padding_bottom_normal.value()};\n"

        # margin
        if parent.lb_margin_normal.value() > 0:
            style += f"\tmargin: {parent.lb_margin_normal.value()};\n"
        if parent.lb_margin_left_normal.value() > 0:
            style += f"\tmargin-left: {parent.lb_margin_left_normal.value()};\n"
        if parent.lb_margin_right_normal.value() > 0:
            style += f"\tmargin-right: {parent.lb_margin_right_normal.value()};\n"
        if parent.lb_margin_top_normal.value() > 0:
            style += f"\tmargin-top: {parent.lb_margin_top_normal.value()};\n"
        if parent.lb_margin_bottom_normal.value() > 0:
            style += f"\tmargin-bottom: {parent.lb_margin_bottom_normal.value()};\n"

        style += "}"  # End of QLabel normal pseudo-state

    # QLabel hover pseudo-state
    if parent.lb_hover:
        if style:  # style is not False
            style += "\n\nQLabel:hover {\n"
        else:
            style = "\n\nQLabel:hover {\n"

        # color
        if parent.lb_fg_color_sel_hover:
            style += f"\tcolor: {parent.lb_fg_color_sel_hover};\n"
        if parent.lb_bg_color_sel_hover:
            style += f"\tbackground-color: {parent.lb_bg_color_sel_hover};\n"

        # border
        border_type_hover = parent.lb_border_type_hover.currentText()
        if border_type_hover != "none":
            style += f"\tborder-style: {border_type_hover};\n"
        if parent.lb_border_color_sel_hover:
            style += f"\tborder-color: {parent.lb_border_color_sel_hover};\n"
        if parent.lb_border_width_hover.value() > 0:
            style += f"\tborder-width: {parent.lb_border_width_hover.value()}px;\n"
        if parent.lb_border_radius_hover.value() > 0:
            style += f"\tborder-radius: {parent.lb_border_radius_hover.value()}px;\n"

        style += "}"  # End of QLabel hover pseudo-state

    # QLabel disabled pseudo-state
    if parent.lb_disabled:
        # color
        if style:  # style is not False
            style += "\n\nQLabel:disabled {\n"
        else:
            style = "\n\nQLabel:disabled {\n"

        if parent.lb_fg_color_sel_disabled:
            style += f"\tcolor: {parent.lb_fg_color_sel_disabled};\n"
        if parent.lb_bg_color_sel_disabled:
            style += f"\tbackground-color: {parent.lb_bg_color_sel_disabled};\n"

        # border
        border_type_disabled = parent.lb_border_type_disabled.currentText()
        if border_type_disabled != "none":
            style += f"\tborder-style: {border_type_disabled};\n"
        if parent.lb_border_color_sel_disabled:
            style += f"\tborder-color: {parent.lb_border_color_sel_disabled};\n"
        if parent.lb_border_width_disabled.value() > 0:
            style += f"\tborder-width: {parent.lb_border_width_disabled.value()}px;\n"
        if parent.lb_border_radius_disabled.value() > 0:
            style += f"\tborder-radius: {parent.lb_border_radius_disabled.value()}px;\n"

        style += "}"  # End of QLabel disabled pseudo-state

    # QLabel build and apply the stylesheet
    parent.lb_stylesheet.clear()
    if style:
        lines = style.splitlines()
        for line in lines:
            parent.lb_stylesheet.appendPlainText(line)
        parent.label.setStyleSheet(style)


def clear_stylesheet(parent):
    parent.lb_normal = False

    pseudo_states = ["normal", "hover", "disabled"]

    # set all the variables to False
    for item in pseudo_states:
        setattr(parent, f"lb_{item}", False)  # build section flag
        setattr(parent, f"lb_fg_color_sel_{item}", False)
        setattr(parent, f"lb_bg_color_sel_{item}", False)
        setattr(parent, f"lb_border_color_sel_{item}", False)

    # clear all the colors
    for item in pseudo_states:
        label = getattr(parent, f"lb_fg_color_{item}").property("label")
        getattr(parent, label).setStyleSheet("background-color: none;")
        label = getattr(parent, f"lb_bg_color_{item}").property("label")
        getattr(parent, label).setStyleSheet("background-color: none;")
        label = getattr(parent, f"lb_border_color_{item}").property("label")
        getattr(parent, label).setStyleSheet("background-color: none;")

    # set border to none and 0
    for item in pseudo_states:
        getattr(parent, f"lb_border_type_{item}").setCurrentIndex(0)
        getattr(parent, f"lb_border_width_{item}").setValue(0)
        getattr(parent, f"lb_border_radius_{item}").setValue(0)

    # clear the font variables
    parent.lb_font_family = False
    parent.lb_font_size = False
    parent.lb_font_weight = False
    parent.lb_font_style = False
    parent.lb_font_italic = False

    parent.lb_min_width_normal.setValue(0)
    parent.lb_min_height_normal.setValue(0)
    parent.lb_max_width_normal.setValue(0)
    parent.lb_max_height_normal.setValue(0)
    parent.lb_padding_normal.setValue(0)
    parent.lb_padding_left_normal.setValue(0)
    parent.lb_padding_right_normal.setValue(0)
    parent.lb_padding_top_normal.setValue(0)
    parent.lb_padding_top_normal.setValue(0)
    parent.lb_margin_normal.setValue(0)
    parent.lb_margin_left_normal.setValue(0)
    parent.lb_margin_right_normal.setValue(0)
    parent.lb_margin_top_normal.setValue(0)
    parent.lb_margin_top_normal.setValue(0)

    parent.lb_stylesheet.clear()
    parent.label.setStyleSheet("")
