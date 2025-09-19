from PyQt6.QtCore import Qt, pyqtProperty, QPointF
from PyQt6.QtGui import QRadialGradient, QBrush, QPainter
from PyQt6.QtWidgets import QPushButton, QLabel


class IndicatorButton(QPushButton):
    _led = False

    def __init__(self, **kwargs):
        super().__init__()
        self.setText(kwargs["text"])
        self._diameter = kwargs["diameter"]
        self._top_offset = kwargs["top_offset"]
        self._right_offset = kwargs["right_offset"]
        self._on_color = kwargs["on_color"]
        self._off_color = kwargs["off_color"]

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        size = self.rect()
        x_center = size.width() - ((self._diameter / 2) + self._right_offset)
        y_center = (self._diameter / 2) + self._top_offset
        x = size.width() - self._diameter - self._right_offset
        y = self._top_offset
        gradient = QRadialGradient(x + self._diameter / 2, y + self._diameter / 2, self._diameter * 0.4, self._diameter * 0.4, self._diameter * 0.4)
        gradient.setColorAt(0, Qt.GlobalColor.white)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        if self._led:
            gradient.setColorAt(1, self._on_color)
            painter.setBrush(QBrush(gradient))
            painter.setPen(self._on_color)
            # Draws the ellipse positioned at center with radii rx and ry.
            painter.drawEllipse(QPointF(x_center, y_center), self._diameter / 2, self._diameter / 2)
        else:
            gradient.setColorAt(1, self._off_color)
            painter.setBrush(QBrush(gradient))
            painter.setPen(self._off_color)
            painter.drawEllipse(QPointF(x_center, y_center), self._diameter / 2, self._diameter / 2)

    def setLed(self, val):
        self._led = val
        self.update()

    def getLed(self):
        self.update()
        return self._led

    led = pyqtProperty(bool, getLed, setLed)


class IndicatorLabel(QLabel):
    _led = False

    def __init__(self, **kwargs):
        super().__init__()
        self.setText(kwargs["text"])
        self._diameter = kwargs["diameter"]
        self._top_offset = kwargs["top_offset"]
        self._right_offset = kwargs["right_offset"]
        self._on_color = kwargs["on_color"]
        self._off_color = kwargs["off_color"]

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        size = self.rect()
        x_center = size.width() - ((self._diameter / 2) + self._right_offset)
        y_center = (self._diameter / 2) + self._top_offset
        x = size.width() - self._diameter - self._right_offset
        y = self._top_offset
        gradient = QRadialGradient(x + self._diameter / 2, y + self._diameter / 2, self._diameter * 0.4, self._diameter * 0.4, self._diameter * 0.4)
        gradient.setColorAt(0, Qt.GlobalColor.white)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        if self._led:
            gradient.setColorAt(1, self._on_color)
            painter.setBrush(QBrush(gradient))
            painter.setPen(self._on_color)
            # Draws the ellipse positioned at center with radii rx and ry.
            painter.drawEllipse(QPointF(x_center, y_center), self._diameter / 2, self._diameter / 2)
        else:
            gradient.setColorAt(1, self._off_color)
            painter.setBrush(QBrush(gradient))
            painter.setPen(self._off_color)
            painter.drawEllipse(QPointF(x_center, y_center), self._diameter / 2, self._diameter / 2)

    def setLed(self, val):
        self._led = val
        self.update()

    def getLed(self):
        self.update()
        return self._led

    led = pyqtProperty(bool, getLed, setLed)
