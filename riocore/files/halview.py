import argparse
import os
import sys
import uuid
import xml.etree.ElementTree as ET

import hal

from PyQt5.QtCore import QPoint, QPointF, QRectF, QTimer, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QMouseEvent, QPainter, QPainterPath, QPen
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsItem,
    QGraphicsPathItem,
    QGraphicsScene,
    QGraphicsView,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

if os.path.isfile(os.path.join("riocore", "__init__.py")):
    sys.path.insert(0, os.getcwd())

from riocore.gui import halgraph

grid_size = 10
grid_color = QColor(150, 150, 150)
max_size = 99999


# generate different colors with different styles
colors = []
cn = 15
for s in (Qt.SolidLine, Qt.DashLine, Qt.DotLine, Qt.DashDotLine, Qt.DashDotDotLine):
    o = 0
    for i in range(cn):
        hue = i / cn + 1 / cn * o / 10
        lightness = 0.7
        saturation = 0.9 / 5 * (10 - o) / 2
        color = QColor.fromHslF(hue, saturation, lightness)
        colors.append((color, s))


class NodeEdge(QGraphicsPathItem):
    width = 3
    width_selected = 6

    def __init__(self, scene, source_node, source_port, des_node, des_port):
        super().__init__(None)
        self.scene = scene
        self._source_node = source_node
        self._source_port = source_port
        self._target_node = des_node
        self._target_port = des_port
        self.color = Qt.GlobalColor.gray
        self.style = Qt.SolidLine
        self._pen_default = QPen(self.color)
        self._pen_default.setWidthF(2)
        self.setZValue(5)
        self.setFlags(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.update_edge_path()
        self.hover = False

    def paint(self, painter: QPainter, option, widget):
        self._pen_default = QPen(self.color)
        if self.hover:
            self._pen_default.setWidthF(self.width_selected)
        else:
            self._pen_default.setWidthF(self.width)
        painter.setPen(self._pen_default)
        self.update_edge_path()
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())

    def update_edge_path(self):
        if not self._source_node or not self._target_node:
            return
        pos1 = self._source_node.port_pos(self._source_port, self._target_node)
        pos2 = self._target_node.port_pos(self._target_port, self._source_node)
        if pos1.x() > pos2.x():
            pos2 = self._source_node.port_pos(self._source_port, self._target_node)
            pos1 = self._target_node.port_pos(self._target_port, self._source_node)

        path = QPainterPath(pos1)

        ctr_offset_y1, ctr_offset_y2 = pos1.y(), pos2.y()
        tangent = abs(ctr_offset_y1 - ctr_offset_y2)

        max_height = 2
        tangent = min(tangent, max_height)
        ctr_offset_y1 -= tangent
        ctr_offset_y2 += tangent

        ctr_point1 = QPointF(pos1.x(), ctr_offset_y1)
        ctr_point2 = QPointF(pos2.x(), ctr_offset_y2)
        path.cubicTo(ctr_point1, ctr_point2, pos2)
        self.setPath(path)

    def hoverEnterEvent(self, event):
        self.hover = True
        self.update()

    def hoverLeaveEvent(self, event):
        self.hover = False
        self.update()


class MyNode(QGraphicsItem):
    name = ""
    radius = 5
    border_size = 4
    border_color = QColor(150, 150, 150)
    border_color_selected = QColor(250, 250, 250)
    border_color_hover = QColor(250, 150, 150)
    bg_color = QColor(100, 100, 100)
    title_size = 9
    info_size = 7
    text_scale = 1.8
    text_font = "Times"
    title_color = QColor(255, 255, 255)
    info_color = QColor(200, 200, 200)
    port_size = 10
    port_border = 2
    port_top = 40
    port_bottom = 10
    port_diff = 15

    def __init__(self, scene, x, y, w, h, title, pins):
        super().__init__()
        self.scene = scene
        self.width = w
        self.height = h
        self.title = title
        self.pins = pins
        if x is not None and y is not None:
            self.setPos(x, y)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.hover = False

    def port_pos(self, port, other_node):
        pos = self.pos()
        pos_x = pos.x()
        pos_y = pos.y()
        opos = other_node.pos()
        if pos_x < opos.x():
            pos_x += self.width - 8
        else:
            pos_x += 8
        if port in self.pins:
            idx = list(self.pins).index(port)
            pos_y += self.radius + idx * 16 + 8

        return QPointF(pos_x, pos_y)

    def boundingRect(self):
        self.height = len(self.pins) * 16 + self.radius * 2
        return QRectF(0, 0, self.width, self.height)

    def paintPort(self, painter, x, y):
        painter.fillRect(QRectF(x - 5, y - 5, 10, 10), Qt.GlobalColor.yellow)
        painter.fillRect(QRectF(x - 4, y - 4, 8, 8), Qt.GlobalColor.black)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)

        if self.hover:
            pen = QPen(self.border_color_hover, self.border_size)
        elif self.isSelected():
            pen = QPen(self.border_color_selected, self.border_size)
        else:
            pen = QPen(self.border_color, self.border_size)

        # path
        rect = self.boundingRect()
        path = QPainterPath()
        path.addRoundedRect(rect, self.radius, self.radius)
        painter.setClipPath(path)

        # background
        brush = QBrush(self.bg_color)
        painter.setBrush(brush)
        painter.fillPath(path, painter.brush())

        # pin text
        painter.setPen(QPen(self.title_color, 1))
        painter.setFont(QFont(self.text_font, self.title_size))
        py = self.radius
        for pin_name, pin_title in self.pins.items():
            # painter.fillRect(QRectF(0, py, self.width, 16), Qt.GlobalColor.black)
            # painter.drawRect(QRectF(0, py, self.width, 16))
            if py != self.radius and pin_title[0] != "-":
                painter.setPen(QPen(self.info_color, 1))
                self.paintPort(painter, 8, py + 8)
                self.paintPort(painter, self.width - 8, py + 8)
                painter.drawText(QRectF(0, py, self.width, 16), Qt.AlignmentFlag.AlignCenter, pin_title)
            else:
                painter.setPen(QPen(self.title_color, 1))
                painter.drawText(QRectF(0, py - 2, self.width, 16), Qt.AlignmentFlag.AlignCenter, pin_title)
            py += 16

        # border
        painter.setPen(pen)
        painter.strokePath(path, painter.pen())

    def hoverEnterEvent(self, event):
        self.hover = True
        self.update()

    def hoverLeaveEvent(self, event):
        self.hover = False
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        QGraphicsItem.mouseReleaseEvent(self, event)


