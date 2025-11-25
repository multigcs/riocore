from functools import partial

from libflexgui import qss_checkbox, qss_label, qss_pushbutton, qss_radiobutton, qss_spinbox, qss_toolbutton


def startup(parent):
    # All
    parent.all_normal = False

    parent.all_apply_style.clicked.connect(partial(all_create_stylesheet, parent))
    parent.all_clear_style.clicked.connect(partial(clear_stylesheet, parent))

    parent.all_fg_color_normal.clicked.connect(parent.color_dialog)
    parent.all_bg_color_normal.clicked.connect(parent.color_dialog)

    parent.all_fg_color_sel_normal = False
    parent.all_bg_color_sel_normal = False

    parent.all_fg_color_hover.clicked.connect(parent.color_dialog)
    parent.all_bg_color_hover.clicked.connect(parent.color_dialog)

    parent.all_fg_color_sel_hover = False
    parent.all_bg_color_sel_hover = False

    parent.all_fg_color_checked.clicked.connect(parent.color_dialog)
    parent.all_bg_color_checked.clicked.connect(parent.color_dialog)

    parent.all_fg_color_sel_checked = False
    parent.all_bg_color_sel_checked = False

    parent.all_fg_color_disabled.clicked.connect(parent.color_dialog)
    parent.all_bg_color_disabled.clicked.connect(parent.color_dialog)

    parent.all_fg_color_sel_disabled = False
    parent.all_bg_color_sel_disabled = False


