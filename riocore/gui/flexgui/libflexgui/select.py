import shutil

from PyQt5.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QLabel, QVBoxLayout


class editor_dialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Editor not found!")

        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("The Editor in the ini file is not installed\nSelect the Editor you want to use.")
        self.layout.addWidget(message)
        self.choice = QComboBox()
        self.choice.addItem("Select", False)

        editor_dict = {
            "Gedit": "gedit",
            "Geany": "geany",
            "Pyroom": "pyroom",
            "Pluma": "pluma",
            "Scite": "scite",
            "Kwrite": "kwrite",
            "Kate": "kate",
            "Mousepad": "mousepad",
            "Jedit": "jedit",
            "XED": "xed",
        }
        editor_list = []
        for key, value in editor_dict.items():  # get a list of installed editors
            if shutil.which(value) is not None:
                editor_list.append([key, value])

        for key, value in editor_list:
            self.choice.addItem(key, value)
        self.layout.addWidget(self.choice)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
