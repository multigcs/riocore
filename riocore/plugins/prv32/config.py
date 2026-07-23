import os
import sys

from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)

try:
    from PyQt5.Qsci import QsciLexerCPP, QsciScintilla

    editor_widget = QsciScintilla
except Exception:
    editor_widget = QTextEdit

plugin_path = os.path.dirname(__file__)


class config:
    def __init__(self, instance, styleSheet=None, parent=None):
        self.instance = instance
        self.parent = parent
        self.plugin_setup = instance.plugin_setup
        self.update_flag = False
        self.ctypes = ("bool", "int8_t", "uint8_t", "int16_t", "uint16_t", "int32_t", "uint32_t")
        self.dirs = ("output", "input")
        self.vcombos = {}
        self.dcombos = {}

    def edited(self):
        if self.update_flag:
            return
        self.plugin_setup["gpios"] = {}
        for row in range(self.pin_table.rowCount()):
            cell0 = self.pin_table.item(row, 0)
            if cell0:
                name = cell0.text()
                if name:
                    self.plugin_setup["gpios"][name] = {"name": name}

        self.plugin_setup["riovars"] = {}
        for row in range(self.variable_table.rowCount()):
            cell0 = self.variable_table.item(row, 0)
            if not cell0:
                continue
            name = cell0.text()
            if not name:
                continue
            if name in self.vcombos:
                ctype = self.vcombos[name].currentText()
                direction = self.dcombos[name].currentText()
            else:
                ctype = "uint32_t"
                direction = "output"
            self.plugin_setup["riovars"][name] = {"ctype": ctype, "dir": direction}

        self.update()

    def update(self):
        self.update_flag = True

        pin_n = 0
        for pin_name in self.plugin_setup.get("gpios", {}):
            self.pin_table.setRowCount(pin_n + 1)
            pitem = QTableWidgetItem(pin_name)
            self.pin_table.setItem(pin_n, 0, pitem)
            pin_n += 1
        self.pin_table.setRowCount(pin_n + 1)

        self.vcombos = {}
        self.dcombos = {}
        variable_n = 0
        for variable_name, variable_data in self.plugin_setup.get("riovars", {}).items():
            self.variable_table.setRowCount(variable_n + 1)
            self.variable_table.setItem(variable_n, 0, QTableWidgetItem(variable_name))

            ctype_set = variable_data.get("ctype", "uint32_t")
            self.variable_table.setItem(variable_n, 1, QTableWidgetItem())
            self.vcombos[variable_name] = QComboBox()
            for ctype in self.ctypes:
                self.vcombos[variable_name].addItem(ctype)
            self.vcombos[variable_name].setCurrentIndex(self.ctypes.index(ctype_set))
            self.vcombos[variable_name].setEditable(False)
            self.vcombos[variable_name].activated.connect(self.edited)
            self.variable_table.setCellWidget(variable_n, 1, self.vcombos[variable_name])

            dir_set = variable_data.get("dir", "output")
            self.variable_table.setItem(variable_n, 2, QTableWidgetItem())
            self.dcombos[variable_name] = QComboBox()
            for rdirs in self.dirs:
                self.dcombos[variable_name].addItem(rdirs)
            self.dcombos[variable_name].setCurrentIndex(self.dirs.index(dir_set))
            self.dcombos[variable_name].setEditable(False)
            self.dcombos[variable_name].activated.connect(self.edited)
            self.variable_table.setCellWidget(variable_n, 2, self.dcombos[variable_name])

            variable_n += 1

        self.variable_table.setRowCount(variable_n + 1)
        self.variable_table.setItem(variable_n, 0, QTableWidgetItem(""))
        source_text = self.plugin_setup.get("source", open(os.path.join(os.path.dirname(__file__), "src", "main.c"), "r").read())
        self.source.setText(source_text)
        self.update_flag = False

    def run(self):
        dialog = QDialog()
        dialog.setWindowTitle("select halpin")
        dialog.setMinimumWidth(800)
        dialog.setMinimumHeight(600)
        dialog.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        dialog.buttonBox.accepted.connect(dialog.accept)
        dialog.layout = QVBoxLayout()

        hlayout = QHBoxLayout()
        dialog.layout.addLayout(hlayout, stretch=1)

        left_layout = QVBoxLayout()
        hlayout.addLayout(left_layout, stretch=1)

        left_layout.addWidget(QLabel("Periphery"), stretch=0)

        left_layout.addWidget(QLabel("gpios"), stretch=0)
        self.pin_table = QTableWidget()
        self.pin_table.setColumnCount(1)
        self.pin_table.setHorizontalHeaderItem(0, QTableWidgetItem("Name"))
        header = self.pin_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        self.pin_table.itemChanged.connect(self.edited)
        left_layout.addWidget(self.pin_table, stretch=1)

        left_layout.addWidget(QLabel("RIO-Variables"), stretch=0)
        self.variable_table = QTableWidget()
        self.variable_table.setColumnCount(3)
        self.variable_table.setHorizontalHeaderItem(0, QTableWidgetItem("Name"))
        self.variable_table.setHorizontalHeaderItem(1, QTableWidgetItem("Type"))
        self.variable_table.setHorizontalHeaderItem(2, QTableWidgetItem("Dir"))
        header = self.variable_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        self.variable_table.itemChanged.connect(self.edited)
        left_layout.addWidget(self.variable_table, stretch=1)

        right_layout = QVBoxLayout()
        hlayout.addLayout(right_layout, stretch=3)

        right_layout.addWidget(QLabel("Source:"))

        self.source = editor_widget()
        if editor_widget != QTextEdit:
            lexer = QsciLexerCPP()
            self.source.setLexer(lexer)
        right_layout.addWidget(self.source)

        dialog.layout.addWidget(dialog.buttonBox)
        dialog.setLayout(dialog.layout)

        self.update()

        if dialog.exec():
            if editor_widget == QTextEdit:
                self.plugin_setup["source"] = self.source.toPlainText()
            else:
                self.plugin_setup["source"] = self.source.text()


if __name__ == "__main__":
    import json
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    class mock_instance:
        def __init__(self):
            self.instances_name = "prv32"
            self.plugin_setup = {
                "gpios": {"pwm": {}, "dir": {}},
                "riovars": {"pulse": {"ctype": "uint32_t"}, "pause": {"ctype": "int32_t", "dir": "input"}, "enable": {"ctype": "bool", "dir": "output"}},
                "source": """
#include <rio.h>

int main() {

    pinMode(GPIO_PWM, OUTPUT);
    digitalWrite(GPIO_PWM, HIGH);

    while (1) {


        digitalWrite(GPIO_PWM, LOW);
        delay(RIO_PULSE);

        digitalWrite(GPIO_PWM, HIGH);
        delay(RIO_PAUSE);

    }
    return 0;
}
""",
            }

    instance = mock_instance()
    config_gui = config(instance)
    config_gui.run()
    print(json.dumps(instance.plugin_setup, indent=4))