class NodeScene(QGraphicsScene):
    def __init__(self, x, y, w, h, parent):
        super().__init__(x, y, w, h)
        self.parent = parent
        self.setBackgroundBrush(QColor("#262626"))

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        """
        zoom = self.parent.view.getZoom()
        if zoom < 0.5:
            return
        left, right = floor(rect.left()), ceil(rect.right())
        top, bottom = floor(rect.top()), ceil(rect.bottom())
        grid_points = []
        for x in range(left - (left % grid_size), right, grid_size):
            for y in range(top - (top % grid_size), bottom, grid_size):
                grid_points.append(QPoint(x, y))

        if len(grid_points) > 0:
            pen = QPen(grid_color)
            pen.setWidthF(1)
            painter.setPen(pen)
            painter.drawPoints(grid_points)
        """


class NodeViewer(QGraphicsView):
    def __init__(self, scene):
        super().__init__()
        self.scene = scene
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setTransformationAnchor(self.ViewportAnchor.AnchorUnderMouse)

        self.button_pressed = 0
        self.mouse_pos_last = QPoint()
        self.mouse_pos = QPoint()

    def getZoom(self):
        transform = self.transform()
        return transform.m11()

    def setZoom(self, zoomFactor):
        transform = self.transform()
        transform.reset()
        transform.scale(zoomFactor, zoomFactor)
        self.setTransform(transform)

    def wheelEvent(self, event):
        zoom = self.getZoom()
        angle = event.angleDelta().y()
        zoomFactor = max(min(1 + (angle / 1000), 1.2), 0.8)
        if zoom < 0.1 and zoomFactor < 1.0:
            return
        if self.getZoom() > 5.0 and zoomFactor > 1.0:
            return
        self.scale(zoomFactor, zoomFactor)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        self.mouse_pos = event.pos()
        self.button_pressed = event.button()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.mouse_pos = event.pos()
        self.button_pressed = 0
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.mouse_pos_last = event.pos()
        if self.button_pressed in [Qt.LeftButton]:
            pass

        elif self.button_pressed in [Qt.MiddleButton]:
            offset = self.mouse_pos - event.pos()
            self.mouse_pos = event.pos()
            dx, dy = offset.x(), offset.y()
            self.horizontalScrollBar().setValue(int(self.horizontalScrollBar().value() + dx))
            self.verticalScrollBar().setValue(int(self.verticalScrollBar().value() + dy))

        super().mouseMoveEvent(event)


