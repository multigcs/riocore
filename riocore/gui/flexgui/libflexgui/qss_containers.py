from functools import partial


def startup(parent):
    border_types = ["none", "solid", "dashed", "dotted", "double", "groove", "ridge", "inset", "outset"]

    ######### QMainWindow Setup #########
    parent.mw_normal = False
    parent.mw_border_color_sel_normal = False

    parent.mw_fg_color_normal.clicked.connect(parent.color_dialog)
    parent.mw_bg_color_normal.clicked.connect(parent.color_dialog)
    parent.mw_border_color_normal.clicked.connect(parent.color_dialog)

    parent.mw_fg_color_sel = False
    parent.mw_bg_color_sel = False

    parent.mw_apply_style.clicked.connect(partial(create_mw_stylesheet, parent))
    parent.mw_clear_style.clicked.connect(partial(clear_mw_stylesheet, parent))

    parent.mw_border_type_normal.addItems(border_types)

    parent.mw_padding_normal.valueChanged.connect(parent.padding)
    parent.mw_padding_left_normal.valueChanged.connect(parent.padding)
    parent.mw_padding_right_normal.valueChanged.connect(parent.padding)
    parent.mw_padding_top_normal.valueChanged.connect(parent.padding)
    parent.mw_padding_bottom_normal.valueChanged.connect(parent.padding)

    parent.mw_margin_normal.valueChanged.connect(parent.margin)
    parent.mw_margin_left_normal.valueChanged.connect(parent.margin)
    parent.mw_margin_right_normal.valueChanged.connect(parent.margin)
    parent.mw_margin_top_normal.valueChanged.connect(parent.margin)
    parent.mw_margin_bottom_normal.valueChanged.connect(parent.margin)

    ######### QFrame Setup #########
    parent.fr_normal = False

    parent.fr_fg_color_normal.clicked.connect(parent.color_dialog)
    parent.fr_bg_color_normal.clicked.connect(parent.color_dialog)

    parent.fr_fg_color_sel = False
    parent.fr_bg_color_sel = False

    parent.fr_apply_style.clicked.connect(partial(create_fr_stylesheet, parent))
    parent.fr_clear_style.clicked.connect(partial(clear_fr_stylesheet, parent))

    ######### QGroupBox Setup #########
    parent.gb_normal = False

    parent.gb_fg_color_normal.clicked.connect(parent.color_dialog)
    parent.gb_bg_color_normal.clicked.connect(parent.color_dialog)

    parent.gb_fg_color_sel = False
    parent.gb_bg_color_sel = False

    parent.gb_apply_style.clicked.connect(partial(create_gb_stylesheet, parent))
    parent.gb_clear_style.clicked.connect(partial(clear_gb_stylesheet, parent))


######### QMainWindow Stylesheet #########


