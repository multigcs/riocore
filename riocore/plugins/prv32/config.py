import os
import sys

from PyQt5.QtWidgets import (
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

plugin_path = os.path.dirname(__file__)


class config:
    def __init__(self, instance, styleSheet=None, parent=None):
        self.instance = instance
        self.parent = parent
        self.plugin_setup = instance.plugin_setup
        self.update_flag = False

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
            cell1 = self.variable_table.item(row, 1)
            cell2 = self.variable_table.item(row, 2)
            if cell0 and cell1 and cell2:
                name = cell0.text()
                bits = cell1.text()
                direction = cell2.text()
                if name and bits.isdigit() and direction in {"input", "output"}:
                    self.plugin_setup["riovars"][name] = {"size": int(bits), "dir": direction}

        self.update()

    def update(self):
        self.update_flag = True
        self.peri_uarts.setValue(1)
        self.peri_pwms.setValue(1)

        pin_n = 0
        for pin_name in self.plugin_setup.get("gpios", {}):
            self.pin_table.setRowCount(pin_n + 1)
            pitem = QTableWidgetItem(pin_name)
            self.pin_table.setItem(pin_n, 0, pitem)
            pin_n += 1
        self.pin_table.setRowCount(pin_n + 1)

        valiable_n = 0
        for valiable_name, valiable_data in self.plugin_setup.get("riovars", {}).items():
            self.variable_table.setRowCount(valiable_n + 1)
            self.variable_table.setItem(valiable_n, 0, QTableWidgetItem(valiable_name))
            self.variable_table.setItem(valiable_n, 1, QTableWidgetItem(str(valiable_data.get("size", "32"))))
            self.variable_table.setItem(valiable_n, 2, QTableWidgetItem(str(valiable_data.get("dir", "output"))))
            valiable_n += 1

        self.variable_table.setRowCount(valiable_n + 1)
        self.variable_table.setItem(valiable_n, 0, QTableWidgetItem(""))
        self.variable_table.setItem(valiable_n, 1, QTableWidgetItem("32"))
        self.variable_table.setItem(valiable_n, 2, QTableWidgetItem("output"))
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

        self.peri_uarts = QSpinBox()
        self.peri_uarts.setMinimum(0)
        self.peri_uarts.setMaximum(1)
        left_layout.addWidget(QLabel("Uart's"))
        left_layout.addWidget(self.peri_uarts, stretch=0)

        self.peri_pwms = QSpinBox()
        self.peri_pwms.setMinimum(0)
        self.peri_pwms.setMaximum(16)
        left_layout.addWidget(QLabel("PWM's"))
        left_layout.addWidget(self.peri_pwms, stretch=0)

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
        self.variable_table.setHorizontalHeaderItem(1, QTableWidgetItem("Size"))
        self.variable_table.setHorizontalHeaderItem(2, QTableWidgetItem("Dir"))
        header = self.variable_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        self.variable_table.itemChanged.connect(self.edited)
        left_layout.addWidget(self.variable_table, stretch=1)

        right_layout = QVBoxLayout()
        hlayout.addLayout(right_layout, stretch=3)

        right_layout.addWidget(QLabel("Source:"))
        self.source = QTextEdit()
        right_layout.addWidget(self.source)

        dialog.layout.addWidget(dialog.buttonBox)
        dialog.setLayout(dialog.layout)

        self.update()

        if dialog.exec():
            self.plugin_setup["source"] = self.source.toPlainText()


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
                "riovars": {"pulse": {"size": 32}, "pause": {"size": 32, "dir": "input"}, "enable": {"size": 1, "dir": "output"}},
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
