from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDial,
    QProgressBar,
    QDoubleSpinBox,
    QSlider,
    QRadioButton,
    QGroupBox,
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from PyQt5.QtGui import QPainter, QPen, QPolygonF, QPainterPath, QFont
from PyQt5.QtCore import QPointF, QRectF
import math

try:
    from lxml import etree
except Exception:
    etree = None
    print("INFO: can not loat lxml")


class MyGauge(QWidget):
    def __init__(
        self,
        text="",
        subtext="",
        size=150,
        vmin=0.0,
        vmax=100.0,
        value=0.0,
        steps=10,
        start_angle=-210.0,
        end_angle=30.0,
        parent=None,
    ):
        super().__init__(parent)
        self.vmin = vmin
        self.vmax = vmax
        self.value = value
        self.steps = steps
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.angle_range = self.end_angle - self.start_angle
        self.setMinimumSize(size, size)
        self.text = text
        self.subtext = subtext

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            rect = self.rect()
            center = rect.center()
            radius = min(rect.width(), rect.height()) / 2 - 2
            painter.translate(center)
            self.drawArc(painter, radius)
            self.drawTicks(painter, radius)
            self.drawNumbers(painter, radius)
            self.drawText(painter)
            self.drawNeedle(painter, radius)

        except Exception as err:
            print(f"ERROR (VCP): {err}")

    def drawArc(self, painter: QPainter, radius):
        painter.save()
        path = QPainterPath()
        arc_rect = QRectF(-radius, -radius, 2 * radius, 2 * radius)
        start_angle_normalized = self.start_angle % 360
        startAngle = -start_angle_normalized
        spanAngle = -(self.angle_range)
        path.arcMoveTo(arc_rect, startAngle)
        path.arcTo(arc_rect, startAngle, spanAngle)
        painter.setPen(QPen(Qt.black, 1))
        painter.drawPath(path)
        painter.restore()

    def drawTicks(self, painter: QPainter, radius):
        painter.save()
        angle_step = self.angle_range / self.steps
        for i in range(self.steps + 1):
            pen = QPen(Qt.black, 1)
            painter.save()
            painter.setPen(pen)
            angle = self.start_angle + i * angle_step
            rad = math.radians(angle)
            x1 = (radius - 5) * math.cos(rad)
            y1 = (radius - 5) * math.sin(rad)
            x2 = radius * math.cos(rad)
            y2 = radius * math.sin(rad)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            painter.restore()

        painter.restore()

    def drawNumbers(self, painter: QPainter, radius):
        painter.save()
        pen = QPen(Qt.gray, 2)
        painter.setPen(pen)
        angle_step = self.angle_range / self.steps
        font = QFont("Arial", 10)
        painter.setFont(font)
        for i in range(self.steps + 1):
            angle = self.start_angle + i * angle_step
            rad = math.radians(angle)
            val = self.vmin + i * (self.vmax - self.vmin) / self.steps
            text_rect = QRectF(-15, -15, 34, 34)
            text_x = (radius - 15) * math.cos(rad)
            text_y = (radius - 15) * math.sin(rad)
            painter.save()
            painter.translate(text_x, text_y)
            painter.drawText(text_rect, Qt.AlignCenter, f"{val:.0f}")
            painter.restore()
        painter.restore()

    def drawText(self, painter: QPainter):
        if self.text:
            text_rect = QRectF(-134, -25, 134, 25)
            painter.save()
            font = QFont("Arial", 14)
            pen = QPen(Qt.black, 2)
            painter.setPen(pen)
            painter.setPen(pen)
            painter.setFont(font)
            painter.translate(134 // 2, 0)
            painter.drawText(text_rect, Qt.AlignCenter, self.text)
            painter.restore()
        if self.subtext:
            text_rect = QRectF(-134, -25, 134, 25)
            painter.save()
            font = QFont("Arial", 11)
            pen = QPen(Qt.black, 2)
            painter.setPen(pen)
            painter.setFont(font)
            painter.translate(134 // 2, 45)
            painter.drawText(text_rect, Qt.AlignCenter, self.subtext)
            painter.restore()

    def drawNeedle(self, painter: QPainter, radius):
        value_range = self.vmax - self.vmin
        if value_range == 0:
            value_ratio = 0.0
        else:
            value_ratio = (self.value - self.vmin) / value_range
        angle = self.start_angle + value_ratio * self.angle_range
        needle = QPolygonF(
            [
                QPointF(0, -2),
                QPointF(radius - 18, 0),
                QPointF(0, 2),
            ]
        )
        painter.save()
        painter.rotate(angle)
        pen = QPen(Qt.blue, 1)
        painter.setPen(pen)
        painter.setBrush(Qt.blue)
        painter.drawPolygon(needle)
        painter.restore()


class MyVCP:
    widget_tab = None
    active_tab = None

    def __init__(self):
        self.dialog = QDialog()
        self.dialog.setWindowTitle("VCP-Preview")
        self.dialog_layout = QVBoxLayout()
        self.dialog.setLayout(self.dialog_layout)
        # self.dialog.show()

    def close(self):
        self.dialog.close()

    def toggle(self):
        if self.dialog.isVisible():
            self.hide()
        else:
            self.show()

    def show(self):
        self.dialog.show()

    def hide(self):
        self.dialog.hide()

    def load(self, filename):
        layout = self.dialog_layout

        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)

        xml = open(filename, "rb").read()
        root = etree.fromstring(xml, parser=etree.XMLParser(remove_comments=True))

        if self.widget_tab:
            index = self.widget_tab.indexOf(self.widget_tab.currentWidget())
            self.active_tab = self.widget_tab.tabText(index)

        for child in root.iterchildren():
            self.show_element(child, layout)

    def show_element(self, element, layout):
        if hasattr(self, f"show_{element.tag}"):
            getattr(self, f"show_{element.tag}")(element, layout)
        else:
            print(f"missing type: {element.tag}")
            layout.addWidget(QLabel(f"## {element.tag} ##"))

    def show_radiobutton(self, element, layout):
        choices = []
        for child in element.iterchildren():
            if child.tag == "choices":
                for name in child.text.strip("[").strip("]").split(","):
                    title = name.strip().strip("'").strip('"')
                    choices.append(title)
                    radio = QRadioButton(title)
                    layout.addWidget(radio)

    def show_scale(self, element, layout):
        orient = "HORIZONTAL"
        for child in element.iterchildren():
            if child.tag == "orient":
                orient = child.text
        if orient == "HORIZONTAL":
            slider = QSlider(Qt.Horizontal)
        else:
            slider = QSlider(Qt.Vertical)
            slider.setMinimumHeight(50)

        for child in element.iterchildren():
            if child.tag == "min":
                slider.setMinimum(float(child.text))
            if child.tag == "max":
                slider.setMaximum(float(child.text))
        layout.addWidget(slider)

    def show_bar(self, element, layout):
        bar = QProgressBar()

        for child in element.iterchildren():
            if child.tag == "min":
                bar.setMinimum(float(child.text))
            if child.tag == "max":
                bar.setMaximum(float(child.text))

        # bar.setOrientation(1)
        bar.setValue(1)
        layout.addWidget(bar)

    def show_dial(self, element, layout):
        label = QDial()
        layout.addWidget(label)

    def show_jogwheel(self, element, layout):
        label = QDial()
        layout.addWidget(label)

    def show_meter(self, element, layout):
        text = ""
        subtext = ""
        vmin = 0
        vmax = 100.0
        size = 130.0
        for child in element.iterchildren():
            if child.tag == "min_":
                vmin = float(child.text)
            if child.tag == "max_":
                vmax = float(child.text)
            if child.tag == "size":
                size = int(child.text)
            if child.tag == "text":
                text = child.text.strip('"')
            if child.tag == "subtext":
                subtext = child.text.strip('"')

        label = MyGauge(
            vmin=vmin,
            vmax=vmax,
            value=0.0,
            size=size,
            text=text,
            subtext=subtext,
        )
        layout.addWidget(label)
        layout.setContentsMargins(0, 0, 0, 0)

    def show_button(self, element, layout):
        text = ""
        for child in element.iterchildren():
            if child.tag == "text":
                text = child.text.strip('"')
        label = QPushButton(text)
        layout.addWidget(label)

    def show_checkbutton(self, element, layout):
        text = ""
        for child in element.iterchildren():
            if child.tag == "text":
                text = child.text.strip('"')
        label = QCheckBox(text)
        layout.addWidget(label)

    def show_label(self, element, layout):
        text = ""
        for child in element.iterchildren():
            if child.tag == "text":
                text = child.text.strip('"')
        label = QLabel(text)
        layout.addWidget(label)

    def show_multilabel(self, element, layout):
        text = ""
        for child in element.iterchildren():
            if child.tag == "legends":
                text = child.text.strip("[").strip("]").split(",")[0].strip("'")
                break
        label = QLabel(text)
        layout.addWidget(label)

    def show_u32(self, element, layout):
        self.show_number(element, layout)

    def show_s32(self, element, layout):
        self.show_number(element, layout)

    def show_number(self, element, layout):
        fmt = "0.1f"
        for child in element.iterchildren():
            if child.tag == "format":
                fmt = child.text.strip('"')
        label = QLabel(f"%{fmt}" % (0.00,))
        layout.addWidget(label)

    def show_spinbox(self, element, layout):
        spinbox = QDoubleSpinBox()
        layout.addWidget(spinbox)

    def show_led(self, element, layout):
        label = QLabel("*")
        layout.addWidget(label)

    def show_labelframe(self, element, layout):
        gbox_layout = QVBoxLayout()
        gbox_widget = QGroupBox()
        gbox_widget.setTitle(element.get("text", ""))
        gbox_widget.setLayout(gbox_layout)
        layout.addWidget(gbox_widget)
        for child in element.iterchildren():
            if child.tag not in {"relief", "font", "bd"}:
                self.show_element(child, gbox_layout)
        layout.addStretch()

    def show_vbox(self, element, layout):
        vbox_layout = QVBoxLayout()
        vbox_widget = QWidget()
        vbox_widget.setLayout(vbox_layout)
        layout.addWidget(vbox_widget)
        for child in element.iterchildren():
            if child.tag not in {"relief", "font", "bd"}:
                self.show_element(child, vbox_layout)
        layout.addStretch()

    def show_hbox(self, element, layout):
        hbox_layout = QHBoxLayout()
        hbox_widget = QWidget()
        hbox_widget.setLayout(hbox_layout)
        layout.addWidget(hbox_widget)
        for child in element.iterchildren():
            if child.tag not in {"relief", "font", "bd"}:
                self.show_element(child, hbox_layout)
        layout.addStretch()

    def show_tabs(self, element, layout):
        tab_names = []
        for child in element.iterchildren():
            if child.tag == "names":
                for name in child.text.strip("[").strip("]").split(","):
                    tab_names.append(name.strip().strip("'").strip('"'))

        tabwidget = QTabWidget()
        layout.addWidget(tabwidget)
        self.widget_tab = tabwidget

        tab_n = 0
        for child in element.iterchildren():
            if child.tag == "names":
                continue

            tab_inner_widget = QWidget()
            tab_inner_layout = QVBoxLayout()
            tab_inner_widget.setLayout(tab_inner_layout)
            tabwidget.addTab(tab_inner_widget, tab_names[tab_n])
            if self.active_tab == tab_names[tab_n]:
                tabwidget.setCurrentWidget(tab_inner_widget)
            tab_n += 1
            self.show_element(child, tab_inner_layout)
