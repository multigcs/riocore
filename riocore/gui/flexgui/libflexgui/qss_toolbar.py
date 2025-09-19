from functools import partial

from libflexgui import qss_toolbutton


def startup(parent):
    # QToolBar
    parent.tbar_normal = False
    parent.tbar_apply_style.clicked.connect(partial(tbar_create_stylesheet, parent))

    parent.tbar_bg_color_normal.clicked.connect(parent.color_dialog)
    parent.toolbar_spacing.valueChanged.connect(partial(spacing, parent))
    parent.tbar_border_color_normal.clicked.connect(parent.color_dialog)
    # variables to build sections in the stylesheet
    parent.build_toolbar = False

    parent.toolbar_bg_sel_color = False
    parent.toolbar_border_sel_color = False

    border_types = ["none", "solid", "dashed", "dotted", "double", "groove", "ridge", "inset", "outset"]
    parent.tbar_border_type.addItems(border_types)

    parent.tbar_padding_normal.valueChanged.connect(parent.padding)
    parent.tbar_padding_left_normal.valueChanged.connect(parent.padding)
    parent.tbar_padding_right_normal.valueChanged.connect(parent.padding)
    parent.tbar_padding_top_normal.valueChanged.connect(parent.padding)
    parent.tbar_padding_bottom_normal.valueChanged.connect(parent.padding)

    parent.tbar_margin_normal.valueChanged.connect(parent.margin)
    parent.tbar_margin_left_normal.valueChanged.connect(parent.margin)
    parent.tbar_margin_right_normal.valueChanged.connect(parent.margin)
    parent.tbar_margin_top_normal.valueChanged.connect(parent.margin)
    parent.tbar_margin_bottom_normal.valueChanged.connect(parent.margin)


######### QToolBar Stylesheet #########


def tbar_create_stylesheet(parent):
    style = False

    # QToolBar
    if parent.tbar_normal:
        style = "QToolBar {\n"

        # background color and spacing
        if parent.toolbar_bg_sel_color:
            style += f"\tbackground: {parent.toolbar_bg_sel_color};\n"
        if parent.toolbar_spacing.value() > 0:
            style += f"\tspacing: {parent.toolbar_spacing.value()}px;\n"

        # border
        border_type = parent.tbar_border_type.currentText()
        if border_type != "none":
            style += f"\tborder-style: {border_type};\n"
            if parent.tbar_border_color_normal:
                style += f"\tborder-color: {parent.toolbar_border_sel_color};\n"
            if parent.tbar_border_width.value() > 0:
                style += f"\tborder-width: {parent.tbar_border_width.value()}px;\n"
            if parent.tbar_border_radius.value() > 0:
                style += f"\tborder-radius: {parent.tbar_border_radius.value()}px;\n"

        # padding
        if parent.tbar_padding_normal.value() > 0:
            style += f"\tpadding: {parent.tbar_padding_normal.value()};\n"
        if parent.tbar_padding_left_normal.value() > 0:
            style += f"\tpadding-left: {parent.tbar_padding_left_normal.value()};\n"
        if parent.tbar_padding_right_normal.value() > 0:
            style += f"\tpadding-right: {parent.tbar_padding_right_normal.value()};\n"
        if parent.tbar_padding_top_normal.value() > 0:
            style += f"\tpadding-top: {parent.tbar_padding_top_normal.value()};\n"
        if parent.tbar_padding_bottom_normal.value() > 0:
            style += f"\tpadding-bottom: {parent.tbar_padding_bottom_normal.value()};\n"

        # margin
        if parent.tbar_margin_normal.value() > 0:
            style += f"\tmargin: {parent.tbar_margin_normal.value()};\n"
        if parent.tbar_margin_left_normal.value() > 0:
            style += f"\tmargin-left: {parent.tbar_margin_left_normal.value()};\n"
        if parent.tbar_margin_right_normal.value() > 0:
            style += f"\tmargin-right: {parent.tbar_margin_right_normal.value()};\n"
        if parent.tbar_margin_top_normal.value() > 0:
            style += f"\tmargin-top: {parent.tbar_margin_top_normal.value()};\n"
        if parent.tbar_margin_bottom_normal.value() > 0:
            style += f"\tmargin-bottom: {parent.tbar_margin_bottom_normal.value()};\n"

        style += "}\n"  # End of QToolBar

    # check for toolbutton style set
    if parent.sender().objectName() == "tbar_apply_style":
        if parent.tb_normal:
            style += qss_toolbutton.tb_create_stylesheet(parent)

    parent.tbar_stylesheet.clear()
    if style:
        lines = style.splitlines()
        for line in lines:
            parent.tbar_stylesheet.appendPlainText(line)

        parent.toolBar.setStyleSheet(style)

    if parent.sender().objectName() == "tb_apply_style":
        return style


def spacing(parent):
    if parent.sender().value() > 0:
        parent.tbar_normal = True
