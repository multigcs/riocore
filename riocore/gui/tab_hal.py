import os


from riocore.gui import halgraph

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QScrollArea,
)

from riocore.gui.widgets import (
    MyQLabel,
)


class TabHal:
    last_x = -1
    last_y = -1
    last_action = 0
    moved = 0

    def __init__(self, parent=None):
        self.parent = parent
        self.overview_img = MyQLabel(self)
        self.scroll_widget = QScrollArea()
        self.scroll_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_widget.setWidgetResizable(True)
        self.scroll_widget.setWidget(self.overview_img)
        self.graph = halgraph.HalGraph()

    def widget(self):
        return self.scroll_widget

    def timer(self):
        pass

    def update(self):
        config_name = self.parent.config.get("name")
        png_data = self.graph.png(os.path.join(self.parent.output_path, config_name, "LinuxCNC", "rio.ini"))
        if png_data:
            self.overview_img.load(png_data)

    def on_click(self, x, y):
        self.last_x = x
        self.last_y = y
        self.last_action = 1
        self.moved = 0

    def on_release(self, x, y):
        self.last_action = 0
        if not self.moved:
            if hasattr(self.graph, "on_click"):
                self.graph.on_click(x, y)
        self.moved = 0

    def on_move(self, x, y):
        if self.last_action == 1:
            xs = self.scroll_widget.horizontalScrollBar()
            ys = self.scroll_widget.verticalScrollBar()
            xs_last = xs.value()
            ys_last = ys.value()
            diff_x = x - self.last_x
            diff_y = y - self.last_y
            if abs(diff_x) > 4 or abs(diff_y) > 4:
                self.moved = 1
            xs.setValue(xs_last - diff_x)
            ys.setValue(ys_last - diff_y)
