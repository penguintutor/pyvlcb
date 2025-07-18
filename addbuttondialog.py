import sys
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QLabel,
    QPushButton,
    QDialogButtonBox,
    QLineEdit
)
from devicemodel import device_model

class AddButtonDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Button")
        self.setGeometry(200, 200, 300, 150)

        self.init_ui()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        
        # Button type
        type_layout = QHBoxLayout()
        type_label = QLabel("Button type:")
        self.type_combo = QComboBox()
        #self.type_combo.addItem("None")
        self.type_combo.addItems(["circle", "rectangle"])
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        main_layout.addLayout(type_layout)

        # Name layout
        id_layout = QHBoxLayout()
        id_label = QLabel("Label ID:")
        self.node_id_textedit = QLineEdit()
        id_layout.addWidget(id_label)
        id_layout.addWidget(self.node_id_textedit)
        main_layout.addLayout(id_layout)

        # Dialog buttons (OK, Cancel)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

    def get_selected_values(self):
        # Returns the selected node and event.
        selected_type = self.type_combo.currentText()
        id_text = self.node_id_textedit.text()
        return [id_text, selected_type]
