import argparse
import os
import sys
import xml.etree.ElementTree as ET

import hal

from PyQt5.QtCore import QByteArray, QRectF, QTimer, Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QMainWindow,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

if os.path.isfile(os.path.join("riocore", "__init__.py")):
    sys.path.insert(0, os.getcwd())

from riocore.gui import halgraph


class SvgWidget(QSvgWidget):
    def __init__(self, *args):
        QSvgWidget.__init__(self, *args)
        self.scale = 1.0

    def paintEvent(self, event):
        renderer = self.renderer()
        if renderer is not None:
            painter = QPainter(self)
            size = renderer.defaultSize()
            renderer.render(painter, QRectF(0, 0, self.width() * self.scale, self.height() * self.scale))
            painter.end()
            if size.width() > 10:
                self.setFixedWidth(int(size.width() * self.scale))
                self.setFixedHeight(int(size.height() * self.scale))


if __name__ == "__main__":

    class MainWindow(QMainWindow):
        def __init__(self, inifile):
            super().__init__()
            self.setWindowTitle("HalView")
            self.resize(800, 600)

            graph = halgraph.HalGraph()
            svg_data = graph.svg(inifile, fill="=000.000")
            self.root = ET.fromstring(svg_data)
            if self.root is None:
                print("ERROR parsing ini file")
                exit(0)

            """
            bg = self.root.find(".//{http://www.w3.org/2000/svg}polygon")
            if bg is not None:
                bg.attrib["fill"] = "gray"

            for poly in self.root.findall(".//{http://www.w3.org/2000/svg}polygon[@stroke='black']"):
                poly.attrib["stroke"] = "white"
                poly.attrib["fill"] = "gray"
            """

            self.h = hal.component("halview5")

            vboxMain = QVBoxLayout()

            self.svgWidget = SvgWidget()

            scroll = QScrollArea()
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll.setWidgetResizable(True)
            scroll.setWidget(self.svgWidget)
            vboxMain.addWidget(scroll)

            scale = QDoubleSpinBox()
            scale.setDecimals(1)
            scale.setSingleStep(0.1)
            scale.setMinimum(0.01)
            scale.setMaximum(10.0)
            scale.setValue(1.0)
            scale.valueChanged.connect(self.scale)
            vboxMain.addWidget(scale)

            self.main = QWidget()
            self.setCentralWidget(self.main)
            self.main.setLayout(vboxMain)

            self.show()

            self.timer = QTimer()
            self.timer.timeout.connect(self.runTimer)
            self.timer.start(100)

        def scale(self, val):
            self.svgWidget.scale = val

        def runTimer(self):
            # get hal data
            data = {}
            listOfDicts = hal.get_info_pins()
            for part in listOfDicts:
                pinName = part.get("NAME")
                pinValue = part.get("VALUE")
                pinType = part.get("TYPE")
                # print(pinName, pinValue, pinType)
                data[pinName] = {
                    "text": str(pinValue),
                    "color": "black",
                    "type": pinType,
                }
                if pinType == 1:
                    if pinValue:
                        data[pinName]["color"] = "red"
                    else:
                        data[pinName]["color"] = "black"
                    # data[pinName]["text"] = ""
                elif pinType == 2:
                    data[pinName]["text"] = f"{pinValue:0.3f}"

            # update edges in svg
            edges = self.root.findall(".//*[@class='edge']")
            for edge in edges:
                eid = edge.attrib["id"]
                if eid in data:
                    path = edge.find(".//{http://www.w3.org/2000/svg}path")
                    if path is not None:
                        path.attrib["stroke"] = data[eid]["color"]
                    polygon = edge.find(".//{http://www.w3.org/2000/svg}polygon")
                    if polygon is not None:
                        polygon.attrib["stroke"] = data[eid]["color"]
                        polygon.attrib["fill"] = data[eid]["color"]
                    # text = edge.find(".//{http://www.w3.org/2000/svg}text")
                    # if text is not None:
                    #    text.text = data[eid]["text"]

            nodes = self.root.findall(".//*[@class='node']")
            for node in nodes:
                title = node.find(".//{http://www.w3.org/2000/svg}title")
                if title is not None:
                    center = 0
                    for element in node:
                        if element.tag == "{http://www.w3.org/2000/svg}polygon":
                            x1 = float(element.attrib["points"].split()[0].split(",")[0])
                            x2 = float(element.attrib["points"].split()[2].split(",")[0])
                            center = x1 + (x2 - x1) / 2
                        elif element.tag == "{http://www.w3.org/2000/svg}text":
                            pin = element.text.split("=")[0]
                            eid = f"{title.text}.{pin}"
                            if eid in data:
                                # print(eid, pin)
                                element.attrib["fill"] = data[eid]["color"]
                                if data[eid]["text"]:
                                    element.attrib["text-anchor"] = "middle"
                                    element.attrib["x"] = str(center)
                                    element.text = f"{pin}={data[eid]['text']}"

            self.svgWidget.load(QByteArray(ET.tostring(self.root)))

    parser = argparse.ArgumentParser()
    parser.add_argument("ini", help="ini file", nargs="?", type=str, default=None)
    args = parser.parse_args()

    if args.ini:
        app = QApplication(sys.argv)
        window = MainWindow(args.ini)
        window.show()
        app.exec()
