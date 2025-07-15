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

class AddLabelDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Label")
        self.setGeometry(200, 200, 300, 150)

        self.init_ui()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()

        # Name layout
        node_layout = QHBoxLayout()
        node_label = QLabel("Label Name:")
        self.node_name_textedit = QLineEdit()
        #self.node_name.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        node_layout.addWidget(node_label)
        node_layout.addWidget(self.node_name_textedit)
        main_layout.addLayout(node_layout)

        # Dialog buttons (OK, Cancel)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

    def get_selected_values(self):
        # Returns the selected node and event.
        node_text = self.node_name_textedit.text()
        return node_text