class MainWindow(QMainWindow):
    def __init__(self, inifile):
        super().__init__()
        self.setWindowTitle("HalView")
        self.resize(1200, 900)

        self.scene = NodeScene(-5000, -5000, 12000, 12000, self)
        self.view = NodeViewer(self.scene)
        self.view.setZoom(1.0)

        graph = halgraph.HalGraph()
        svg_data = graph.svg(inifile, clustering=False, fill="=000.000")
        open("/tmp/g.svg", "w").write(svg_data.decode())

        self.root = ET.fromstring(svg_data)
        if self.root is None:
            print("ERROR parsing ini file")
            exit(0)

        self.h = hal.component(f"halview-{uuid.uuid4()}")

        button_fit = QPushButton("FIT")
        button_fit.clicked.connect(self.fit_view)

        vboxMain = QVBoxLayout()
        vboxMain.addWidget(button_fit)
        vboxMain.addWidget(self.view)

        self.main = QWidget()
        self.setCentralWidget(self.main)
        self.main.setLayout(vboxMain)

        self.readGraph()
        self.show()
        self.fit_view()

        # self.runTimer()
        self.timer = QTimer()
        self.timer.timeout.connect(self.runTimer)
        self.timer.start(100)

    def readGraph(self):
        self.pinsdict = {}
        self.nodesdict = {}
        nodes = self.root.findall(".//*[@class='node']")
        for node in nodes:
            title = node.find(".//{http://www.w3.org/2000/svg}title")
            if title is not None:
                polygon = node.find(".//{http://www.w3.org/2000/svg}polygon")
                x1 = float(polygon.attrib["points"].split()[0].split(",")[0])
                y1 = float(polygon.attrib["points"].split()[0].split(",")[1])
                x2 = float(polygon.attrib["points"].split()[2].split(",")[0])
                y2 = float(polygon.attrib["points"].split()[2].split(",")[1])
                for polygon in node.findall(".//{http://www.w3.org/2000/svg}polygon"):
                    for point in polygon.attrib["points"].split():
                        x, y = point.split(",")
                        x1 = min(float(x), x1)
                        y1 = min(float(y), y1)
                        x2 = max(float(x), x2)
                        y2 = max(float(y), y2)

                pins = {}
                for text in node.findall(".//{http://www.w3.org/2000/svg}text"):
                    pin_name = text.text.split("=")[0]
                    pins[pin_name] = text.text
                    if title.text != pin_name:
                        self.pinsdict[f"{title.text}.{pin_name.strip('-')}"] = (title.text, pin_name)

                w = abs(x2 - x1) + 50
                h = abs(y2 - y1)
                w = max(w, 70)
                h = max(h, 40)
                self.nodesdict[title.text] = MyNode(self.scene, x1 + 500, y1 + 1300, w, h, title.text, pins)
                self.scene.addItem(self.nodesdict[title.text])

        self.edges = {}
        nodes = self.root.findall(".//*[@class='edge']")
        for node in nodes:
            title = node.find(".//{http://www.w3.org/2000/svg}title")
            if title is not None:
                begin, end = title.text.split("->")
                begin_node, begin_pin = begin.split(":")
                end_node, end_pin = end.split(":")
                edge = NodeEdge(self.scene, self.nodesdict[begin_node], begin_pin, self.nodesdict[end_node], end_pin)
                self.scene.addItem(edge)
                pin = f"{begin_node}.{begin_pin}"
                if pin not in self.edges:
                    self.edges[pin] = []
                self.edges[pin].append(edge)

    def runTimer(self):
        # get hal data
        listOfDicts = hal.get_info_pins()
        updates = set()
        for part in listOfDicts:
            pinName = part.get("NAME")
            pinValue = part.get("VALUE")
            pinType = part.get("TYPE")
            dataColor = Qt.GlobalColor.white
            if pinType == 1:
                if pinValue:
                    dataColor = Qt.GlobalColor.green
                else:
                    dataColor = Qt.GlobalColor.red
            elif pinType == 2:
                pinValue = f"{pinValue:0.3f}"
            if pinName in self.pinsdict:
                node_name, pin_name = self.pinsdict[pinName]
                node = self.nodesdict[node_name]
                text = f"{pin_name}={pinValue}"
                if node.pins[pin_name] != text:
                    if pin_name[0] == "-":
                        node.pins[pin_name] = f"{pin_name}={pinValue}-"
                    else:
                        node.pins[pin_name] = f"{pin_name}={pinValue}"
                    updates.add(node)

            if pinName in self.edges:
                for edge in self.edges[pinName]:
                    edge.color = dataColor
                    updates.add(edge)

        for node in updates:
            node.update()

    def fit_view(self):
        min_x = max_size
        min_y = max_size
        max_x = -max_size
        max_y = -max_size
        for item in self.scene.items():
            if isinstance(item, NodeEdge):
                continue
            px = item.pos().x()
            py = item.pos().y()
            min_x = min((min_x, px))
            min_y = min((min_y, py))
            max_x = max(max_x, px + item.width)
            max_y = max(max_y, py + item.height)
        # calc scale and offsets
        if min_x == max_size:
            min_x = 0
            max_x = 800
            min_y = 0
            max_y = 800
        w = max_x - min_x
        h = max_y - min_y
        slider_size = 20
        vw = self.view.width() - slider_size
        vh = self.view.height() - slider_size

        border = 50
        scale = min((vw - border) / w, (vh - border) / h)
        pos_x = int(min_x * scale)
        pos_y = int(min_y * scale)
        # center
        diff_x = vw - w * scale
        diff_y = vh - h * scale
        pos_x -= diff_x / 2
        pos_y -= diff_y / 2

        self.view.setZoom(scale)
        self.view.horizontalScrollBar().setSliderPosition(int(pos_x))
        self.view.verticalScrollBar().setSliderPosition(int(pos_y))

        self.update()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ini", help="ini file", nargs="?", type=str, default=None)
    args = parser.parse_args()

    if args.ini:
        app = QApplication(sys.argv)
        window = MainWindow(args.ini)
        window.show()
        app.exec()
