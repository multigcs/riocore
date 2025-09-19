from functools import partial


def startup(parent):
    parent.gr_first_sel_color = False
    parent.gr_second_sel_color = False
    parent.gr_third_sel_color = False
    parent.gr_fourth_sel_color = False

    directions = [
        ("Left > Right", [0, 0, 1, 0]),
        ("Right > Left", [1, 0, 0, 0]),
        ("Top > Bottom", [0, 0, 0, 1]),
        ("Bottom > Top", [0, 1, 0, 0]),
        ("LL > UR", [0, 1, 1, 0]),
        ("UL > LR", [0, 0, 1, 1]),
        ("UR > LL", [1, 0, 0, 1]),
        ("LR > UL", [1, 1, 0, 0]),
    ]
    parent.gradiant_direction.addItem("Select Direction", userData=False)
    for text, data in directions:
        parent.gradiant_direction.addItem(text, userData=data)

    # parent.gradiant_direction.currentIndexChanged.connect(partial(index_changed, parent))
    parent.gr_first_color.clicked.connect(parent.color_dialog)
    parent.gr_second_color.clicked.connect(parent.color_dialog)
    parent.gr_third_color.clicked.connect(parent.color_dialog)
    parent.gr_fourth_color.clicked.connect(parent.color_dialog)

    parent.gr_apply.clicked.connect(partial(apply_style, parent))


def apply_style(parent):
    color_1 = parent.gr_first_sel_color
    color_2 = parent.gr_second_sel_color
    color_3 = parent.gr_third_sel_color
    color_4 = parent.gr_fourth_sel_color

    c1_start = parent.qr_stop_first_start.cleanText()
    c1_end = parent.qr_stop_first_end.cleanText()
    c2_start = parent.qr_stop_second_start.cleanText()
    c2_end = parent.qr_stop_second_end.cleanText()
    c3_start = parent.qr_stop_third_start.cleanText()
    c3_end = parent.qr_stop_third_end.cleanText()
    c4_start = parent.qr_stop_fourth_start.cleanText()
    c4_end = parent.qr_stop_fourth_end.cleanText()

    if parent.gradiant_direction.currentData() and color_1:
        x1 = parent.gradiant_direction.currentData()[0]
        y1 = parent.gradiant_direction.currentData()[1]
        x2 = parent.gradiant_direction.currentData()[2]
        y2 = parent.gradiant_direction.currentData()[3]

        style = "QWidget {\n"
        style += "\tbackground: QLinearGradient(\n"
        style += f"\tx1: {x1}, y1: {y1}, x2: {x2}, y2: {y2},\n"

        style += f"\tstop: {c1_start} {color_1}"
        if c1_end != "0.00":
            style += f",\n\tstop: {c1_end} {color_1}"

        style += f",\n\tstop: {c2_start} {color_2}"
        if c2_end != "0.00":
            style += f",\n\tstop: {c2_end} {color_2}"

        if color_3:
            style += f",\n\tstop: {c3_start} {color_3}"
            if c3_end != "0.00":
                style += f",\n\tstop: {c3_end} {color_3}"

        if color_4:
            style += f",\n\tstop: {c4_start} {color_4}"
            if c4_end != "0.00":
                style += f",\n\tstop: {c4_end} {color_4}"

        style += ");\n"
        style += "}"

        """
		QLabel {
			background: QLinearGradient( x1: 0, y1: 1, x2: 0, y2: 0,
			stop: 0 green, stop: 0.5 yellow,stop: 1 red);
		}
		"""

        # stop: 0 green, stop: 0.5 yellow,stop: 1 red);

        parent.gr_stylesheet.clear()
        parent.gr_stylesheet.setPlainText(style)
        parent.gr_lb.setStyleSheet(style)
        parent.gr_pushbutton.setStyleSheet(style)
        parent.gr_radiobutton.setStyleSheet(style)
        parent.gr_checkbox.setStyleSheet(style)
        parent.gr_progressbar.setStyleSheet(style)
        parent.gr_label.setStyleSheet(style)


def index_changed(parent, index):
    data = parent.gradiant_direction.itemData(index)
    print(f"Selected item: {parent.gradiant_direction.currentText()}, Data: {data}")

    """
	data_list = [
		("Item 1", 10), 
		("Item 2", 20), 
		("Item 3", 30)
	]

	for text, data in data_list:
		self.combo_box.addItem(text, userData=data)
	"""