def create_mw_stylesheet(parent):
    style = False
    style_print = "QMainWindow"
    style_apply = "QLable"

    # QMainWindow normal pseudo-state
    if parent.mw_normal:
        style = "replace_here {\n"

        # color
        if parent.mw_fg_color_sel:
            style += f"\tcolor: {parent.mw_fg_color_sel};\n"
        if parent.mw_bg_color_sel:
            style += f"\tbackground-color: {parent.mw_bg_color_sel};\n"

        # border
        border_type_normal = parent.mw_border_type_normal.currentText()
        if border_type_normal != "none":
            style += f"\tborder-style: {border_type_normal};\n"
        if parent.mw_border_color_sel_normal:
            style += f"\tborder-color: {parent.mw_border_color_sel_normal};\n"
        if parent.mw_border_width_normal.value() > 0:
            style += f"\tborder-width: {parent.mw_border_width_normal.value()}px;\n"
        if parent.mw_border_radius_normal.value() > 0:
            style += f"\tborder-radius: {parent.mw_border_radius_normal.value()}px;\n"

        # padding
        if parent.mw_padding_normal.value() > 0:
            style += f"\tpadding: {parent.mw_padding_normal.value()};\n"
        if parent.mw_padding_left_normal.value() > 0:
            style += f"\tpadding-left: {parent.mw_padding_left_normal.value()};\n"
        if parent.mw_padding_right_normal.value() > 0:
            style += f"\tpadding-right: {parent.mw_padding_right_normal.value()};\n"
        if parent.mw_padding_top_normal.value() > 0:
            style += f"\tpadding-top: {parent.mw_padding_top_normal.value()};\n"
        if parent.mw_padding_bottom_normal.value() > 0:
            style += f"\tpadding-bottom: {parent.mw_padding_bottom_normal.value()};\n"

        # margin
        if parent.mw_margin_normal.value() > 0:
            style += f"\tmargin: {parent.mw_margin_normal.value()};\n"
        if parent.mw_margin_left_normal.value() > 0:
            style += f"\tmargin-left: {parent.mw_margin_left_normal.value()};\n"
        if parent.mw_margin_right_normal.value() > 0:
            style += f"\tmargin-right: {parent.mw_margin_right_normal.value()};\n"
        if parent.mw_margin_top_normal.value() > 0:
            style += f"\tmargin-top: {parent.mw_margin_top_normal.value()};\n"
        if parent.mw_margin_bottom_normal.value() > 0:
            style += f"\tmargin-bottom: {parent.mw_margin_bottom_normal.value()};\n"

        style += "}"  # End of QMainWindow normal pseudo-state

    # QMainWindow build and apply the stylesheet
    parent.mw_stylesheet.clear()
    if style:
        stylesheet = style.replace("replace_here", style_print)
        lines = stylesheet.splitlines()
        for line in lines:
            parent.mw_stylesheet.appendPlainText(line)

        parent.mw_frame.setStyleSheet(style.replace("replace_here", style_apply))


def clear_mw_stylesheet(parent):
    parent.mw_normal = False
    parent.mw_fg_color_sel = False
    parent.mw_bg_color_sel = False
    parent.mw_fg_color_lb.setStyleSheet("")
    parent.mw_bg_color_lb.setStyleSheet("")
    parent.mw_frame.setStyleSheet("")
    parent.mw_stylesheet.clear()


######### QFrame Stylesheet #########


def create_fr_stylesheet(parent):
    style = False

    # QMainWindow normal pseudo-state
    if parent.fr_normal:
        style = "QFrame {\n"

        # color
        if parent.fr_fg_color_sel:
            style += f"\tcolor: {parent.fr_fg_color_sel};\n"
        if parent.fr_bg_color_sel:
            style += f"\tbackground-color: {parent.fr_bg_color_sel};\n"

        style += "}"  # End of QMainWindow normal pseudo-state

    # QMainWindow build and apply the stylesheet
    parent.fr_stylesheet.clear()
    if style:
        lines = style.splitlines()
        for line in lines:
            parent.fr_stylesheet.appendPlainText(line)

        parent.fr_frame.setStyleSheet(style)


def clear_fr_stylesheet(parent):
    parent.fr_normal = False
    parent.fr_fg_color_sel = False
    parent.fr_bg_color_sel = False
    parent.fr_fg_color_lb.setStyleSheet("")
    parent.fr_bg_color_lb.setStyleSheet("")
    parent.fr_frame.setStyleSheet("")
    parent.fr_stylesheet.clear()


######### QGroupBox Stylesheet #########


def create_gb_stylesheet(parent):
    style = False

    # QMainWindow normal pseudo-state
    if parent.gb_normal:
        style = "QGroupBox {\n"

        # color
        if parent.gb_fg_color_sel:
            style += f"\tcolor: {parent.gb_fg_color_sel};\n"
        if parent.gb_bg_color_sel:
            style += f"\tbackground-color: {parent.gb_bg_color_sel};\n"

        style += "}"  # End of QMainWindow normal pseudo-state

    # QMainWindow build and apply the stylesheet
    parent.gb_stylesheet.clear()
    if style:
        lines = style.splitlines()
        for line in lines:
            parent.gb_stylesheet.appendPlainText(line)

        parent.gb_groupbox.setStyleSheet(style)


def clear_gb_stylesheet(parent):
    parent.gb_normal = False
    parent.gb_fg_color_sel = False
    parent.gb_bg_color_sel = False
    parent.gb_fg_color_lb.setStyleSheet("")
    parent.gb_bg_color_lb.setStyleSheet("")
    parent.gb_groupbox.setStyleSheet("")
    parent.gb_stylesheet.clear()