def all_create_stylesheet(parent):
    # Foreground Color Normal
    if parent.all_fg_color_sel_normal:
        color = parent.all_fg_color_sel_normal

        # QPushButton
        if not parent.pb_fg_color_sel_normal:
            parent.pb_normal = True
            label = parent.pb_fg_color_normal.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.pb_fg_color_sel_normal = color

        # QCheckBox
        if not parent.cb_fg_color_sel_normal:
            parent.cb_normal = True
            label = parent.cb_fg_color_normal.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.cb_fg_color_sel_normal = color

        # QRadioButton
        if not parent.rb_fg_color_sel_normal:
            parent.rb_normal = True
            label = parent.rb_fg_color_normal.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.rb_fg_color_sel_normal = color

        # QToolBar
        if not parent.toolbar_bg_sel_color:
            parent.tbar_normal = True
            label = parent.tbar_bg_color_normal.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.tbar_bg_sel_color = color

        # QToolButton
        if not parent.tb_fg_color_sel_normal:
            parent.tb_normal = True
            label = parent.tb_fg_color_normal.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.tb_fg_color_sel_normal = color

        # QSpinBox
        if not parent.sb_fg_color_sel_normal:
            parent.sb_normal = True
            label = parent.sb_fg_color_normal.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.sb_fg_color_sel_normal = color

        # QLabel
        if not parent.lb_fg_color_sel_normal:
            parent.lb_normal = True
            label = parent.lb_fg_color_normal.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.lb_fg_color_sel_normal = color

    # Background Color Normal
    if parent.all_bg_color_sel_normal:
        color = parent.all_bg_color_sel_normal

        # QPushButton
        if not parent.pb_bg_color_sel_normal:
            parent.pb_normal = True
            label = parent.pb_bg_color_normal.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.pb_bg_color_sel_normal = color

        # QCheckBox
        if not parent.cb_bg_color_sel_normal:
            parent.cb_normal = True
            label = parent.cb_bg_color_normal.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.cb_bg_color_sel_normal = color

        # QRadioButton
        if not parent.rb_bg_color_sel_normal:
            parent.rb_normal = True
            label = parent.rb_bg_color_normal.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.rb_bg_color_sel_normal = color

        # QToolButton
        if not parent.tb_bg_color_sel_normal:
            parent.tb_normal = True
            label = parent.tb_bg_color_normal.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.tb_bg_color_sel_normal = color

        # QSpinBox
        if not parent.sb_bg_color_sel_normal:
            parent.sb_normal = True
            label = parent.sb_bg_color_normal.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.sb_bg_color_sel_normal = color

        # QLabel
        if not parent.lb_bg_color_sel_normal:
            parent.lb_normal = True
            label = parent.lb_bg_color_normal.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.lb_bg_color_sel_normal = color

    # Foreground Color Hover
    if parent.all_fg_color_sel_hover:
        color = parent.all_fg_color_sel_hover

        # QPushButton
        if not parent.pb_fg_color_sel_hover:
            parent.pb_hover = True
            label = parent.pb_fg_color_hover.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.pb_fg_color_sel_hover = color

        # QCheckBox
        if not parent.cb_fg_color_sel_hover:
            parent.cb_hover = True
            label = parent.cb_fg_color_hover.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.cb_fg_color_sel_hover = color

        # QRadioButton
        if not parent.rb_fg_color_sel_hover:
            parent.rb_hover = True
            label = parent.rb_fg_color_hover.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.rb_fg_color_sel_hover = color

        # QToolButton
        if not parent.tb_fg_color_sel_hover:
            parent.tb_hover = True
            label = parent.tb_fg_color_hover.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.tb_fg_color_sel_hover = color

        # QSpinBox
        if not parent.sb_fg_color_sel_hover:
            parent.sb_hover = True
            label = parent.sb_fg_color_hover.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.sb_fg_color_sel_hover = color

        # QLabel
        if not parent.lb_fg_color_sel_hover:
            parent.lb_hover = True
            label = parent.lb_fg_color_hover.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.lb_fg_color_sel_hover = color

    # Background Color Hover
    if parent.all_bg_color_sel_hover:
        color = parent.all_bg_color_sel_hover

        # QPushButton
        if not parent.pb_bg_color_sel_hover:
            parent.pb_hover = True
            label = parent.pb_bg_color_hover.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.pb_bg_color_sel_hover = color

        # QCheckBox
        if not parent.cb_bg_color_sel_hover:
            parent.cb_hover = True
            label = parent.cb_bg_color_hover.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.cb_bg_color_sel_hover = color

        # QRadioButton
        if not parent.rb_bg_color_sel_hover:
            parent.rb_hover = True
            label = parent.rb_bg_color_hover.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.rb_bg_color_sel_hover = color

        # QToolButton
        if not parent.tb_bg_color_sel_hover:
            parent.tb_hover = True
            label = parent.tb_bg_color_hover.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.tb_bg_color_sel_hover = color

        # QSpinBox
        if not parent.sb_bg_color_sel_hover:
            parent.sb_hover = True
            label = parent.sb_bg_color_hover.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.sb_bg_color_sel_hover = color

        # QLabel
        if not parent.lb_bg_color_sel_hover:
            parent.lb_hover = True
            label = parent.lb_bg_color_hover.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.lb_bg_color_sel_hover = color

    # Foreground Color Checked
    if parent.all_fg_color_sel_checked:
        color = parent.all_fg_color_sel_checked

        # QPushButton
        if not parent.pb_fg_color_sel_checked:
            parent.pb_checked = True
            label = parent.pb_fg_color_checked.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.pb_fg_color_sel_checked = color

        # QCheckBox
        if not parent.cb_fg_color_sel_checked:
            parent.cb_checked = True
            label = parent.cb_fg_color_checked.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.cb_fg_color_sel_checked = color

        # QRadioButton
        if not parent.rb_fg_color_sel_checked:
            parent.rb_checked = True
            label = parent.rb_fg_color_checked.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.rb_fg_color_sel_checked = color

        # QToolButton
        if not parent.tb_fg_color_sel_checked:
            parent.tb_checked = True
            label = parent.tb_fg_color_checked.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.tb_fg_color_sel_checked = color

    # Background Color Checked
    if parent.all_bg_color_sel_checked:
        color = parent.all_bg_color_sel_checked

        # QPushButton
        if not parent.pb_bg_color_sel_checked:
            parent.pb_checked = True
            label = parent.pb_bg_color_checked.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.pb_bg_color_sel_checked = color

        # QCheckBox
        if not parent.cb_bg_color_sel_checked:
            parent.cb_checked = True
            label = parent.cb_bg_color_checked.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.cb_bg_color_sel_checked = color

        # QRadioButton
        if not parent.rb_bg_color_sel_checked:
            parent.rb_checked = True
            label = parent.rb_bg_color_checked.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.rb_bg_color_sel_checked = color

        # QToolButton
        if not parent.tb_bg_color_sel_checked:
            parent.tb_checked = True
            label = parent.tb_bg_color_checked.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.tb_bg_color_sel_checked = color

    # Foreground Color Disabled
    if parent.all_fg_color_sel_disabled:
        color = parent.all_fg_color_sel_disabled

        # QPushButton
        if not parent.pb_fg_color_sel_disabled:
            parent.pb_disabled = True
            label = parent.pb_fg_color_disabled.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.pb_fg_color_sel_disabled = color

        # QCheckBox
        if not parent.cb_fg_color_sel_disabled:
            parent.cb_disabled = True
            label = parent.cb_fg_color_disabled.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.cb_fg_color_sel_disabled = color

        # QRadioButton
        if not parent.rb_fg_color_sel_disabled:
            parent.rb_disabled = True
            label = parent.rb_fg_color_disabled.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.rb_fg_color_sel_disabled = color

        # QToolButton
        if not parent.tb_fg_color_sel_disabled:
            parent.tb_disabled = True
            label = parent.tb_fg_color_disabled.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.tb_fg_color_sel_disabled = color

        # QSpinBox
        if not parent.sb_fg_color_sel_disabled:
            parent.sb_disabled = True
            label = parent.sb_fg_color_disabled.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.sb_fg_color_sel_disabled = color

        # QLabel
        if not parent.lb_fg_color_sel_disabled:
            parent.lb_disabled = True
            label = parent.lb_fg_color_disabled.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.lb_fg_color_sel_disabled = color

    # Background Color Disabled
    if parent.all_bg_color_sel_disabled:
        color = parent.all_bg_color_sel_disabled

        # QPushButton
        if not parent.pb_bg_color_sel_disabled:
            parent.pb_disabled = True
            label = parent.pb_bg_color_disabled.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.pb_bg_color_sel_disabled = color

        # QCheckBox
        if not parent.cb_bg_color_sel_disabled:
            parent.cb_disabled = True
            label = parent.cb_bg_color_disabled.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.cb_bg_color_sel_disabled = color

        # QRadioButton
        if not parent.rb_bg_color_sel_disabled:
            parent.rb_disabled = True
            label = parent.rb_bg_color_disabled.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.rb_bg_color_sel_disabled = color

        # QToolButton
        if not parent.tb_bg_color_sel_disabled:
            parent.tb_disabled = True
            label = parent.tb_bg_color_disabled.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.tb_bg_color_sel_disabled = color

        # QSpinBox
        if not parent.sb_bg_color_sel_disabled:
            parent.sb_disabled = True
            label = parent.sb_bg_color_disabled.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.sb_bg_color_sel_disabled = color

        # QLabel
        if not parent.lb_bg_color_sel_disabled:
            parent.lb_disabled = True
            label = parent.lb_bg_color_disabled.property("label")
            getattr(parent, label).setStyleSheet(f"background-color: {color};")
            parent.lb_bg_color_sel_disabled = color

    qss_pushbutton.create_stylesheet(parent)
    qss_checkbox.create_stylesheet(parent)
    qss_radiobutton.create_stylesheet(parent)
    qss_toolbutton.create_stylesheet(parent)
    qss_spinbox.create_stylesheet(parent)
    qss_label.create_stylesheet(parent)


def clear_stylesheet(parent):
    qss_pushbutton.clear_stylesheet(parent)
    qss_checkbox.clear_stylesheet(parent)
    qss_radiobutton.clear_stylesheet(parent)
    qss_toolbutton.clear_stylesheet(parent)
    qss_spinbox.clear_stylesheet(parent)
    qss_label.clear_stylesheet(parent)

    parent.all_fg_color_lb.setStyleSheet("")
    parent.all_bg_color_lb.setStyleSheet("")
    parent.all_fg_color_hover_lb.setStyleSheet("")
    parent.all_bg_color_hover_lb.setStyleSheet("")
    parent.all_fg_color_checked_lb.setStyleSheet("")
    parent.all_bg_color_checked_lb.setStyleSheet("")
    parent.all_fg_color_disabled_lb.setStyleSheet("")
    parent.all_bg_color_disabled_lb.setStyleSheet("")
